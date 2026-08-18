"""
Playwright Browser Controller for Heisenberg V2 Architecture
Extends BrowserController with Playwright Chromium driver for full DOM extraction,
page navigation, clicking, typing, and page inspection.
"""

from typing import Dict, Any, Optional, List
from tools.browser_tools import BrowserController, FallbackBrowserController


class PlaywrightBrowserController(BrowserController):
    """
    Interactive Browser Controller using Playwright.
    Subclasses BrowserController and provides dynamic escalation from FallbackBrowserController.
    """
    def __init__(self, headless: bool = True):
        self.headless = headless
        self._playwright = None
        self._browser = None
        self._page = None
        self._initialized = False

    def _ensure_browser(self) -> bool:
        if self._initialized and self._page:
            return True
        try:
            from playwright.sync_api import sync_playwright
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch(headless=self.headless)
            self._page = self._browser.new_page()
            self._initialized = True
            return True
        except Exception as e:
            print(f"[PlaywrightBrowserController Warning] Could not launch Playwright: {e}")
            return False

    def navigate(self, url: str) -> bool:
        if not url.startswith("http://") and not url.startswith("https://"):
            url = f"https://{url}"

        if self._ensure_browser():
            try:
                self._page.goto(url, timeout=15000)
                return True
            except Exception as e:
                print(f"[PlaywrightBrowserController Error] Navigation to '{url}' failed: {e}")
                return False
        else:
            # Fall back to default browser opener
            fallback = FallbackBrowserController()
            return fallback.navigate(url)

    def media_action(self, action: str) -> bool:
        fallback = FallbackBrowserController()
        return fallback.media_action(action)

    def click_element(self, selector: str) -> bool:
        if self._ensure_browser():
            try:
                self._page.click(selector, timeout=5000)
                return True
            except Exception as e:
                print(f"[PlaywrightBrowserController Error] Click on '{selector}' failed: {e}")
                return False
        return False

    def type_text(self, selector: str, text: str) -> bool:
        if self._ensure_browser():
            try:
                self._page.fill(selector, text, timeout=5000)
                return True
            except Exception as e:
                print(f"[PlaywrightBrowserController Error] Type into '{selector}' failed: {e}")
                return False
        return False

    def inspect_page(self) -> Dict[str, Any]:
        if self._ensure_browser():
            try:
                title = self._page.title()
                url = self._page.url
                
                # Extract interactive elements summary
                buttons = self._page.eval_on_selector_all("button, input[type='button'], input[type='submit']", "els => els.slice(0, 10).map(e => e.innerText || e.value || e.id || 'button')")
                links = self._page.eval_on_selector_all("a[href]", "els => els.slice(0, 10).map(e => ({text: e.innerText.trim(), href: e.href}))")
                
                return {
                    "title": title,
                    "url": url,
                    "active_driver": "Playwright (Chromium)",
                    "buttons": buttons,
                    "sample_links": links
                }
            except Exception as e:
                print(f"[PlaywrightBrowserController Error] Inspection failed: {e}")

        fallback = FallbackBrowserController()
        return fallback.inspect_page()

    def close(self):
        try:
            if self._browser:
                self._browser.close()
            if self._playwright:
                self._playwright.stop()
        except Exception:
            pass
        self._initialized = False
