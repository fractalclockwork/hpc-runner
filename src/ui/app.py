"""Streamlit UI — minimal scaffolding for the HPC Regression Platform."""

import sys
from pathlib import Path

import streamlit as st

# Allow importing runner from the same directory when launched via `streamlit run`
sys.path.insert(0, str(Path(__file__).resolve().parent))
from runner import run_tests  # noqa: E402
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
    get_all_metrics_flat,
)
from charts import render_runtime_trend, render_mlups_trend, render_metric_heatmap  # noqa: E402

from harness import get_db_path

DB_PATH = get_db_path()


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
# Sidebar navigation
# ---------------------------------------------------------------------------
PAGES = ["Home", "Run Jobs", "Run History", "Long-Term Trends", "Tests", "Configs"]

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

    available = get_available_metrics()
    if not available:
        st.info("No metrics data yet. Run jobs via Run Jobs or the CLI to collect metrics.")
        return

    options = [f"{solver} / {metric}" for solver, metric in available]
    selected = st.selectbox(
        "Select solver and metric to view",
        options=options,
        key="home-metric-select",
    )
    if not selected:
        return

    idx = options.index(selected)
    solver_name, metric_name = available[idx]
    history = get_metric_history(solver_name, metric_name, limit=500)

    if not history:
        st.warning("No history for this metric.")
        return

    import pandas as pd

    df = pd.DataFrame(history, columns=["timestamp", "value"])
    df = df.set_index("timestamp")

    st.subheader(f"{solver_name} — {metric_name}")
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

    try:
        from harness.storage import get_runs, init_db
    except ImportError as e:
        st.error(f"Cannot load harness: {e}")
        return

    if not DB_PATH.exists():
        st.info("No runs yet. Run jobs via Run Jobs or the CLI to collect data.")
        return

    init_db(DB_PATH)

    runs_all = get_runs(DB_PATH, limit=500)
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
    filtered = get_runs(DB_PATH, solver=solver_arg, processor=processor_arg, limit=100)

    st.write(f"Showing {len(filtered)} run(s)")

    import json
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
        from harness import load_all, run_jobs, init_db, store_run, ConfigError
    except ImportError as e:
        st.error(f"Cannot load harness: {e}")
        return

    try:
        _, systems, solvers, jobs = load_all(CONFIGS_DIR)
    except ConfigError as e:
        st.error(f"Config error: {e}")
        return

    job_list = list(jobs.values())
    if not job_list:
        st.warning("No jobs configured. Add jobs in configs/jobs/.")
        return

    job_names = [j.name for j in job_list]
    selected = st.multiselect(
        "Select jobs to run",
        options=job_names,
        default=job_names,
        key="run-jobs-select",
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
            job_objs = [j for j in job_list if j.name in to_run]
            with st.spinner(f"Running {len(job_objs)} job(s)…"):
                results = run_jobs(job_objs, solvers, systems)
                init_db(DB_PATH)
                for r in results:
                    store_run(DB_PATH, r)

            st.session_state.run_job_results = results
            st.rerun()

    if "run_job_results" in st.session_state and st.session_state.run_job_results:
        results = st.session_state.run_job_results
        st.subheader("Results")
        for r in results:
            if r.passed:
                status, icon = "Passed", "✅"
            elif getattr(r, "validation_errors", None):
                status, icon = "Validation failed", "⚠️"
            else:
                status, icon = "Run failed", "❌"
            st.write(f"{icon} **{r.job_name}** — {status} (returncode={r.returncode}, runtime={r.runtime_seconds:.2f}s)")
            if getattr(r, "validation_errors", None) and r.validation_errors:
                for err in r.validation_errors:
                    st.caption(f"  • {err}")


# ---------------------------------------------------------------------------
# Page: Configs
# ---------------------------------------------------------------------------

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

    df_flat_all = get_all_metrics_flat(str(DB_PATH))

    if df_flat_all.empty:
        st.info("No data available for heatmap yet.")
    else:
        date_mask = (
            (df_flat_all["timestamp"].dt.date >= start_date)
            & (df_flat_all["timestamp"].dt.date <= end_date)
        )
        df_flat = df_flat_all[date_mask]

        if heatmap_mode == "All metrics for one solver/system":
            available_series = sorted(df_flat["series"].unique().tolist())
            if not available_series:
                st.info("No data for the selected date range.")
            else:
                selected_heatmap_series = st.selectbox(
                    "Solver / System",
                    options=available_series,
                    key="heatmap-series-select",
                )
                df_series = df_flat[df_flat["series"] == selected_heatmap_series].copy()
                df_series = df_series.sort_values("timestamp")
                # Limit to 30 most recent unique run timestamps to keep heatmap readable
                recent_ts = df_series["timestamp"].drop_duplicates().nlargest(30)
                df_series = df_series[df_series["timestamp"].isin(recent_ts)]
                df_series["run_label"] = df_series["timestamp"].dt.strftime("%m-%d %H:%M")
                pivot = df_series.pivot_table(
                    index="metric_name", columns="run_label", values="value", aggfunc="mean"
                )
                render_metric_heatmap(
                    pivot,
                    title=f"All Metrics — {selected_heatmap_series}",
                    normalize_rows=True,
                )
        else:
            # Apply sidebar solver/system filter so users can narrow scope
            df_flat_filtered = df_flat[
                df_flat["solver_name"].isin(selected_solvers)
                & df_flat["system_name"].isin(selected_systems)
            ]
            available_metrics = sorted(df_flat_filtered["metric_name"].unique().tolist())
            if not available_metrics:
                st.info("No metrics found for the selected filters.")
            else:
                selected_hm_metric = st.selectbox(
                    "Metric",
                    options=available_metrics,
                    key="heatmap-metric-select",
                )
                df_metric = df_flat_filtered[
                    df_flat_filtered["metric_name"] == selected_hm_metric
                ].copy()
                df_metric = df_metric.sort_values("timestamp")
                recent_ts = df_metric["timestamp"].drop_duplicates().nlargest(30)
                df_metric = df_metric[df_metric["timestamp"].isin(recent_ts)]
                df_metric["run_label"] = df_metric["timestamp"].dt.strftime("%m-%d %H:%M")
                pivot = df_metric.pivot_table(
                    index="series", columns="run_label", values="value", aggfunc="mean"
                )
                render_metric_heatmap(
                    pivot,
                    title=f"{selected_hm_metric} — All Solvers/Systems",
                    normalize_rows=False,
                )

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

def page_tests() -> None:
    _testid("page-tests")
    st.header("Tests")
    st.write("")

    _testid("btn-run-test")
    if st.button("Run Test", key="btn-run-test"):
        with st.spinner("Running tests…"):
            result = run_tests()

        st.session_state.test_result = result
        st.rerun()

    st.write("")

    if st.session_state.test_result is None:
        st.info("No test results yet. Click Run Test above to execute the suite.")
        return

    result = st.session_state.test_result

    if result.success:
        st.success(f"All tests passed  (exit code {result.returncode})")
    else:
        st.error(f"Tests failed  (exit code {result.returncode})")

    st.write("")

    if result.stdout:
        st.subheader("stdout")
        st.code(result.stdout, language="text")

    if result.stderr:
        st.subheader("stderr")
        st.code(result.stderr, language="text")


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
elif st.session_state.page == "Tests":
    page_tests()
elif st.session_state.page == "Configs":
    page_configs()
