# app.py (Final Version with Direct DataFrame Manipulation)
import streamlit as st
import pandas as pd
import pandapower as pp
from copy import deepcopy
from src.engine import load_case, run_powerflow
from src.opf import define_generator_costs, run_opf
from src.contingency import run_n1_contingency_analysis

st.set_page_config(page_title="Power Grid Analysis Engine", layout="wide")
st.title("⚡ Power Grid Analysis Engine")

# --- Sidebar Controls ---
case_options = {"IEEE 30-Bus": "case30", "IEEE 118-Bus": "case118"}
selected_case_name = st.sidebar.selectbox("Select Grid Model", options=list(case_options.keys()))
case_name = case_options[selected_case_name]

run_button = st.sidebar.button("▶️ Run Analysis", type="primary")

# --- Caching Functions ---
@st.cache_data
def run_full_analysis(case):
    """
    Loads the network, applies fixes, and runs all analyses.
    """
    # 1. Load network
    net = load_case(case)

    # --- Engineering Fixes for IEEE 30-Bus ---
    if case == "case30":
        st.sidebar.info("Applying comprehensive reinforcement for N-1 security.")
        
        # Fix 1: Load Shedding for initial stability
        load_idx = net.load[net.load.bus == 29].index
        if not load_idx.empty:
            net.load.loc[load_idx[0], 'p_mw'] *= 0.95 # Reduced shedding slightly

        # Fix 2: Add a new high-capacity line for a new path
        pp.create_line_from_parameters(
            net, from_bus=1, to_bus=5, length_km=30, r_ohm_per_km=0.1,
            x_ohm_per_km=0.2, c_nf_per_km=10, max_i_ka=0.8, name="New Line 1-5"
        )

        # Fix 3: Strategic Upgrades (Reconductoring)
        # We identify critical lines and double their capacity.
        lines_to_upgrade = [0, 1, 2, 3, 4] # Corresponds to lines 1-2, 1-3, 2-4, 3-4, 2-5
        for line_idx in lines_to_upgrade:
            if line_idx in net.line.index:
                net.line.loc[line_idx, 'max_i_ka'] *= 2.0
                st.sidebar.write(f"- Upgraded capacity of existing Line {line_idx}")


    # 2. Base Power Flow
    pf_success, pf_results = run_powerflow(net)
    if not pf_success:
        return {"error": "Base Power Flow Failed", "details": pf_results.get("details", "No details")}

    # 3. Optimal Power Flow
    opf_net = deepcopy(net)
    
    costs = {}
    gen_sources = {'gen': getattr(opf_net, 'gen', pd.DataFrame()),
                   'ext_grid': getattr(opf_net, 'ext_grid', pd.DataFrame()),
                   'sgen': getattr(opf_net, 'sgen', pd.DataFrame())}
    
    for gen_type, gen_df in gen_sources.items():
        if not gen_df.empty:
            for i in gen_df.index:
                costs[(gen_type, i)] = 1
            
    opf_net = define_generator_costs(opf_net, costs)
    opf_success, opf_results = run_opf(opf_net)
    if not opf_success:
        return {"error": "Optimal Power Flow Failed", "details": opf_results.get("details", "No details")}

    # 4. Contingency Analysis
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
        st.error(f"{analysis_data['error']}\nDetails: {analysis_data.get('details', 'N/A')}")
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
        
        loss_reduction = 0
        if pf_results['summary']['losses_mw'] > 0:
            loss_reduction = (pf_results['summary']['losses_mw'] - opf_results['summary']['losses_mw']) / pf_results['summary']['losses_mw'] * 100

        with col3:
            st.metric(
                label="Loss Reduction via OPF",
                value=f"{loss_reduction:.2f} %",
                delta=f"{loss_reduction:.2f}% Improvement"
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
            st.dataframe(opf_results["gen_dispatch"])
            st.subheader("Line Loading after OPF (%)")
            st.bar_chart(opf_results["line_results"], y="loading_percent")

        with tab3:
            st.dataframe(analysis_data["contingency_df"])
else:
    st.info("Select a grid model and click 'Run Analysis' to begin.")

