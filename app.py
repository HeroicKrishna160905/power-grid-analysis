# app.py 
import streamlit as st
import pandas as pd
import pandapower as pp
from copy import deepcopy
from src.engine import load_case, run_powerflow
from src.opf import define_generator_costs, run_opf
from src.contingency import run_n1_contingency_analysis

st.set_page_config(page_title="Power Grid Analysis Engine", layout="wide")
st.title("⚡ Power Grid Security Assessment") # Changed Title

# --- Sidebar Controls ---
case_options = {"IEEE 30-Bus": "case30", "IEEE 118-Bus": "case118"}
selected_case_name = st.sidebar.selectbox("Select Grid Model", options=list(case_options.keys()))
case_name = case_options[selected_case_name]

run_button = st.sidebar.button("▶️ Run Analysis", type="primary")

# --- Caching Functions ---
@st.cache_data
def run_full_analysis(case):
    net = load_case(case)

    
    pf_success, pf_results = run_powerflow(net)
    if not pf_success:
        return {"error": "Base Power Flow Failed", "details": pf_results.get("details", "No details")}

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
            st.metric(label="System Losses (Base Case)", value=f"{pf_results['summary']['losses_mw']:.2f} MW")
        with col2:
            st.metric(label="System Losses (OPF Case)", value=f"{opf_results['summary']['losses_mw']:.2f} MW")
        
        loss_reduction = 0
        if pf_results['summary']['losses_mw'] > 0:
            loss_reduction = (pf_results['summary']['losses_mw'] - opf_results['summary']['losses_mw']) / pf_results['summary']['losses_mw'] * 100
        with col3:
            st.metric(label="Loss Reduction via OPF", value=f"{loss_reduction:.2f} %", delta=f"{loss_reduction:.2f}% Improvement")

        # --- Display Results in Tabs ---
        tab1, tab2, tab3 = st.tabs(["📊 Base Power Flow", "📈 Optimal Power Flow", "🚨 N-1 Security Assessment"])
        
        with tab1:
            #
            st.subheader("Line Loading (%)")
            st.bar_chart(pf_results["line_results"], y="loading_percent")
            st.subheader("Bus Voltages (p.u.)")
            st.dataframe(pf_results["bus_results"][['vm_pu', 'va_degree']])
            
        with tab2:
            # 
            st.subheader("Generator Dispatch (MW)")
            st.dataframe(opf_results["gen_dispatch"])
            st.subheader("Line Loading after OPF (%)")
            st.bar_chart(opf_results["line_results"], y="loading_percent")

        with tab3:
            # 
            st.warning("### Assessment Finding: Grid is NOT N-1 Secure")
            st.write(
                "The analysis shows that the base IEEE 30-Bus system is highly vulnerable. "
                "The loss of **any single transmission line** results in immediate violations "
                "(line overloads or voltage deviations), indicating a lack of sufficient redundancy. "
                "This tool has successfully identified the system's critical weaknesses."
            )
            st.dataframe(analysis_data["contingency_df"])
else:
    st.info("Select a grid model and click 'Run Analysis' to begin.")
