#!/usr/bin/env python
r"""
Test script to validate code.py before full execution.
Tests: imports, Selenium setup, URL reachability, and script structure.
"""
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Verify all required imports work."""
    print("[TEST] Checking imports...")
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from webdriver_manager.chrome import ChromeDriverManager
        import keyring
        print("  ✓ All imports successful")
        return True
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        return False


def test_url_reachability():
    """Test that the Power Apps URL is reachable."""
    print("[TEST] Checking URL reachability...")
    try:
        import requests
        url = "https://apps.powerapps.com"
        response = requests.head(url, timeout=5, allow_redirects=True)
        if response.status_code < 500:
            print(f"  ✓ URL reachable (status {response.status_code})")
            return True
        else:
            print(f"  ✗ URL returned error status {response.status_code}")
            return False
    except ImportError:
        print("  ⚠ requests not installed; skipping URL check (optional)")
        return True
    except Exception as e:
        print(f"  ✗ URL check failed: {e}")
        return False


def test_selenium_driver():
    """Test that ChromeDriver can be initialized (without opening browser)."""
    print("[TEST] Testing Selenium ChromeDriver setup...")
    try:
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        # Just verify the driver manager can download/locate ChromeDriver
        driver_path = ChromeDriverManager().install()
        if os.path.exists(driver_path):
            print(f"  ✓ ChromeDriver available at {driver_path}")
            return True
        else:
            print(f"  ✗ ChromeDriver path not found: {driver_path}")
            return False
    except Exception as e:
        print(f"  ✗ ChromeDriver setup failed: {e}")
        return False


def test_code_py_structure():
    """Test that code.py has required functions and structure."""
    print("[TEST] Validating code.py structure...")
    try:
        code_path = os.path.join(os.path.dirname(__file__), "code.py")
        with open(code_path, 'r') as f:
            content = f.read()
        
        required_items = [
            "POWERAPPS_URL",
            "def build_driver",
            "def try_send_keys_if_present",
            "def try_click_if_present",
            "def wait_for_url_contains",
            "def main",
            "if __name__"
        ]
        
        missing = []
        for item in required_items:
            if item not in content:
                missing.append(item)
        
        if not missing:
            print("  ✓ All required functions and structure found")
            return True
        else:
            print(f"  ✗ Missing items: {missing}")
            return False
    except Exception as e:
        print(f"  ✗ Structure check failed: {e}")
        return False


def test_keyring_setup():
    """Test that keyring can be accessed."""
    print("[TEST] Checking keyring/Windows Credential Manager...")
    try:
        import keyring
        backend = keyring.get_keyring()
        print(f"  ✓ Keyring backend: {backend.__class__.__name__}")
        return True
    except Exception as e:
        print(f"  ✗ Keyring check failed: {e}")
        return False


def main():
    print("=" * 60)
    print("POWER APPS LOGIN AUTOMATION - PRE-EXECUTION TEST SUITE")
    print("=" * 60)
    print()
    
    tests = [
        ("Imports", test_imports),
        ("URL Reachability", test_url_reachability),
        ("Selenium ChromeDriver", test_selenium_driver),
        ("code.py Structure", test_code_py_structure),
        ("Keyring Setup", test_keyring_setup),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"  ✗ Unexpected error: {e}")
            results[test_name] = False
        print()
    
    # Summary
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    print()
    print(f"Result: {passed}/{total} tests passed")
    print()
    
    if passed == total:
        print("✓ All pre-execution tests passed!")
        print()
        print("NEXT STEPS:")
        print("1. Run code.py locally on your machine:")
        print("   $env:POWERAPPS_USER = 'bhawna.arora@protivitiglobal.in'")
        print("   python C:/Users/bhawna.arora/PycharmProjects/PythonProject/PythonProject2/code.py")
        print()
        print("2. When prompted, enter your password (it will not be echoed)")
        print("3. Complete MFA approval on your device")
        print("4. The script will detect successful login and save a screenshot")
        return 0
    else:
        print("✗ Some tests failed. Please fix the issues above before running code.py")
        return 1


if __name__ == "__main__":
    sys.exit(main())

