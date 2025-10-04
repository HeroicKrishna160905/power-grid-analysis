# src/engine.py
"""
Core engine for loading cases and running AC power flow.
"""
import pandapower as pp
import pandapower.networks as pn
import pandas as pd

def load_case(case_name: str = "case30"):
    """Loads a standard pandapower network case by name."""
    if not hasattr(pn, case_name):
        raise ValueError(f"Unknown case: {case_name}. Please use a valid pandapower.networks case.")
    return getattr(pn, case_name)()

def run_powerflow(net, **kwargs):
    """
    Runs an AC power flow (pp.runpp) with safe error handling and result validation.
    Accepts additional keyword arguments to pass to pp.runpp.
    """
    try:
        # Pass any extra arguments (like max_iteration) directly to pandapower
        pp.runpp(net, enforce_q_lims=True, calculate_voltage_angles=True, **kwargs)
        
        # Summarize violations
        v_min, v_max = 0.95, 1.05
        bus_v = net.res_bus['vm_pu']
        line_loading = net.res_line['loading_percent']
        
        violations = {
            "voltage_violations": int(((bus_v < v_min) | (bus_v > v_max)).sum()),
            "overloaded_lines": int((line_loading > 100).sum())
        }
        
        total_gen = net.res_gen.p_mw.sum() if not net.res_gen.empty else 0
        total_loss = net.res_line.pl_mw.sum() if not net.res_line.empty else 0

        results = {
            "net": net,
            "bus_results": net.res_bus,
            "line_results": net.res_line,
            "violations": violations,
            "summary": {
                "total_load_mw": net.load.p_mw.sum(),
                "total_gen_mw": total_gen,
                "losses_mw": total_loss,
                "loss_percent": (total_loss / total_gen * 100) if total_gen > 0 else 0
            }
        }
        return True, results
    except pp.LoadflowNotConverged as e:
        return False, {"error": "Power flow did not converge.", "details": str(e)}
    except Exception as e:
        return False, {"error": "An unexpected error occurred during power flow.", "details": str(e)}

