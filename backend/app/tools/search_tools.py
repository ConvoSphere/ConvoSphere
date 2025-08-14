"""
Search tools for the AI Assistant Platform.

This module provides tools for web search and Wikipedia search functionality.
"""

from typing import Any
import os
import asyncio
import aiohttp
from urllib.parse import urlencode

from .base import BaseTool


class WebSearchTool(BaseTool):
    """Tool for performing web searches (SearxNG preferred)."""

    name = "web_search"
    description = "Search the web for current information (SearxNG preferred)"
    parameters = {
        "query": {"type": "string", "description": "The search query"},
        "top_k": {
            "type": "integer",
            "description": "Maximum number of results to return",
            "default": 5,
        },
        "time_range": {
            "type": "string",
            "description": "Time range filter (day|week|month|year|any)",
            "default": "any",
        },
        "lang": {
            "type": "string",
            "description": "Language (ISO code)",
            "default": "en",
        },
        "site": {
            "type": "string",
            "description": "Restrict search to a specific site (e.g., example.com)",
            "default": "",
        },
        "safe_mode": {
            "type": "boolean",
            "description": "Enable SafeSearch",
            "default": True,
        },
        "sources": {
            "type": "array",
            "description": "SearxNG engines to use (optional)",
            "items": {"type": "string"},
            "default": [],
        },
    }

    async def execute(
        self,
        query: str,
        top_k: int = 5,
        time_range: str = "any",
        lang: str = "en",
        site: str = "",
        safe_mode: bool = True,
        sources: list[str] | None = None,
    ) -> dict[str, Any]:
        """Execute a web search via SearxNG JSON API with fallback."""
        try:
            searx_url = os.getenv("SEARXNG_URL")
            backend = None
            results: list[dict[str, Any]] = []

            if site:
                query = f"site:{site} {query}"

            if searx_url:
                backend = "searxng"
                params = {
                    "q": query,
                    "format": "json",
                    "language": lang,
                    "safesearch": 1 if safe_mode else 0,
                }
                if time_range and time_range != "any":
                    params["time_range"] = time_range
                if sources:
                    params["engines"] = ",".join(sources)

                headers = {"Accept": "application/json"}
                auth = os.getenv("SEARXNG_BASIC_AUTH")
                if auth:
                    headers["Authorization"] = f"Basic {auth}"

                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{searx_url}/search", params=params, headers=headers, timeout=15) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            for item in data.get("results", [])[: max(1, min(top_k, 20))]:
                                results.append(
                                    {
                                        "title": item.get("title"),
                                        "url": item.get("url"),
                                        "snippet": item.get("content"),
                                        "source": item.get("engine"),
                                        "published_at": item.get("publishedDate"),
                                    }
                                )
                        else:
                            return {
                                "success": False,
                                "error": f"SearxNG HTTP {resp.status}",
                                "backend": backend,
                            }

            else:
                # Placeholder fallback; integrate SerpAPI/Brave here if configured
                backend = "placeholder"
                for i in range(min(top_k, 3)):
                    results.append(
                        {
                            "title": f"Search result {i + 1} for: {query}",
                            "url": f"https://example{i + 1}.com",
                            "snippet": f"Placeholder result {i + 1} for the query: {query}",
                            "source": "placeholder",
                            "published_at": None,
                        }
                    )

            return {
                "success": True,
                "results": results,
                "query": query,
                "total_results": len(results),
                "backend": backend,
            }
        except asyncio.TimeoutError:
            return {"success": False, "error": "Search timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}


class WikipediaSearchTool(BaseTool):
    """Tool for searching Wikipedia."""

    name = "wikipedia_search"
    description = "Search Wikipedia for information"
    parameters = {
        "query": {
            "type": "string",
            "description": "The search query to perform",
        },
        "language": {
            "type": "string",
            "description": "Wikipedia language code (e.g., 'en', 'de')",
            "default": "en",
        },
    }

    async def execute(self, query: str, language: str = "en") -> dict[str, Any]:
        """Execute a Wikipedia search (placeholder)."""
        try:
            return {
                "success": True,
                "results": [
                    {
                        "title": f"Wikipedia article: {query}",
                        "url": f"https://{language}.wikipedia.org/wiki/{query.replace(' ', '_')}",
                        "snippet": f"This is a placeholder Wikipedia result for: {query}",
                        "language": language,
                    },
                ],
                "query": query,
                "language": language,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "language": language,
            }
