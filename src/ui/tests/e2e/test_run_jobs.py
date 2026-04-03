"""E2E tests for Run Solvers page."""

from playwright.sync_api import expect


def test_run_solvers_overview_visible(page, streamlit_url, streamlit_process):
    """Solvers page shows run panel markers and solver overview (expander label) when configured."""
    page.goto(streamlit_url)
    page.locator('section[data-testid="stSidebar"]').get_by_text("Solvers", exact=True).click()
    expect(page.get_by_test_id("page-solvers")).to_be_attached()
    expect(page.get_by_test_id("page-run-solvers")).to_be_attached()
    main = page.get_by_test_id("stMainBlockContainer")
    expect(main.get_by_role("heading", name="Solvers").first).to_be_visible()

    overview = page.get_by_text("Solver overview", exact=True)
    expect(overview).to_be_visible()
