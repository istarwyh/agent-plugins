#!/usr/bin/env python3
"""
Gemini Image Generation Script
Generate images using Gemini and download them
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
from browser_utils import BrowserFactory, StealthUtils


# Input selectors (Gemini uses Quill editor)
INPUT_SELECTORS = [
    ".ql-editor.textarea",          # Quill editor (primary, 2025+)
    "rich-textarea",                 # Legacy rich-textarea element
    "div[contenteditable='true']",   # Generic contenteditable fallback
]

# Image result selectors (broadened for Gemini UI updates)
IMAGE_RESULT_SELECTORS = [
    "generated-image img.image",                         # Legacy generated-image tag
    "generated-image img",                               # Legacy fallback
    "img[src*='googleusercontent.com']",                 # Any Google CDN image
    "single-image img[src*='googleusercontent.com']",    # Single image wrapper
]

# Response text selectors (for detecting text-only responses)
RESPONSE_TEXT_SELECTORS = [
    ".model-response-text",
    "message-content",
    ".response-container .markdown",
    ".markdown",
]


def _wait_for_input(page, timeout=60):
    """Poll for input element with JS (more reliable than wait_for_selector for Gemini SPA)."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        for selector in INPUT_SELECTORS:
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


def _find_generated_images(page):
    """Find generated images on the page, excluding icons/SVGs/small images/avatars."""
    import re
    for selector in IMAGE_RESULT_SELECTORS:
        try:
            elements = page.query_selector_all(selector)
            loaded = []
            for img in elements:
                src = img.get_attribute('src') or ''
                cls = img.get_attribute('class') or ''
                # Skip SVGs, icons
                if src.endswith('.svg') or 'icon' in cls.lower():
                    continue
                if 'googleusercontent.com' not in src:
                    continue
                # Skip small images (avatars, profile pics): =s32, =s48, =s64 etc.
                size_match = re.search(r'=s(\d+)', src)
                if size_match and int(size_match.group(1)) < 200:
                    continue
                # Skip avatar-style URLs (contain /ogw/ path)
                if '/ogw/' in src or '/a/' in src.split('googleusercontent.com')[-1][:10]:
                    continue
                # Check rendered size via bounding box
                try:
                    box = img.bounding_box()
                    if box and (box['width'] < 100 or box['height'] < 100):
                        continue
                except:
                    pass
                loaded.append(img)
            if loaded:
                return loaded, selector
        except:
            continue
    return [], None


def generate_image(prompt: str, output_dir: str = ".", headless: bool = False, debug: bool = False) -> list:
    """
    Generate image using Gemini and download it

    Args:
        prompt: Image generation prompt
        output_dir: Directory to save images
        headless: Run browser in headless mode
        debug: Enable debug mode

    Returns:
        List of saved image paths
    """
    print(f"🎨 Generating image: {prompt}")

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
        print("  🌐 Opening Gemini with new chat...")
        page.goto("https://gemini.google.com/app", wait_until="domcontentloaded", timeout=PAGE_LOAD_TIMEOUT)

        # Wait for page to initialize, then click "Create image" tool button
        print("  🔍 Looking for 'Create image' button...")
        create_image_clicked = False

        # Poll for the button (Gemini SPA tool buttons may take time to render)
        btn_deadline = time.time() + 30
        while time.time() < btn_deadline:
            for text_match in ["Create image", "创建图片"]:
                try:
                    loc = page.locator("button").filter(has_text=text_match)
                    if loc.count() > 0 and loc.first.is_visible():
                        btn_text = loc.first.inner_text().strip()[:60]
                        print(f"  ✓ Found button: {btn_text}")
                        loc.first.click()
                        create_image_clicked = True
                        time.sleep(2)  # Wait for mode switch
                        break
                except Exception:
                    continue
            if create_image_clicked:
                break
            time.sleep(2)

        if not create_image_clicked:
            print("  ⚠️ 'Create image' button not found, will try direct prompt")

        # Wait for input field (Gemini SPA needs time to initialize)
        print("  ⏳ Waiting for input field...")
        input_element, input_selector = _wait_for_input(page, timeout=60)

        if not input_element:
            print("  ❌ Could not find input field")
            return None

        print(f"  ✓ Found input: {input_selector}")

        # Type prompt
        print("  ⏳ Typing prompt...")
        try:
            input_element.click()
            time.sleep(0.5)

            if len(prompt) > 100:
                # For long prompts, try fill() first, fallback to type()
                try:
                    input_element.fill(prompt)
                    print(f"  📊 Filled {len(prompt)} characters")
                except Exception:
                    input_element.type(prompt, delay=10)
            else:
                page.keyboard.type(prompt, delay=20)

            if debug:
                print(f"  🐛 DEBUG: Pausing for 10 seconds to inspect...")
                time.sleep(10)
            else:
                time.sleep(1)

            print(f"  ✓ Typed: {prompt[:50]}..." if len(prompt) > 50 else f"  ✓ Typed: {prompt}")
        except Exception as e:
            print(f"  ❌ Typing failed: {e}")
            return None

        # Submit using Enter key (most reliable for Gemini's Quill editor)
        print("  📤 Submitting...")
        page.keyboard.press("Enter")

        # Small pause for navigation
        StealthUtils.random_delay(1000, 2000)

        # Wait for image generation
        print("  ⏳ Waiting for image generation (this may take a while)...")

        images_found = []
        stable_count = 0
        last_image_count = 0
        last_log_time = 0
        deadline = time.time() + 300  # 5 minutes timeout

        while time.time() < deadline:
            now = time.time()

            # Check for generated images
            found_images, found_selector = _find_generated_images(page)
            if found_images:
                loaded_count = len(found_images)
                if loaded_count == last_image_count and loaded_count > 0:
                    stable_count += 1
                    if stable_count >= 3:  # Stable for 3 polls
                        print(f"  ✓ Found {loaded_count} generated images (via {found_selector})")
                        images_found = found_images
                        break
                else:
                    stable_count = 0
                    last_image_count = loaded_count
                    print(f"  📝 Found {loaded_count} images, verifying...")

            # Periodic diagnostics
            if now - last_log_time > 15:
                last_log_time = now
                elapsed = int(now - (deadline - 300))
                # Check for text response (Gemini might refuse image generation)
                for sel in RESPONSE_TEXT_SELECTORS:
                    try:
                        resp_els = page.query_selector_all(sel)
                        if resp_els:
                            text = resp_els[-1].inner_text().strip()[:200]
                            if text and len(text) > 20:
                                print(f"  📝 [{elapsed}s] Text response: {text}")
                                break
                    except:
                        continue

            time.sleep(2)

        if not images_found:
            print("  ❌ No images found after timeout")
            # Show final response text for debugging
            for sel in RESPONSE_TEXT_SELECTORS:
                try:
                    resp_els = page.query_selector_all(sel)
                    if resp_els:
                        text = resp_els[-1].inner_text().strip()[:500]
                        if text:
                            print(f"  📝 Final response: {text}")
                            break
                except:
                    continue
            if not headless:
                print("\n  ⏸️  Browser will stay open for 60 seconds for inspection...")
                time.sleep(60)
            return None

        # Download images
        print(f"  💾 Downloading {len(images_found)} images...")
        saved_paths = []
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Try download button approach first (via generated-image wrapper)
        generated_image_wrappers = page.query_selector_all("generated-image")

        if generated_image_wrappers:
            for i, gen_img in enumerate(generated_image_wrappers):
                try:
                    print(f"    📥 Downloading image {i+1}...")

                    # Find download button
                    download_button = gen_img.query_selector('button[data-test-id="download-generated-image-button"]')

                    if not download_button:
                        # Fallback to screenshot
                        img_elem = gen_img.query_selector('img')
                        if img_elem:
                            screenshot_path = output_path / f"gemini_image_{i+1}_{int(time.time())}.png"
                            img_elem.screenshot(path=str(screenshot_path))
                            saved_paths.append(str(screenshot_path))
                            print(f"    ✓ Saved (screenshot): {screenshot_path}")
                        continue

                    # Download via button
                    with page.expect_download() as download_info:
                        download_button.click()

                    download = download_info.value
                    suggested_filename = download.suggested_filename
                    file_ext = Path(suggested_filename).suffix or '.png'
                    filename = output_path / f"gemini_image_{i+1}_{int(time.time())}{file_ext}"
                    download.save_as(str(filename))
                    saved_paths.append(str(filename))
                    print(f"    ✓ Downloaded: {filename}")

                except Exception as e:
                    print(f"    ❌ Failed to download image {i+1}: {e}")
                    try:
                        img_elem = gen_img.query_selector('img')
                        if img_elem:
                            screenshot_path = output_path / f"gemini_image_{i+1}_{int(time.time())}.png"
                            img_elem.screenshot(path=str(screenshot_path))
                            saved_paths.append(str(screenshot_path))
                            print(f"    ✓ Saved (fallback screenshot): {screenshot_path}")
                    except Exception as fallback_error:
                        print(f"    ❌ Fallback also failed: {fallback_error}")
                    continue
        else:
            # No generated-image wrappers, download images via src URL
            print("  ⚠️ No download button available, downloading via src URL")
            for i, img in enumerate(images_found):
                try:
                    src = img.get_attribute('src') or ''
                    if src and 'googleusercontent.com' in src:
                        # Use page.request to download (carries cookies/session)
                        response = page.request.get(src)
                        if response.ok:
                            file_path = output_path / f"gemini_image_{i+1}_{int(time.time())}.png"
                            file_path.write_bytes(response.body())
                            saved_paths.append(str(file_path))
                            print(f"    ✓ Downloaded via URL: {file_path}")
                        else:
                            raise Exception(f"HTTP {response.status}")
                    else:
                        raise Exception(f"No valid src URL: {src[:80]}")
                except Exception as e:
                    print(f"    ⚠️ URL download failed for image {i+1}: {e}, trying screenshot...")
                    try:
                        screenshot_path = output_path / f"gemini_image_{i+1}_{int(time.time())}.png"
                        img.screenshot(path=str(screenshot_path))
                        saved_paths.append(str(screenshot_path))
                        print(f"    ✓ Saved (screenshot): {screenshot_path}")
                    except Exception as e2:
                        print(f"    ❌ Screenshot also failed: {e2}")

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

        if not headless:
            print("\n  ⏸️  Browser will stay open for 30 seconds for debugging...")
            time.sleep(30)

        return None

    finally:
        if context:
            BrowserFactory.cleanup(context)
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

    saved_paths = generate_image(
        prompt=args.prompt,
        output_dir=args.output,
        headless=args.headless,
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
