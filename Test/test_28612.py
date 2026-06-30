import pytest
from playwright.sync_api import sync_playwright, expect
import os


@pytest.fixture(scope="session")
def page():
    auth_paths = [
        os.path.join(os.path.dirname(__file__), "..", "Scripts", "auth.json"),
        os.path.join(os.path.dirname(__file__), "..", "auth.json"),
        os.path.join(os.path.dirname(__file__), "..", "..", "Scripts", "auth.json"),
        os.path.join(os.path.dirname(__file__), "..", "..", "auth.json"),
    ]

    auth_path = None
    for path in auth_paths:
        abs_path = os.path.abspath(path)
        if os.path.exists(abs_path):
            auth_path = abs_path
            break

    if not auth_path:
        raise FileNotFoundError("auth.json not found in expected locations.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            storage_state=auth_path,
            viewport={"width": 1366, "height": 768}
        )
        page = context.new_page()
        yield page
        context.close()
        browser.close()


def test_contract_fields_visible(page):

    url = "https://apps.powerapps.com/play/e/4d750f69-e41e-eef2-9f2d-0a1a538a9c00/a/024c5985-82c9-48bc-82a0-e73da686773e?tenantId=16532572-d567-4d67-8727-f12f7bb6aed3&source=AppSharedV3&hint=d033a915-af0b-4cf2-915b-c5d049485010&sourcetime=1747834684577"

    page.goto(url, wait_until="domcontentloaded")

    frame = page.frame_locator("iframe[name='fullscreen-app-host']")

    # Begin
    begin_btn = frame.get_by_role("button", name="Begin")
    expect(begin_btn).to_be_visible(timeout=90000)
    begin_btn.click()

    # Agree
    agree_btn = frame.get_by_role("button", name="Agree", exact=True)
    expect(agree_btn).to_be_visible(timeout=90000)
    agree_btn.click()

    # Open dropdown
    dropdown = frame.get_by_role("combobox")
    expect(dropdown).to_be_visible(timeout=20000)
    dropdown.click()

    # Select Contracts
    contracts_option = frame.get_by_role("option", name="Contracts")
    expect(contracts_option).to_be_visible(timeout=70000)
    contracts_option.click()

    labels = ["Contract Title", "Contract ID", "Contract Duration", "Party Name", "Party Reference Name", "Party Address",
              "Party Description", "Execution Date", "Effective Date", "Expiration Date", "Jurisdiction Details", "Renewal Date", "Jurisdiction",
              ]

    for label in labels:
        label_locator = frame.get_by_text(label, exact=True)
        expect(label_locator).to_be_visible(timeout=100000)

    print("✅ All Contract fields are visible.")



