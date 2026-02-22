#!/usr/bin/env python3
"""
Gemini Question Interface
Ask questions to Gemini (gemini.google.com) using browser automation
Based on NotebookLM ask_question.py implementation
"""

import argparse
import sys
import time
from pathlib import Path

from patchright.sync_api import sync_playwright

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from auth_manager import AuthManager
from config import PAGE_LOAD_TIMEOUT
from browser_utils import BrowserFactory


# Input selectors (Gemini uses Quill editor)
GEMINI_INPUT_SELECTORS = [
    ".ql-editor.textarea",          # Quill editor (primary, 2025+)
    "rich-textarea",                 # Legacy rich-textarea element
    "div[contenteditable='true']",   # Generic contenteditable fallback
]

GEMINI_RESPONSE_SELECTORS = [
    ".model-response-text",
    "message-content",
    ".response-container .markdown",
    ".markdown",
]


def _wait_for_input(page, timeout=60):
    """Poll for input element with JS (more reliable than wait_for_selector for Gemini SPA)."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        for selector in GEMINI_INPUT_SELECTORS:
            try:
                el = page.query_selector(selector)
                if el:
                    box = el.bounding_box()
                    if box and box['width'] > 50:
                        return el, selector
            except:
                continue
        time.sleep(2)
    return None, None


def ask_gemini(question: str, headless: bool = True) -> str:
    """
    Ask a question to Gemini

    Args:
        question: Question to ask
        headless: Run browser in headless mode

    Returns:
        Answer text from Gemini
    """
    print(f"💬 Asking Gemini: {question}")

    playwright = None
    context = None

    try:
        # Start playwright
        playwright = sync_playwright().start()

        # Create browser context (CDP first, then fallback)
        context = BrowserFactory.create_context(
            playwright,
            headless=headless
        )

        # Auth check: skip if using CDP (user's Chrome is already logged in)
        if not BrowserFactory.is_cdp_mode():
            auth = AuthManager()
            if not auth.is_authenticated():
                print("⚠️ Not authenticated. Run: python scripts/run.py auth_manager.py setup")
                return None

        # Navigate to Gemini
        page = BrowserFactory.new_page(context)
        print("  🌐 Opening Gemini...")
        page.goto("https://gemini.google.com/app", wait_until="domcontentloaded", timeout=PAGE_LOAD_TIMEOUT)

        # Wait for input field (Gemini SPA needs time to initialize)
        print("  ⏳ Waiting for input field...")
        input_element, input_selector = _wait_for_input(page, timeout=60)

        if not input_element:
            print("  ❌ Could not find input field")
            if not headless:
                print("\n  ⏸️  Browser will stay open for 60 seconds for inspection...")
                time.sleep(60)
            return None

        print(f"  ✓ Found input: {input_selector}")

        # Type question
        print("  ⏳ Typing question...")
        try:
            input_element.click()
            time.sleep(0.5)

            if len(question) > 100:
                try:
                    input_element.fill(question)
                except Exception:
                    input_element.type(question, delay=10)
            else:
                page.keyboard.type(question, delay=20)

            time.sleep(1)
            print(f"  ✓ Typed: {question[:50]}..." if len(question) > 50 else f"  ✓ Typed: {question}")
        except Exception as e:
            print(f"  ❌ Typing failed: {e}")
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
            BrowserFactory.cleanup(context)

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
