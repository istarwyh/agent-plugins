"""
Browser Utilities for Gemini Skill
Handles browser launching, stealth features, and common interactions.

Default mode: connect to an existing Chrome instance via CDP.
Fallback: launch a new persistent browser context.
"""

import json
import time
import random
import platform
import os
import shutil
from typing import Optional
from pathlib import Path

from patchright.sync_api import Playwright, Browser, BrowserContext, Page
from config import BROWSER_PROFILE_DIR, STATE_FILE, BROWSER_ARGS, USER_AGENT, CDP_ENDPOINT


def get_chrome_path() -> Optional[str]:
    """Get Chrome executable path for current platform"""
    system = platform.system()

    if system == "Darwin":
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if os.path.exists(chrome_path):
            return chrome_path
    elif system == "Windows":
        possible_paths = [
            os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
    elif system == "Linux":
        chrome_cmd = shutil.which("google-chrome") or shutil.which("chrome") or shutil.which("chromium")
        if chrome_cmd:
            return chrome_cmd
        possible_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/chrome",
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path

    return None


class BrowserFactory:
    """Factory for creating browser contexts.

    Default: connect to an existing Chrome via CDP (reuse instance).
    Fallback: launch a new persistent context.
    """

    # Track CDP browser reference for proper cleanup
    _cdp_browser: Optional[Browser] = None
    # Track whether current context is CDP-based
    _is_cdp: bool = False
    # Track pages we created (for cleanup in CDP mode)
    _our_pages: list = []

    @staticmethod
    def create_context(
        playwright: Playwright,
        headless: bool = True,
        use_cdp: bool = True,
        cdp_endpoint: str = CDP_ENDPOINT,
    ) -> BrowserContext:
        """Create a browser context.

        Tries CDP connection first (default). Falls back to launching
        a new persistent context if CDP is unavailable.

        Args:
            playwright: Playwright instance
            headless: Headless mode (only for fallback launch)
            use_cdp: Try CDP connection first (default True)
            cdp_endpoint: CDP endpoint URL

        Returns:
            BrowserContext ready to use
        """
        BrowserFactory._our_pages = []

        if use_cdp:
            try:
                ctx = BrowserFactory._connect_cdp(playwright, cdp_endpoint)
                BrowserFactory._is_cdp = True
                return ctx
            except Exception as e:
                print(f"  ⚠️ CDP connection failed ({e}), falling back to new browser instance")

        BrowserFactory._is_cdp = False
        return BrowserFactory._launch_persistent(playwright, headless)

    @staticmethod
    def is_cdp_mode() -> bool:
        """Check if current context is CDP-based (reusing existing Chrome)."""
        return BrowserFactory._is_cdp

    @staticmethod
    def new_page(context: BrowserContext) -> Page:
        """Create a new page and track it for cleanup.

        Use this instead of context.new_page() directly so that
        pages are properly closed during cleanup in CDP mode.
        """
        page = context.new_page()
        BrowserFactory._our_pages.append(page)
        return page

    @staticmethod
    def _connect_cdp(playwright: Playwright, cdp_endpoint: str) -> BrowserContext:
        """Connect to an existing Chrome instance via CDP."""
        print(f"  🔗 Connecting to Chrome via CDP: {cdp_endpoint}")
        browser = playwright.chromium.connect_over_cdp(cdp_endpoint)
        BrowserFactory._cdp_browser = browser

        # Use the default context (the user's existing browser session)
        contexts = browser.contexts
        if contexts:
            context = contexts[0]
            print(f"  ✅ Connected to existing Chrome (reusing session with {len(context.pages)} open pages)")
            return context

        # No existing context, create a new one
        context = browser.new_context()
        print("  ✅ Connected to existing Chrome (new context)")
        return context

    @staticmethod
    def _launch_persistent(playwright: Playwright, headless: bool) -> BrowserContext:
        """Launch a new persistent browser context (fallback)."""
        print("  🚀 Launching new browser instance...")
        chrome_path = get_chrome_path()

        launch_args = {
            "user_data_dir": str(BROWSER_PROFILE_DIR),
            "headless": headless,
            "no_viewport": True,
            "ignore_default_args": ["--enable-automation"],
            "user_agent": USER_AGENT,
            "args": BROWSER_ARGS
        }

        if chrome_path:
            launch_args["executable_path"] = chrome_path

        context = playwright.chromium.launch_persistent_context(**launch_args)

        # Cookie workaround for Playwright bug #36139
        BrowserFactory._inject_cookies(context)

        return context

    @staticmethod
    def launch_persistent_context(
        playwright: Playwright,
        headless: bool = True,
        user_data_dir: str = str(BROWSER_PROFILE_DIR)
    ) -> BrowserContext:
        """Legacy method - now delegates to create_context().

        Kept for backward compatibility with auth_manager.py setup flow
        which needs a dedicated browser instance (not CDP).
        """
        return BrowserFactory.create_context(playwright, headless=headless)

    @staticmethod
    def launch_persistent_context_no_cdp(
        playwright: Playwright,
        headless: bool = True,
    ) -> BrowserContext:
        """Launch a new persistent context, bypassing CDP.

        Used by auth setup which needs its own browser instance.
        """
        return BrowserFactory._launch_persistent(playwright, headless)

    @staticmethod
    def cleanup(context: BrowserContext):
        """Clean up browser resources properly."""
        # Close pages we created (important for CDP mode to avoid orphan tabs)
        for page in BrowserFactory._our_pages:
            try:
                if not page.is_closed():
                    page.close()
            except Exception:
                pass
        BrowserFactory._our_pages = []

        if BrowserFactory._cdp_browser:
            # For CDP: don't close the user's browser, just disconnect
            try:
                BrowserFactory._cdp_browser.close()
            except Exception:
                pass
            BrowserFactory._cdp_browser = None
            BrowserFactory._is_cdp = False
        else:
            # For launched browser: close context
            try:
                context.close()
            except Exception:
                pass

    @staticmethod
    def _inject_cookies(context: BrowserContext):
        """Inject cookies from state.json if available"""
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, 'r') as f:
                    state = json.load(f)
                    if 'cookies' in state and len(state['cookies']) > 0:
                        context.add_cookies(state['cookies'])
            except Exception as e:
                print(f"  ⚠️  Could not load state.json: {e}")


class StealthUtils:
    """Human-like interaction utilities"""

    @staticmethod
    def random_delay(min_ms: int = 100, max_ms: int = 500):
        time.sleep(random.uniform(min_ms / 1000, max_ms / 1000))

    @staticmethod
    def human_type(page: Page, selector: str, text: str, wpm_min: int = 320, wpm_max: int = 480):
        element = page.query_selector(selector)
        if not element:
            try:
                element = page.wait_for_selector(selector, timeout=2000)
            except:
                pass

        if not element:
            print(f"⚠️ Element not found for typing: {selector}")
            return

        element.click()

        for char in text:
            element.type(char, delay=random.uniform(25, 75))
            if random.random() < 0.05:
                time.sleep(random.uniform(0.15, 0.4))

    @staticmethod
    def realistic_click(page: Page, selector: str):
        element = page.query_selector(selector)
        if not element:
            return

        box = element.bounding_box()
        if box:
            x = box['x'] + box['width'] / 2
            y = box['y'] + box['height'] / 2
            page.mouse.move(x, y, steps=5)

        StealthUtils.random_delay(100, 300)
        element.click()
        StealthUtils.random_delay(100, 300)
