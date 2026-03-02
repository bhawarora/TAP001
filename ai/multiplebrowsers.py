import pytest
from playwright.sync_api import sync_playwright, expect
import os


# Parameterize browser names
@pytest.fixture(scope="session", params=["chromium", "firefox"])
def browser_name(request):
    return request.param


@pytest.fixture(scope="session")
def auth_path():
    auth_paths = [
        os.path.join(os.path.dirname(__file__), "..", "Scripts", "auth.json"),
        os.path.join(os.path.dirname(__file__), "..", "auth.json"),
        os.path.join(os.path.dirname(__file__), "..", "..", "Scripts", "auth.json"),
        os.path.join(os.path.dirname(__file__), "..", "..", "auth.json"),
    ]

    for path in auth_paths:
        abs_path = os.path.abspath(path)
        if os.path.exists(abs_path):
            return abs_path

    raise FileNotFoundError("auth.json not found in expected locations.")


@pytest.fixture(scope="function")
def page(browser_name, auth_path):
    with sync_playwright() as p:
        browser = getattr(p, browser_name).launch(headless=False)

        context = browser.new_context(
            storage_state=auth_path,
            viewport={"width": 1366, "height": 768},
        )

        page = context.new_page()
        yield page

        context.close()
        browser.close()


def test_begin_button_flow(page):
    url = "https://apps.powerapps.com/play/e/4d750f69-e41e-eef2-9f2d-0a1a538a9c00/a/024c5985-82c9-48bc-82a0-e73da686773e?tenantId=16532572-d567-4d67-8727-f12f7bb6aed3&source=AppSharedV3&hint=d033a915-af0b-4cf2-915b-c5d049485010&sourcetime=1747834684577"

    page.goto(url, wait_until="domcontentloaded")

    # Wait for the iframe to load
    frame = page.frame_locator("iframe[name='fullscreen-app-host']")
    begin_btn = frame.get_by_role("button", name="Begin", exact=True)

    expect(begin_btn).to_be_visible(timeout=90000)
    begin_btn.click(force=True)

    # Add more assertions as needed
