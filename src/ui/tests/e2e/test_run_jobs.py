"""E2E tests for Run Solvers page."""

from playwright.sync_api import expect


def test_run_solvers_overview_visible(page, streamlit_url, streamlit_process):
    """Solvers landing page shows Run Solvers section and solver overview table when configured."""
    page.goto(streamlit_url)
    expect(page.get_by_test_id("page-solvers")).to_be_attached()
    expect(page.get_by_test_id("page-run-solvers")).to_be_attached()
    expect(page.get_by_role("heading", name="Run Solvers")).to_be_visible()

    overview = page.get_by_text("Solver overview", exact=True)
    expect(overview).to_be_visible()
