"""E2E tests for sidebar navigation."""

from playwright.sync_api import expect


def test_sidebar_nav_visible(page, streamlit_url, streamlit_process):
    """Sidebar has navigation options; default route is Home."""
    page.goto(streamlit_url)
    expect(page.get_by_test_id("nav-sidebar")).to_be_attached()
    expect(page.get_by_test_id("page-home")).to_be_attached()
    expect(
        page.get_by_role("heading", name="Welcome to the HPC Regression Platform", exact=True).first
    ).to_be_visible()
    # Streamlit radio renders options as clickable labels in the sidebar
    sb = page.locator('section[data-testid="stSidebar"]')
    expect(sb.get_by_text("Solvers", exact=True)).to_be_visible()
    expect(sb.get_by_text("Run Matrix", exact=True)).to_be_visible()
    expect(sb.get_by_text("Run History", exact=True)).to_be_visible()
    expect(sb.get_by_text("Configs", exact=True)).to_be_visible()
    sb.get_by_text("Solvers", exact=True).click()
    main = page.get_by_test_id("stMainBlockContainer")
    expect(main.get_by_role("heading", name="Solvers").first).to_be_visible()


def test_navigate_to_configs(page, streamlit_url, streamlit_process):
    """Clicking Configs navigates to that page."""
    page.goto(streamlit_url)
    page.locator('section[data-testid="stSidebar"]').get_by_text("Configs", exact=True).click()
    expect(page.get_by_test_id("page-configs")).to_be_attached()
    expect(page.get_by_role("heading", name="Configs")).to_be_visible()


def test_navigate_to_run_history(page, streamlit_url, streamlit_process):
    """Clicking Run History navigates to that page."""
    page.goto(streamlit_url)
    page.locator('section[data-testid="stSidebar"]').get_by_text("Run History", exact=True).click()
    expect(page.get_by_test_id("page-run-history")).to_be_attached()
    expect(page.get_by_role("heading", name="Run History")).to_be_visible()
