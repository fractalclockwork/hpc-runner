"""E2E smoke tests for Individual Trends page."""

from playwright.sync_api import expect


def test_individual_trends_nav_and_page(page, streamlit_url, streamlit_process):
    """Sidebar navigates to Individual Trends; page marker and header render."""
    page.goto(streamlit_url)
    page.locator('section[data-testid="stSidebar"]').get_by_text("Individual Trends", exact=True).click()
    expect(page.get_by_test_id("page-individual-trends")).to_be_attached()
    main = page.get_by_test_id("stMainBlockContainer")
    expect(main.get_by_role("heading", name="Individual Trends").first).to_be_visible()
