import os
import sys
import asyncio
from playwright.async_api import async_playwright

async def verify_page(page_name):
    print(f"Verifying {page_name}...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Load file using file:// protocol
        file_path = os.path.abspath(page_name)
        url = f"file://{file_path}"
        await page.goto(url)

        # 1. Check default state (English, LTR)
        html_element = page.locator("html")
        lang = await html_element.get_attribute("lang")
        direction = await html_element.get_attribute("dir")

        # We also need to check localStorage, but since we are using file:// protocol,
        # localStorage should work fine. Let's trigger the toggle and check values.
        print(f"Initial State: lang={lang}, dir={direction}")
        assert lang == "en" or lang is None or lang == "", f"Expected default lang 'en', got '{lang}'"

        # Locate language toggle button
        lang_toggle = page.locator("#lang-toggle")
        await lang_toggle.click()

        # 2. Check updated state (Arabic, RTL)
        lang = await html_element.get_attribute("lang")
        direction = await html_element.get_attribute("dir")
        print(f"After First Toggle: lang={lang}, dir={direction}")
        assert lang == "ar", f"Expected lang 'ar' after toggle, got '{lang}'"
        assert direction == "rtl", f"Expected dir 'rtl' after toggle, got '{direction}'"

        # Check a specific translated element to see if data-ar text is displayed
        seal_text = page.locator("[data-en='DR. MAGED ATEF EL-ESSI']")
        text_content = await seal_text.text_content()
        print(f"Seal Text: {text_content.strip()}")
        assert "ماجد" in text_content, f"Expected Arabic translation for seal text, got '{text_content}'"

        # Toggle back to English
        await lang_toggle.click()
        lang = await html_element.get_attribute("lang")
        direction = await html_element.get_attribute("dir")
        print(f"After Second Toggle: lang={lang}, dir={direction}")
        assert lang == "en", f"Expected lang 'en' after toggling back, got '{lang}'"

        # Reload page and check if state persists in localStorage
        # Toggle to Arabic again
        await lang_toggle.click()
        await page.reload()
        lang = await html_element.get_attribute("lang")
        direction = await html_element.get_attribute("dir")
        print(f"After Reload (expected persistence): lang={lang}, dir={direction}")
        assert lang == "ar", f"Expected persisted lang 'ar' after reload, got '{lang}'"

        await browser.close()
    print(f"Verification of {page_name} passed successfully!\n")

async def main():
    try:
        await verify_page("index.html")
        await verify_page("main.html")
        print("All verifications passed perfectly!")
    except Exception as e:
        print(f"Verification failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
