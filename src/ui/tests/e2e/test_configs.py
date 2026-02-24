"""E2E tests for Configs page."""

from playwright.sync_api import expect


def test_configs_page_shows_editor(page, streamlit_url, streamlit_process):
    """Configs page shows category selector, file selector, and Validate/Save buttons."""
    page.goto(streamlit_url)
    page.get_by_text("Configs", exact=True).click()
    expect(page.get_by_test_id("page-configs")).to_be_attached()
    expect(page.get_by_role("heading", name="Configs")).to_be_visible()
    expect(page.get_by_text("Category")).to_be_visible()
    expect(page.get_by_text("File")).to_be_visible()
    expect(page.get_by_role("button", name="Validate")).to_be_visible()
    expect(page.get_by_role("button", name="Save")).to_be_visible()


def test_configs_validate_success(page, streamlit_url, streamlit_process):
    """Validate button shows success when configs are valid."""
    page.goto(streamlit_url)
    page.get_by_text("Configs", exact=True).click()
    expect(page.get_by_test_id("page-configs")).to_be_attached()
    page.get_by_role("button", name="Validate").click()
    expect(page.get_by_text("All configs valid.")).to_be_visible(timeout=3000)
