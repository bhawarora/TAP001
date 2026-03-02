
from playwright.sync_api import Page, expect
import os

from Scripts.create_auth_state import page


def test_power_app_flow(page: Page):
    page.goto(
        "https://apps.powerapps.com/play/e/4d750f69-e41e-eef2-9f2d-0a1a538a9c00/a/024c5985-82c9-48bc-82a0-e73da686773e?tenantId=16532572-d567-4d67-8727-f12f7bb6aed3&source=AppSharedV3&hint=d033a915-af0b-4cf2-915b-c5d049485010&sourcetime=1747834684577",
        wait_until="domcontentloaded"
    )

    frame = page.frame_locator("iframe[name='fullscreen-app-host']")


    begin_btn = frame.get_by_role("button", name="Begin", exact=True)
    expect(begin_btn).to_be_visible(timeout=90000)
    begin_btn.click(force=True)

    page.wait_for_timeout(5000)


    agree_btn = frame.get_by_role("button", name="Agree", exact=True)
    expect(agree_btn).to_be_visible(timeout=90000)
    agree_btn.click(force=True)

    page.wait_for_timeout(1000)

    frame.get_by_role("button", name="Drag and drop your file here").click()
    frame.get_by_role("button", name="Drag and drop your file here").set_input_files("JPEG1.jpg")

    page.wait_for_timeout(5000)
