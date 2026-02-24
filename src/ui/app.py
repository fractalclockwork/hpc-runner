"""Streamlit UI — minimal scaffolding for the HPC Regression Testing Platform."""

import sys
from pathlib import Path

import streamlit as st

# Allow importing runner from the same directory when launched via `streamlit run`
sys.path.insert(0, str(Path(__file__).resolve().parent))
from runner import run_tests  # noqa: E402


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

if "test_result" not in st.session_state:
    st.session_state.test_result = None

# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
PAGES = ["Home", "Test Results"]

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
    st.write("Click the button below to execute the full test suite.")
    st.write("")

    _testid("btn-run-test")
    if st.button("Run Test", key="btn-run-test"):
        with st.spinner("Running tests…"):
            result = run_tests()

        st.session_state.test_result = result
        st.session_state.page = "Test Results"
        st.rerun()


# ---------------------------------------------------------------------------
# Page: Test Results
# ---------------------------------------------------------------------------

def page_test_results() -> None:
    _testid("page-test-results")
    st.header("Test Results")
    st.write("")

    if st.session_state.test_result is None:
        st.info("No test results yet. Go to Home and run the tests first.")
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
elif st.session_state.page == "Test Results":
    page_test_results()
