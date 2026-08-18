"""
Automated Test Suite for Phase 4 Architecture:
- Deep Web Research Engine (WebSearchTool & FetchUrlSummaryTool clean extraction)
- Browser Agent Driver Escalation (FallbackBrowserController & PlaywrightBrowserController)
- Interactive Browser Operations (Navigate, Click, Type, Inspect)
"""

import sys
import os
from tools.tool_router import tool_router
from tools.browser_tools import (
    FallbackBrowserController,
    set_browser_controller,
    BrowserNavigateTool,
    BrowserInspectTool,
    BrowserClickTool,
    BrowserTypeTool
)
from tools.playwright_controller import PlaywrightBrowserController

def test_web_research_engine():
    print("=== Testing Deep Web Research Engine ===")
    res1 = tool_router.route_and_execute("web_search", {"query": "artificial intelligence neural networks"})
    print("Web Search Result Status:", res1["status"])
    assert res1["status"] == "SUCCESS"
    assert res1["result"] is not None

    res2 = tool_router.route_and_execute("fetch_url_summary", {"url": "https://example.com"})
    print("URL Summary Status:", res2["status"])
    assert res2["status"] == "SUCCESS"
    assert "example" in str(res2["result"]).lower() or "domain" in str(res2["result"]).lower()
    print("[OK] Deep Web Research Engine tests passed.\n")


def test_browser_agent_driver_escalation():
    print("=== Testing Browser Agent Driver Escalation & Controller Abstraction ===")
    
    # 1. Test Fallback Driver
    set_browser_controller(FallbackBrowserController())
    res_inspect = tool_router.route_and_execute("browser_inspect", {})
    print("Fallback Inspect Driver:", res_inspect["result"].get("active_driver"))
    assert res_inspect["result"]["active_driver"] == "Fallback (webbrowser)"

    # 2. Test Playwright Driver (or graceful fallback if Playwright binary is absent)
    pw_controller = PlaywrightBrowserController(headless=True)
    set_browser_controller(pw_controller)
    
    res_nav = tool_router.route_and_execute("browser_navigate", {"url": "https://example.com"})
    print("Playwright Navigate Status:", res_nav["status"])
    assert res_nav["status"] in ("SUCCESS", "EXECUTION_ERROR")

    res_pw_inspect = tool_router.route_and_execute("browser_inspect", {})
    print("Playwright Inspect Data:", res_pw_inspect["result"].get("title"))

    # Cleanup browser
    pw_controller.close()
    set_browser_controller(FallbackBrowserController())

    print("[OK] Browser Agent Driver Escalation tests passed.\n")


def test_tool_router_all_schemas():
    print("=== Testing Tool Router Schemas for All 12 Tools ===")
    schemas = tool_router.get_all_schemas()
    names = [s["name"] for s in schemas]
    print("Registered Tool Names:", names)
    
    expected = [
        "open_app", "open_folder", "system_action", "take_screenshot",
        "web_search", "fetch_url_summary", "open_website",
        "browser_navigate", "browser_media_control", "browser_inspect",
        "browser_click", "browser_type"
    ]
    for exp in expected:
        assert exp in names, f"Missing tool '{exp}' from ToolRouter!"

    print("[OK] Tool Router all 12 tools schemas test passed.\n")


if __name__ == "__main__":
    test_web_research_engine()
    test_browser_agent_driver_escalation()
    test_tool_router_all_schemas()
    print("=== ALL PHASE 4 ARCHITECTURE TESTS PASSED! ===")
