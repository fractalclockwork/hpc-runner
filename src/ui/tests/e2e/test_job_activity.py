"""E2E tests for Job Activity page (stored runs + live invocations)."""

from playwright.sync_api import expect


def test_job_activity_page_loads(page, streamlit_url, streamlit_process):
    """Job Activity page shows header and intro caption."""
    page.goto(streamlit_url)
    page.locator('section[data-testid="stSidebar"]').get_by_text("Job Activity", exact=True).click()
    expect(page.get_by_test_id("page-job-activity")).to_be_attached()
    expect(page.get_by_role("heading", name="Job Activity")).to_be_visible()
    expect(page.get_by_text("Choose one job below.")).to_be_visible()
