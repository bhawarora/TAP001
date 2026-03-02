import pytest
from playwright.sync_api import sync_playwright, expect
import os

@pytest.fixture(scope="session")
def page():
    # Try both possible locations for auth.json
    auth_paths = [
        os.path.join(os.path.dirname(__file__), "..", "Scripts", "auth.json"),
        os.path.join(os.path.dirname(__file__), "..", "auth.json"),
        os.path.join(os.path.dirname(__file__), "..", "..", "Scripts", "auth.json"),
        os.path.join(os.path.dirname(__file__), "..", "..", "auth.json"),
    ]
    auth_path = None
    for path in auth_paths:
        if os.path.exists(os.path.abspath(path)):
            auth_path = os.path.abspath(path)
            break
    if not auth_path:
        raise FileNotFoundError("auth.json not found in expected locations.")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            storage_state=auth_path,
            viewport={"width": 1366, "height": 768}  # type: ignore
        )
        page = context.new_page()
        yield page
        context.close()
        browser.close()

def test_requestform_product_flow(page):
    url = "https://apps.powerapps.com/play/e/4d750f69-e41e-eef2-9f2d-0a1a538a9c00/a/024c5985-82c9-48bc-82a0-e73da686773e?tenantId=16532572-d567-4d67-8727-f12f7bb6aed3&source=AppSharedV3&hint=d033a915-af0b-4cf2-915b-c5d049485010&sourcetime=1747834684577"
    page.goto(url, wait_until="domcontentloaded")

    # Wait for the iframe to load
    frame = page.frame_locator("iframe[name='fullscreen-app-host']")
    begin_btn = frame.get_by_role("button", name="Begin", exact=True)
    expect(begin_btn).to_be_visible(timeout=90000)
    begin_btn.click(force=True)

    agree_btn = frame.get_by_role("button", name="Agree", exact=True)
    expect(agree_btn).to_be_visible(timeout=90000)
    agree_btn.click(force=True)

    # Upload the attached document (assume a file named 'test_upload1.pdf' in the workspace root)
    upload_btn = frame.get_by_role("button", name="Drag and drop your file here")
    expect(upload_btn).to_be_visible(timeout=60000)
    upload_btn.set_input_files("test_upload1.pdf")

    # Click the drop down arrow under document type
    # Try alternative selectors for the document type dropdown
    # Option 1: Try by text
    try:
        doc_type_dropdown = frame.get_by_text("Document Type")
        expect(doc_type_dropdown).to_be_visible(timeout=10000)
        doc_type_dropdown.click()
    except Exception:
        # Option 2: Try by placeholder or label
        try:
            doc_type_dropdown = frame.locator("[aria-label*='document type'], [placeholder*='document type']")
            expect(doc_type_dropdown).to_be_visible(timeout=10000)
            doc_type_dropdown.click()
        except Exception:
            # Option 3: Fallback to any visible dropdown after upload
            dropdowns = frame.locator("select, [role='combobox'], .dropdown, .Select-control")
            expect(dropdowns.nth(0)).to_be_visible(timeout=10000)
            dropdowns.nth(0).click()

    # Select 'Invoices' from the drop down list
    invoices_option = frame.get_by_text("Invoices")
    expect(invoices_option).to_be_visible(timeout=10000)
    invoices_option.click()

    # Click Select All button under Fields to Extract-ADI
    select_all_btn = frame.get_by_role("button", name="Select All")
    expect(select_all_btn).to_be_visible(timeout=10000)
    select_all_btn.click()

    # Select all checkboxes under Fields to Extract-ADI
    # Try to find all checkboxes in the visible area after Select All
    checkboxes = frame.locator("input[type='checkbox']")
    for i in range(checkboxes.count()):
        cb = checkboxes.nth(i)
        if cb.is_visible() and not cb.is_checked():
            cb.check()

    # Scroll down to the bottom of the screen
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(2000)  # Wait for scroll to complete

    # Check the checkbox for Terms & Conditions
    # Try by label text first
    try:
        terms_checkbox = frame.get_by_label("I agree to the Terms & Conditions and confirm that I have the necessary rights to process these documents")
        expect(terms_checkbox).to_be_visible(timeout=10000)
        if not terms_checkbox.is_checked():
            terms_checkbox.check()
    except Exception:
        # Fallback: try by text or role
        try:
            terms_checkbox = frame.get_by_text("I agree to the Terms & Conditions and confirm that I have the necessary rights to process these documents")
            expect(terms_checkbox).to_be_visible(timeout=10000)
            terms_checkbox.click()
        except Exception:
            # Fallback: try any visible checkbox
            checkboxes = frame.locator("input[type='checkbox']")
            for i in range(checkboxes.count()):
                cb = checkboxes.nth(i)
                if cb.is_visible() and not cb.is_checked():
                    cb.check()
                    break

    # Stay on screen for 60 seconds
    page.wait_for_timeout(60000)

    # Optionally, validate the product name in the results (update selector as needed)
    # product_name = frame.get_by_text("Expected Product Name")
    # expect(product_name).to_be_visible(timeout=30000)
    # assert product_name.inner_text() == "Expected Product Name"

    # Add more steps/assertions as required by the app's flow

