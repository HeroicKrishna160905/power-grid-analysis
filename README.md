# power-grid-analysis

An open-source, extensible platform for simulating, analyzing, and visualizing electrical power grids.

**Live demo:** https://power-grid-analysis-fzpwb7od7z5dbjjn7urehh.streamlit.app/

**Repository:** https://github.com/HeroicKrishna160905/power-grid-analysis

---

## Overview

`power-grid-analysis` is a modular, interactive framework built to help students, researchers, and engineers model, simulate, and understand electrical power systems. The project emphasizes reproducible experiments, clear visualizations, and a production-ready simulation workflow that combines:

- AC load flow (steady-state) analysis
- Optimal Power Flow (OPF) for loss/cost minimization
- N-1 contingency (single-line outage) analysis
- Interactive dashboards and notebooks for exploration and documentation

Key technologies: **Python**, **pandapower**, **pandas**, **streamlit**, **NetworkX**, **Jupyter Notebooks**, and **pytest**.

---

## Features

- **One-click analyses:** Run base power flow, OPF, and contingency flows from the Streamlit UI.
- **Robust simulation engine:** Handles convergence issues with fallbacks and targeted engineering fixes for known unstable cases.
- **OPF pipeline:** Deep-copies networks for isolated OPF runs, sets cost models, and aggregates dispatch tables for all generator types.
- **N-1 Security assessment:** Iterates over line outages and reports pass/fail along with detailed reasons (voltage violations, overloads, solver errors).
- **Interactive visualization:** Line loading charts, bus voltage tables, generator dispatch summaries, and contingency dashboards served via Streamlit.
- **Reproducibility:** `requirements.txt` and notebooks enable reproducible experiments and transparent workflows.
- **Automated tests:** Pytest-based tests to validate convergence, OPF behavior, and contingency outcomes.

---

## Quickstart

```bash
git clone https://github.com/HeroicKrishna160905/power-grid-analysis.git
cd power-grid-analysis
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows (PowerShell)

pip install -r requirements.txt

# Run the Streamlit app
streamlit run app.py
