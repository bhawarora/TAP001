import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="session")
def page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        context = browser.new_context(
            storage_state="C:\\Users\\bhawna.arora\\PycharmProjects\\PythonProject\\TAP\\Scripts/auth.json",
            viewport={"width": 1366, "height": 768}
        )
        page = context.new_page()
        yield page

        context.close()
        browser.close()
