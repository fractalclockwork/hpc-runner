"""E2E tests for Home page."""

from playwright.sync_api import expect


def test_home_page_loads(page, streamlit_url, streamlit_process):
    """Home page shows header and Run Test button."""
    page.goto(streamlit_url)
    expect(page.get_by_test_id("page-home")).to_be_attached()
    expect(page.get_by_role("heading", name="HPC Regression Testing Platform")).to_be_visible()
    expect(page.get_by_role("button", name="Run Test")).to_be_visible()


def test_run_test_button_clickable(page, streamlit_url, streamlit_process):
    """Run Test button is enabled."""
    page.goto(streamlit_url)
    expect(page.get_by_role("button", name="Run Test")).to_be_enabled()
