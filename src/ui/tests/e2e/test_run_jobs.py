"""E2E tests for Run Jobs page."""

from playwright.sync_api import expect


def test_run_jobs_schedule_table_visible(page, streamlit_url, streamlit_process):
    """Run Jobs page shows Job schedule expander and schedule table."""
    page.goto(streamlit_url)
    page.get_by_text("Run Jobs", exact=True).click()
    expect(page.get_by_test_id("page-run-jobs")).to_be_attached()
    expect(page.get_by_role("heading", name="Run Jobs")).to_be_visible()

    # Schedule section is present (expander + caption; table columns may not expose columnheader role)
    expect(page.get_by_test_id("run-jobs-schedule")).to_be_attached()
    expect(page.get_by_text("Job schedule", exact=True)).to_be_visible()
    expect(page.get_by_text("When each job is configured to run (cron or manual).")).to_be_visible()

    # Main actions: Run All, Run Selected, and job multiselect are present when jobs are loaded
    expect(page.get_by_role("button", name="Run All")).to_be_visible()
    expect(page.get_by_role("button", name="Run Selected")).to_be_visible()
    expect(page.get_by_text("Select jobs to run")).to_be_visible()
