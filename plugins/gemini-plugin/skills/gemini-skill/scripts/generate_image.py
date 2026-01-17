#!/usr/bin/env python3
"""
Gemini Image Generation Script
Generate images using Gemini and download them
"""

import argparse
import sys
import time
import re
from pathlib import Path
import requests
import os

from patchright.sync_api import sync_playwright

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from auth_manager import AuthManager
from config import PAGE_LOAD_TIMEOUT
from browser_utils import BrowserFactory, StealthUtils


# Image generation selectors (to be discovered)
IMAGE_BUTTON_SELECTORS = [
    "button[aria-label*='Image']",
    "button[aria-label*='image']",
    "[data-test-id*='image']",
    "button:has-text('Image')",
]

# Generated image selectors (based on actual Gemini HTML structure)
IMAGE_RESULT_SELECTORS = [
    "generated-image img.image",  # Primary: generated-image tag with img.image class
    "single-image img[src*='googleusercontent.com']",  # Images from Google's CDN
    "generated-image img",  # Fallback: any img in generated-image
]


def generate_image(prompt: str, output_dir: str = ".", headless: bool = False, debug: bool = False) -> list:
    """
    Generate image using Gemini and download it

    Args:
        prompt: Image generation prompt
        output_dir: Directory to save images
        headless: Run browser in headless mode

    Returns:
        List of saved image paths
    """
    auth = AuthManager()

    if not auth.is_authenticated():
        print("⚠️ Not authenticated. Run: python scripts/run.py auth_manager.py setup")
        return None

    print(f"🎨 Generating image: {prompt}")

    playwright = None
    context = None

    try:
        # Start playwright
        playwright = sync_playwright().start()

        # Launch persistent browser context
        context = BrowserFactory.launch_persistent_context(
            playwright,
            headless=headless
        )

        # Navigate to Gemini - use a new URL to start fresh chat
        page = context.new_page()
        print("  🌐 Opening Gemini with new chat...")
        # Add a timestamp to force new chat session
        page.goto("https://gemini.google.com/app", wait_until="domcontentloaded", timeout=PAGE_LOAD_TIMEOUT)

        # Wait for page to load
        print("  ⏳ Waiting for page to load...")
        time.sleep(5)  # Give more time for full page load

        # Try to find and click Image button
        print("  🔍 Looking for Image generation mode...")
        image_button_found = False

        for selector in IMAGE_BUTTON_SELECTORS:
            try:
                print(f"    Trying selector: {selector}")
                button = page.wait_for_selector(selector, timeout=5000, state="visible")
                if button:
                    print(f"  ✓ Found Image button: {selector}")
                    button.click()
                    image_button_found = True
                    time.sleep(1)
                    break
            except Exception as e:
                print(f"    ✗ Not found: {selector}")
                continue

        if not image_button_found:
            print("  ⚠️ Image button not found, trying direct text input...")

        # Find input field
        print("  🔍 Looking for input field...")
        input_element = None

        input_selectors = [
            "rich-textarea",
            "textarea",
            "div[contenteditable='true']",
        ]

        for selector in input_selectors:
            try:
                input_element = page.wait_for_selector(selector, timeout=10000, state="visible")
                if input_element:
                    print(f"  ✓ Found input: {selector}")
                    break
            except:
                continue

        if not input_element:
            print("  ❌ Could not find input field")
            return None

        # Type prompt
        print("  ⏳ Typing prompt...")

        # Click to focus and type
        try:
            input_element.click()
            time.sleep(0.5)

            # For long prompts, find the actual textarea inside and use Playwright's fill
            if len(prompt) > 100:
                print("  📝 Using Playwright fill for long prompt...")
                # Try to find the actual textarea/contenteditable element
                actual_input = None

                # Try different selectors for the actual input
                for selector in ['rich-textarea textarea', 'rich-textarea [contenteditable="true"]', 'textarea', '[contenteditable="true"]']:
                    try:
                        actual_input = page.query_selector(selector)
                        if actual_input:
                            print(f"    ✓ Found actual input: {selector}")
                            break
                    except:
                        continue

                if actual_input:
                    # Use Playwright's native fill which handles complex inputs better
                    actual_input.fill(prompt)
                    print(f"  📊 Filled {len(prompt)} characters")

                    if debug:
                        print(f"  🐛 DEBUG: Pausing for 10 seconds to inspect...")
                        time.sleep(10)
                    else:
                        time.sleep(1)
                else:
                    print("  ⚠️ Could not find actual input element, trying fallback...")
                    input_element.type(prompt, delay=10)  # Very fast typing as fallback
            else:
                # Use type() with reduced delay for more natural input
                input_element.type(prompt, delay=20)  # 20ms between chars

            print(f"  ✓ Typed: {prompt[:50]}..." if len(prompt) > 50 else f"  ✓ Typed: {prompt}")
        except Exception as e:
            print(f"  ❌ Typing failed: {e}")
            return None

        # Submit
        print("  📤 Submitting...")
        page.keyboard.press("Enter")

        # Wait for image generation
        print("  ⏳ Waiting for image generation (this may take a while)...")

        images_found = []
        deadline = time.time() + 300  # 5 minutes timeout for image generation

        # Wait for generated-image element to appear
        print("  🔍 Waiting for generated-image element...")
        try:
            page.wait_for_selector("generated-image", timeout=300000)  # 5 minutes
            print("  ✓ Found generated-image element")
            time.sleep(2)  # Give it time to fully render
        except Exception as e:
            print(f"  ❌ No generated-image element found: {e}")
            if not headless:
                print("\n  ⏸️  Browser will stay open for 60 seconds for inspection...")
                time.sleep(60)
            return None

        # Wait for loader to disappear (image is loading)
        print("  ⏳ Waiting for images to load...")
        time.sleep(5)  # Wait for initial load

        # Now find the actual images
        stable_count = 0
        last_image_count = 0

        for attempt in range(30):  # 30 attempts, 1 second each
            for selector in IMAGE_RESULT_SELECTORS:
                try:
                    img_elements = page.query_selector_all(selector)
                    if img_elements:
                        current_count = len(img_elements)

                        # Check if all images are loaded (have src and not loading)
                        loaded_images = []
                        for img in img_elements:
                            src = img.get_attribute('src')
                            # Check if image has src and is from googleusercontent
                            if src and 'googleusercontent.com' in src:
                                loaded_images.append(img)

                        if loaded_images:
                            loaded_count = len(loaded_images)
                            if loaded_count == last_image_count and loaded_count > 0:
                                stable_count += 1
                                if stable_count >= 3:  # Stable for 3 seconds
                                    print(f"  ✓ Found {loaded_count} generated images")
                                    images_found = loaded_images
                                    break
                            else:
                                stable_count = 0
                                last_image_count = loaded_count
                                print(f"  📝 Found {loaded_count} images, verifying...")
                except Exception as e:
                    if not headless:
                        print(f"  ✗ Selector '{selector}' error: {e}")
                    continue

            if images_found:
                break

            time.sleep(1)

        if not images_found:
            print("  ❌ No images found after timeout")

            # Debug: Keep browser open
            if not headless:
                print("\n  ⏸️  Browser will stay open for 60 seconds for inspection...")
                time.sleep(60)

            return None

        # Download images using download button
        print(f"  💾 Downloading {len(images_found)} images using download button...")
        saved_paths = []

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Find all generated-image elements
        generated_images = page.query_selector_all("generated-image")

        for i, gen_img in enumerate(generated_images):
            try:
                print(f"    📥 Downloading image {i+1}...")

                # Find download button within this generated-image element
                download_button = gen_img.query_selector('button[data-test-id="download-generated-image-button"]')

                if not download_button:
                    print(f"    ⚠️ Image {i+1}: No download button found, using screenshot fallback")
                    # Fallback to screenshot
                    img_elem = gen_img.query_selector('img.image')
                    if img_elem:
                        screenshot_path = output_path / f"gemini_image_{i+1}_{int(time.time())}.png"
                        img_elem.screenshot(path=str(screenshot_path))
                        saved_paths.append(str(screenshot_path))
                        print(f"    ✓ Saved (screenshot): {screenshot_path}")
                    continue

                # Set up download event listener
                with page.expect_download() as download_info:
                    download_button.click()

                download = download_info.value

                # Wait for download to complete
                print(f"    ⏳ Waiting for download to complete...")

                # Get suggested filename
                suggested_filename = download.suggested_filename
                file_ext = Path(suggested_filename).suffix or '.png'

                # Save to output directory with custom name
                filename = output_path / f"gemini_image_{i+1}_{int(time.time())}{file_ext}"
                download.save_as(str(filename))

                saved_paths.append(str(filename))
                print(f"    ✓ Downloaded: {filename}")

            except Exception as e:
                print(f"    ❌ Failed to download image {i+1}: {e}")
                # Fallback to screenshot
                try:
                    img_elem = gen_img.query_selector('img.image')
                    if img_elem:
                        screenshot_path = output_path / f"gemini_image_{i+1}_{int(time.time())}.png"
                        img_elem.screenshot(path=str(screenshot_path))
                        saved_paths.append(str(screenshot_path))
                        print(f"    ✓ Saved (fallback screenshot): {screenshot_path}")
                except Exception as fallback_error:
                    print(f"    ❌ Fallback also failed: {fallback_error}")
                continue

        if saved_paths:
            print(f"\n  ✅ Successfully downloaded {len(saved_paths)} images!")
            return saved_paths
        else:
            print("  ❌ No images were downloaded")
            return None

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
    parser = argparse.ArgumentParser(description='Generate images using Gemini')

    parser.add_argument('--prompt', required=True, help='Image generation prompt')
    parser.add_argument('--output', default='.', help='Output directory for images')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode (hidden)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode with pauses')

    args = parser.parse_args()

    # Generate images (default: browser visible)
    saved_paths = generate_image(
        prompt=args.prompt,
        output_dir=args.output,
        headless=args.headless,  # 默认 False，只有加了 --headless 才隐藏
        debug=args.debug
    )

    if saved_paths:
        print("\n" + "=" * 60)
        print(f"Prompt: {args.prompt}")
        print("=" * 60)
        print("\nGenerated images:")
        for path in saved_paths:
            print(f"  - {path}")
        print("\n" + "=" * 60)
        return 0
    else:
        print("\n❌ Failed to generate images")
        return 1


if __name__ == "__main__":
    sys.exit(main())
