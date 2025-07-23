"""
API tools for the AI Assistant Platform.

This module provides tools for making HTTP requests.
"""

from typing import Any

from .base import BaseTool


class HTTPRequestTool(BaseTool):
    """Tool for making HTTP requests."""

    name = "http_request"
    description = "Make HTTP requests to external APIs"
    parameters = {
        "url": {
            "type": "string",
            "description": "URL to make the request to",
        },
        "method": {
            "type": "string",
            "description": "HTTP method (GET, POST, PUT, DELETE)",
            "default": "GET",
        },
        "headers": {
            "type": "object",
            "description": "HTTP headers to include",
            "default": {},
        },
        "data": {
            "type": "object",
            "description": "Data to send with the request",
            "default": {},
        },
    }

    async def execute(
        self, url: str, method: str = "GET", headers: dict = None, data: dict = None,
    ) -> dict[str, Any]:
        """Make an HTTP request."""
        try:
            import requests

            response = requests.request(
                method=method.upper(),
                url=url,
                headers=headers or {},
                json=data or {},
                timeout=10,
            )

            return {
                "success": True,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content": response.text,
                "url": url,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": url,
            }
