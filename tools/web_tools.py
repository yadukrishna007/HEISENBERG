"""
Web Research Tools for Heisenberg V2 Architecture
Handles lightweight, non-interactive web search, URL content summary, and article text extraction.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Any
from tools.base_tool import BaseTool, ToolResult
from system_actions import fetch_info


class WebSearchTool(BaseTool):
    name = "web_search"
    description = "Search the web or Wikipedia for factual information, news, or query answers."
    risk_level = 0  # Low risk
    parameters_schema = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Topic or query to search for."
            }
        },
        "required": ["query"]
    }

    def execute(self, query: str, **kwargs) -> ToolResult:
        try:
            info = fetch_info(query)
            return ToolResult(success=True, data=info)
        except Exception as e:
            return ToolResult(success=False, error=f"Web search failed for '{query}': {str(e)}")


class FetchUrlSummaryTool(BaseTool):
    name = "fetch_url_summary"
    description = "Fetch and extract text content directly from a URL via HTTP without opening a browser GUI."
    risk_level = 0  # Low risk
    parameters_schema = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "Full URL of the web page to fetch (e.g. 'https://example.com/article')."
            }
        },
        "required": ["url"]
    }

    def execute(self, url: str, **kwargs) -> ToolResult:
        target_url = url.strip()
        if not target_url.startswith(("http://", "https://")):
            target_url = "https://" + target_url

        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            resp = requests.get(target_url, headers=headers, timeout=5)
            if resp.status_code != 200:
                return ToolResult(success=False, error=f"HTTP request returned status {resp.status_code}")

            soup = BeautifulSoup(resp.text, "html.parser")
            
            # Remove scripts, styles, navs
            for element in soup(["script", "style", "nav", "header", "footer"]):
                element.decompose()

            paragraphs = [p.get_text().strip() for p in soup.find_all("p") if p.get_text().strip()]
            extracted_text = "\n\n".join(paragraphs[:10])

            if not extracted_text:
                extracted_text = soup.get_text()[:1000]

            return ToolResult(
                success=True,
                data={
                    "url": target_url,
                    "title": soup.title.string if soup.title else "No Title",
                    "content_summary": extracted_text[:1500]
                }
            )
        except Exception as e:
            return ToolResult(success=False, error=f"Failed to fetch URL content for '{url}': {str(e)}")


class OpenWebsiteTool(BaseTool):
    name = "open_website"
    description = "Open a website in the default browser."
    risk_level = 0  # Low risk
    parameters_schema = {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "Website URL or domain name to open."
            }
        },
        "required": ["target"]
    }

    def execute(self, target: str, **kwargs) -> ToolResult:
        from tools.browser_tools import active_browser_controller
        success = active_browser_controller.navigate(target)
        if success:
            return ToolResult(success=True, data=f"Opened website '{target}' in browser.")
        return ToolResult(success=False, error=f"Failed to open website '{target}'.")
