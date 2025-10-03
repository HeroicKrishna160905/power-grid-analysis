 #src/engine.py (Simplified Version)
import pandapower as pp
import pandapower.networks as pn

def load_case(case_name: str = "case_ieee30"):
    """Loads a standard pandapower network case by name."""
    return getattr(pn, case_name)()

def run_powerflow(net):
    """
    Runs a basic AC power flow and returns the result.
    No complex error handling for this diagnostic test.
    """
    try:
        pp.runpp(net, init="dc", numba=False)
        if net["converged"]:
            return True, {"bus_results": net.res_bus}
        else:
            # This will only be reached if pp.runpp completes but doesn't converge.
            return False, {"error": "Solver finished but did not converge."}
    except Exception as e:
        # This will be reached if pp.runpp itself throws a Python-level error.
        return False, {"error": f"An exception occurred inside pandapower: {e}"}


