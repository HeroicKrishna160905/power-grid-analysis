# app.py
import streamlit as st
import pandas as pd
import pandapower as pp
from src.engine import load_case, run_powerflow
from src.opf import define_generator_costs, run_opf
from src.contingency import run_n1_contingency_analysis

st.set_page_config(page_title="Power Grid Analysis Engine", layout="wide")
st.title("⚡ Power Grid Analysis Engine")

# --- Sidebar Controls ---
st.sidebar.header("Configuration")
case_options = {"IEEE 30-Bus": "case_ieee30", "IEEE 118-Bus": "case_ieee118"}
selected_case_name = st.sidebar.selectbox("Select Grid Model", options=list(case_options.keys()))
case_name = case_options[selected_case_name]

run_button = st.sidebar.button("▶️ Run Analysis", type="primary")

# --- Caching Functions ---
@st.cache_data
def run_full_analysis(case):
    # 1. Load network
    net = load_case(case)

    # --- ENGINEERING FIXES TO IMPROVE GRID STABILITY ---
    # The standard IEEE test cases are often not N-1 secure. We can add
    # reinforcements here to solve contingency violations and demonstrate
    # the impact of grid improvements.
    if case == "case_ieee30":
        # Add a shunt capacitor to a weak bus (e.g., Bus 29) to provide
        # reactive power support and prevent voltage collapse during contingencies.
        pp.create_shunt(net, bus=29, q_mvar=50, name="Capacitor Bank at Bus 29")
    # --- All subsequent analyses will now run on this *reinforced* network ---

    # 2. Base Power Flow on the reinforced network
    pf_success, pf_results = run_powerflow(net)
    if not pf_success:
        return {"error": "Base Power Flow Failed on the reinforced network."}

    # 3. Optimal Power Flow on a copy of the reinforced network
    opf_net = net.copy() # Use a copy to keep base case results clean
    costs = {('gen', i): (i + 1) * 10 for i in opf_net.gen.index} # Example costs
    opf_net = define_generator_costs(opf_net, costs)
    opf_success, opf_results = run_opf(opf_net)
    if not opf_success:
        return {"error": "Optimal Power Flow Failed on the reinforced network."}

    # 4. Contingency Analysis on the reinforced network
    contingency_df = run_n1_contingency_analysis(pf_results['net'])

    return {
        "pf_results": pf_results,
        "opf_results": opf_results,
        "contingency_df": contingency_df
    }

# --- Main Page ---
if run_button:
    with st.spinner(f"Running analysis for {selected_case_name}..."):
        analysis_data = run_full_analysis(case_name)

    if "error" in analysis_data:
        st.error(analysis_data["error"])
    else:
        st.success("Analysis Complete!")
        
        pf_results = analysis_data["pf_results"]
        opf_results = analysis_data["opf_results"]
        
        # --- Display KPIs ---
        st.header("Key Performance Indicators (KPIs)")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                label="System Losses (Base Case)", 
                value=f"{pf_results['summary']['losses_mw']:.2f} MW",
                help=f"{pf_results['summary']['loss_percent']:.2f}% of total generation"
            )
        with col2:
            st.metric(
                label="System Losses (OPF Case)", 
                value=f"{opf_results['summary']['losses_mw']:.2f} MW",
                help=f"{opf_results['summary']['loss_percent']:.2f}% of total generation"
            )
        
        # Avoid division by zero if losses are zero
        initial_losses = pf_results['summary']['losses_mw']
        if initial_losses > 0:
            loss_reduction = (initial_losses - opf_results['summary']['losses_mw']) / initial_losses * 100
        else:
            loss_reduction = 0

        with col3:
            st.metric(
                label="Loss Reduction via OPF",
                value=f"{loss_reduction:.2f} %",
                delta=f"{loss_reduction:.2f}% Improvement", delta_color="normal"
            )

        # --- Display Results in Tabs ---
        tab1, tab2, tab3 = st.tabs(["📊 Base Power Flow", "📈 Optimal Power Flow", "🚨 N-1 Contingency Report"])
        
        with tab1:
            st.subheader("Line Loading (%)")
            st.bar_chart(pf_results["line_results"], y="loading_percent")
            st.subheader("Bus Voltages (p.u.)")
            st.dataframe(pf_results["bus_results"][['vm_pu', 'va_degree']])
            
        with tab2:
            st.subheader("Generator Dispatch (MW)")
            st.dataframe(opf_results["gen_dispatch"][['p_mw', 'q_mvar']])
            st.subheader("Line Loading after OPF (%)")
            st.bar_chart(opf_results["line_results"], y="loading_percent")

        with tab3:
            st.dataframe(analysis_data["contingency_df"])
else:
    st.info("Select a grid model and click 'Run Analysis' to begin.")
