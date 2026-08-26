"""
Geocoding Service

Provides reverse geocoding to convert latitude/longitude into readable location names.
Uses the free Nominatim API (OpenStreetMap).
"""

import logging
from typing import Optional, Dict, Any
import httpx

logger = logging.getLogger(__name__)


class GeocodingError(Exception):
    """Exception raised for geocoding errors"""
    pass


class GeocodingService:
    """
    Service for reverse geocoding coordinates to place names.
    """

    # Nominatim API endpoint (free, no API key required)
    NOMINATIM_BASE_URL = "https://nominatim.openstreetmap.org"

    def __init__(self, timeout: float = 5.0):
        """
        Initialize the geocoding service.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self._cache: Dict[str, Dict[str, Any]] = {}  # Simple in-memory cache

    async def reverse_geocode(
        self,
        latitude: float,
        longitude: float
    ) -> Optional[Dict[str, Any]]:
        """
        Convert latitude/longitude to readable place information.

        Args:
            latitude: Location latitude
            longitude: Location longitude

        Returns:
            Dictionary with location details (city, state, country, formatted_address)
            or None if geocoding fails
        """
        # Check cache first
        cache_key = f"{latitude:.4f},{longitude:.4f}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        url = f"{self.NOMINATIM_BASE_URL}/reverse"
        params = {
            "format": "json",
            "lat": str(latitude),
            "lon": str(longitude),
            "zoom": "18",  # Building/street level for most accurate results
            "accept-language": "en",  # Prefer English names
        }
        headers = {
            "User-Agent": "ProductComparison/1.0",  # Required by Nominatim
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                data = response.json()

                location_data = self._parse_nominatim_response(data)

                # Log what we got for debugging
                logger.info(f"Geocoded ({latitude}, {longitude}) -> {location_data}")

                # Cache the result
                if location_data:
                    self._cache[cache_key] = location_data

                return location_data

        except httpx.TimeoutException:
            logger.warning(f"Geocoding request timed out for ({latitude}, {longitude})")
            return None
        except httpx.HTTPStatusError as e:
            logger.warning(f"Geocoding request failed: {e.response.status_code}")
            return None
        except Exception as e:
            logger.warning(f"Geocoding failed: {e}")
            return None

    def _parse_nominatim_response(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse Nominatim API response into our location format.

        Args:
            data: Raw API response from Nominatim

        Returns:
            Dictionary with location details
        """
        if not data or "error" in data:
            return None

        address = data.get("address", {})
        display_name = data.get("display_name", "")

        # Extract location components with better fallbacks
        city = (
            address.get("city") or
            address.get("town") or
            address.get("village") or
            address.get("suburb") or
            address.get("county") or
            address.get("district") or
            address.get("municipality")
        )

        state = (
            address.get("state") or
            address.get("state_district") or
            address.get("region") or
            address.get("province")
        )

        country = address.get("country", "")

        # Pincode if available
        postcode = address.get("postcode")

        # Build formatted address - prioritize locality/city name
        parts = []

        # Try to get the most specific location name
        locality = address.get("suburb") or address.get("neighbourhood") or city
        if locality:
            parts.append(locality)

        if city and city != locality:
            parts.append(city)

        if state and state not in parts:
            parts.append(state)

        # If we still don't have good parts, use the first part of display name
        formatted = ", ".join(parts) if parts else display_name.split(",")[0].strip()

        return {
            "city": city,
            "state": state,
            "country": country,
            "postcode": postcode,
            "formatted_address": formatted,
            "full_address": display_name,
        }

    def get_location_display(
        self,
        latitude: float,
        longitude: float
    ) -> str:
        """
        Get a human-readable location string.

        Synchronous version that returns a default string if geocoding hasn't been done.
        """
        cache_key = f"{latitude:.4f},{longitude:.4f}"
        if cache_key in self._cache:
            location = self._cache[cache_key]
            return location.get("formatted_address", "Unknown Location")

        # Default fallback before async geocoding completes
        return f"{latitude:.2f}, {longitude:.2f}"
