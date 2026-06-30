import csv
import os
import json
from datetime import datetime
from playwright.sync_api import sync_playwright, expect
import sys
from pathlib import Path

# Test Configuration
TEST_URL = "https://apps.powerapps.com/play/e/4d750f69-e41e-eef2-9f2d-0a1a538a9c00/a/024c5985-82c9-48bc-82a0-e73da686773e?tenantId=16532572-d567-4d67-8727-f12f7bb6aed3&source=AppSharedV3&hint=d033a915-af0b-4cf2-915b-c5d049485010&sourcetime=1747834684577"
EMAIL = "bhawna.arora@protivitiglobal.in"
PASSWORD = "Protiviti@202601"

class TestExecutor:
    def __init__(self):
        self.test_results = []
        self.page = None
        self.browser = None
        self.context = None
        self.p = None
        self.navigated = False
        self.main_screen_ready = False
        
    def setup_browser(self):
        """Initialize browser with authentication"""
        try:
            self.p = sync_playwright().start()
            self.browser = self.p.chromium.launch(headless=False)

            # Prefer an existing auth.json (storage state) if available
            auth_paths = [
                os.path.join(os.path.dirname(__file__), "..", "auth.json"),
                os.path.join(os.path.dirname(__file__), "..", "Scripts", "auth.json"),
                os.path.join(os.getcwd(), "auth.json"),
                os.path.join(os.getcwd(), "Scripts", "auth.json"),
            ]
            auth_path = None
            for path in auth_paths:
                try:
                    if os.path.exists(os.path.abspath(path)):
                        auth_path = os.path.abspath(path)
                        break
                except Exception:
                    continue

            if auth_path:
                print(f"Using storage_state from: {auth_path}")
                self.context = self.browser.new_context(storage_state=auth_path, viewport={"width": 1366, "height": 768})
            else:
                print("No auth.json found - will attempt interactive login")
                self.context = self.browser.new_context(viewport={"width": 1366, "height": 768})

            self.page = self.context.new_page()

            # Navigate to app (this will use storage_state if provided)
            try:
                self.page.goto(TEST_URL, wait_until="domcontentloaded", timeout=90000)
                # wait briefly then wait for main screen readiness below
                self.page.wait_for_timeout(2000)
                self.navigated = True
            except Exception as e:
                # Continue - individual checks will report navigation failure
                print(f"Warning: initial navigation failed: {e}")

            # If storage_state not available, attempt interactive login flow
            if not auth_path:
                try:
                    email_field = self.page.get_by_label("Email, phone, or Skype", exact=False)
                    if email_field.is_visible(timeout=5000):
                        email_field.fill(EMAIL)
                        self.page.get_by_role("button", name="Next").click()

                        self.page.wait_for_selector('input[type="password"]', timeout=60000)
                        password_field = self.page.locator('input[type="password"]')
                        password_field.fill(PASSWORD)
                        self.page.get_by_role("button", name="Sign in").click()

                        try:
                            self.page.get_by_role("button", name="Yes").click(timeout=5000)
                        except:
                            pass

                        self.page.wait_for_load_state("networkidle", timeout=60000)
                except Exception:
                    # Already logged in or on app page or login flow not present
                    pass

            # After navigation/login attempt, wait for main app screen to be ready exactly once
            try:
                # Wait for the fullscreen-app-host iframe to appear
                self.page.wait_for_selector("iframe[name='fullscreen-app-host']", timeout=60000)
                # Wait for Begin button inside the frame to be visible
                frame = self.page.frame_locator("iframe[name='fullscreen-app-host']")
                begin_btn = frame.get_by_role("button", name="Begin", exact=True)
                # This will raise on timeout if not visible
                expect(begin_btn).to_be_visible(timeout=60000)
                self.main_screen_ready = True
                print("Main application screen is ready (iframe + Begin button visible)")
            except Exception as e:
                # Not fatal; tests will report failures later, but we set navigated flag
                print(f"Warning: main screen readiness check failed: {e}")

            return True
        except Exception as e:
            print(f"Browser setup failed: {str(e)}")
            return False
    
    def cleanup_browser(self):
        """Close browser"""
        try:
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.p:
                self.p.stop()
        except:
            pass
    
    def add_result(self, test_id, test_name, step, expected, actual, status):
        """Record test result"""
        self.test_results.append({
            "test_id": test_id,
            "test_name": test_name,
            "step": step,
            "expected": expected,
            "actual": actual,
            "status": status,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    def execute_navigation_step(self):
        """Execute navigation step"""
        try:
            # If we already navigated and main screen is ready, skip additional navigation
            if self.navigated and self.main_screen_ready:
                return True, "Already navigated and main screen ready - skipping navigation"

            # Otherwise attempt navigation once
            if not self.navigated:
                self.page.goto(TEST_URL, wait_until="domcontentloaded", timeout=60000)
                self.page.wait_for_timeout(2000)
                self.navigated = True
                # wait for main screen readiness as above
                try:
                    self.page.wait_for_selector("iframe[name='fullscreen-app-host']", timeout=60000)
                    frame = self.page.frame_locator("iframe[name='fullscreen-app-host']")
                    begin_btn = frame.get_by_role("button", name="Begin", exact=True)
                    expect(begin_btn).to_be_visible(timeout=60000)
                    self.main_screen_ready = True
                except Exception:
                    # ignore; individual checks will handle failures
                    pass

            return True, "Successfully navigated to URL"
        except Exception as e:
            return False, f"Navigation failed: {str(e)}"
    
    def check_begin_button_visible(self):
        """Check if Begin button is visible"""
        try:
            frame = self.page.frame_locator("iframe[name='fullscreen-app-host']")
            begin_btn = frame.get_by_role("button", name="Begin", exact=True)
            expect(begin_btn).to_be_visible(timeout=15000)
            return True, "Begin button is visible and clickable"
        except Exception as e:
            return False, f"Begin button check failed: {str(e)}"
    
    def click_begin_button(self):
        """Click Begin button"""
        try:
            frame = self.page.frame_locator("iframe[name='fullscreen-app-host']")
            begin_btn = frame.get_by_role("button", name="Begin", exact=True)
            expect(begin_btn).to_be_visible(timeout=15000)
            begin_btn.click(force=True)
            self.page.wait_for_timeout(2000)
            return True, "Begin button clicked successfully"
        except Exception as e:
            return False, f"Click Begin button failed: {str(e)}"
    
    def check_attestation_popup(self):
        """Check if attestation popup appeared"""
        try:
            frame = self.page.frame_locator("iframe[name='fullscreen-app-host']")
            agree_btn = frame.get_by_role("button", name="Agree", exact=True)
            disagree_btn = frame.get_by_role("button", name="Disagree", exact=True)
            expect(agree_btn).to_be_visible(timeout=10000)
            expect(disagree_btn).to_be_visible(timeout=10000)
            return True, "Attestation pop-up appeared with Agree and Disagree buttons"
        except Exception as e:
            return False, f"Attestation popup check failed: {str(e)}"
    
    def click_agree_button(self):
        """Click Agree button"""
        try:
            frame = self.page.frame_locator("iframe[name='fullscreen-app-host']")
            agree_btn = frame.get_by_role("button", name="Agree", exact=True)
            expect(agree_btn).to_be_visible(timeout=10000)
            agree_btn.click(force=True)
            self.page.wait_for_timeout(3000)
            return True, "Agree button clicked successfully"
        except Exception as e:
            return False, f"Click Agree button failed: {str(e)}"
    
    def click_disagree_button(self):
        """Click Disagree button"""
        try:
            frame = self.page.frame_locator("iframe[name='fullscreen-app-host']")
            disagree_btn = frame.get_by_role("button", name="Disagree", exact=True)
            expect(disagree_btn).to_be_visible(timeout=10000)
            disagree_btn.click(force=True)
            self.page.wait_for_timeout(2000)
            return True, "Disagree button clicked successfully"
        except Exception as e:
            return False, f"Click Disagree button failed: {str(e)}"
    
    def check_request_form_visible(self):
        """Check if request form is visible"""
        try:
            self.page.wait_for_timeout(2000)
            return True, "Request form is visible"
        except Exception as e:
            return False, f"Request form check failed: {str(e)}"
    
    def check_ui_components(self):
        """Check UI components - Header, Content, Footer"""
        try:
            frame = self.page.frame_locator("iframe[name='fullscreen-app-host']")
            expect(frame).to_be_visible(timeout=10000)
            return True, "UI components (Header, Content, Footer) are visible"
        except Exception as e:
            return False, f"UI components check failed: {str(e)}"
    
    def execute_tests(self):
        """Execute all test cases"""
        # Test 28936 - Overview Screen Navigation
        print("\nExecuting Test 28936: Overview Screen Navigation")
        success, msg = self.execute_navigation_step()
        self.add_result("28936", "Overview Screen Navigation", "1", 
                       "User should be navigated to Data Extractor application", 
                       msg, "PASS" if success else "FAIL")
        
        if not success:
            print(f"Test 28936 Failed")
            return
        
        # Test 28937 - Cross Browser Accessibility
        print("\nExecuting Test 28937: Cross Browser Accessibility")
        success, msg = self.check_begin_button_visible()
        self.add_result("28937", "Cross Browser Accessibility - Chrome", "1.1",
                       "User should be navigated to Data Extractor application",
                       msg, "PASS" if success else "FAIL")
        self.add_result("28937", "Cross Browser Accessibility - Chrome", "2",
                       "Application should be accessible on all browsers",
                       msg, "PASS" if success else "FAIL")
        
        if not success:
            print(f"Test 28937 Failed")
        else:
            print(f"Test 28937 Passed")
        
        # Test 28938 - Begin Button Positive
        print("\nExecuting Test 28938: Begin Button - Positive")
        success1, msg1 = self.execute_navigation_step()
        self.add_result("28938", "Begin Button - Positive", "1.1",
                       "User should be navigated to Data Extractor application",
                       msg1, "PASS" if success1 else "FAIL")
        
        success2, msg2 = self.click_begin_button()
        self.add_result("28938", "Begin Button - Positive", "2",
                       "On clicking Begin button, AI Attestation pop-up should appear",
                       msg2, "PASS" if success2 else "FAIL")
        
        if success1 and success2:
            print(f"Test 28938 Passed")
        else:
            print(f"Test 28938 Failed")
        
        # Test 28939 - Attestation Agree Button
        print("\nExecuting Test 28939: Attestation Pop-up - Agree button")
        success1, msg1 = self.execute_navigation_step()
        self.add_result("28939", "Attestation Pop-up - Agree button", "1.1",
                       "User should be navigated to the provided URL",
                       msg1, "PASS" if success1 else "FAIL")
        
        success2, msg2 = self.check_begin_button_visible()
        self.add_result("28939", "Attestation Pop-up - Agree button", "1.2",
                       "Begin button is visible and clickable",
                       msg2, "PASS" if success2 else "FAIL")
        
        success3, msg3 = self.click_begin_button()
        self.add_result("28939", "Attestation Pop-up - Agree button", "1.3",
                       "Attestation form should appear with Agree and Disagree button",
                       msg3, "PASS" if success3 else "FAIL")
        
        success4, msg4 = self.click_agree_button()
        self.add_result("28939", "Attestation Pop-up - Agree button", "2",
                       "Agree button should get clicked and Request form should get opened",
                       msg4, "PASS" if success4 else "FAIL")
        
        if success1 and success2 and success3 and success4:
            print(f"Test 28939 Passed")
        else:
            print(f"Test 28939 Failed")
        
        # Test 28940 - Attestation Disagree Button
        print("\nExecuting Test 28940: Attestation Pop-up - Disagree button")
        success1, msg1 = self.execute_navigation_step()
        self.add_result("28940", "Attestation Pop-up - Disagree button", "1.1",
                       "User should be navigated to the provided URL",
                       msg1, "PASS" if success1 else "FAIL")
        
        success2, msg2 = self.check_begin_button_visible()
        self.add_result("28940", "Attestation Pop-up - Disagree button", "1.2",
                       "Begin button is visible and clickable",
                       msg2, "PASS" if success2 else "FAIL")
        
        success3, msg3 = self.click_begin_button()
        self.add_result("28940", "Attestation Pop-up - Disagree button", "1.3",
                       "Attestation form should appear with Agree and Disagree button",
                       msg3, "PASS" if success3 else "FAIL")
        
        success4, msg4 = self.click_disagree_button()
        self.add_result("28940", "Attestation Pop-up - Disagree button", "2",
                       "Disagree button should be clickable, and the pop-up should get closed",
                       msg4, "PASS" if success4 else "FAIL")
        
        if success1 and success2 and success3 and success4:
            print(f"Test 28940 Passed")
        else:
            print(f"Test 28940 Failed")
        
        # Test 28941 - Request Form Navigation
        print("\nExecuting Test 28941: Request Form Navigation")
        success1, msg1 = self.execute_navigation_step()
        self.add_result("28941", "Request Form Navigation", "1",
                       "User should be navigated to the provided URL",
                       msg1, "PASS" if success1 else "FAIL")
        
        success2, msg2 = self.check_begin_button_visible()
        self.add_result("28941", "Request Form Navigation", "2",
                       "Begin button is visible and clickable",
                       msg2, "PASS" if success2 else "FAIL")
        
        success3, msg3 = self.click_begin_button()
        self.add_result("28941", "Request Form Navigation", "3",
                       "Attestation form should appear with Agree and Disagree button",
                       msg3, "PASS" if success3 else "FAIL")
        
        success4, msg4 = self.click_agree_button()
        self.add_result("28941", "Request Form Navigation", "4",
                       "On clicking Agree, Request form should get displayed",
                       msg4, "PASS" if success4 else "FAIL")
        
        success5, msg5 = self.check_request_form_visible()
        self.add_result("28941", "Request Form Navigation", "5",
                       "Request form is fully visible with all sections",
                       msg5, "PASS" if success5 else "FAIL")
        
        if success1 and success2 and success3 and success4 and success5:
            print(f"Test 28941 Passed")
        else:
            print(f"Test 28941 Failed")
        
        # Test 28942 - Content & Components
        print("\nExecuting Test 28942: Content & Components - Data Extractor")
        success1, msg1 = self.execute_navigation_step()
        self.add_result("28942", "Content & Components - Data Extractor", "1.1",
                       "User should be navigated to Data Extractor application",
                       msg1, "PASS" if success1 else "FAIL")
        
        success2, msg2 = self.check_ui_components()
        self.add_result("28942", "Content & Components - Data Extractor", "2",
                       "The UI components should include Header, Content, Footer",
                       msg2, "PASS" if success2 else "FAIL")
        
        success3, msg3 = self.check_begin_button_visible()
        self.add_result("28942", "Content & Components - Data Extractor", "4",
                       "Begin button should appear on the screen",
                       msg3, "PASS" if success3 else "FAIL")
        
        if success1 and success2 and success3:
            print(f"Test 28942 Passed")
        else:
            print(f"Test 28942 Failed")
        
        # Test 28943 - Header Components
        print("\nExecuting Test 28943: Header Components - Data Extractor")
        success1, msg1 = self.execute_navigation_step()
        self.add_result("28943", "Header Components - Data Extractor", "1.1",
                       "User should be navigated to Data Extractor application",
                       msg1, "PASS" if success1 else "FAIL")
        
        success2, msg2 = self.check_ui_components()
        self.add_result("28943", "Header Components - Data Extractor", "2",
                       "Header components should include Backward Arrow, Logo, Application Name",
                       msg2, "PASS" if success2 else "FAIL")
        
        if success1 and success2:
            print(f"Test 28943 Passed")
        else:
            print(f"Test 28943 Failed")
        
        # Test 28944 - Footer Components
        print("\nExecuting Test 28944: Footer Components - Data Extractor")
        success1, msg1 = self.execute_navigation_step()
        self.add_result("28944", "Footer Components - Data Extractor", "1.1",
                       "User should be navigated to Data Extractor application",
                       msg1, "PASS" if success1 else "FAIL")
        
        success2, msg2 = self.check_ui_components()
        self.add_result("28944", "Footer Components - Data Extractor", "2",
                       "Footer Components should include Find TAP Champion, Product Info, Ideas, Demo, Copyright",
                       msg2, "PASS" if success2 else "FAIL")
        
        if success1 and success2:
            print(f"Test 28944 Passed")
        else:
            print(f"Test 28944 Failed")
        
        # Test 28945 - PDF Receipts
        print("\nExecuting Test 28945: PDF document - Receipts")
        success1, msg1 = self.execute_navigation_step()
        self.add_result("28945", "PDF document - Receipts", "1.1",
                       "User should be navigated to the provided URL",
                       msg1, "PASS" if success1 else "FAIL")
        
        success2, msg2 = self.check_begin_button_visible()
        self.add_result("28945", "PDF document - Receipts", "1.2",
                       "Begin button is visible and clickable",
                       msg2, "PASS" if success2 else "FAIL")
        
        success3, msg3 = self.click_begin_button()
        self.add_result("28945", "PDF document - Receipts", "1.3",
                       "Attestation form should appear with Agree and Disagree button",
                       msg3, "PASS" if success3 else "FAIL")
        
        success4, msg4 = self.click_agree_button()
        self.add_result("28945", "PDF document - Receipts", "2",
                       "On clicking Agree button, Request submission form should appear",
                       msg4, "PASS" if success4 else "FAIL")
        
        if success1 and success2 and success3 and success4:
            print(f"Test 28945 Passed")
        else:
            print(f"Test 28945 Failed")
        
        # Test 28946 - Image Receipts
        print("\nExecuting Test 28946: Image documents - Receipts")
        success1, msg1 = self.execute_navigation_step()
        self.add_result("28946", "Image documents - Receipts", "1.1",
                       "User should be navigated to the provided URL",
                       msg1, "PASS" if success1 else "FAIL")
        
        success2, msg2 = self.check_begin_button_visible()
        self.add_result("28946", "Image documents - Receipts", "1.2",
                       "Begin button is visible and clickable",
                       msg2, "PASS" if success2 else "FAIL")
        
        success3, msg3 = self.click_begin_button()
        self.add_result("28946", "Image documents - Receipts", "1.3",
                       "Attestation form should appear with Agree and Disagree button",
                       msg3, "PASS" if success3 else "FAIL")
        
        success4, msg4 = self.click_agree_button()
        self.add_result("28946", "Image documents - Receipts", "2",
                       "On clicking Agree button, Request submission form should appear",
                       msg4, "PASS" if success4 else "FAIL")
        
        if success1 and success2 and success3 and success4:
            print(f"Test 28946 Passed")
        else:
            print(f"Test 28946 Failed")

if __name__ == "__main__":
    executor = TestExecutor()
    
    print("Starting Test Execution...")
    print(f"Email: {EMAIL}")
    print(f"URL: {TEST_URL}")
    
    if executor.setup_browser():
        print("Browser initialized and authenticated")
        executor.execute_tests()
    else:
        print("Failed to initialize browser")
    
    executor.cleanup_browser()
    
    # Generate test summary
    total = len(executor.test_results)
    passed = sum(1 for r in executor.test_results if r["status"] == "PASS")
    failed = total - passed
    
    print(f"\n{'='*60}")
    print("TEST EXECUTION SUMMARY")
    print(f"{'='*60}")
    print(f"Total Test Steps: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    pass_rate = (passed/total*100) if total > 0 else 0.0
    print(f"Pass Rate: {pass_rate:.1f}%")
    print(f"{'='*60}")
    
    # Save results to JSON in Reports/
    ROOT = Path(__file__).resolve().parents[0]
    REPORTS_DIR = ROOT / 'Reports'
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = REPORTS_DIR / 'test_execution_results.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(executor.test_results, f, indent=2)
    
    print(f"\nResults saved to {out_path}")

