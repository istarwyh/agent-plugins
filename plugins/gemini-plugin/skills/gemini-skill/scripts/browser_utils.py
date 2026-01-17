"""
Browser Utilities for NotebookLM Skill
Handles browser launching, stealth features, and common interactions
"""

import json
import time
import random
import platform
import os
import shutil
from typing import Optional, List
from pathlib import Path

from patchright.sync_api import Playwright, BrowserContext, Page
from config import BROWSER_PROFILE_DIR, STATE_FILE, BROWSER_ARGS, USER_AGENT


def get_chrome_path() -> Optional[str]:
    """
    Get Chrome executable path for current platform

    Returns:
        Path to Chrome executable, or None to use default Chromium
    """
    system = platform.system()

    if system == "Darwin":  # macOS
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if os.path.exists(chrome_path):
            return chrome_path

    elif system == "Windows":
        # Try common Windows paths
        possible_paths = [
            os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path

    elif system == "Linux":
        # Try to find chrome in PATH
        chrome_cmd = shutil.which("google-chrome") or shutil.which("chrome") or shutil.which("chromium")
        if chrome_cmd:
            return chrome_cmd

        # Try common Linux paths
        possible_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/chrome",
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path

    # Return None to use Patchright's bundled Chromium
    return None


class BrowserFactory:
    """Factory for creating configured browser contexts"""

    @staticmethod
    def launch_persistent_context(
        playwright: Playwright,
        headless: bool = True,
        user_data_dir: str = str(BROWSER_PROFILE_DIR)
    ) -> BrowserContext:
        """
        Launch a persistent browser context with anti-detection features
        and cookie workaround.
        """
        # Get Chrome path for current platform
        chrome_path = get_chrome_path()

        # Build launch args
        launch_args = {
            "user_data_dir": user_data_dir,
            "headless": headless,
            "no_viewport": True,
            "ignore_default_args": ["--enable-automation"],
            "user_agent": USER_AGENT,
            "args": BROWSER_ARGS
        }

        # Only set executable_path if Chrome is found
        # Otherwise use Patchright's bundled Chromium
        if chrome_path:
            launch_args["executable_path"] = chrome_path

        # Launch persistent context
        context = playwright.chromium.launch_persistent_context(**launch_args)

        # Cookie Workaround for Playwright bug #36139
        # Session cookies (expires=-1) don't persist in user_data_dir automatically
        BrowserFactory._inject_cookies(context)

        return context

    @staticmethod
    def _inject_cookies(context: BrowserContext):
        """Inject cookies from state.json if available"""
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, 'r') as f:
                    state = json.load(f)
                    if 'cookies' in state and len(state['cookies']) > 0:
                        context.add_cookies(state['cookies'])
                        # print(f"  🔧 Injected {len(state['cookies'])} cookies from state.json")
            except Exception as e:
                print(f"  ⚠️  Could not load state.json: {e}")


class StealthUtils:
    """Human-like interaction utilities"""

    @staticmethod
    def random_delay(min_ms: int = 100, max_ms: int = 500):
        """Add random delay"""
        time.sleep(random.uniform(min_ms / 1000, max_ms / 1000))

    @staticmethod
    def human_type(page: Page, selector: str, text: str, wpm_min: int = 320, wpm_max: int = 480):
        """Type with human-like speed"""
        element = page.query_selector(selector)
        if not element:
            # Try waiting if not immediately found
            try:
                element = page.wait_for_selector(selector, timeout=2000)
            except:
                pass
        
        if not element:
            print(f"⚠️ Element not found for typing: {selector}")
            return

        # Click to focus
        element.click()
        
        # Type
        for char in text:
            element.type(char, delay=random.uniform(25, 75))
            if random.random() < 0.05:
                time.sleep(random.uniform(0.15, 0.4))

    @staticmethod
    def realistic_click(page: Page, selector: str):
        """Click with realistic movement"""
        element = page.query_selector(selector)
        if not element:
            return

        # Optional: Move mouse to element (simplified)
        box = element.bounding_box()
        if box:
            x = box['x'] + box['width'] / 2
            y = box['y'] + box['height'] / 2
            page.mouse.move(x, y, steps=5)

        StealthUtils.random_delay(100, 300)
        element.click()
        StealthUtils.random_delay(100, 300)
