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
        if os.path.exists(os.path.abspath(path)):
            auth_path = os.path.abspath(path)
            break
    if not auth_path:
        raise FileNotFoundError(f"auth.json not found in expected locations: {auth_paths}")
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

def test_customoption_product_flow(page):
    url = "https://apps.powerapps.com/play/e/4d750f69-e41e-eef2-9f2d-0a1a538a9c00/a/024c5985-82c9-48bc-82a0-e73da686773e?tenantId=16532572-d567-4d67-8727-f12f7bb6aed3&source=AppSharedV3&hint=d033a915-af0b-4cf2-915b-c5d049485010&sourcetime=1747834684577"
    page.goto(url, wait_until="domcontentloaded")

    frame = page.frame_locator("iframe[name='fullscreen-app-host']")
    begin_btn = frame.get_by_role("button", name="Begin", exact=True)
    expect(begin_btn).to_be_visible(timeout=90000)
    begin_btn.click(force=True)

    agree_btn = frame.get_by_role("button", name="Agree", exact=True)
    expect(agree_btn).to_be_visible(timeout=90000)
    agree_btn.click(force=True)

    upload_btn = frame.get_by_role("button", name="Drag and drop your file here")
    expect(upload_btn).to_be_visible(timeout=60000)
    upload_btn.set_input_files("test_upload1.pdf")

    doc_type_dropdown = frame.locator("[aria-label*='document type'], [placeholder*='document type'], select, [role='combobox'], .dropdown, .Select-control")
    expect(doc_type_dropdown.first).to_be_visible(timeout=10000)
    doc_type_dropdown.first.click()

    custom_option = frame.get_by_text("Custom (Beta - Free)")
    expect(custom_option).to_be_visible(timeout=10000)
    custom_option.click()

    # Scroll down till Column Header appears
    for _ in range(20):
        if frame.get_by_text("Column Header").is_visible():
            break
        page.evaluate("window.scrollBy(0, 100)")
        page.wait_for_timeout(500)
    expect(frame.get_by_text("Column Header")).to_be_visible(timeout=10000)

    # Debug: Print all visible input and textarea fields after Column Header
    visible_fields = frame.locator("input, textarea").all()
    print(f"Found {len(visible_fields)} input/textarea fields after Column Header:")
    for idx, field in enumerate(visible_fields):
        try:
            print(f"Field {idx}: tag={field.evaluate('el => el.tagName')}, type={field.get_attribute('type')}, placeholder={field.get_attribute('placeholder')}, aria-label={field.get_attribute('aria-label')}, value={field.input_value()}")
        except Exception as e:
            print(f"Field {idx}: Could not evaluate - {e}")

    # Under Column Header, Remove text "Customer ID" and Add text "Total Amount"
    editable_inputs = frame.locator("input[type='text']:not([readonly])")
    expect(editable_inputs.first).to_be_visible(timeout=10000)
    editable_inputs.first.fill("")
    editable_inputs.first.type("Total Amount")

    # Under AI Prompt, Remove text "Describe what to extract..." and Add text "What is the Total Amount"
    ai_prompt_input = None
    try:
        ai_prompt_input = frame.get_by_placeholder("Describe what to extract...")
        expect(ai_prompt_input).to_be_visible(timeout=5000)
    except Exception:
        ai_prompt_input = frame.locator("textarea, input[aria-label*='AI Prompt'], input[aria-label*='extract']")
        expect(ai_prompt_input.first).to_be_visible(timeout=10000)
        ai_prompt_input = ai_prompt_input.first
    ai_prompt_input.fill("")
    ai_prompt_input.type("What is the Total Amount")

    # Under Sample Value, Remove text "CUST-12345" and Add text "1234"
    sample_value_input = frame.get_by_placeholder("CUST-12345")
    expect(sample_value_input).to_be_visible(timeout=10000)
    sample_value_input.fill("")
    sample_value_input.type("1234")

    # Click Add Parameter button
    add_param_btn = frame.get_by_role("button", name="Add Parameter")
    expect(add_param_btn).to_be_visible(timeout=10000)
    add_param_btn.click()

    # Scroll to bottom
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(2000)

    # Check Terms & Conditions checkbox
    terms_checkbox = frame.locator("input[type='checkbox']:visible, label:has-text('I agree to the Terms & Conditions')")
    expect(terms_checkbox.first).to_be_visible(timeout=10000)
    if not terms_checkbox.first.is_checked():
        terms_checkbox.first.check()

    page.wait_for_timeout(60000)
