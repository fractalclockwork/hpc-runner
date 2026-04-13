"""
Playwright test: clicking a Plotly line plot navigates to the correct
page with the expected element expanded.
"""

from playwright.sync_api import expect


import re
import pytest
from playwright.sync_api import Page, expect

# ── Config ────────────────────────────────────────────────────────────────────
BASE_URL = "http://localhost:8501"
CHART_URL = f"{BASE_URL}"          # page that hosts the Plotly chart
EXPECTED_PATH_RE = re.compile(r"/detail/\d+")  # URL pattern after click
DETAIL_SECTION_SELECTOR = '[data-testid="detail-section"]'
EXPANDED_ATTRIBUTE = "aria-expanded"


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_plotly_canvas(page: Page):
    """Return the <canvas> (or SVG layer) inside the Plotly chart."""
    # Plotly renders an <svg> with class "main-svg"; the interactive overlay
    # is a <rect class="nsewdrag drag">.  We click that overlay.
    return page.locator(".nsewdrag.drag").first


def click_first_data_point(page: Page) -> None:
    """
    Click the first visible data point on the Plotly line chart.

    Strategy: Plotly exposes each trace point as an SVG <path> or <circle>
    inside `.scatterlayer .trace`.  We click the first one.
    If your chart uses scatter markers, the selector is `.point`; for a pure
    line trace without markers use the midpoint of the SVG line path.
    """
    # Works for scatter+lines mode (markers visible)
    point_locator = page.locator(".scatterlayer .trace .points .point").first

    # Fall back: click the drag overlay at the position of the first tick
    if point_locator.count() == 0:
        # Click at ~10 % of the chart width (first segment of the line)
        canvas = get_plotly_canvas(page)
        box = canvas.bounding_box()
        assert box is not None, "Could not find Plotly drag overlay"
        page.mouse.click(
            box["x"] + box["width"] * 0.10,
            box["y"] + box["height"] * 0.50,
        )
    else:
        point_locator.click()


def test_page_loads_with_chart(self, page: Page) -> None:
    """
    Check the chart page renders a Plotly SVG.
    """
    page.goto(CHART_URL)
    page.locator('section[data-testid="stSidebar"]').get_by_text("Long-Term Trends", exact=True).click()
    page.wait_for_selector(".main-svg", timeout=10_000)
    expect(page.locator(".main-svg")).to_be_visible()


def test_click_navigates_to_detail_page(self, page: Page) -> None:
    """
    Clicking a data point triggers navigation to the detail URL.
    """
    page.goto(CHART_URL)
    page.wait_for_selector(".main-svg", timeout=10_000)

    # Wait for any loading spinners to disappear
    page.wait_for_load_state("networkidle")

    with page.expect_navigation(
        url=EXPECTED_PATH_RE,
        timeout=8_000,
        wait_until="domcontentloaded",
    ):
        click_first_data_point(page)

    assert EXPECTED_PATH_RE.search(page.url), (
        f"Expected URL matching {EXPECTED_PATH_RE.pattern}, got {page.url}"
    )


def test_detail_section_is_expanded_after_navigation(self, page: Page) -> None:
    """
    After navigating from the chart click, the relevant detail section
    must be expanded (aria-expanded='true').
    """
    page.goto(CHART_URL)
    page.wait_for_selector(".main-svg", timeout=10_000)
    page.wait_for_load_state("networkidle")

    with page.expect_navigation(url=EXPECTED_PATH_RE, timeout=8_000):
        click_first_data_point(page)

    # Wait for the detail section to appear and be expanded
    section = page.locator(DETAIL_SECTION_SELECTOR)
    expect(section).to_be_visible(timeout=8_000)
    expect(section).to_have_attribute(EXPANDED_ATTRIBUTE, "true", timeout=5_000)


def test_correct_detail_id_in_url(self, page: Page) -> None:
    """
    The detail page URL should contain the ID that corresponds to the
    clicked data point.  Here we verify it is a non-zero integer.
    """
    page.goto(CHART_URL)
    page.wait_for_selector(".main-svg", timeout=10_000)
    page.wait_for_load_state("networkidle")

    with page.expect_navigation(url=EXPECTED_PATH_RE, timeout=8_000):
        click_first_data_point(page)

    match = EXPECTED_PATH_RE.search(page.url)
    assert match, f"Detail ID not found in URL: {page.url}"
    detail_id = int(match.group(0).split("/")[-1])
    assert detail_id > 0, f"Expected positive detail ID, got {detail_id}"


def test_back_navigation_returns_to_chart(self, page: Page) -> None:
    """
    Pressing browser Back from the detail page returns to the chart.
    """
    page.goto(CHART_URL)
    page.wait_for_selector(".main-svg", timeout=10_000)
    page.wait_for_load_state("networkidle")

    with page.expect_navigation(url=EXPECTED_PATH_RE, timeout=8_000):
        click_first_data_point(page)

    page.go_back(wait_until="domcontentloaded")
    expect(page.locator(".main-svg")).to_be_visible(timeout=8_000)


# ── Parametrized variant: test multiple data points ───────────────────────────

@pytest.mark.parametrize("x_fraction", [0.10, 0.50, 0.90])
def test_multiple_points_navigate_correctly(page: Page, x_fraction: float) -> None:
    """
    Clicking at three positions along the chart (left, mid, right) should
    each navigate to a valid detail page with the section expanded.
    """
    page.goto(CHART_URL)
    page.wait_for_selector(".main-svg", timeout=10_000)
    page.wait_for_load_state("networkidle")

    canvas = get_plotly_canvas(page)
    box = canvas.bounding_box()
    assert box is not None

    with page.expect_navigation(url=EXPECTED_PATH_RE, timeout=8_000):
        page.mouse.click(
            box["x"] + box["width"] * x_fraction,
            box["y"] + box["height"] * 0.50,
        )

    assert EXPECTED_PATH_RE.search(page.url), f"No match at x_fraction={x_fraction}"

    section = page.locator(DETAIL_SECTION_SELECTOR)
    expect(section).to_be_visible(timeout=8_000)
    expect(section).to_have_attribute(EXPANDED_ATTRIBUTE, "true", timeout=5_000)

    # Return to chart for the next parametrized case
    page.goto(CHART_URL)
    page.wait_for_selector(".main-svg", timeout=10_000)
