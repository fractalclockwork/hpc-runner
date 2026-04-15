"""E2E tests for Home landing page."""

from playwright.sync_api import expect


def test_home_page_loads(page, streamlit_url, streamlit_process):
    """Home page shows welcome heading on initial load."""
    page.goto(streamlit_url)
    expect(page.get_by_test_id("page-home")).to_be_attached()
    expect(page.get_by_role("heading", name="Welcome to the HPC Regression Platform", exact=True).first).to_be_visible()
