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
```

## Typical Workflow

1. **Launch the Streamlit app.**
2. **Select a test system** (e.g., IEEE 30-bus, IEEE 118-bus) in the sidebar.
3. **Run Base Power Flow** to observe voltages, losses, and line loadings.
4. **Run Optimal Power Flow (OPF)** to minimize losses/costs and view generator dispatch.
5. **Run N-1 Contingency Analysis** to evaluate resilience and identify weak points.
6. **Export results (CSV/JSON)** or open the corresponding Jupyter notebook for reproducible documentation.

---

## Architecture & Key Modules

- `app.py` — Streamlit application and user-facing UI.  
- `src/engine.py` — Grid loading, base power flow orchestration, and engineering fixes.  
- `src/opf.py` — OPF setup, cost modeling, and dispatch aggregation.  
- `src/contingency.py` — N-1 simulation loop and contingency reporting.  
- `notebook/` — Jupyter notebooks for experiments and demonstrations.  
- `tests/` — Unit tests (pytest) for validating core functionality.  
- `requirements.txt` — Pinning dependencies for reproducibility.

---

## Example Outputs

- **Network visualizations:** Node/edge graphs showing topology and loading.  
- **Bus & line tables:** Voltages, angle, MW/MVar flows, and line loadings.  
- **Generator dispatch tables:** Pre- and post-OPF schedules and costs.  
- **Contingency matrix:** Per-line outage pass/fail status and failure reasons.

---

## Design Decisions

- **Pandapower** selected for its realistic power-system modeling API and ecosystem compatibility.  
- **Streamlit** chosen for rapid, interactive visualization and easy deployment.  
- **Notebooks + Tests:** Notebooks enable exploration and teaching; tests provide reliability for research-grade outputs.  
- **Modular codebase:** Clean separation between engine logic, OPF handling, and UI to simplify extension and testing.

---

## Roadmap / Future Work

- Add renewable generation (PV/wind) models and time-series simulation.  
- Integrate ML models for load forecasting and fault prediction.  
- Real-time data ingestion (e.g., PMU / SCADA-like feeds) for near-real-time dashboards.  
- Enhanced visualization (Plotly/Dash/Bokeh) and export-ready reporting.  
- Expanded test-suite across more IEEE benchmark systems.

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.  
Suggested contribution steps:

1. Fork the repo and create a feature branch.  
2. Add tests for new functionality.  
3. Keep changes modular and documented with notebooks or unit tests.  
4. Submit a PR referencing the issue and a short description of your changes.

---

## Citation / Attribution

If you use this project in research or a publication, please cite the repository URL and include a short description of how you used it.

---

## License

This project is released under the **MIT License** — see `LICENSE` for details.

---

## Contact

**Author:** Krishna Barai (Panini)  
**Project Repo:** [https://github.com/HeroicKrishna160905/power-grid-analysis](https://github.com/HeroicKrishna160905/power-grid-analysis)  
**Live Demo:** [https://power-grid-analysis-fzpwb7od7z5dbjjn7urehh.streamlit.app/](https://power-grid-analysis-fzpwb7od7z5dbjjn7urehh.streamlit.app/)

---

*Made with ⚡ by an engineer who believes accessible tools accelerate better power systems.*

# Run the Streamlit app
streamlit run app.py
