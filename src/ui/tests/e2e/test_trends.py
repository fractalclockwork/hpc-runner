"""E2E tests for Long-Term Trends page — runtime and MLUPS trend charts."""

import pytest
from playwright.sync_api import expect


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _go_to_trends(page, streamlit_url: str) -> None:
    """Navigate to the Long-Term Trends page and wait for the testid marker."""
    page.goto(streamlit_url)
    page.get_by_text("Long-Term Trends", exact=True).click()
    expect(page.get_by_test_id("page-long-term-trends")).to_be_attached()


def _has_run_data(page) -> bool:
    """Return True if the page loaded trend sections (i.e. DB has run data)."""
    return page.get_by_test_id("section-runtime-trend").count() > 0


# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------

def test_long_term_trends_nav_item_visible(page, streamlit_url, streamlit_process):
    """'Long-Term Trends' option is present in the sidebar navigation."""
    page.goto(streamlit_url)
    expect(page.get_by_text("Long-Term Trends", exact=True)).to_be_visible()


def test_long_term_trends_page_loads(page, streamlit_url, streamlit_process):
    """Navigating to Long-Term Trends renders the page header."""
    _go_to_trends(page, streamlit_url)
    expect(page.get_by_role("heading", name="Long-Term Trends")).to_be_visible()


# ---------------------------------------------------------------------------
# No-data state
# ---------------------------------------------------------------------------

def test_long_term_trends_empty_state(page, streamlit_url, streamlit_process):
    """When the DB has no runs, an informational message is shown instead of charts."""
    _go_to_trends(page, streamlit_url)
    if _has_run_data(page):
        pytest.skip("DB contains run data — empty-state not visible")
    expect(page.get_by_text("No run data available yet")).to_be_visible()


# ---------------------------------------------------------------------------
# Runtime trend section
# ---------------------------------------------------------------------------

def test_runtime_trend_section_present(page, streamlit_url, streamlit_process):
    """Runtime trend section marker and subheading are present when data exists."""
    _go_to_trends(page, streamlit_url)
    if not _has_run_data(page):
        pytest.skip("No run data in DB — runtime trend section not rendered")
    expect(page.get_by_test_id("section-runtime-trend")).to_be_attached()
    expect(page.get_by_role("heading", name="Runtime (wall-clock) Trend")).to_be_visible()


def test_runtime_trend_chart_or_empty_message(page, streamlit_url, streamlit_process):
    """Runtime section shows either a Plotly chart or an empty-state info message."""
    _go_to_trends(page, streamlit_url)
    if not _has_run_data(page):
        pytest.skip("No run data in DB — runtime trend section not rendered")
    # After sidebar filters are applied, either a chart or an info message is shown
    charts = page.locator('[data-testid="stPlotlyChart"]')
    no_runtime_msg = page.get_by_text("No run data available yet")
    no_filter_msg = page.get_by_text("No runtime data recorded")
    assert (
        charts.count() > 0
        or no_runtime_msg.count() > 0
        or no_filter_msg.count() > 0
    ), "Expected a chart or an empty-state message in the runtime trend section"


# ---------------------------------------------------------------------------
# MLUPS trend section
# ---------------------------------------------------------------------------

def test_mlups_trend_section_present(page, streamlit_url, streamlit_process):
    """MLUPS trend section marker and subheading are present when data exists."""
    _go_to_trends(page, streamlit_url)
    if not _has_run_data(page):
        pytest.skip("No run data in DB — MLUPS trend section not rendered")
    expect(page.get_by_test_id("section-mlups-trend")).to_be_attached()
    expect(page.get_by_role("heading", name="Throughput Trend (MLUPS)")).to_be_visible()


def test_mlups_trend_chart_or_empty_message(page, streamlit_url, streamlit_process):
    """MLUPS section shows either a Plotly chart or an expected empty-state message."""
    _go_to_trends(page, streamlit_url)
    if not _has_run_data(page):
        pytest.skip("No run data in DB — MLUPS trend section not rendered")
    charts = page.locator('[data-testid="stPlotlyChart"]')
    no_mlups_msg = page.get_by_text("No MLUPS data available")
    no_mlups_recorded = page.get_by_text("No MLUPS values recorded")
    assert (
        charts.count() > 0
        or no_mlups_msg.count() > 0
        or no_mlups_recorded.count() > 0
    ), "Expected a chart or an empty-state message in the MLUPS trend section"


# ---------------------------------------------------------------------------
# Sidebar filters (only shown when data is present)
# ---------------------------------------------------------------------------

def test_long_term_trends_sidebar_filters(page, streamlit_url, streamlit_process):
    """Sidebar shows the solver, system, and date-range filter widgets when data exists."""
    _go_to_trends(page, streamlit_url)
    if not _has_run_data(page):
        pytest.skip("No run data in DB — sidebar filters only render when data is present")
    expect(page.get_by_text("Long-Term Trends Filters")).to_be_visible()
    expect(page.get_by_text("Solver(s)")).to_be_visible()
    expect(page.get_by_text("System(s)")).to_be_visible()
    expect(page.get_by_text("Date range")).to_be_visible()
