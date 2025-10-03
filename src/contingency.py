# src/contingency.py
"""
N-1 Contingency Analysis Engine.
"""
from copy import deepcopy
import pandas as pd
from src.engine import run_powerflow
from src.opf import run_opf

def run_n1_contingency_analysis(base_net, run_opf_after=False):
    """
    Performs an N-1 contingency analysis on all transmission lines.

    Args:
        base_net (pandapowerNet): The initial, solved network state.
        run_opf_after (bool): If True, runs OPF for each contingency; otherwise, runs power flow.

    Returns:
        pd.DataFrame: A DataFrame summarizing the results of each contingency.
    """
    results_list = []
    lines_to_test = base_net.line.index

    for line_id in lines_to_test:
        net_copy = deepcopy(base_net)
        net_copy.line.at[line_id, 'in_service'] = False
        
        contingency_name = f"Line {line_id}"
        
        if run_opf_after:
            success, results = run_opf(net_copy)
        else:
            success, results = run_powerflow(net_copy)

        if not success:
            results_list.append({
                "contingency": contingency_name,
                "status": "FAIL",
                "reason": "Solver Error",
                "details": results.get("error")
            })
            continue

        v_viol = results["violations"]["voltage_violations"]
        o_viol = results["violations"]["overloaded_lines"]
        
        if v_viol > 0 or o_viol > 0:
            status = "FAIL"
            reason = f"{v_viol} voltage violations, {o_viol} overloads"
        else:
            status = "OK"
            reason = "Stable"
            
        results_list.append({
            "contingency": contingency_name,
            "status": status,
            "reason": reason,
            "details": ""
        })
        
    return pd.DataFrame(results_list)
