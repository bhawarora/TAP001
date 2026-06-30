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
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context(
            storage_state=auth_path,
            viewport={"width": 1366, "height": 768}
        )
        page = context.new_page()
        yield page
        context.close()
        browser.close()


def test_validate_invoice_labels_present(page):
    url = "https://apps.powerapps.com/play/e/4d750f69-e41e-eef2-9f2d-0a1a538a9c00/a/024c5985-82c9-48bc-82a0-e73da686773e?tenantId=16532572-d567-4d67-8727-f12f7bb6aed3&source=AppSharedV3&hint=d033a915-af0b-4cf2-915b-c5d049485010&sourcetime=1747834684577"
    page.goto(url, wait_until="domcontentloaded")

    frame = page.frame_locator("iframe[name='fullscreen-app-host']")

    # Begin
    begin_btn = frame.get_by_role("button", name="Begin", exact=True)
    expect(begin_btn).to_be_visible(timeout=90000)
    begin_btn.click(force=True)

    # Agree
    agree_btn = frame.get_by_role("button", name="Agree", exact=True)
    expect(agree_btn).to_be_visible(timeout=90000)
    agree_btn.click(force=True)

    # Upload file
    upload_btn = frame.get_by_role("button", name="Drag and drop your file here")
    expect(upload_btn).to_be_visible(timeout=60000)
    upload_btn.set_input_files("test_upload1.pdf")

    # Open Document Type dropdown
    doc_type_dropdown = frame.get_by_text("Document Type")
    expect(doc_type_dropdown).to_be_visible(timeout=10000)
    doc_type_dropdown.click()

    # Select Invoices
    invoices_option = frame.get_by_text("Invoices", exact=True)
    expect(invoices_option).to_be_visible(timeout=10000)
    invoices_option.click()

    # ✅ Validate Labels Are Present
    expected_labels = ["Vendor Name", "Invoice ID", "Due Date", "Sub Total"]

    for label in expected_labels:
        label_locator = frame.get_by_text(label, exact=False)
        expect(label_locator).to_be_visible(timeout=20000)

    print("✅ All required invoice labels are present and visible.")

    page.wait_for_timeout(5000)
