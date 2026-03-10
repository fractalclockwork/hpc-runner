"""Streamlit UI — minimal scaffolding for the HPC Regression Platform."""

import sys
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
import requests
import typing
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import uuid
import json

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
)
from charts import render_runtime_trend, render_mlups_trend  # noqa: E402

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
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
PAGES = ["Home", "Run Jobs", "Run History", "Long-Term Trends", "Configs"]

st.sidebar.markdown(
    '<span data-testid="nav-sidebar" style="display:none" aria-hidden="true"></span>',
    unsafe_allow_html=True,
)
st.sidebar.title("Navigation")
page_index = PAGES.index(st.session_state.page) if st.session_state.page in PAGES else 0
selected_page = st.sidebar.radio(
    "Go to",
    PAGES,
    index=page_index,
    key="nav-pages",
)
st.session_state.page = selected_page

# ---------------------------------------------------------------------------
# Page: Home (Metrics over job history)
# ---------------------------------------------------------------------------

def page_home() -> None:
    _testid("page-home")
    st.header("HPC Regression Platform")
    st.write("Metrics for each solver over the entire job history.")

    try:
        available: list[dict[str, str]]  = requests.get(API_URL + "/api/available_metrics").json()
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

    try:
        history: list[dict[str, Any]]  = requests.get(API_URL + "/api/metrics/" + solver_name + "/" + metric_name).json()
    except requests.exceptions.RequestException as e:

        print(f"Error making request: {e}")


    if not history:
        st.warning("No history for this metric.")
        return

    import pandas as pd

    df = pd.DataFrame(history, columns=["timestamp", "value"])
    df = df.set_index("timestamp")

    st.subheader(f"{solver_name} — {metric_name}", help = "Displays a single variable line chart for the solver/metric combination showing time series changes for the metric.")
    st.line_chart(df)

    with st.expander("View raw data"):
        raw_df = pd.DataFrame(history, columns=["timestamp", "value"])
        st.dataframe(raw_df, use_container_width=True)


# ---------------------------------------------------------------------------
# Page: Run History
# ---------------------------------------------------------------------------

def page_run_history() -> None:
    _testid("page-run-history")
    st.header("Run History")
    st.write("Browse past runs. Filter by solver or processor.")

    runs_all = requests.get(API_URL + "/api/runs").json()
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
    filtered = requests.get(API_URL + "/api/runs", params=params).json()
    # filtered = get_runs(DB_PATH, solver=solver_arg, processor=processor_arg, limit=100)
    if solver_filter != "(all)":
        single_solver_heatmap(filtered)
    else:
        multi_solver_heatmap("runtime_seconds", filtered)


    st.write(f"Showing {len(filtered)} run(s)")

    for r in filtered:
        passed = "Passed" if r.get("passed") else "Failed"
        if r.get("passed"):
            icon = "✅"
        elif r.get("validation_errors"):
            icon = "⚠️"
        else:
            icon = "❌"
        with st.expander(f"{icon} {r['job_name']} — {passed} ({r.get('timestamp', '')})"):
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
            # if validation errors are present, show them
            if r.get("validation_errors") and r.get("validation_errors") != "[]":
                try:
                    validation_errors = json.loads(r["validation_errors"])
                    st.subheader("Validation Errors")
                    st.json(validation_errors)
                except json.JSONDecodeError:
                    st.text(r["validation_errors"])


# ---------------------------------------------------------------------------
# Page: Run Jobs
# ---------------------------------------------------------------------------

def page_run_jobs() -> None:
    _testid("page-run-jobs")
    st.header("Run Jobs")
    st.write("Execute HPC regression jobs. Select jobs and run them.")

    try:
        #_, systems, solvers, jobs = load_all(CONFIGS_DIR)
        systems: list[dict[str, Any]]  = requests.get(API_URL + "/api/systems").json()
        solvers: list[dict[str, Any]]  = requests.get(API_URL + "/api/solvers").json()
        jobs: list[dict[str, Any]]  = requests.get(API_URL + "/api/jobs").json()
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")

    job_list = jobs
    if not job_list:
        st.warning("No jobs configured. Add jobs in configs/jobs/.")
        return

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
                payload = {"jobs": to_run}
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
            elif getattr(r, "validation_errors", None):
                status, icon = "Validation failed", "⚠️"
            else:
                status, icon = "Run failed", "❌"
            st.write(f"{icon} **{r['job_name']}** — {status} (returncode={r['returncode']}, runtime={r['runtime_seconds']:.2f}s)")
            if getattr(r, "validation_errors", None) and r['validation_errors']:
                for err in r.validation_errors:
                    st.caption(f"  • {err}")


# ---------------------------------------------------------------------------
# Page: Configs
# ---------------------------------------------------------------------------

# Shawn: Would be better to have the backend handle what we need from this
# but its less of a headache to remove dependencies so will keep for now
def page_configs() -> None:
    _testid("page-configs")
    st.header("Configs")
    st.write("View and edit jobs, resources, solvers, and systems. Edits are validated before saving.")

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

    edited = st.text_area(
        "Edit YAML",
        value=current_content,
        height=400,
        key=f"config-editor-{selected.path}",
    )

    col1, col2, col3 = st.columns([1, 1, 4])
    def _build_temp_config(tmp_path: Path, edited_content: str) -> None:
        """Populate temp config dir with edited file applied."""
        for sub in ("resources", "systems", "jobs"):
            (tmp_path / sub).mkdir(exist_ok=True)
            src = CONFIGS_DIR / sub
            if src.exists():
                for f in list(src.glob("*.yaml")) + list(src.glob("*.yml")):
                    c = edited_content if f == selected.path else f.read_text()
                    (tmp_path / sub / f.name).write_text(c)
        (tmp_path / "solvers").mkdir(exist_ok=True)
        solvers_src = CONFIGS_DIR / "solvers"
        if solvers_src.exists():
            for d in solvers_src.iterdir():
                if d.is_dir():
                    (tmp_path / "solvers" / d.name).mkdir(exist_ok=True)
                    for f in d.iterdir():
                        if f.is_file():
                            c = edited_content if f == selected.path else f.read_text()
                            (tmp_path / "solvers" / d.name / f.name).write_text(c)

    with col1:
        if st.button("Validate", key="config-validate"):
            yaml_data, yaml_err = parse_yaml(edited)
            if yaml_err:
                st.error(f"YAML syntax error: {yaml_err}")
            else:
                import tempfile
                with tempfile.TemporaryDirectory() as tmp:
                    tmp_path = Path(tmp)
                    _build_temp_config(tmp_path, edited)
                    ok, msg = validate_all_configs(tmp_path)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)

    with col2:
        if st.button("Save", key="config-save"):
            yaml_data, yaml_err = parse_yaml(edited)
            if yaml_err:
                st.error(f"YAML syntax error: {yaml_err}")
            else:
                import tempfile
                with tempfile.TemporaryDirectory() as tmp:
                    tmp_path = Path(tmp)
                    _build_temp_config(tmp_path, edited)
                    ok, msg = validate_all_configs(tmp_path)
                    if not ok:
                        st.error(f"Validation failed: {msg}")
                    else:
                        write_config(selected.path, edited)
                        st.success("Saved successfully.")
                        st.rerun()


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

    # --- Runtime trend chart -----------------------------------------------
    st.subheader("Runtime (wall-clock) Trend")
    render_runtime_trend(df_filtered)

    # --- MLUPS trend chart -------------------------------------------------
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
    render_mlups_trend(df_mlups_filtered)

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
        solver_runs = [
            r for r in heatmap_runs if r.get("solver_name") in selected_solvers
        ]
        if not solver_runs:
            st.info("No metric data for the selected solver/system in this date range.")
        else:
            single_solver_heatmap(solver_runs)
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
            multi_solver_heatmap(selected_hm_metric, heatmap_runs)

    # --- Raw data expander -------------------------------------------------
    with st.expander("View raw data"):
        if df_filtered.empty:
            st.info("No rows match the current filters.")
        else:
            st.dataframe(
                df_filtered[["timestamp", "solver_name", "system_name", "job_name", "runtime_seconds", "passed"]],
                use_container_width=True,
            )


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

def single_solver_heatmap(filtered, solver_name: str = ""):
    column_names = [key for key in json.loads(filtered[0]['metrics_json'])]
    row_names = [x['timestamp'] for x in filtered]
 #   truncated_names = [name[:8] + '...' if len(name) > 8 else name for name in row_names]
    # idk way its very wonky trying to use the timestamp as the row name
    #row_names = [i for i in range(len(filtered))]
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
    print(df)
    numeric_df = df.apply(pd.to_numeric, errors='coerce')
    # numeric_df = df.select_dtypes(include=['float64', 'int64', 'float32', 'int32'])
    numeric_df = numeric_df.dropna(axis=1, how="all")
    normalized = (numeric_df - numeric_df.min()) / (numeric_df.max() - numeric_df.min())
    normalized = normalized.fillna(0)
    normalized= normalized.transpose()
    print(normalized)
    fig = go.Figure(data=go.Heatmap(
        customdata=numeric_df.transpose(),
        z=normalized,
        x=normalized.columns,
        y=normalized.index,
        colorscale='Viridis',
        xgap=2,  # Makes vertical gridlines
        ygap=2,  # Makes horizontal gridlines
        hovertemplate='Non-Normalized Value: %{customdata:.4f}<extra></extra>',
    ))
    fig.update_layout(
        xaxis=dict(
            type="category"
        )
    )
    st.header(f"Single Metric Heatmap",help="Heatmap compares numeric metrics for a single solver using per metric normalized values. You can hover over to see the non-normalized value for reference.  The raw data table shows non normalized values for each metric.")
    # Display in Streamlit
    st.plotly_chart(fig)
    with st.expander("View raw data"):
        st.dataframe(numeric_df, use_container_width=True)

def multi_solver_heatmap(metric_name: str, filtered):
    solvers: list[dict[str, Any]]  = requests.get(API_URL + "/api/solvers").json()
    column_names = [x['name'] for x in solvers]
#    row_names = [x['timestamp'] for x in filtered]
#    truncated_names = [name[:8] + '...' if len(name) > 8 else name for name in row_names]
    # idk way its very wonky trying to use the timestamp as the row name
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
        # row.append(filtered[i]['name'])
                row.append(filtered[i]['timestamp'][:10])
                row.append(metric_name)
                row.append(solver_name)

        data.append(row)
    # descending time order is more intuitive
    data.reverse()
    # Min-max normalization (0 to 1)
    df = pd.DataFrame(data, index=row_names)
    print(df)
    pivot = pd.pivot_table(df, values = 0, columns = 3, index = 1)
    # pivot = pivot.reset_index()
    #pivot = pivot.drop(labels = 1, axis = 1)
    pivot = pivot.transpose()
    print(pivot)
    #numeric_df = df.apply(pd.to_numeric, errors='coerce')
    ## numeric_df = df.select_dtypes(include=['float64', 'int64', 'float32', 'int32'])
    #numeric_df = numeric_df.dropna(axis=1, how="all")
    #normalized = (numeric_df - numeric_df.min()) / (numeric_df.max() - numeric_df.min())
    #normalized = normalized.fillna(0)
    fig = go.Figure(data=go.Heatmap(
        customdata=pivot,
        z=pivot,
        x=pivot.columns,
        y=pivot.index,
        colorscale='Viridis',
        hovertemplate='Non-Normalized Value: %{customdata:.4f}<extra></extra>',
        xgap=2,  # Makes vertical gridlines
        ygap=2,  # Makes horizontal gridlines
    ))

    fig.update_layout(
        xaxis=dict(
            type="category"
        )
    )
    st.header(f"{metric_name} Heatmap",help=f"Heatmap compares the shared metric {metric_name} for all solvers with available data for that metic. The raw data table shows daily metrics information for the shared metric across solvers")
    # Display in Streamlit
    st.plotly_chart(fig)
    with st.expander("View raw data"):
        st.dataframe(df, use_container_width=True)

# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

if st.session_state.page == "Home":
    page_home()
elif st.session_state.page == "Run Jobs":
    page_run_jobs()
elif st.session_state.page == "Run History":
    page_run_history()
elif st.session_state.page == "Long-Term Trends":
    page_long_term_trends()
#elif st.session_state.page == "Tests":
#    page_tests()
elif st.session_state.page == "Configs":
    page_configs()
