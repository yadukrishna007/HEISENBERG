"""
Automated Test Suite for Phase 3 Architecture:
- Tool Router (Stage 1 Validation + Stage 2 Safety dispatching across tool families)
- Web Tools (lightweight search, HTTP URL summary without GUI)
- Browser Tools (FallbackBrowserController abstraction, navigation, media control, page inspect)
- OS Tools & TakeScreenshotTool (scratch/screenshots/ storage & auto-cleanup)
"""

import os
import time
from tools.tool_router import tool_router
from tools.web_tools import WebSearchTool, FetchUrlSummaryTool
from tools.browser_tools import BrowserNavigateTool, BrowserMediaTool, BrowserInspectTool, FallbackBrowserController, active_browser_controller
from tools.os_tools import OpenAppTool, OpenFolderTool, SystemControlTool, TakeScreenshotTool, SCRATCH_SCREENSHOTS_DIR, cleanup_scratch_screenshots


def test_tool_router_registration():
    print("=== Testing Tool Router Registration ===")
    schemas = tool_router.get_all_schemas()
    tool_names = [s["name"] for s in schemas]
    print(f"Registered Tool Names: {tool_names}")
    
    expected = [
        "open_app", "open_folder", "system_action", "take_screenshot",
        "web_search", "fetch_url_summary", "open_website",
        "browser_navigate", "browser_media_control", "browser_inspect"
    ]
    for exp in expected:
        assert exp in tool_names, f"Expected tool '{exp}' missing from ToolRouter!"

    print("[OK] Tool Router registration tests passed.\n")


def test_web_tools():
    print("=== Testing Web Tools (Non-interactive) ===")
    
    # 1. web_search
    res1 = tool_router.route_and_execute("web_search", {"query": "python programming language"})
    print(f"Web Search Status: {res1['status']}")
    assert res1["status"] == "SUCCESS", "Web search failed"

    # 2. fetch_url_summary
    res2 = tool_router.route_and_execute("fetch_url_summary", {"url": "https://example.com"})
    print(f"Fetch URL Summary Status: {res2['status']}")
    assert res2["status"] == "SUCCESS", "Fetch URL summary failed"
    assert "content_summary" in res2["result"], "Missing content summary"

    print("[OK] Web Tools tests passed.\n")


def test_browser_tools():
    print("=== Testing Browser Tools & Abstraction ===")
    assert isinstance(active_browser_controller, FallbackBrowserController), "Browser controller should use FallbackBrowserController"

    # 1. browser_media_control
    res1 = tool_router.route_and_execute("browser_media_control", {"action": "play_pause"})
    print(f"Media Control Status: {res1['status']}")
    assert res1["status"] == "SUCCESS", "Media control failed"

    # 2. browser_inspect
    res2 = tool_router.route_and_execute("browser_inspect", {})
    print(f"Browser Inspect Status: {res2['status']}")
    assert res2["status"] == "SUCCESS", "Browser inspect failed"

    print("[OK] Browser Tools tests passed.\n")


def test_os_tools_and_screenshots():
    print("=== Testing OS Tools & Screenshot Scratch Storage ===")
    
    # 1. High-risk safety check (shutdown)
    res_high = tool_router.route_and_execute("system_action", {"action": "shutdown"})
    print(f"High-risk action status: {res_high['status']}")
    assert res_high["status"] == "NEEDS_CONFIRMATION", "High-risk action should require safety confirmation"

    # 2. Take screenshot to scratch/screenshots/
    res_shot = tool_router.route_and_execute("take_screenshot", {})
    print(f"Screenshot Status: {res_shot['status']}")
    assert res_shot["status"] == "SUCCESS", "Screenshot capture failed"
    
    filepath = res_shot["result"]["filepath"]
    print(f"Captured Screenshot Path: {filepath}")
    assert os.path.exists(filepath), f"Screenshot file missing at {filepath}"
    assert "scratch" in filepath and "screenshots" in filepath, "Screenshot not saved under scratch/screenshots/"

    # Test auto-cleanup function
    cleanup_scratch_screenshots(max_age_seconds=0)  # Clean all for test
    print(f"Post-cleanup scratch directory exists: {os.path.exists(SCRATCH_SCREENSHOTS_DIR)}")

    print("[OK] OS Tools & Screenshot Scratch storage tests passed.\n")


if __name__ == "__main__":
    test_tool_router_registration()
    test_web_tools()
    test_browser_tools()
    test_os_tools_and_screenshots()
    print("=== ALL PHASE 3 ARCHITECTURE TESTS PASSED! ===")
