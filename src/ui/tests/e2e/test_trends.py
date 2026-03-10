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
    # Scope to main content to avoid matching sidebar "Long-Term Trends Filters"
    main = page.get_by_test_id("stMainBlockContainer")
    expect(main.get_by_role("heading", name="Long-Term Trends")).to_be_visible()


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
    # Wait for Streamlit to render chart or empty-state message
    chart_first = page.locator('[data-testid="stPlotlyChart"]').first
    no_runtime_first = page.get_by_text("No run data available yet").first
    no_filter_first = page.get_by_text("No runtime data recorded").first
    unexpected_first = page.get_by_text("Unexpected data format").first
    expect(chart_first.or_(no_runtime_first).or_(no_filter_first).or_(unexpected_first)).to_be_visible(timeout=10000)
    # Then assert at least one of the expected outcomes
    charts = page.locator('[data-testid="stPlotlyChart"]')
    no_runtime_msg = page.get_by_text("No run data available yet")
    no_filter_msg = page.get_by_text("No runtime data recorded")
    unexpected_fmt = page.get_by_text("Unexpected data format")
    assert (
        charts.count() > 0
        or no_runtime_msg.count() > 0
        or no_filter_msg.count() > 0
        or unexpected_fmt.count() > 0
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
    # Wait for Streamlit to render chart or empty-state message
    chart_first = page.locator('[data-testid="stPlotlyChart"]').first
    no_mlups_first = page.get_by_text("No MLUPS data available").first
    no_mlups_rec_first = page.get_by_text("No MLUPS values recorded").first
    expect(chart_first.or_(no_mlups_first).or_(no_mlups_rec_first)).to_be_visible(timeout=10000)
    # Then assert at least one of the expected outcomes
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
    # Scope to sidebar to avoid matching main content or date picker's "Selected date range..." text
    sidebar = page.get_by_test_id("stSidebar")
    expect(sidebar.get_by_text("Date range", exact=True)).to_be_visible()
