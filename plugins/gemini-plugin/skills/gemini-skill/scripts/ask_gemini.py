#!/usr/bin/env python3
"""
Gemini Question Interface
Ask questions to Gemini (gemini.google.com) using browser automation
Based on NotebookLM ask_question.py implementation
"""

import argparse
import sys
import time
import re
from pathlib import Path

from patchright.sync_api import sync_playwright

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from auth_manager import AuthManager
from config import PAGE_LOAD_TIMEOUT
from browser_utils import BrowserFactory, StealthUtils


# Gemini selectors (to be discovered)
GEMINI_INPUT_SELECTORS = [
    "rich-textarea[placeholder*='输入']",  # Chinese
    "rich-textarea[placeholder*='Enter']",  # English
    "rich-textarea",  # Fallback
    ".ql-editor[contenteditable='true']",  # Rich text editor
    "div[contenteditable='true'][role='textbox']",  # Generic contenteditable
]

GEMINI_RESPONSE_SELECTORS = [
    ".model-response-text",
    ".response-container .markdown",
    "message-content",
    "[data-test-id*='conversation']",
    ".markdown",
    "[class*='response']",
    "[class*='message']",
    "div[class*='model']",
]


def ask_gemini(question: str, headless: bool = True) -> str:
    """
    Ask a question to Gemini

    Args:
        question: Question to ask
        headless: Run browser in headless mode

    Returns:
        Answer text from Gemini
    """
    auth = AuthManager()

    if not auth.is_authenticated():
        print("⚠️ Not authenticated. Run: python scripts/run.py auth_manager.py setup")
        return None

    print(f"💬 Asking Gemini: {question}")

    playwright = None
    context = None

    try:
        # Start playwright
        playwright = sync_playwright().start()

        # Launch persistent browser context using factory
        context = BrowserFactory.launch_persistent_context(
            playwright,
            headless=headless
        )

        # Navigate to Gemini
        page = context.new_page()
        print("  🌐 Opening Gemini...")
        page.goto("https://gemini.google.com/app", wait_until="domcontentloaded", timeout=PAGE_LOAD_TIMEOUT)

        # Wait for page to be ready
        print("  ⏳ Waiting for page to load...")
        time.sleep(3)  # Give page time to initialize

        # Debug: Print page content to understand structure
        if not headless:
            print("  🔍 Debug mode: Browser window is visible")
            print("  💡 Inspect the page to find correct selectors")

        # Try to find input field
        print("  ⏳ Looking for input field...")
        input_element = None

        for selector in GEMINI_INPUT_SELECTORS:
            try:
                print(f"    Trying selector: {selector}")
                input_element = page.wait_for_selector(
                    selector,
                    timeout=10000,
                    state="visible"
                )
                if input_element:
                    print(f"  ✓ Found input: {selector}")
                    break
            except Exception as e:
                print(f"    ✗ Failed: {e}")
                continue

        if not input_element:
            print("  ❌ Could not find input field")
            print("  💡 Let's try to inspect the page...")

            # Keep browser open for inspection if not headless
            if not headless:
                print("\n  ⏸️  Browser will stay open for 60 seconds for inspection...")
                print("  🔍 Please inspect the page and identify the input selector")
                time.sleep(60)

            return None

        # Type question
        print("  ⏳ Typing question...")

        # Store which selector worked
        working_selector = None
        for selector in GEMINI_INPUT_SELECTORS:
            try:
                test_elem = page.query_selector(selector)
                if test_elem and test_elem.is_visible():
                    working_selector = selector
                    break
            except:
                continue

        if not working_selector:
            print("  ❌ Could not find working selector")
            return None

        # Try different typing methods
        try:
            # Method 1: Click and type
            input_element.click()
            time.sleep(0.5)
            input_element.type(question, delay=50)  # Type with delay
        except Exception as e:
            print(f"  ⚠️ Typing method 1 failed: {e}")
            try:
                # Method 2: Fill
                input_element.fill(question)
            except Exception as e2:
                print(f"  ⚠️ Typing method 2 failed: {e2}")
                # Method 3: JavaScript with safe parameter passing
                try:
                    page.evaluate("""
                        (selector, text) => {
                            const elem = document.querySelector(selector);
                            if (elem) {
                                elem.value = text;
                                elem.dispatchEvent(new Event('input', { bubbles: true }));
                                elem.dispatchEvent(new Event('change', { bubbles: true }));
                            }
                        }
                    """, working_selector, question)
                except Exception as e3:
                    print(f"  ⚠️ All typing methods failed: {e3}")
                    return None

        # Submit
        print("  📤 Submitting...")
        page.keyboard.press("Enter")

        # Wait for response
        print("  ⏳ Waiting for answer...")

        answer = None
        stable_count = 0
        last_text = None
        deadline = time.time() + 120  # 2 minutes timeout
        found_selectors = set()

        while time.time() < deadline:
            # Try to find response
            for selector in GEMINI_RESPONSE_SELECTORS:
                try:
                    elements = page.query_selector_all(selector)
                    if elements and selector not in found_selectors:
                        found_selectors.add(selector)
                        print(f"    📌 Found elements with selector: {selector} ({len(elements)} elements)")

                    if elements:
                        # Get last (newest) response
                        latest = elements[-1]
                        text = latest.inner_text().strip()

                        if text and text != question and len(text) > 10:  # Avoid echoing the question
                            if text == last_text:
                                stable_count += 1
                                if stable_count >= 3:  # Stable for 3 polls
                                    answer = text
                                    print(f"    ✓ Response stable, got {len(text)} characters")
                                    break
                            else:
                                stable_count = 0
                                last_text = text
                                print(f"    📝 Got partial response ({len(text)} chars)...")
                except Exception as e:
                    if not headless:
                        print(f"    ✗ Selector '{selector}' failed: {e}")
                    continue

            if answer:
                break

            time.sleep(1)

        if not answer:
            print("  ❌ Timeout waiting for answer")

            # Keep browser open for debugging if not headless
            if not headless:
                print("\n  ⏸️  Browser will stay open for 30 seconds for debugging...")
                time.sleep(30)

            return None

        print("  ✅ Got answer!")
        return answer

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()

        # Keep browser open for debugging if not headless
        if not headless:
            print("\n  ⏸️  Browser will stay open for 30 seconds for debugging...")
            time.sleep(30)

        return None

    finally:
        # Always clean up
        if context:
            try:
                context.close()
            except:
                pass

        if playwright:
            try:
                playwright.stop()
            except:
                pass


def main():
    parser = argparse.ArgumentParser(description='Ask Gemini a question')

    parser.add_argument('--question', required=True, help='Question to ask')
    parser.add_argument('--show-browser', action='store_true', help='Show browser for debugging')

    args = parser.parse_args()

    # Ask the question
    answer = ask_gemini(
        question=args.question,
        headless=not args.show_browser
    )

    if answer:
        print("\n" + "=" * 60)
        print(f"Question: {args.question}")
        print("=" * 60)
        print()
        print(answer)
        print()
        print("=" * 60)
        return 0
    else:
        print("\n❌ Failed to get answer")
        return 1


if __name__ == "__main__":
    sys.exit(main())
