"""E2E: Run Matrix page navigation."""

from playwright.sync_api import expect


def test_navigate_to_run_matrix(page, streamlit_url, streamlit_process):
    """Sidebar includes Run Matrix; page shows heading and test id."""
    page.goto(streamlit_url)
    sb = page.locator('section[data-testid="stSidebar"]')
    sb.get_by_text("Run Matrix", exact=True).click()
    expect(page.get_by_test_id("page-run-matrix")).to_be_attached()
    expect(page.get_by_test_id("run-matrix-grid")).to_be_attached()
    main = page.get_by_test_id("stMainBlockContainer")
    expect(main.get_by_role("heading", name="Run Matrix").first).to_be_visible()
