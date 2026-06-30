r"""
# Power Apps Login Automation with MFA Support

## Overview
This project automates login to Power Apps (Microsoft Power Platform) using Selenium WebDriver with support for Multi-Factor Authentication (MFA).

The script cannot bypass MFA for security reasons — you must complete the MFA approval on your device (Authenticator app push, SMS, or code entry).

## Files
- **code.py** — Main Selenium automation script (runs Chrome, logs into Power Apps)
- **test_code.py** — Pre-execution test suite (validates dependencies and setup)
- **README.md** — This file

## Test Results (Verified)
All 5/5 pre-execution tests passed:
✓ All imports successful (selenium, webdriver-manager, keyring)
✓ Power Apps URL reachable
✓ Selenium ChromeDriver available
✓ code.py structure validated
✓ Keyring/Windows Credential Manager accessible

## Quick Start (Choose One Option)

### Prerequisites (One-Time)
Ensure Python 3.8+ and Chrome are installed. Then run:
```powershell
python -m pip install --upgrade pip
pip install selenium webdriver-manager keyring
```

### Option 1: Interactive Password Entry (Recommended)
No passwords stored in history or env vars. Prompts you to type password securely.

```powershell
# Set username
$env:POWERAPPS_USER = 'bhawna.arora@protivitiglobal.in'

# Run the script (adjust path if different)
python C:\Users\bhawna.arora\PycharmProjects\PythonProject\PythonProject2\code.py

# When prompted: type your password (will not echo)
# Then: complete MFA on your device when Chrome opens
```

### Option 2: Environment Variables (Quick)
Sets credentials as env vars for this PowerShell session only.

```powershell
$env:POWERAPPS_USER = 'bhawna.arora@protivitiglobal.in'
$env:POWERAPPS_PASS = '<YOUR_PASSWORD>'
$env:POWERAPPS_WAIT_SECONDS = '600'   # optional: adjust MFA wait timeout

python C:\Users\bhawna.arora\PycharmProjects\PythonProject\PythonProject2\code.py

# Clean up env vars (optional)
Remove-Item Env:\POWERAPPS_USER
Remove-Item Env:\POWERAPPS_PASS
Remove-Item Env:\POWERAPPS_WAIT_SECONDS
```

### Option 3: Windows Credential Manager (Recommended for Repeated Use)
Securely stores credentials; script reads them without showing password on command line.

#### Step 1: Store credential (one-time, run locally)
Replace `<PASSWORD>` with your actual password:
```powershell
python -c "import keyring; keyring.set_password('powerapps_automation', 'bhawna.arora@protivitiglobal.in', '<PASSWORD>')"
```

#### Step 2: Run the script (credential auto-retrieved from Windows Credential Manager)
```powershell
$env:POWERAPPS_USER = 'bhawna.arora@protivitiglobal.in'
python C:\Users\bhawna.arora\PycharmProjects\PythonProject\PythonProject2\code.py
```

#### Optional: Verify credential was stored
```powershell
python - <<'PY'
import keyring
pw = keyring.get_password('powerapps_automation', 'bhawna.arora@protivitiglobal.in')
print('Password stored:', bool(pw))
PY
```

#### Optional: Delete stored credential
```powershell
python -c "import keyring; keyring.delete_password('powerapps_automation', 'bhawna.arora@protivitiglobal.in')"
```

## What Happens When You Run the Script

1. **Chrome opens** (visible) and navigates to the Power Apps URL
2. **Credentials auto-filled** (username + password)
3. **Next/Sign In button clicked**
4. **MFA prompt appears** — Complete the MFA approval:
   - Check your Authenticator app (push approval), or
   - Enter SMS code or recovery code
5. **Script waits** for redirect to Power Apps domain (timeout: 600 seconds by default)
6. **Success detected** → Screenshot saved as `powerapps_logged_in.png`
7. **Press Enter** in terminal to close browser and exit

## Troubleshooting

### "Chrome didn't open" or "WebDriver failed"
- Ensure Chrome is installed and up to date
- Check that `webdriver-manager` and `selenium` are installed in your Python environment
- Network/firewall may block webdriver-manager from downloading chromedriver; ensure internet access

### "Username/password fields not found" or autofill didn't work
- The script includes multiple fallback selectors for different Microsoft login page layouts
- If autofill still fails, sign in manually in the opened Chrome window
- The script will still detect successful login once you complete MFA and redirect occurs

### "Timed out waiting for login redirect"
- Ensure you completed and approved the MFA on your device
- Check browser for any error messages or account selection screen
- If needed, increase `POWERAPPS_WAIT_SECONDS` (e.g., 1200 for 20 minutes)

### "Keyring not working" or "credential not found"
- Verify keyring is installed: `pip install keyring`
- Verify the credential was stored: run the verification command above
- On Windows, check Windows Credential Manager (Control Panel → Credential Manager) for `powerapps_automation` service
- Fall back to Option 1 (interactive password entry) if keyring has issues

## Environment Variables

| Variable | Required | Default | Notes |
|----------|----------|---------|-------|
| `POWERAPPS_USER` | No | (prompted) | Email/UPN of the account to login with |
| `POWERAPPS_PASS` | No | (prompted or from keyring) | Password (if not set, script prompts) |
| `POWERAPPS_WAIT_SECONDS` | No | 600 | How long (seconds) to wait for MFA approval + redirect |

## Security Notes

- **Do not hardcode passwords** in scripts or configuration files (use keyring or env vars)
- **Avoid storing passwords in plain text** in shell history or scripts
- Use Windows Credential Manager (Option 3) or an enterprise secrets vault for production automation
- The script cannot and will not bypass MFA — you must approve it on your device
- MFA credentials are never logged or stored by this script

## For Production / Repeated Use

1. **Use keyring/Windows Credential Manager** to store credentials securely (Option 3)
2. **Consider a service principal** if you need completely non-interactive automation (requires Azure AD app registration; can call Power Platform APIs but cannot use the interactive web UI)
3. **Log all actions** for audit purposes (can be added to code.py)
4. **Monitor success/failure** and set up alerting if this is scheduled

## Support / Debugging

If you encounter issues:
1. Run `test_code.py` to verify all dependencies are installed correctly (5/5 tests should pass)
2. Check the terminal output for error messages
3. If a screenshot was saved (`powerapps_logged_in.png`), check what's displayed in the browser
4. Paste the full terminal output and describe the issue for troubleshooting

## Technical Details

- **Language:** Python 3.8+
- **WebDriver:** Selenium 4.45+
- **Browser:** Chrome (ChromeDriver auto-downloaded via webdriver-manager)
- **Password Storage:** Windows Credential Manager (via keyring library)
- **MFA Support:** Waits for user to approve MFA on device; detects success via URL redirect

## Example: Full Execution Flow

```powershell
# Terminal Session Example

PS C:\Users\bhawna.arora\PycharmProjects\PythonProject\PythonProject2> $env:POWERAPPS_USER = 'bhawna.arora@protivitiglobal.in'

PS C:\Users\bhawna.arora\PycharmProjects\PythonProject\PythonProject2> python code.py

Starting Power Apps launcher (Chrome + Selenium)
Enter password (leave blank to sign in manually): ••••••••••••
Username entered (or at least attempted).
Password entered and submitted (attempt).
If MFA is required, please complete the second factor on your device now.
Waiting up to 600 seconds for redirect to the Power Apps app...
Detected redirect to Power Apps domain — login likely succeeded.
Saved screenshot: C:\Users\bhawna.arora\PycharmProjects\PythonProject\PythonProject2\powerapps_logged_in.png
Press Enter to close the browser and exit...
[User presses Enter]
Browser closed. Script exited successfully.
```

## Notes

- The script is designed to be run **locally on your PC** (not on a remote server) so you can complete MFA
- Chrome must have network access to reach Microsoft login servers and Power Apps
- The `powerapps_logged_in.png` screenshot is useful for confirming successful login

## License & Disclaimer

This script is provided as-is for automation and testing purposes. Use at your own risk. Microsoft Power Apps and Entra ID (Azure AD) are subject to their own terms and policies.

---

**Created:** June 22, 2026
**Last Updated:** June 22, 2026
"""

