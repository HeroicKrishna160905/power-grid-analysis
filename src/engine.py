 #src/engine.py
"""
Core engine for loading cases and running AC power flow.
Includes diagnostic tools for debugging convergence issues.
"""
import pandapower as pp
import pandapower.networks as pn
import pandas as pd

def load_case(case_name: str = "case_ieee30"):
    """
    Loads a standard pandapower network case by name.
    """
    if not hasattr(pn, case_name):
        raise ValueError(f"Unknown case: {case_name}. Please use a valid pandapower.networks case.")
    return getattr(pn, case_name)()

def run_powerflow(net, init="dc"):
    """
    Runs an AC power flow (pp.runpp) with safe error handling and result validation.
    Includes a diagnostic mode to debug convergence failures.
    """
    try:
        # First, try to run with the robust settings
        pp.runpp(net, enforce_q_lims=True, calculate_voltage_angles=True, init=init)
    except pp.LoadflowNotConverged as e:
        # --- NEW: DIAGNOSTIC MODE ---
        # If it fails, print a detailed report to the terminal and then raise the error.
        print("\n" + "="*50)
        print(" POWER FLOW FAILED TO CONVERGE. DIAGNOSTIC REPORT:")
        print("="*50)
        print(f"Error Details: {e}")
        
        # Check if there are any results at all to display
        if net.res_bus.empty:
            print("No results available. The solver failed at an early stage.")
        else:
            # Print the bus voltages from the last unconverged iteration
            print("\n--- Bus Voltages at Last Iteration ---")
            pd.set_option('display.max_rows', 150) # Ensure all buses are shown
            print(net.res_bus[['vm_pu', 'va_degree']])
            
            # Highlight buses with extreme voltage issues
            extreme_voltages = net.res_bus[(net.res_bus.vm_pu < 0.8) | (net.res_bus.vm_pu > 1.2)]
            if not extreme_voltages.empty:
                print("\n--- CRITICAL VOLTAGE ISSUES DETECTED AT: ---")
                print(extreme_voltages[['vm_pu']])
        
        print("="*50)
        print(" END OF DIAGNOSTIC REPORT")
        print("="*50 + "\n")

        # Re-raise the exception to stop the Streamlit app and show the error.
        # The useful information is now in your terminal.
        raise e

    # If successful, proceed as normal
    v_min, v_max = 0.95, 1.05
    bus_v = net.res_bus['vm_pu']
    line_loading = net.res_line['loading_percent']
    
    violations = {
        "voltage_violations": int(((bus_v < v_min) | (bus_v > v_max)).sum()),
        "overloaded_lines": int((line_loading > 100).sum())
    }
    
    results = {
        "net": net,
        "bus_results": net.res_bus,
        "line_results": net.res_line,
        "violations": violations,
        "summary": {
            "total_load_mw": net.load.p_mw.sum(),
            "total_gen_mw": net.res_gen.p_mw.sum(),
            "losses_mw": net.res_line.pl_mw.sum(),
            "loss_percent": net.res_line.pl_mw.sum() / net.res_gen.p_mw.sum() * 100 if net.res_gen.p_mw.sum() != 0 else 0
        }
    }
    return True, results

