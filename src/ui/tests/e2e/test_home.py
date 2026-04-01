"""E2E tests for Solvers landing page."""

from playwright.sync_api import expect


def test_home_page_loads(page, streamlit_url, streamlit_process):
    """Solvers page shows primary heading and run panel markers."""
    page.goto(streamlit_url)
    expect(page.get_by_test_id("page-solvers")).to_be_attached()
    expect(page.get_by_test_id("page-run-solvers")).to_be_attached()
    expect(page.get_by_role("heading", name="Solvers", exact=True).first).to_be_visible()
