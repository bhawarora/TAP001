import pytest
from playwright.sync_api import sync_playwright
import time

# Path to the PDF file to upload
DOCUMENT_PATH = "test_upload1.pdf"

# Test URL
TEST_URL = "https://apps.powerapps.com/play/e/4d750f69-e41e-eef2-9f2d-0a1a538a9c00/a/024c5985-82c9-48bc-82a0-e73da686773e?tenantId=16532572-d567-4d67-8727-f12f7bb6aed3&source=AppSharedV3&hint=d033a915-af0b-4cf2-915b-c5d049485010&sourcetime=1747834684577#"

@pytest.mark.order(1)
def test_verify_product():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context()
        page = context.new_page()
        page.goto(TEST_URL)

        # Step 1: Click Begin button
        page.wait_for_selector("text=Begin", timeout=60000)
        page.click("text=Begin")

        # Step 2: Click Agree button
        page.wait_for_selector("text=Agree", timeout=60000)
        page.click("text=Agree")

        # Step 3: Upload the document
        page.wait_for_selector("input[type='file']", timeout=60000)
        page.set_input_files("input[type='file']", DOCUMENT_PATH)

        # Step 4: Click the drop down arrow under document type
        page.wait_for_selector("[aria-label='Document Type']", timeout=60000)
        page.click("[aria-label='Document Type']")
        page.wait_for_selector("text=Invoices", timeout=60000)
        page.click("text=Invoices")

        # Step 5: Select checkboxes under Fields to Extract-ADI
        fields = ["Vendor Name", "Invoice ID", "Due Date", "Sub Total"]
        for field in fields:
            # Scroll to the field and check the box
            locator = page.locator(f"text={field}")
            locator.scroll_into_view_if_needed()
            # Try to check the checkbox next to the field
            checkbox = page.locator(f"//label[contains(., '{field}')]/preceding-sibling::input[@type='checkbox']")
            if not checkbox.is_checked():
                checkbox.check()

        # Step 6: Scroll down to the bottom of the screen
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

        # Step 7: Check the agreement checkbox
        agreement_label = "I agree to the Terms & Conditions and confirm that I have the necessary rights to process these documents"
        agreement_checkbox = page.locator(f"//label[contains(., '{agreement_label}')]/preceding-sibling::input[@type='checkbox']")
        agreement_checkbox.scroll_into_view_if_needed()
        if not agreement_checkbox.is_checked():
            agreement_checkbox.check()

        # Step 8: Stay on screen for 60 seconds
        time.sleep(60)

        # Optionally, validate the product name in the results (update selector as needed)
        # assert page.is_visible("text=Product Name")

        context.close()
        browser.close()

