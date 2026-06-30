r"""
Single-file script to open a Power Apps URL in Chrome using Selenium,
optionally enter username/password, and wait for MFA approval.

Usage:
  - Ensure Chrome is installed on the host machine.
  - From PowerShell (Windows):
      python -m pip install --upgrade pip ; pip install selenium webdriver-manager keyring
      python C:/Users/bhawna.arora/PycharmProjects/PythonProject/PythonProject2/code.py

Environment variables (optional):
  POWERAPPS_USER  - username (UPN/email)
  POWERAPPS_PASS  - password (if you want the script to enter it)
  POWERAPPS_WAIT_SECONDS - how many seconds to wait for MFA/login redirect (default 600)

Windows Credential Manager (recommended):
  This script can read credentials from the Windows Credential Manager using
  the Python `keyring` library. To store credentials for later runs, execute:

    python -c "import keyring; keyring.set_password('powerapps_automation',
      'bhawna.arora@protiviti.com', 'Protiviti@202601')"

  The script will then retrieve the password automatically when you run it.

Note on MFA: The script cannot bypass MFA. It will pause and wait for you to
complete the second factor (Authenticator push/code/SMS). It detects successful
login by watching for a redirect back to the Power Apps domain.
"""
import os
import sys
import getpass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

try:
    # webdriver_manager is optional but convenient
    from webdriver_manager.chrome import ChromeDriverManager
except Exception:
    ChromeDriverManager = None


try:
    import keyring
except Exception:
    keyring = None


POWERAPPS_URL = (
    "https://apps.powerapps.com/play/e/4d750f69-e41e-eef2-9f2d-0a1a538a9c00/"
    "a/a3c7aa7f-b23c-4abb-97fa-b5134f6f8c56?tenantId=16532572-d567-4d67-8727-"
    "f12f7bb6aed3&hint=5fbbcdb0-8caf-41f1-ad8c-4c36bae0d8e6&sourcetime=1731506807354"
    "&source=portal&source=teamsLinkUnfurling"
)

SHORT_TIMEOUT = 20
DEFAULT_LONG_TIMEOUT = int(os.getenv("POWERAPPS_WAIT_SECONDS", "600"))


def install_instructions_and_exit(missing_pkg: str):
    print(f"Missing optional package: {missing_pkg}.")
    print("Run the following in PowerShell to install requirements:")
    print("python -m pip install --upgrade pip ; pip install selenium webdriver-manager")
    sys.exit(1)


def build_driver():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    # Leave browser visible so user can perform MFA
    # chrome_options.add_argument("--headless=new")  # NOT recommended for MFA

    if ChromeDriverManager is None:
        install_instructions_and_exit("webdriver-manager")

    driver_path = ChromeDriverManager().install()
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def try_send_keys_if_present(driver, by, selector, value, timeout=SHORT_TIMEOUT):
    try:
        el = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, selector)))
        el.clear()
        el.send_keys(value)
        return True
    except Exception:
        return False


def try_click_if_present(driver, by, selector, timeout=SHORT_TIMEOUT):
    try:
        el = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, selector)))
        el.click()
        return True
    except Exception:
        return False


def wait_for_url_contains(driver, substring, timeout=DEFAULT_LONG_TIMEOUT):
    try:
        WebDriverWait(driver, timeout).until(lambda d: substring in d.current_url)
        return True
    except Exception:
        return False


def main():
    print("Starting Power Apps launcher (Chrome + Selenium)")

    username = os.getenv("POWERAPPS_USER") or input("Enter username (UPN/email): ").strip()
    password = os.getenv("POWERAPPS_PASS")

    # If password not provided by env, try to load from keyring (Windows Credential Manager)
    SERVICE_NAME = "powerapps_automation"
    if not password and keyring is not None:
        try:
            if username:
                pw = keyring.get_password(SERVICE_NAME, username)
                if pw:
                    password = pw
        except Exception:
            # ignore keyring lookup errors
            pass

        # If still not found, try keyring.get_credential (some backends support it)
        if not password:
            try:
                cred = None
                if hasattr(keyring, "get_credential"):
                    cred = keyring.get_credential(SERVICE_NAME, None)
                if cred:
                    # credential may provide username/password
                    if not username and getattr(cred, "username", None):
                        username = cred.username
                    if getattr(cred, "password", None):
                        password = cred.password
            except Exception:
                pass

    if not password:
        pwd_in = getpass.getpass("Enter password (leave blank to sign in manually): ")
        password = pwd_in if pwd_in else None

    try:
        driver = build_driver()
    except Exception as e:
        print("Failed to start Chrome WebDriver:", str(e))
        print("Ensure Chrome is installed and 'webdriver-manager' & 'selenium' are available.")
        sys.exit(1)

    try:
        print("Navigating to Power Apps URL...")
        driver.get(POWERAPPS_URL)

        # Attempt to enter username (common selectors + fallbacks for custom pages)
        entered = False
        user_selectors = [
            (By.ID, "i0116"),
            (By.NAME, "loginfmt"),
            (By.ID, "login"),
            (By.CSS_SELECTOR, "input[type='email']"),
            (By.CSS_SELECTOR, "input[type='text'][autocomplete='username']"),
            (By.XPATH, "//input[contains(@placeholder, 'Email') or contains(@placeholder, 'Email or phone') or contains(@placeholder, 'Username')]") ,
            (By.XPATH, "//input[contains(@aria-label, 'Email') or contains(@aria-label, 'Username')]") ,
        ]
        for by, sel in user_selectors:
            if try_send_keys_if_present(driver, by, sel, username, timeout=8):
                entered = True
                break

        # Click Next / Sign in button if present (multiple fallbacks)
        next_selectors = [
            (By.ID, "idSIButton9"),
            (By.XPATH, "//input[@type='submit']"),
            (By.XPATH, "//button[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'next')]") ,
            (By.XPATH, "//button[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'sign in')]") ,
            (By.XPATH, "//button[@type='submit']"),
        ]
        for by, sel in next_selectors:
            try:
                if try_click_if_present(driver, by, sel, timeout=5):
                    break
            except Exception:
                pass

        if not entered:
            print("Username field not detected or auto-entry skipped. Please complete sign-in manually in the opened browser window.")
        else:
            print("Username entered (or at least attempted).")

        # Try to enter password if provided (with fallback selectors)
        if password:
            pwd_sent = False
            pass_selectors = [
                (By.ID, "i0118"),
                (By.NAME, "passwd"),
                (By.NAME, "Password"),
                (By.CSS_SELECTOR, "input[type='password']"),
                (By.XPATH, "//input[contains(@aria-label, 'Password') or contains(@placeholder, 'Password')]") ,
            ]
            for by, sel in pass_selectors:
                if try_send_keys_if_present(driver, by, sel, password, timeout=8):
                    pwd_sent = True
                    break

            if pwd_sent:
                # Click sign in
                try_click_if_present(driver, By.ID, "idSIButton9", timeout=5)
                print("Password entered and submitted (attempt).")
            else:
                print("Password field not detected or auto-entry failed; please enter password manually.")

        print("If MFA is required, please complete the second factor on your device now.")
        print(f"Waiting up to {DEFAULT_LONG_TIMEOUT} seconds for redirect to the Power Apps app...")

        success = wait_for_url_contains(driver, "apps.powerapps.com", timeout=DEFAULT_LONG_TIMEOUT)
        if success:
            print("Detected redirect to Power Apps domain — login likely succeeded.")
            try:
                screenshot = os.path.join(os.getcwd(), "powerapps_logged_in.png")
                driver.save_screenshot(screenshot)
                print(f"Saved screenshot: {screenshot}")
            except Exception:
                pass
        else:
            print("Timed out waiting for login redirect. Check the opened browser to complete sign-in/MFA.")
            print("Current URL:", driver.current_url)

        input("Press Enter to close the browser and exit...")

    finally:
        try:
            driver.quit()
        except Exception:
            pass


if __name__ == "__main__":
    main()

