"""E2E tests for Run Jobs page."""

from playwright.sync_api import expect


def test_run_jobs_schedule_table_visible(page, streamlit_url, streamlit_process):
    """Run Jobs page shows Job schedule expander and schedule table."""
    page.goto(streamlit_url)
    page.get_by_text("Run Jobs", exact=True).click()
    expect(page.get_by_test_id("page-run-jobs")).to_be_attached()
    expect(page.get_by_role("heading", name="Run Jobs")).to_be_visible()

    # Schedule section is present
    expect(page.get_by_test_id("run-jobs-schedule")).to_be_attached()
    expect(page.get_by_text("Job schedule", exact=True)).to_be_visible()
    expect(page.get_by_text("When each job is configured to run (cron or manual).")).to_be_visible()

    # Schedule table has expected columns (Streamlit dataframe renders as table)
    expect(page.get_by_text("Job", exact=True).first).to_be_visible()
    expect(page.get_by_text("Solver", exact=True).first).to_be_visible()
    expect(page.get_by_text("System", exact=True).first).to_be_visible()
    expect(page.get_by_text("Schedule", exact=True).first).to_be_visible()
