"""Streamlit UI — minimal scaffolding for the HPC Regression Testing Platform."""

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
)


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

# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
PAGES = ["Home", "Tests", "Configs"]

st.sidebar.markdown(
    '<span data-testid="nav-sidebar" style="display:none" aria-hidden="true"></span>',
    unsafe_allow_html=True,
)
st.sidebar.title("Navigation")
selected_page = st.sidebar.radio(
    "Go to",
    PAGES,
    index=PAGES.index(st.session_state.page),
    key="nav-pages",
)
st.session_state.page = selected_page

# ---------------------------------------------------------------------------
# Page: Home
# ---------------------------------------------------------------------------

def page_home() -> None:
    _testid("page-home")
    st.header("HPC Regression Testing Platform")
    st.write("")
    st.write("Use Tests to run the suite and view results.")
    st.write("")

    # Metrics dashboard
    available = get_available_metrics()
    if not available:
        st.info("No metrics data yet. Run jobs via the harness (e.g. `hpc-runner configs` or the API) to collect metrics.")
        return

    options = [f"{solver} / {metric}" for solver, metric in available]
    selected = st.selectbox(
        "Select metric to view",
        options=options,
        key="home-metric-select",
    )
    if not selected:
        return

    idx = options.index(selected)
    solver_name, metric_name = available[idx]
    history = get_metric_history(solver_name, metric_name)

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
elif st.session_state.page == "Tests":
    page_tests()
elif st.session_state.page == "Configs":
    page_configs()
