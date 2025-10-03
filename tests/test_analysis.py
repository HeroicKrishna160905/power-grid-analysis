# tests/test_analysis.py
import pytest
from src.engine import load_case, run_powerflow
from src.opf import define_generator_costs, run_opf

def test_powerflow_ieee30_success():
    """Tests that a standard power flow on IEEE 30-bus system converges without violations."""
    net = load_case("case_ieee30")
    success, results = run_powerflow(net)
    
    assert success, "Power flow failed to converge."
    assert results["violations"]["voltage_violations"] == 0, "Voltage violations found in base case."
    assert results["violations"]["overloaded_lines"] == 0, "Line overloads found in base case."

def test_opf_cost_reduction():
    """Tests that OPF correctly dispatches the cheaper generator and reduces total cost."""
    net = load_case("case_ieee30")
    
    # Define arbitrary high costs for all generators
    initial_costs = {('gen', i): 100 for i in net.gen.index}
    net = define_generator_costs(net, initial_costs)
    success_initial, res_initial = run_opf(net)
    assert success_initial, "Initial OPF run failed"
    initial_total_cost = res_initial["objective_cost"]
    
    # Make one generator significantly cheaper
    cheaper_costs = initial_costs.copy()
    cheaper_costs[('gen', 0)] = 10  # Make generator 0 very cheap
    
    net = define_generator_costs(net, cheaper_costs)
    success_final, res_final = run_opf(net)
    assert success_final, "Final OPF run failed"
    final_total_cost = res_final["objective_cost"]

    # Assert that the final cost is lower and the cheap generator is dispatched
    assert final_total_cost < initial_total_cost, "OPF did not reduce the total generation cost."
    assert res_final["gen_dispatch"].loc[0, 'p_mw'] > 0, "Cheaper generator was not dispatched."
