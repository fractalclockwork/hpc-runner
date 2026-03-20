"""Streamlit UI — minimal scaffolding for the HPC Regression Platform."""

import sys
from pathlib import Path
import pandas as pd

import streamlit as st
import streamlit.components.v1 as components
import requests
import typing
from typing import Any
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import uuid
import json
from typing import Any
import plotly.express as px

# Allow importing runner from the same directory when launched via `streamlit run`
from config_editor import (  # noqa: E402
    discover_config_files,
    read_config,
    write_config,
    parse_yaml,
    validate_all_configs,
    ConfigFile,
    CONFIGS_DIR,
)
from metrics_dashboard import (  # noqa: E402
    get_available_metrics,
    get_metric_history,
    get_runtime_trend_data,
    get_mlups_trend_data,
    get_baseline_values_for_metric,
    get_solver_baseline_metrics,
    get_baseline_comparison,
)
from charts import (
    render_runtime_trend,
    render_mlups_trend,
    single_solver_heatmap,
    multi_solver_heatmap,
    render_manual_baseline_overrides,
    render_single_solver_runs_vs_baseline,
    render_multi_solver_runs_vs_baseline,
)  # noqa: E402

from harness import get_db_path

DB_PATH = get_db_path()
API_URL = "http://localhost:8000"


def _testid(id: str) -> None:
    """Inject hidden data-testid marker for Playwright."""
    st.markdown(
        f'<span data-testid="{id}" style="display:none" aria-hidden="true"></span>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "Home"
if st.session_state.page == "Test Results":
    st.session_state.page = "Tests"

if "test_result" not in st.session_state:
    st.session_state.test_result = None
if "run_job_results" not in st.session_state:
    st.session_state.run_job_results = None
if "page_change_requested" not in st.session_state:
    st.session_state.page_change_requested = False

# ---------------------------------------------------------------------------
# Global theme overrides (dark sidebar, card styles)
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* ── Dark sidebar ── */
    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] > div:first-child {
        background-color: #111827;
    }
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: rgba(255, 255, 255, 0.85) !important;
    }
    section[data-testid="stSidebar"] [data-testid="stRadio"] label {
        border-radius: 6px;
        padding: 0.35rem 0.75rem;
        transition: background-color 0.15s ease;
    }
    section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background-color: rgba(255, 255, 255, 0.07);
    }
    /* ── Metric cards ── */
    [data-testid="metric-container"] {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        box-shadow: 0 1px 6px rgba(0, 0, 0, 0.06);
    }
    /* ── Expanders ── */
    details {
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
    }
    /* ── Dividers ── */
    hr { border-color: #E2E8F0; }
    /* ── Run History: compact Baseline button on the right; shaded (primary) when set; clearer on hover ── */
    [data-testid="stHorizontalBlock"]:has(.stButton) .stButton button {
        opacity: 0.7;
        transition: opacity 0.15s ease;
        padding: 0.2rem 0.5rem !important;
        font-size: 0.8rem !important;
    }
    [data-testid="stHorizontalBlock"]:has(.stButton):hover .stButton button {
        opacity: 1;
    }
    [data-testid="stHorizontalBlock"]:has([data-testid="stCaptionContainer"]) [data-testid="stCaptionContainer"] {
        opacity: 0.85;
        transition: opacity 0.15s ease;
    }
    [data-testid="stHorizontalBlock"]:hover [data-testid="stCaptionContainer"] {
        opacity: 1;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
PAGES = ["Home", "Run Jobs", "Run History", "Individual Trends", "Long-Term Trends", "Configs"]

st.sidebar.markdown(
    '<span data-testid="nav-sidebar" style="display:none" aria-hidden="true"></span>',
    unsafe_allow_html=True,
)
st.sidebar.title("HPC Regression Testing Platform")
st.sidebar.markdown("---")

if 'page' not in st.session_state:
    st.session_state.page = PAGES[0]

def on_page_change():
    if not st.session_state.page_change_requested:
        st.session_state.page = st.session_state.page_radio
    else:
        print("page change was requested")
        st.session_state.page_change_requested = False

selected_page = st.sidebar.radio(
    "Go to",
    PAGES,
    index=PAGES.index(st.session_state.page),
    key="page_radio",
    on_change=on_page_change
)

# ---------------------------------------------------------------------------
# Page: Home
# ---------------------------------------------------------------------------

def page_home() -> None:
    _testid("page-home")
    st.header("Welcome to the HPC Regression Testing Platform")

    st.markdown(
        """
        The **HPC Regression Testing Platform** is an execution-agnostic harness for running
        solver jobs and tracking their performance over time. Submit jobs through the UI or
        the CLI, monitor runtime and throughput trends, inspect raw run history, and manage
        your solver and job configurations — all in one place.

        Solvers are treated as black-box scripts, so the platform works with any HPC workload
        without needing access to schedulers like SLURM or MPI.
        """
    )

    st.info(
        "For a detailed breakdown of the system design and component architecture, see "
        "`docs/architecture.md` in the repository."
    )

    st.markdown("")

    if st.button("Get Started →", type="primary", key="home-get-started"):
        st.session_state.page = "Run Jobs"
        st.rerun()


# ---------------------------------------------------------------------------
# Page: Individual Trends (formerly Home — Metrics over job history)
# ---------------------------------------------------------------------------

def page_individual_trends() -> None:
    _testid("page-individual-trends")
    st.header("Individual Trends")
    st.write("Metrics for each solver over the entire job history.")

    available: list[dict[str, str]] = []
    try:
        available = requests.get(API_URL + "/api/available_metrics").json()
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")

    if not available:
        st.info("No metrics data yet. Run jobs via Run Jobs or the CLI to collect metrics.")
        return

    options = [f"{dictionary['solver']} / {dictionary['metric']}" for dictionary in available]
    selected = st.selectbox(
        "Select solver and metric to view",
        options=options,
        key="home-metric-select",
        help="Solver metric combinations are defined in the backend configuration .yaml files. To add more, edit your configuration files on your backend host's filesystem.",
    )
    if not selected:
        return

    idx = options.index(selected)
    solver_name, metric_name = available[idx]["solver"], available[idx]["metric"]
    # history = get_metric_history(solver_name, metric_name, limit=500)

    history: list[dict[str, Any]] = []
    try:
        history = requests.get(API_URL + "/api/metrics/" + solver_name + "/" + metric_name).json()
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")

    if not history:
        st.warning("No history for this metric.")
        return

    df = pd.DataFrame(history, columns=["timestamp", "value"])
    df = df.set_index("timestamp")

    # Try to fetch baseline for this solver/metric and plot it as a flat line
    baseline_val = None
    try:
        resp = requests.get(API_URL + f"/api/solvers/{solver_name}/baseline")
        if resp.status_code == 200:
            data = resp.json()
            metrics = data.get("metrics") or {}
            val = metrics.get(metric_name)
            if isinstance(val, (int, float)):
                baseline_val = float(val)
    except requests.exceptions.RequestException:
        baseline_val = None

    if baseline_val is not None:
        df["baseline"] = baseline_val
        subplot_help = (
            "Displays the metric over time for this solver. "
            "The flat 'baseline' line comes from the solver's current baseline run."
        )
    else:
        subplot_help = (
            "Displays the metric over time for this solver. "
            "No baseline line is shown because no baseline run is configured for this solver/metric."
        )

    st.subheader(f"{solver_name} — {metric_name}", help=subplot_help)
    st.line_chart(df)

    with st.expander("View raw data"):
        raw_df = pd.DataFrame(history, columns=["timestamp", "value"])
        st.dataframe(raw_df, width="stretch")


# ---------------------------------------------------------------------------
# Page: Run History
# ---------------------------------------------------------------------------

def page_run_history() -> None:
    _testid("page-run-history")
    st.header("Run History")
    st.write("Browse past runs. Filter by solver or processor.")

    runs_all: list[dict[str, Any]] = []
    try:
        runs_all = requests.get(API_URL + "/api/runs").json()
    except requests.exceptions.RequestException as e:
        st.error(f"API unavailable: {e}")
        return

    if not runs_all:
        st.info("No runs in database.")
        return

    solvers = sorted({r["solver_name"] for r in runs_all})
    processors = sorted({r.get("processor") or "unknown" for r in runs_all})

    col1, col2 = st.columns(2)
    with col1:
        solver_filter = st.selectbox("Filter by solver", ["(all)"] + solvers, key="history-solver")
    with col2:
        processor_filter = st.selectbox("Filter by processor", ["(all)"] + processors, key="history-processor")

    solver_arg = solver_filter if solver_filter != "(all)" else None
    processor_arg = processor_filter if processor_filter != "(all)" else None

    params = {"solver": solver_arg, "processor": processor_arg}
    filtered: list[dict[str, Any]] = []
    try:
        filtered = requests.get(API_URL + "/api/runs", params=params).json()
    except requests.exceptions.RequestException as e:
        st.error(f"API unavailable: {e}")
        return

    try:
        job_batch_uuids = requests.get(API_URL + "/api/get_job_batch_uuids").json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to get batch job uuids")
        return

    # Use a graph mapping uuids to index of result in filtered to make a batch job
    # view
    batch_index_graph: dict[str, list[int]] = {}

    job_batch_uuids.append("")
    batch_count = 0
    for job in job_batch_uuids:
        for i, r in enumerate(filtered):
            if job == r['job_batch_uuid']:
                batch_count  += 1
                if job not in batch_index_graph:
                    batch_index_graph[job] = [i]
                else:
                    batch_index_graph[job].append(i)

    st.write(f"Showing {len(batch_index_graph)} batch(s) with {len(filtered)} run(s)")

    for batch_uuid in batch_index_graph.keys():
        batch_name = filtered[batch_index_graph[batch_uuid][0]]["job_batch_name"]
        batch_date = filtered[batch_index_graph[batch_uuid][0]]["job_batch_date"]
        i = batch_index_graph[batch_uuid]
        if batch_name != "":
            label = f"Batch ID: {batch_uuid} Batch Name: {batch_name} Batch Date: {batch_date}"
        else:
            label = f"Batch ID: {batch_uuid} Batch Date: {batch_date}"
        with st.expander(label, expanded=True):
            for i in batch_index_graph[batch_uuid]:
                render_job_expander(filtered[i])

def render_job_expander(r: dict[str: Any]) -> None:

    passed = "Passed" if r.get("passed") else "Failed"
    if r.get("passed"):
        icon = "✅"
    else:
        # ❌ if system failed (returncode != 0); ⚠️ only when failed solely due to validation
        returncode = r.get("returncode", 0)
        try:
            errs = json.loads(r.get("validation_errors") or "[]")
            has_validation_errors = isinstance(errs, list) and len(errs) > 0
        except (json.JSONDecodeError, TypeError):
            has_validation_errors = False
        if r.get("returncode", 0) != 0:
            icon = "❌"  # system/process failure
        elif r.get("validation_errors"):
            icon = "⚠️"  # validation only (returncode was 0)
        else:
            icon = "❌"
    is_baseline = r.get("is_baseline", False)
    run_id = r.get("id")
    # Row: expander (tab) on left, baseline control on the right; hover shows right side clearer
    col_expander, col_baseline = st.columns([5, 1])
    with col_expander:
        with st.expander(f"{icon} {r['job_name']} — {passed}({r.get('timestamp', '')})"):
            st.write(f"**Solver:** {r['solver_name']} | **System:** {r['system_name']} | **Returncode:** {r.get('returncode')} | **Runtime:** {r.get('runtime_seconds')}s")
            if r.get("stdout"):
                st.subheader("stdout")
                st.code(r["stdout"], language="text")
            if r.get("stderr"):
                st.subheader("stderr")
                st.code(r["stderr"], language="text")
            if r.get("metrics_json"):
                try:
                    metrics = json.loads(r["metrics_json"])
                    st.subheader("Metrics")
                    st.json(metrics)
                except json.JSONDecodeError:
                    st.text(r["metrics_json"])
            raw_errors = r.get("validation_errors")
            if raw_errors and raw_errors != "[]":
                if isinstance(raw_errors, str):
                    try:
                        validation_errors = json.loads(raw_errors)
                        st.subheader("Validation Errors")
                        st.json(validation_errors)
                    except json.JSONDecodeError:
                        st.subheader("Validation Errors")
                        st.text(raw_errors)
                else:
                    st.subheader("Validation Errors")
                    st.json(raw_errors)
    with col_baseline:
        if run_id is not None:
            if is_baseline:
                st.button(
                    "Baseline",
                    key=f"set-baseline-{run_id}",
                    type="primary",
                    help="This run is the current baseline",
                )
            else:
                if st.button(
                    "Baseline",
                    key=f"set-baseline-{run_id}",
                    help="Set this run as the baseline for comparison",
                ):
                    try:
                        resp = requests.post(API_URL + f"/api/runs/{run_id}/set_baseline")
                        if resp.status_code == 200:
                            st.success("Baseline set.")
                            st.rerun()
                        else:
                            st.error(resp.text or f"Error {resp.status_code}")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Request failed: {e}")

# ---------------------------------------------------------------------------
# Page: Run Jobs
# ---------------------------------------------------------------------------


def page_run_jobs() -> None:
    _testid("page-run-jobs")
    st.header("Run Jobs")
    st.write("Execute HPC regression jobs. Select jobs and run them.")

    systems: list[dict[str, Any]] = []
    solvers: list[dict[str, Any]] = []
    jobs: list[dict[str, Any]] = []
    try:
        #_, systems, solvers, jobs = load_all(CONFIGS_DIR)
        systems = requests.get(API_URL + "/api/systems").json()
        solvers = requests.get(API_URL + "/api/solvers").json()
        jobs = requests.get(API_URL + "/api/jobs").json()
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")

    job_list = jobs
    if not job_list:
        st.warning("No jobs configured. Add jobs in configs/jobs/.")
        return

    # Job schedule summary # test
    schedule_data = [
        {
            "Job": j["name"],
            "Solver": j["solver"],
            "System": j["system"],
            "Schedule": j.get("schedule") or "Manual",
        }
        for j in job_list
    ]
    schedule_df = pd.DataFrame(schedule_data)
    with st.expander("Job schedule", expanded=True):
        _testid("run-jobs-schedule")
        st.caption("When each job is configured to run (cron or manual).")
        st.dataframe(schedule_df, width='stretch', hide_index=True)

    batch_name = st.text_input("Job Batch Name", "", help = "Optionally enter a name to help describe this batch run.")

    job_names = [j["name"] for j in job_list]
    selected = st.multiselect(
        "Select jobs to run",
        options=job_names,
        default=job_names,
        key="run-jobs-select",
        help = "Solver and job configurations are defined in /configs/solvers and /configs/jobs respectively. Once a job is properly configured and validated, it will appear here. Please apply validation to check if your configuration is valid if it does not appear in the list."
    )

    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        run_all = st.button("Run All", key="run-jobs-all")
    with col2:
        run_selected = st.button("Run Selected", key="run-jobs-selected")

    if run_all or run_selected:
        to_run = job_names if run_all else selected
        if not to_run:
            st.warning("Select at least one job.")
        else:
            with st.spinner(f"Running {len(job_names)} job(s)…"):
                # results = run_jobs(job_objs, solvers, systems)
                # use the post request to run jobs
                payload = {"jobs": to_run, "batch_name":batch_name}
                endpoint = API_URL + "/api/run_jobs"
                try:
                    # Make the POST request with JSON body
                    response = requests.post(
                        endpoint,
                        json=payload
                    )

                    # Check if request was successful
                    response.raise_for_status()
                    results = response.json()
                except requests.exceptions.RequestException as e:
                    print(f"Error making request: {e}")

            st.session_state.run_job_results = results
            st.rerun()

    if "run_job_results" in st.session_state and st.session_state.run_job_results:
        results = st.session_state.run_job_results
        st.subheader("Results")
        for r in results:
            if r['passed']:
                status, icon = "Passed", "✅"
            elif r.get("returncode", 0) != 0:
                status, icon = "Run failed", "❌"  # system/process failure
            elif r.get("validation_errors"):
                status, icon = "Validation failed", "⚠️"  # validation only (returncode was 0)
            else:
                status, icon = "Run failed", "❌"
            st.write(f"{icon} **{r['job_name']}** — {status} (returncode={r['returncode']}, runtime={r['runtime_seconds']:.2f}s)")
            if r.get("validation_errors"):
                for err in (r.get("validation_errors") or []):
                    st.caption(f"  • {err}")


# ---------------------------------------------------------------------------
# Page: Configs
# ---------------------------------------------------------------------------

# Shawn: Would be better to have the backend handle what we need from this
# but its less of a headache to remove dependencies so will keep for now
def page_configs() -> None:
    _testid("page-configs")
    st.header("Configs")
    st.write("View jobs, resources, solvers, and systems configurations.")

    config_files = discover_config_files()
    if not config_files:
        st.warning("No config files found in configs/.")
        return

    # Group by category
    by_category: dict[str, list[ConfigFile]] = {}
    for cf in config_files:
        by_category.setdefault(cf.category, []).append(cf)

    category = st.selectbox(
        "Category",
        options=sorted(by_category.keys()),
        key="config-category",
    )
    files_in_cat = by_category[category]
    selected = st.selectbox(
        "File",
        options=files_in_cat,
        format_func=lambda f: f.display_name,
        key="config-file",
    )

    if not selected:
        return

    # Load current content
    try:
        current_content = read_config(selected.path)
    except OSError as e:
        st.error(f"Cannot read file: {e}")
        return

    st.code(current_content, language="yaml")


# ---------------------------------------------------------------------------
# Page: Long-Term Trends (Page 4)
# ---------------------------------------------------------------------------

def page_long_term_trends() -> None:
    _testid("page-long-term-trends")
    st.header("Long-Term Trends")
    st.write("Performance of solvers over time. Use the sidebar to filter by solver, system, and date range.")

    df_all = get_runtime_trend_data(str(DB_PATH))

    if df_all.empty:
        st.info("No run data available yet. Run jobs via Run Jobs or the CLI to collect data.")
        return

    # --- Sidebar filters ---------------------------------------------------
    all_solvers = sorted(df_all["solver_name"].unique().tolist())
    all_systems = sorted(df_all["system_name"].unique().tolist())

    min_date = df_all["timestamp"].dt.date.min()
    max_date = df_all["timestamp"].dt.date.max()

    # Persist date range in session state so it survives page navigation
    if "trend_date_start" not in st.session_state:
        st.session_state.trend_date_start = min_date
    if "trend_date_end" not in st.session_state:
        st.session_state.trend_date_end = max_date

    st.sidebar.markdown("### Long-Term Trends Filters")

    selected_solvers = st.sidebar.multiselect(
        "Solver(s)",
        options=all_solvers,
        default=all_solvers,
        key="trend-solver-filter",
    )
    selected_systems = st.sidebar.multiselect(
        "System(s)",
        options=all_systems,
        default=all_systems,
        key="trend-system-filter",
    )
    date_range = st.sidebar.date_input(
        "Date range",
        value=(st.session_state.trend_date_start, st.session_state.trend_date_end),
        min_value=min_date,
        max_value=max_date,
        key="trend-date-filter",
    )

    # Update session state whenever the widget changes
    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        st.session_state.trend_date_start = date_range[0]
        st.session_state.trend_date_end = date_range[1]
        start_date, end_date = date_range
    else:
        start_date = end_date = date_range[0] if date_range else min_date

    # --- Filter DataFrame --------------------------------------------------
    import pandas as pd

    mask = (
        df_all["solver_name"].isin(selected_solvers)
        & df_all["system_name"].isin(selected_systems)
        & (df_all["timestamp"].dt.date >= start_date)
        & (df_all["timestamp"].dt.date <= end_date)
    )
    df_filtered = df_all[mask]

    # --- Heatmap -----------------------------------------------------------
    st.subheader("Metrics Heatmap")

    heatmap_mode = st.radio(
        "Heatmap mode",
        options=["All metrics for one solver/system", "One metric across all solvers/systems"],
        horizontal=True,
        key="heatmap-mode",
    )

    # Fetch runs from API and apply date + system filters in Python
    try:
        params = {}
        if len(selected_solvers) == 1:
            params["solver"] = selected_solvers[0]
        heatmap_runs = requests.get(API_URL + "/api/runs", params=params).json()
        heatmap_runs = [
            r for r in heatmap_runs
            if r.get("metrics_json")
            and start_date <= pd.Timestamp(r["timestamp"]).date() <= end_date
            and r.get("system_name") in selected_systems
        ]
    except requests.exceptions.RequestException as e:
        st.warning(f"Could not fetch runs for heatmap: {e}")
        heatmap_runs = []

    if not heatmap_runs:
        st.info("No data available for heatmap with the current filters.")
    elif heatmap_mode == "All metrics for one solver/system":
        # This mode is intended for a single solver + system. If multiple are selected,
        # let the user pick which one to visualize.
        solver_pick = selected_solvers[0] if selected_solvers else None
        system_pick = selected_systems[0] if selected_systems else None
        if len(selected_solvers) > 1:
            solver_pick = st.selectbox(
                "Solver (for all-metrics heatmap)",
                options=selected_solvers,
                key="heatmap-all-metrics-solver-pick",
            )
        if len(selected_systems) > 1:
            system_pick = st.selectbox(
                "System (for all-metrics heatmap)",
                options=selected_systems,
                key="heatmap-all-metrics-system-pick",
            )

        solver_runs = [
            r
            for r in heatmap_runs
            if r.get("solver_name") == solver_pick and r.get("system_name") == system_pick
        ]
        if not solver_runs:
            st.info("No metric data for the selected solver/system in this date range.")
        else:
            heatmap_color_mode_single = st.selectbox(
                "Heatmap color scaling",
                options=["Default (min-max)", "Baseline (per metric)"],
                key="heatmap-color-mode-single",
                help="Baseline mode colors each metric relative to its baseline value for this solver.",
            )

            if heatmap_color_mode_single.startswith("Baseline") and solver_pick:
                baseline_metrics_api = get_solver_baseline_metrics(str(solver_pick))

                # Manual overrides (per-metric) for this solver
                metric_keys = sorted(json.loads(solver_runs[0]["metrics_json"]).keys())
                baseline_metrics = render_manual_baseline_overrides(
                    item_labels=metric_keys,
                    defaults=baseline_metrics_api,
                    key_prefix=f"manual_baseline_all_{solver_pick}",
                    caption_text=(
                        "Type a baseline value per metric to use instead of (or when there is no) "
                        "run-based baseline. Pre-filled from the current baseline run when available."
                    ),
                    input_help="Baseline value for {label}",
                )

                if not baseline_metrics:
                    st.info("No baseline metrics available. Set a baseline in Run History or enter manual values above.")
                    single_solver_heatmap(solver_runs, solver_name=str(solver_pick))
                else:
                    baseline_comparison_data = get_baseline_comparison(
                        solver_name=str(solver_pick), limit=200
                    )
                    single_solver_heatmap(
                        solver_runs,
                        solver_name=str(solver_pick),
                        baseline_metrics=baseline_metrics,
                        baseline_comparison_data=baseline_comparison_data if baseline_comparison_data else None,
                    )
            else:
                single_solver_heatmap(solver_runs, solver_name=str(solver_pick or ""))
    else:
        available_metrics_hm = sorted({
            k
            for r in heatmap_runs
            for k in json.loads(r["metrics_json"]).keys()
        })
        if not available_metrics_hm:
            st.info("No dynamic metrics available for the selected filters.")
        else:
            selected_hm_metric = st.selectbox(
                "Metric",
                options=available_metrics_hm,
                key="heatmap-metric-select",
            )
            heatmap_color_mode = st.selectbox(
                "Heatmap color scaling",
                options=["Default (spec / min-max)", "Baseline (per solver)"],
                key="heatmap-color-mode",
                help="Baseline mode colors each solver relative to its baseline value for the selected metric.",
            )
            if selected_hm_metric == "mlups":
                metric_dictionary = {"python-solver": (2.1e6, 4e6)}
            elif selected_hm_metric == "runtime_seconds":
                metric_dictionary = {
                    "python-solver": (0.008, 0.01),
                    "echo-solver": (0.0, 0.01),
                    "cpuinfo-test": (0.0, 0.01),
                }
            else:
                metric_dictionary = {}

            if heatmap_color_mode.startswith("Baseline"):
                solver_names_for_baseline = sorted({r["solver_name"] for r in heatmap_runs})
                baseline_values_api = get_baseline_values_for_metric(
                    selected_hm_metric, solver_names_for_baseline
                )
                baseline_values = render_manual_baseline_overrides(
                    item_labels=solver_names_for_baseline,
                    defaults=baseline_values_api,
                    key_prefix=f"manual_baseline_{selected_hm_metric}",
                    caption_text=(
                        "Type a baseline value per solver to use instead of (or when there is no) "
                        "run-based baseline. Pre-filled from current run baselines when available."
                    ),
                    input_help=f"Baseline value for {selected_hm_metric}",
                )
                if not baseline_values:
                    st.info(
                        "No baseline values available. Set baselines in Run History or enter manual values above."
                    )
                    multi_solver_heatmap(selected_hm_metric, heatmap_runs, metric_dictionary or None)
                else:
                    baseline_comparison_data = get_baseline_comparison(limit=100)
                    multi_solver_heatmap(
                        selected_hm_metric,
                        heatmap_runs,
                        None,
                        baseline_values=baseline_values,
                        baseline_comparison_data=baseline_comparison_data if baseline_comparison_data else None,
                    )
            else:
                if not metric_dictionary:
                    st.info("Define the spec ranges for each metric for each solver to show a specification range heatmap.")
                else:
                    multi_solver_heatmap(selected_hm_metric, heatmap_runs, metric_dictionary)


    # --- Raw data expander -------------------------------------------------
    with st.expander("View data summary"):
        if df_filtered.empty:
            st.info("No rows match the current filters.")
        else:
            st.dataframe(
                df_filtered[["timestamp", "solver_name", "system_name", "job_name", "runtime_seconds", "passed"]],
                width='stretch',
            )
    # --- Runtime trend chart -----------------------------------------------
    _testid("section-runtime-trend")
    st.subheader("Runtime (wall-clock) Trend")
    render_runtime_trend(df_filtered, st.session_state)

    # --- MLUPS trend chart -------------------------------------------------
    _testid("section-mlups-trend")
    st.subheader("Throughput Trend (MLUPS)")
    df_mlups_all = get_mlups_trend_data(str(DB_PATH))
    if not df_mlups_all.empty:
        mlups_mask = (
            df_mlups_all["solver_name"].isin(selected_solvers)
            & df_mlups_all["system_name"].isin(selected_systems)
            & (df_mlups_all["timestamp"].dt.date >= start_date)
            & (df_mlups_all["timestamp"].dt.date <= end_date)
        )
        df_mlups_filtered = df_mlups_all[mlups_mask]
    else:
        df_mlups_filtered = df_mlups_all
    render_mlups_trend(df_mlups_filtered, st.session_state)



# ---------------------------------------------------------------------------
# Page: Tests
# ---------------------------------------------------------------------------

#def page_tests() -> None:
#    _testid("page-tests")
#    st.header("Tests")
#    st.write("")
#
#    _testid("btn-run-test")
#    if st.button("Run Test", key="btn-run-test"):
#        with st.spinner("Running tests…"):
#            result = run_tests()
#
#        st.session_state.test_result = result
#        st.rerun()
#
#    st.write("")
#
#    if st.session_state.test_result is None:
#        st.info("No test results yet. Click Run Test above to execute the suite.")
#        return
#
#    result = st.session_state.test_resul
#
#    if result.success:
#        st.success(f"All tests passed  (exit code {result.returncode})")
#    else:
#        st.error(f"Tests failed  (exit code {result.returncode})")
#
#    st.write("")
#
#    if result.stdout:
#        st.subheader("stdout")
#        st.code(result.stdout, language="text")
#
#    if result.stderr:
#        st.subheader("stderr")
#        st.code(result.stderr, language="text")


def goto_selected_run(point):
    '''
    Uses the streamlit on_select event info to goto the run information for a run that was clicked on.
    Uses a custom HTML injection script to scroll to the corresponding component and check the target
    against the text in the <p> element inside of it.
    Notably this feature could conceivably be slow or bork if we implement a date range cutoff that
    is not synced with what is shown in the line plots, should consider adding a separate view
    or refactoring the run history page to suport filtering by a specific date range.
    This should probably go to some job view in the future
    '''
    target = point['x'].replace(' ', 'T', 1).split(".")[0]
    components.html(f"""

    <script>
        const target = "{target}".toLowerCase();

        console.log(target)
        function openAndScroll() {{
            const summaries = window.parent.document.querySelectorAll('summary');

            for (const summary of summaries) {{
                // Check the <p> inside the summary instead of the summary itself
                const p = summary.querySelector('p');
                const text = (p ? p.innerText : summary.innerText).trim().toLowerCase();
                console.log(summary)
                console.log(text)
                console.log(target)
                if (text.includes(target)) {{
                    if (text.includes("—")) {{
                        const expander = summary.closest('details');
                        if (!expander.hasAttribute('open')) {{
                            summary.click();
                        }}
                        summary.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                        break;
                    }}
                }}
            }}
        }}

        setTimeout(openAndScroll, 300);
    </script>
    """, height=0)

def single_solver_heatmap(
    filtered,
    solver_name: str = "",
    *,
    baseline_metrics: dict[str, float] | None = None,
    baseline_comparison_data: list[dict[str, Any]] | None = None,
) -> None:
    column_names = [key for key in json.loads(filtered[0]['metrics_json'])]
    row_names = [x['timestamp'] for x in filtered]
    data = []
    # blegh this will have NaN data if some dates are missing metrics
    for i in range(len(filtered)):
        row = []
        metrics_json = json.loads(filtered[i]['metrics_json'])
        for key, value in metrics_json.items():
            row.append(value)
        data.append(row)
    # descending time order is more intuitive
    data.reverse()
    # Min-max normalization (0 to 1)
    df = pd.DataFrame(data, columns=column_names, index=row_names)
    numeric_df = df.apply(pd.to_numeric, errors='coerce')
    numeric_df = numeric_df.dropna(axis=1, how="all")

    # heatmap in baseline mode
    if baseline_metrics:
        # Baseline ratio per metric (value / baseline_metric)
        cols = [c for c in numeric_df.columns if c in baseline_metrics and baseline_metrics.get(c, 0) > 0]
        # check if any of the columns are in the baseline_comparison_data
        if not cols:
            st.info("No baseline values found for the metrics in this heatmap; showing default view.")
            baseline_metrics = None
        else:
            ratio_df = numeric_df[cols].copy()
            # baseline ratio per metric
            for c in cols:
                ratio_df[c] = ratio_df[c] / float(baseline_metrics[c])
            ratio_df = ratio_df.replace([np.inf, -np.inf], np.nan).fillna(0)
            z = ratio_df.transpose() # transpose the dataframe to get the metrics as the columns and the dates as the rows
            custom = numeric_df[cols].transpose() 
            zmin = 0.0
            zmax = 2.0
            colorscale = [
                [0.0, "red"],
                [0.25, "orange"],
                [0.5, "green"],
                [0.75, "orange"],
                [1.0, "red"],
            ]
            colorbar = dict(
                tickvals=[0.0, 1.0, 2.0],
                ticktext=["0× baseline", "1× baseline", "2× baseline"],
                ticks="outside",
            )
            hovertemplate = "Value: %{customdata:.4f}<br>× baseline: %{z:.2f}×<extra></extra>"
            help_text = "Baseline view colors each metric by value ÷ baseline (green near 1×; red further away)."

            fig = go.Figure(
                data=go.Heatmap(
                    customdata=custom,
                    z=z,
                    x=z.columns,
                    y=z.index,
                    zmin=zmin,
                    zmax=zmax,
                    colorscale=colorscale,
                    colorbar=colorbar,
                    xgap=2,
                    ygap=2,
                    hovertemplate=hovertemplate,
                )
            )
    if not baseline_metrics:
        normalized = (numeric_df - numeric_df.min()) / (numeric_df.max() - numeric_df.min())
        normalized = normalized.fillna(0)
        normalized = normalized.transpose()
        fig = go.Figure(
            data=go.Heatmap(
                customdata=numeric_df.transpose(),
                z=normalized,
                x=normalized.columns,
                y=normalized.index,
                colorscale="Viridis",
                xgap=2,
                ygap=2,
                hovertemplate="Non-Normalized Value: %{customdata:.4f}<extra></extra>",
            )
        )
        help_text = (
            "Heatmap compares numeric metrics for a single solver/system using per-metric min-max normalized values."
        )
    fig.update_layout(
        xaxis=dict(
            type="category"
        )
    )
    st.header("All Metrics Heatmap", help=help_text)
    st.plotly_chart(fig)

    # In baseline mode, hide raw table and show comparison expander instead
    # this is just my stylistic choice, we can change this if we want
    if not baseline_metrics:
        with st.expander("View heatmap data"):
            st.dataframe(numeric_df, use_container_width=True)
    else:
        # make it nice and pretty with baseline metrics
        # perhaps, I can move this segment to clean code later
        if baseline_comparison_data:
            render_single_solver_runs_vs_baseline(
                solver_name=solver_name,
                baseline_metrics=baseline_metrics,
                baseline_comparison_data=baseline_comparison_data,
            )

def multi_solver_heatmap(
    metric_name: str,
    filtered,
    min_max_dictionary: dict[str, tuple[float, float]] | None = None,
    *,
    baseline_values: dict[str, float] | None = None,
    baseline_comparison_data: list[dict[str, Any]] | None = None,
) -> None:
    def normalize_row(row):
        solver = row.name
        if baseline_values:
            base_val = baseline_values.get(solver)
            if base_val is None or base_val == 0:
                # No usable baseline for this solver; leave as zeros
                return row * 0.0
            return row / base_val
        if min_max_dictionary:
            if solver in min_max_dictionary:
                min_value, max_value = min_max_dictionary[solver]
            else:
                st.warning(
                    f"Supplied min_max dictionary does not have entry for {solver}, "
                    "will use observed range 0–1."
                )
                min_value, max_value = 0.0, 1.0
            return (row - min_value) / (max_value - min_value)
        # Fallback: simple min–max per solver if no spec or baseline is provided
        observed_min = float(row.min())
        observed_max = float(row.max())
        if observed_max == observed_min:
            return row * 0.0
        return (row - observed_min) / (observed_max - observed_min)
    try:
        solvers: list[dict[str, Any]] = requests.get(API_URL + "/api/solvers").json()
    except requests.exceptions.RequestException:
        solvers = []
    column_names = [x['name'] for x in solvers]
    row_names = [i for i in range(len(filtered))]
    data = []
    # blegh this will have NaN data if some dates are missing metrics
    for i in range(len(filtered)):
        solver_name = filtered[i]['solver_name']
        row = []
        metrics_json = json.loads(filtered[i]['metrics_json'])
        for key, value in metrics_json.items():
            if key == metric_name:
                row.append(value)
                row.append(filtered[i]['timestamp'][:19])
                row.append(metric_name)
                row.append(solver_name)

        data.append(row)
    # descending time order is more intuitive
    data.reverse()
    # Min-max normalization (0 to 1)
    df = pd.DataFrame(data, index=row_names)
    pivot = pd.pivot_table(df, values = 0, columns = 3, index = 1)
    pivot = pivot.transpose()
    # normalize value based on either baseline ratios or the supplied spec ranges
    normalized = pivot.apply(normalize_row, axis=1)

    if baseline_values:
        zmin = 0.0
        zmax = 2.0
        # Divergent scale: green at 1× baseline, red when further from baseline (above or below)
        colorscale = [
            [0.0, "red"],
            [0.25, "orange"],
            [0.5, "green"],
            [0.75, "orange"],
            [1.0, "red"],
        ]
        colorbar = dict(
            tickvals=[0.0, 1.0, 2.0],
            ticktext=["0× baseline", "1× baseline", "2× baseline"],
            ticks="outside",
        )
        help_text = (
            f"Heatmap shows {metric_name} as a ratio to each solver's baseline value. "
            "Green = at baseline; red = further from baseline (above or below)."
        )
    else:
        zmin = 0.0
        zmax = 1.0
        colorscale = [
            [0.0, "green"],
            [0.5, "yellow"],
            [1.0, "red"],
        ]
        colorbar = dict(
            tickvals=np.arange(0.0, 1.0, 1.0 / 3.0),  # center ticks in each band
            ticktext=["Within Spec", "Near Average", "Out of Spec "],
            ticks="outside",
        )
        help_text = (
            f"Heatmap shows whether {metric_name} is within a specified per-solver "
            "normalized range over the time series if a range was supplied; otherwise "
            "it uses observed min/max."
        )

    if baseline_values:
        hovertemplate = "Value: %{customdata:.4f}<br>× baseline: %{z:.2f}×<extra></extra>"
    else:
        hovertemplate = "Non-Normalized Value: %{customdata:.4f}<extra></extra>"

    fig = go.Figure(
        data=go.Heatmap(
            customdata=pivot,
            z=normalized,
            x=normalized.columns,
            y=normalized.index,
            zmin=zmin,
            zmax=zmax,
            colorscale=colorscale,
            colorbar=colorbar,
            hovertemplate=hovertemplate,
            xgap=2,  # Makes vertical gridlines
            ygap=2,  # Makes horizontal gridlines
        )
    )

    fig.update_layout(xaxis=dict(type="category"))
    st.header(
        f"{metric_name} Heatmap",
        help=help_text,
    )
    # Display in Streamlit
    st.plotly_chart(fig)
    if not baseline_values:
        with st.expander(f"View heatmap data"):
            st.dataframe(df, use_container_width=True)
    if baseline_values and baseline_comparison_data:
        render_multi_solver_runs_vs_baseline(
            metric_name=metric_name,
            baseline_values=baseline_values,
            baseline_comparison_data=baseline_comparison_data,
        )
    if min_max_dictionary:
        with st.expander(f"Specification Ranges"):
            st.dataframe(pd.DataFrame(min_max_dictionary).rename(index={0: "Lower Spec Range", 1: "Upper Spec Range"}).transpose(), use_container_width=True)

# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

if st.session_state.page == "Home":
    page_home()
elif st.session_state.page == "Run Jobs":
    page_run_jobs()
elif st.session_state.page == "Individual Trends":
    page_individual_trends()
elif st.session_state.page == "Run History":
    page_run_history()
    if "clicked_point" in st.session_state:
        goto_selected_run(st.session_state["clicked_point"])
        del st.session_state["clicked_point"]

elif st.session_state.page == "Long-Term Trends":
    page_long_term_trends()
#elif st.session_state.page == "Tests":
#    page_tests()
elif st.session_state.page == "Configs":
    page_configs()
