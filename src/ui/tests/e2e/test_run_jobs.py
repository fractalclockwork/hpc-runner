"""E2E tests for Run Solvers page."""

from playwright.sync_api import expect


def test_run_solvers_overview_visible(page, streamlit_url, streamlit_process):
    """Run Solvers page shows solver overview expander when solvers are configured."""
    page.goto(streamlit_url)
    page.get_by_text("Run Solvers", exact=True).click()
    expect(page.get_by_role("heading", name="Run Solvers")).to_be_visible()

    overview = page.get_by_text("Solver overview", exact=True)
    expect(overview).to_be_visible()
