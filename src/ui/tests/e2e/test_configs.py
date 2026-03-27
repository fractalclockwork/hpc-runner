"""E2E tests for Configs page (read-only YAML; no in-UI edit or validate)."""

from playwright.sync_api import expect


def test_configs_page_readonly_view(page, streamlit_url, streamlit_process):
    """Configs page shows category/file selectors and read-only YAML preview."""
    page.goto(streamlit_url)
    page.get_by_text("Configs", exact=True).click()
    expect(page.get_by_test_id("page-configs")).to_be_attached()
    expect(page.get_by_role("heading", name="Configs")).to_be_visible()
    expect(
        page.get_by_text("View jobs, resources, solvers, and systems configurations.")
    ).to_be_visible()
    expect(page.get_by_text("Category")).to_be_visible()
    expect(page.get_by_text("File")).to_be_visible()
    # st.code() renders as a pre/code block once a file is selected
    expect(page.locator("pre")).to_be_visible(timeout=10000)
