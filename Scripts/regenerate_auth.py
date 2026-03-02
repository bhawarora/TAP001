from playwright.sync_api import sync_playwright

def regenerate_auth():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1366, "height": 768})
        page = context.new_page()
        page.goto("https://apps.powerapps.com")

        print("Please log in manually in the browser window.")
        input("Press Enter after completing the login process...")

        # Save the authenticated session state
        context.storage_state(path="Scripts/auth.json")
        print("Authentication state saved to Scripts/auth.json")

        browser.close()

if __name__ == "__main__":
    regenerate_auth()
