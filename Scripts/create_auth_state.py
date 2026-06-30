from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto(
        "https://apps.powerapps.com/play/e/4d750f69-e41e-eef2-9f2d-0a1a538a9c00/a/024c5985-82c9-48bc-82a0-e73da686773e?tenantId=16532572-d567-4d67-8727-f12f7bb6aed3&source=AppSharedV3&hint=d033a915-af0b-4cf2-915b-c5d049485010&sourcetime=1747834684577")

    page.get_by_label("Email, phone, or Skype").fill("bhawna.arora@protivitiglobal.in")
    page.get_by_role("button", name="Next").click()


    page.wait_for_selector('input[type="password"]', timeout=60000)

    page.locator('input[type="password"]').fill("Protiviti@202601")
    page.get_by_role("button", name="Sign in").click()


    try:
        page.get_by_role("button", name="Yes").click(timeout=5000)
    except:
        pass


    page.wait_for_load_state("networkidle")


    context.storage_state(path="auth.json")

    browser.close()
