"""E2E tests for Run Matrix page (submit solver@system runs)."""

from playwright.sync_api import expect


def test_run_matrix_visible(page, streamlit_url, streamlit_process):
    """Run Matrix page shows header and matrix grid when API returns solvers/systems."""
    page.goto(streamlit_url)
    page.locator('section[data-testid="stSidebar"]').get_by_text("Run Matrix", exact=True).click()
    expect(page.get_by_test_id("page-run-matrix")).to_be_attached()
    main = page.get_by_test_id("stMainBlockContainer")
    expect(main.get_by_role("heading", name="Run Matrix").first).to_be_visible()
    expect(main.get_by_role("button", name="Save", exact=True)).to_be_visible()
    expect(main.get_by_role("button", name="Delete", exact=True)).to_be_visible()
    expect(page.get_by_text("Select runs", exact=True)).to_be_visible()
