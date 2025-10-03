# src/engine.py
"""
Core engine for loading cases and running AC power flow.
Includes "brute force" diagnostic tools that write directly to the
system error stream to guarantee visibility in logs.
"""
import pandapower as pp
import pandapower.networks as pn
import pandas as pd
import sys # Import the system library

def load_case(case_name: str = "case_ieee30"):
    """
    Loads a standard pandapower network case by name.
    """
    if not hasattr(pn, case_name):
        raise ValueError(f"Unknown case: {case_name}. Please use a valid pandapower.networks case.")
    return getattr(pn, case_name)()

def run_powerflow(net, init="dc"):
    """
    Runs an AC power flow (pp.runpp) and forces diagnostic output to the
    system error log on failure.
    """
    # Tell pandapower to NOT raise an error. We will check for convergence manually.
    # This guarantees our diagnostic code will run.
    try:
        # We explicitly disable numba to prevent warnings that clutter the log.
        pp.runpp(net, enforce_q_lims=True, calculate_voltage_angles=True, init=init, numba=False)
        converged = net["converged"]
    except Exception as e:
        # Catch any other unexpected errors during the run
        print(f"A critical pandapower error occurred before convergence check: {e}", file=sys.stderr)
        converged = False

    if not converged:
        # --- THIS IS THE GUARANTEED DIAGNOSTIC SECTION ---
        # We write directly to sys.stderr, which will show up in Streamlit logs.
        print("\n" + "="*50, file=sys.stderr)
        print(" POWER FLOW FAILED TO CONVERGE. DIAGNOSTIC REPORT:", file=sys.stderr)
        print("="*50, file=sys.stderr)
        
        if net.res_bus.empty:
            print("No results available. The solver failed at a very early stage.", file=sys.stderr)
        else:
            print("\n--- Bus Voltages at Last Unconverged Iteration ---", file=sys.stderr)
            pd.set_option('display.max_rows', 150) # Ensure we can see all buses
            print(net.res_bus[['vm_pu', 'va_degree']].to_string(), file=sys.stderr)
            
            extreme_voltages = net.res_bus[(net.res_bus.vm_pu < 0.8) | (net.res_bus.vm_pu > 1.2)]
            if not extreme_voltages.empty:
                print("\n--- CRITICAL VOLTAGE ISSUES DETECTED AT: ---", file=sys.stderr)
                print(extreme_voltages[['vm_pu']].to_string(), file=sys.stderr)
        
        print("="*50, file=sys.stderr)
        print(" END OF DIAGNOSTIC REPORT", file=sys.stderr)
        print("="*50 + "\n", file=sys.stderr)
        sys.stderr.flush() # Force the buffer to write to the log immediately

        # Return the failure signal to the Streamlit app
        return False, {"error": "Power flow did not converge. Detailed report is in the application log."}

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

