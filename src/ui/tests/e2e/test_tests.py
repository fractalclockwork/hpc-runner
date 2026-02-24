"""E2E tests for Tests page."""

from playwright.sync_api import expect


def test_tests_page_shows_run_button(page, streamlit_url, streamlit_process):
    """Tests page shows Run Test button."""
    page.goto(streamlit_url)
    page.get_by_text("Tests", exact=True).click()
    expect(page.get_by_test_id("page-tests")).to_be_attached()
    expect(page.get_by_role("button", name="Run Test")).to_be_visible()


def test_tests_page_shows_results_section(page, streamlit_url, streamlit_process):
    """Tests page shows results section (no results yet)."""
    page.goto(streamlit_url)
    page.get_by_text("Tests", exact=True).click()
    expect(page.get_by_test_id("page-tests")).to_be_attached()
    expect(page.get_by_text("No test results yet.")).to_be_visible()


def test_run_test_button_clickable(page, streamlit_url, streamlit_process):
    """Run Test button is enabled."""
    page.goto(streamlit_url)
    page.get_by_text("Tests", exact=True).click()
    expect(page.get_by_role("button", name="Run Test")).to_be_enabled()
