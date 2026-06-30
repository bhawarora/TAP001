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


def test_mortgage_1003(page):

    url = "https://apps.powerapps.com/play/e/4d750f69-e41e-eef2-9f2d-0a1a538a9c00/a/024c5985-82c9-48bc-82a0-e73da686773e?tenantId=16532572-d567-4d67-8727-f12f7bb6aed3&source=AppSharedV3&hint=d033a915-af0b-4cf2-915b-c5d049485010&sourcetime=1747834684577"

    page.goto(url, wait_until="domcontentloaded")

    frame = page.frame_locator("iframe[name='fullscreen-app-host']")

    # Click Begin
    begin_btn = frame.get_by_role("button", name="Begin")
    expect(begin_btn).to_be_visible(timeout=90000)
    begin_btn.click()

    # Click Agree
    agree_btn = frame.get_by_role("button", name="Agree", exact=True)
    expect(agree_btn).to_be_visible(timeout=90000)
    agree_btn.click()

    # Open dropdown
    dropdown = frame.get_by_role("combobox")
    expect(dropdown).to_be_visible(timeout=20000)
    dropdown.click()

    # Select Mortgage 1003 URLA
    mortgage_option = frame.get_by_role("option", name="Mortgage 1003 URLA")
    expect(mortgage_option).to_be_visible(timeout=70000)
    mortgage_option.click()

    page.wait_for_timeout(2000)

    # Scroll inside iframe
    frame.locator("body").evaluate("window.scrollBy(0, 400)")

    # Expand Borrower Details
    expand_icon = frame.locator(
        ".container_1f0sgyp > div:nth-child(2) > "
        ".appmagic-borderfill-container > "
        ".appmagic-border-inner > "
        ".react-knockout-control > "
        ".powerapps-icon"
    ).first

    expect(expand_icon).to_be_visible(timeout=60000)
    expand_icon.click()

    page.wait_for_timeout(2000)

    # -------------------------
    # Select Borrower Fields
    # -------------------------

    # Click SSN checkbox
    ssn_checkbox = frame.locator("label", has_text="SSN").locator("rect")
    expect(ssn_checkbox).to_be_visible(timeout=30000)
    ssn_checkbox.click()

    # Click additional borrower checkboxes
    borrower_checkboxes = frame.locator(
        ".appmagic-checkbox-control svg g rect"
    )

    for i in range(min(2, borrower_checkboxes.count())):
        checkbox = borrower_checkboxes.nth(i)
        if checkbox.is_visible():
            checkbox.click()

    print("✅ Mortgage 1003 → Borrower Details flow completed successfully.")
