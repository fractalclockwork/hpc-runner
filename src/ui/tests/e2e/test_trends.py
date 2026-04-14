"""E2E tests for Long-Term Trends page — metric trend chart (numeric metrics from runs)."""

import pytest
from playwright.sync_api import expect


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _go_to_trends(page, streamlit_url: str) -> None:
    """Navigate to the Long-Term Trends page and wait for the testid marker."""
    page.goto(streamlit_url)
    page.locator('section[data-testid="stSidebar"]').get_by_text("Long-Term Trends", exact=True).click()
    expect(page.get_by_test_id("page-long-term-trends")).to_be_attached()
    # page-long-term-trends is emitted at the top; charts and sidebar filters render later.
    # Wait so _has_run_data and empty-state checks are not flaky on slower runs.
    empty_msg = page.get_by_text("No run data available yet")
    filters = page.get_by_text("Long-Term Trends Filters")
    expect(empty_msg.or_(filters)).to_be_visible(timeout=15000)


def _has_run_data(page) -> bool:
    """Return True if the Long-Term Trends page has run data (filters + tabs are shown).

    Do not rely on ``section-metric-trend`` alone: that marker lives inside the **Metric trends**
    tab and may not be in the DOM until the tab is opened, which made skips flaky.
    """
    return page.get_by_role("tab", name="Metric trends").count() > 0


def _open_metric_trends_tab(page) -> None:
    """Long-Term Trends defaults to Heatmap; metric chart lives on the second tab."""
    page.get_by_role("tab", name="Metric trends").click()


def _metric_trend_chart_locator(page):
    """Plotly chart in the active tab only.

    The Heatmap tab may still render ``stPlotlyChart`` nodes in the DOM while hidden;
    ``:first`` matches that hidden chart. Restrict to visible charts so we assert the
    Metric trends tab content.
    """
    return page.locator('[data-testid="stPlotlyChart"]:visible').first


# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------

def test_long_term_trends_nav_item_visible(page, streamlit_url, streamlit_process):
    """'Long-Term Trends' option is present in the sidebar navigation."""
    page.goto(streamlit_url)
    sb = page.locator('section[data-testid="stSidebar"]')
    expect(sb.get_by_text("Long-Term Trends", exact=True)).to_be_visible()


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
    if _has_run_data(page) or page.get_by_text("Long-Term Trends Filters").is_visible():
        pytest.skip("DB contains run data — empty-state not visible")
    expect(page.get_by_text("No run data available yet")).to_be_visible()


# ---------------------------------------------------------------------------
# Metric trend section (numeric metrics from parser output)
# ---------------------------------------------------------------------------

def test_metric_trend_section_present(page, streamlit_url, streamlit_process):
    """Metric trend section marker; Plotly chart or empty-state when data exists."""
    _go_to_trends(page, streamlit_url)
    if not _has_run_data(page):
        pytest.skip("No run data in DB — metric trend section not rendered")
    _open_metric_trends_tab(page)
    expect(page.get_by_test_id("section-metric-trend")).to_be_attached()
    # Plotly titles live in SVG tspans that Playwright treats as not visible — assert chart widget or empty-state text
    chart_visible = _metric_trend_chart_locator(page)
    no_numeric = page.get_by_text("No numeric metrics in stored runs")
    no_values = page.get_by_text("No values recorded for")
    unexpected = page.get_by_text("Unexpected data format")
    expect(chart_visible.or_(no_numeric).or_(no_values).or_(unexpected)).to_be_visible(timeout=10000)


def test_metric_trend_chart_or_empty_message(page, streamlit_url, streamlit_process):
    """Metric trends tab shows either a Plotly chart or an expected empty-state message."""
    _go_to_trends(page, streamlit_url)
    if not _has_run_data(page):
        pytest.skip("No run data in DB — metric trend section not rendered")
    _open_metric_trends_tab(page)
    chart_visible = _metric_trend_chart_locator(page)
    no_numeric_first = page.get_by_text("No numeric metrics in stored runs").first
    no_values_first = page.get_by_text("No values recorded for").first
    unexpected_first = page.get_by_text("Unexpected data format").first
    expect(chart_visible.or_(no_numeric_first).or_(no_values_first).or_(unexpected_first)).to_be_visible(
        timeout=10000
    )
    charts_visible = page.locator('[data-testid="stPlotlyChart"]:visible')
    no_numeric_msg = page.get_by_text("No numeric metrics in stored runs")
    no_values_msg = page.get_by_text("No values recorded for")
    unexpected_fmt = page.get_by_text("Unexpected data format")
    assert (
        charts_visible.count() > 0
        or no_numeric_msg.count() > 0
        or no_values_msg.count() > 0
        or unexpected_fmt.count() > 0
    ), "Expected a chart or an empty-state message in the metric trends section"


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
