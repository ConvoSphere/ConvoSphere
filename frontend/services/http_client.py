"""
HTTP client for making real API requests to the backend.

This module provides a robust HTTP client using aiohttp for
asynchronous requests with proper error handling and retry logic.
"""

import asyncio
import json
from typing import Any

from aiohttp import ClientError, ClientSession, ClientTimeout
from aiohttp.client_exceptions import ClientResponseError


class HTTPClient:
    """Robust HTTP client for API communication."""

    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 30):
        """
        Initialize the HTTP client.

        Args:
            base_url: Base URL for the API
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = ClientTimeout(total=timeout)
        self.session: ClientSession | None = None
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self.retry_attempts = 3
        self.retry_delay = 1.0

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def connect(self):
        """Create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = ClientSession(timeout=self.timeout)

    async def close(self):
        """Close aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()

    def set_auth_token(self, token: str):
        """Set authentication token."""
        self.headers["Authorization"] = f"Bearer {token}"

    def clear_auth_token(self):
        """Clear authentication token."""
        if "Authorization" in self.headers:
            del self.headers["Authorization"]

    async def request(
        self,
        method: str,
        endpoint: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        Make HTTP request with retry logic.

        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request data
            params: Query parameters
            headers: Additional headers

        Returns:
            Dict containing response data

        Raises:
            Exception: If request fails after retries
        """
        await self.connect()

        url = f"{self.base_url}{endpoint}"
        request_headers = {**self.headers}
        if headers:
            request_headers.update(headers)

        for attempt in range(self.retry_attempts):
            try:
                async with self.session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    headers=request_headers,
                ) as response:
                    return await self._handle_response(response)

            except ClientResponseError as e:
                if e.status == 401:
                    # Unauthorized - clear token and raise
                    self.clear_auth_token()
                    raise Exception("Authentication required")
                if e.status >= 500:
                    # Server error - retry
                    if attempt < self.retry_attempts - 1:
                        await asyncio.sleep(self.retry_delay * (attempt + 1))
                        continue
                    raise Exception(f"Server error: {e.status}")
                # Client error - don't retry
                raise Exception(f"Request failed: {e.status} - {e.message}")

            except ClientError as e:
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                raise Exception(f"Network error: {str(e)}")

            except Exception as e:
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                raise Exception(f"Request failed: {str(e)}")

        raise Exception("Request failed after all retry attempts")

    async def _handle_response(self, response) -> dict[str, Any]:
        """Handle HTTP response."""
        try:
            content_type = response.headers.get("content-type", "")

            if "application/json" in content_type:
                data = await response.json()
            else:
                text = await response.text()
                data = {"text": text}

            if response.status >= 400:
                error_msg = data.get("detail", data.get("message", "Unknown error"))
                raise Exception(f"HTTP {response.status}: {error_msg}")

            return data

        except json.JSONDecodeError:
            text = await response.text()
            if response.status >= 400:
                raise Exception(f"HTTP {response.status}: {text}")
            return {"text": text}

    # Convenience methods
    async def get(
        self, endpoint: str, params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make GET request."""
        return await self.request("GET", endpoint, params=params)

    async def post(
        self, endpoint: str, data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make POST request."""
        return await self.request("POST", endpoint, data=data)

    async def put(
        self, endpoint: str, data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make PUT request."""
        return await self.request("PUT", endpoint, data=data)

    async def delete(self, endpoint: str) -> dict[str, Any]:
        """Make DELETE request."""
        return await self.request("DELETE", endpoint)

    async def patch(
        self, endpoint: str, data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make PATCH request."""
        return await self.request("PATCH", endpoint, data=data)


# Global HTTP client instance
http_client = HTTPClient()
