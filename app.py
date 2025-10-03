# app.py (Sanity Check Version)
import streamlit as st
import pandapower as pp
from src.engine import load_case, run_powerflow

st.set_page_config(page_title="Power Grid Sanity Check", layout="wide")
st.title("⚠️ Power Grid Sanity Check")
st.info("This is a temporary app to diagnose a critical failure. Click the button to begin.")

run_button = st.button("▶️ Run Diagnostic", type="primary")

if run_button:
    try:
        st.write("---")
        st.write("✅ **Step 1:** Loading `case_ieee30`...")
        net = load_case("case_ieee30")
        st.write("✅ **Step 2:** Case loaded successfully.")
        
        st.write("✅ **Step 3:** Applying engineering fix (adding 20MVAr shunt to bus 29)...")
        pp.create_shunt(net, bus=29, q_mvar=20, name="Diagnostic Capacitor Bank")
        st.write("✅ **Step 4:** Shunt added to the network object.")

        st.write("⏳ **Step 5:** Attempting the `run_powerflow` function call...")
        
        # This is the step we suspect is crashing.
        success, results = run_powerflow(net)
        
        # If we see the message below, it means the function returned without crashing.
        st.write("✅ **Step 6:** `run_powerflow` function executed and returned a result.")
        
        if success:
            st.success("🎉 Power Flow Converged Successfully!")
            st.dataframe(results["bus_results"])
        else:
            st.error(f"Power flow did NOT converge. Reason: {results.get('error', 'Unknown')}")

    except Exception as e:
        st.error(f"A critical exception occurred during the diagnostic test: {e}")

