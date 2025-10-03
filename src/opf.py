# src/opf.py
"""
Functions for running Optimal Power Flow (OPF).
"""
import pandapower as pp

def define_generator_costs(net, cost_per_mw: dict):
    """
    Creates polynomial cost functions for generators in the network.
    It first clears any existing costs to prevent errors.

    Args:
        net (pandapowerNet): The network object.
        cost_per_mw (dict): A dictionary mapping (element_type, index) to a linear cost.
                            Example: {('gen', 0): 10, ('gen', 1): 20}
    """
    # Clear any existing costs before creating new ones
    if not net.poly_cost.empty:
        net.poly_cost.drop(net.poly_cost.index, inplace=True)

    for (etype, idx), price in cost_per_mw.items():
        if etype not in net or idx not in net[etype].index:
            print(f"Warning: Element {etype} with index {idx} not found. Skipping cost creation.")
            continue
        pp.create_poly_cost(net, element=idx, et=etype, cp1_eur_per_mw=price)
    return net


def run_opf(net):
    """
    Runs an Optimal Power Flow (pp.runopp) with error handling.

    Args:
        net (pandapowerNet): The network with defined generator costs.

    Returns:
        tuple[bool, dict]: A tuple containing:
                           - success (bool): True if OPF was successful.
                           - results (dict): A dictionary with results or an error message.
    """
    try:
        pp.runopp(net, calculate_voltage_angles=True)
        results = {
            "net": net,
            "objective_cost": net.res_cost,
            "gen_dispatch": net.res_gen,
            "bus_results": net.res_bus,
            "line_results": net.res_line,
            "summary": {
                "total_load_mw": net.load.p_mw.sum(),
                "total_gen_mw": net.res_gen.p_mw.sum(),
                "losses_mw": net.res_line.pl_mw.sum(),
                "loss_percent": net.res_line.pl_mw.sum() / net.res_gen.p_mw.sum() * 100 if net.res_gen.p_mw.sum() != 0 else 0
            }
        }
        return True, results
    except Exception as e:
        return False, {"error": "An unexpected error occurred during OPF.", "details": str(e)}
