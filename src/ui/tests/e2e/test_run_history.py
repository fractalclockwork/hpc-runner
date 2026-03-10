"""E2E tests for Run History page."""

from playwright.sync_api import expect


def test_run_history_page_loads(page, streamlit_url, streamlit_process):
    """Run History page shows header and intro text."""
    page.goto(streamlit_url)
    page.get_by_text("Run History", exact=True).click()
    expect(page.get_by_test_id("page-run-history")).to_be_attached()
    expect(page.get_by_role("heading", name="Run History")).to_be_visible()
    expect(page.get_by_text("Browse past runs. Filter by solver or processor.")).to_be_visible()
