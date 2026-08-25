"""
QuickCommerce API Client

Async HTTP client for the QuickCommerce API.
Handles all external API communication with proper error handling and timeout management.
"""

import os
from typing import List, Dict, Any, Optional
import httpx
from app.core.config import settings


class QuickCommerceClientError(Exception):
    """Base exception for QuickCommerce client errors"""
    pass


class QuickCommerceTimeoutError(QuickCommerceClientError):
    """Exception raised when API request times out"""
    pass


class QuickCommerceAPIError(QuickCommerceClientError):
    """Exception raised when API returns error response"""
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class QuickCommerceClient:
    """
    Async client for QuickCommerce API.

    This client handles:
    - Authentication via API key
    - Timeout management
    - Error handling and retries
    - Response validation
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
    ):
        """
        Initialize the QuickCommerce client.

        Args:
            api_key: QuickCommerce API key (defaults to settings)
            base_url: API base URL (defaults to settings)
            timeout: Request timeout in seconds
        """
        self.api_key = api_key or settings.QUICKCOMMERCE_API_KEY
        self.base_url = base_url or settings.QUICKCOMMERCE_BASE_URL
        self.timeout = timeout

        if not self.api_key:
            raise ValueError(
                "QuickCommerce API key not configured. "
                "Set QUICKCOMMERCE_API_KEY environment variable."
            )

    async def group_search(
        self,
        query: str,
        latitude: float,
        longitude: float,
        platforms: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Perform group search across multiple platforms.

        This endpoint searches multiple platforms in a single request.

        Args:
            query: Search query (e.g., 'milk')
            latitude: Location latitude
            longitude: Location longitude
            platforms: List of platform names (optional, defaults to all supported)

        Returns:
            API response dictionary with results grouped by platform

        Raises:
            QuickCommerceTimeoutError: If request times out
            QuickCommerceAPIError: If API returns error
            QuickCommerceClientError: For other client errors
        """
        if platforms is None:
            platforms = ["BlinkIt", "Zepto", "Swiggy"]

        url = f"{self.base_url}/v1/groupsearch"
        params = {
            "q": query,
            "lat": latitude,
            "lon": longitude,
            "platforms": ",".join(platforms),
        }
        headers = {
            "X-API-Key": self.api_key,
            "Accept": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                return response.json()

        except httpx.TimeoutException:
            raise QuickCommerceTimeoutError(
                f"Request timed out after {self.timeout} seconds"
            )

        except httpx.HTTPStatusError as e:
            # Try to parse error response
            error_data = None
            try:
                error_data = e.response.json()
            except:
                pass

            raise QuickCommerceAPIError(
                message=f"API returned error status: {e.response.status_code}",
                status_code=e.response.status_code,
                response_data=error_data,
            )

        except httpx.RequestError as e:
            raise QuickCommerceClientError(f"Request failed: {str(e)}")

        except Exception as e:
            raise QuickCommerceClientError(f"Unexpected error: {str(e)}")

    async def search_platform(
        self,
        query: str,
        latitude: float,
        longitude: float,
        platform: str,
    ) -> List[Dict[str, Any]]:
        """
        Search a single platform (for individual platform queries).

        Args:
            query: Search query
            latitude: Location latitude
            longitude: Location longitude
            platform: Single platform name

        Returns:
            List of product results from the platform

        Raises:
            QuickCommerceTimeoutError: If request times out
            QuickCommerceAPIError: If API returns error
            QuickCommerceClientError: For other client errors
        """
        result = await self.group_search(
            query=query,
            latitude=latitude,
            longitude=longitude,
            platforms=[platform],
        )

        # Extract results for the single platform
        if result.get("status") != "success":
            return []

        data = result.get("data", {})
        results = data.get("results", {})
        return results.get(platform, [])
