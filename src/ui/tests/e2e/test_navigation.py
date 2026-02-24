"""E2E tests for sidebar navigation."""

from playwright.sync_api import expect


def test_sidebar_nav_visible(page, streamlit_url, streamlit_process):
    """Sidebar has navigation options."""
    page.goto(streamlit_url)
    expect(page.get_by_test_id("nav-sidebar")).to_be_attached()
    # Streamlit radio renders options as clickable labels
    expect(page.get_by_text("Home", exact=True)).to_be_visible()
    expect(page.get_by_text("Test Results", exact=True)).to_be_visible()


def test_navigate_to_test_results(page, streamlit_url, streamlit_process):
    """Clicking Test Results navigates to that page."""
    page.goto(streamlit_url)
    page.get_by_text("Test Results", exact=True).click()
    expect(page.get_by_test_id("page-test-results")).to_be_attached()
    expect(page.get_by_role("heading", name="Test Results")).to_be_visible()
