# src/opf.py
import pandas as pd
import pandapower as pp

def define_generator_costs(net, cost_per_mw: dict):
    """
    Creates polynomial cost functions for generators in the network.
    It first clears any existing costs to prevent errors.
    """
    # Clear any existing costs before creating new ones
    if hasattr(net, 'poly_cost') and not net.poly_cost.empty:
        net.poly_cost.drop(net.poly_cost.index, inplace=True)

    for (etype, idx), price in cost_per_mw.items():
        if etype not in net or idx not in net[etype].index:
            print(f"Warning: Element {etype} with index {idx} not found. Skipping cost creation.")
            continue
        pp.create_poly_cost(net, element=idx, et=etype, cp1_eur_per_mw=price)
    return net


def run_opf(net):
    """
    Runs an Optimal Power Flow (pp.runopp) with robust error and result handling.
    """
    try:
        pp.runopp(net, calculate_voltage_angles=True)

        # Robustly assemble generator dispatch results from all possible sources
        dispatch_dfs = []
        if hasattr(net, 'res_gen') and not net.res_gen.empty:
            dispatch_dfs.append(net.res_gen[['p_mw', 'q_mvar']])
        if hasattr(net, 'res_ext_grid') and not net.res_ext_grid.empty:
            dispatch_dfs.append(net.res_ext_grid[['p_mw', 'q_mvar']])
        if hasattr(net, 'res_sgen') and not net.res_sgen.empty:
            dispatch_dfs.append(net.res_sgen[['p_mw', 'q_mvar']])
        
        gen_dispatch = pd.concat(dispatch_dfs) if dispatch_dfs else pd.DataFrame(columns=['p_mw', 'q_mvar'])

        total_gen = gen_dispatch.p_mw.sum()
        total_loss = net.res_line.pl_mw.sum() if hasattr(net, 'res_line') and not net.res_line.empty else 0
        
        results = {
            "net": net,
            "objective_cost": net.res_cost,
            "gen_dispatch": gen_dispatch,
            "bus_results": net.res_bus,
            "line_results": net.res_line,
            "summary": {
                "total_load_mw": net.load.p_mw.sum(),
                "total_gen_mw": total_gen,
                "losses_mw": total_loss,
                "loss_percent": (total_loss / total_gen * 100) if total_gen > 0 else 0
            }
        }
        return True, results
    except Exception as e:
        return False, {"error": "An unexpected error occurred during OPF.", "details": str(e)}

