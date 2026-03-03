"""Streamlit UI — minimal scaffolding for the HPC Regression Platform."""

import sys
from pathlib import Path

import streamlit as st
import requests
import typing
import pandas as pd
import plotly.graph_objects as go

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
# Sidebar navigation
# ---------------------------------------------------------------------------
PAGES = ["Home", "Run Jobs", "Run History", "Configs"]

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

    #available = get_available_metrics()
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
    )
    if not selected:
        return

    idx = options.index(selected)
    solver_name, metric_name = available[idx]["solver"], available[idx]["metric"]
    print(available)
    # history = get_metric_history(solver_name, metric_name, limit=500)
    print(API_URL + "/api/metrics/" + solver_name + "/" + metric_name)

    try:
        history: list[dict[str, Any]]  = requests.get(API_URL + "/api/metrics/" + solver_name + "/" + metric_name).json()
    except requests.exceptions.RequestException as e:

        print(f"Error making request: {e}")
    print(f"history: {history}")


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

    runs_all = requests.get(API_URL + "/api/runs").json()
    if not runs_all:
        st.info("No runs in database.")
        return

    print(f"runs_all: {runs_all}")
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
    import json
    if solver_filter != "(all)":
        column_names = [key for key in json.loads(filtered[0]['metrics_json'])]
        row_names = [x['timestamp'] for x in filtered]
        truncated_names = [name[:8] + '...' if len(name) > 8 else name for name in row_names]
        # idk way its very wonky trying to use the timestamp as the row name
        row_names = [i for i in range(len(filtered))]
        print((row_names, column_names))
        data = []
        # blegh this will have NaN data if some dates are missing metrics
        for i in range(len(filtered)):
            row = []
            metrics_json = json.loads(filtered[i]['metrics_json'])
            for key, value in metrics_json.items():
                row.append(value)
            data.append(row)
        df = pd.DataFrame(data)
        print(df)
        fig = go.Figure(data=go.Heatmap(
            z=data,
            x=column_names,
            y=row_names,
            colorscale='Viridis',
            xgap=2,  # Makes vertical gridlines
            ygap=2,  # Makes horizontal gridlines
        ))
        st.title("Metrics Heatmap")
        # Display in Streamlit
        st.plotly_chart(fig)


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
        #_, systems, solvers, jobs = load_all(CONFIGS_DIR)
        systems: list[dict[str, Any]]  = requests.get(API_URL + "/api/systems").json()
        solvers: list[dict[str, Any]]  = requests.get(API_URL + "/api/solvers").json()
        jobs: list[dict[str, Any]]  = requests.get(API_URL + "/api/jobs").json()
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")

    print(f"jobs: {jobs}")
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
                    print(f"results: {results}")
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
#    result = st.session_state.test_result
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


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

if st.session_state.page == "Home":
    page_home()
elif st.session_state.page == "Run Jobs":
    page_run_jobs()
elif st.session_state.page == "Run History":
    page_run_history()
#elif st.session_state.page == "Tests":
#    page_tests()
elif st.session_state.page == "Configs":
    page_configs()
