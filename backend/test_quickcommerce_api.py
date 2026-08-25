"""
QuickCommerce API Integration Test - PHASE 1

This script tests the QuickCommerce API integration before building
the full application. It verifies:

1. API authentication works
2. Group search endpoint returns data
3. Response structure matches documentation
4. Chennai location works with supported platforms

SECURITY: Never print or expose the API key in logs or output.
"""

import asyncio
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import httpx


@dataclass
class PlatformProduct:
    """Normalized product data from a platform"""
    platform: str
    product_id: str
    name: str
    price: Optional[float] = None
    mrp: Optional[float] = None
    discount: Optional[float] = None
    available: bool = False
    delivery_time_minutes: Optional[int] = None
    product_url: Optional[str] = None


class QuickCommerceAPITester:
    """Test client for QuickCommerce API"""

    def __init__(self):
        self.api_key = os.getenv("QUICKCOMMERCE_API_KEY")
        self.base_url = os.getenv("QUICKCOMMERCE_BASE_URL", "https://api.quickcommerceapi.com")

        if not self.api_key or self.api_key == "your_api_key_here":
            raise ValueError(
                "QUICKCOMMERCE_API_KEY not set. Please set it in .env file.\n"
                "Get your API key from: https://quickcommerceapi.com"
            )

    def _print_safe(self, message: str) -> None:
        """Print with safe API key masking"""
        safe_message = message.replace(self.api_key, "***API_KEY_REDACTED***")
        print(safe_message)

    async def search_products(
        self,
        query: str,
        latitude: float,
        longitude: float,
        platforms: List[str],
    ) -> Dict[str, Any]:
        """
        Search products using QuickCommerce API.

        Args:
            query: Search query (e.g., 'milk')
            latitude: Location latitude (Chennai: ~13.08)
            longitude: Location longitude (Chennai: ~80.27)
            platforms: List of platform names

        Returns:
            API response as dictionary
        """
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

        self._print_safe(f"\n🔍 Searching for: '{query}'")
        self._print_safe(f"📍 Location: ({latitude}, {longitude})")
        self._print_safe(f"🛒 Platforms: {', '.join(platforms)}")
        self._print_safe(f"🌐 Endpoint: {url}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                self._print_safe(f"❌ HTTP Error: {e.response.status_code}")
                self._print_safe(f"Response: {e.response.text[:200]}")
                raise
            except httpx.TimeoutException:
                self._print_safe("❌ Request timed out")
                raise
            except Exception as e:
                self._print_safe(f"❌ Unexpected error: {str(e)}")
                raise

    def parse_delivery_time(self, sla: str) -> Optional[int]:
        """Parse delivery time from SLA string"""
        if not sla:
            return None

        # Handle various formats: "8 mins", "10-15 mins", "30 min"
        sla_lower = sla.lower().replace("min", "").replace(" ", "")

        try:
            if "-" in sla_lower:
                # Take the lower bound for range
                return int(sla_lower.split("-")[0])
            return int(sla_lower)
        except (ValueError, IndexError):
            return None

    def normalize_response(self, response: Dict[str, Any], query: str) -> List[PlatformProduct]:
        """
        Normalize API response into our internal format.

        Args:
            response: Raw API response
            query: Original search query

        Returns:
            List of normalized products
        """
        products: List[PlatformProduct] = []

        if response.get("status") != "success":
            self._print_safe(f"⚠️  API returned status: {response.get('status')}")
            return products

        data = response.get("data", {})
        results = data.get("results", {})

        for platform_name, platform_results in results.items():
            self._print_safe(f"\n📦 {platform_name} Results:")

            if not platform_results:
                self._print_safe("   No products found")
                continue

            for item in platform_results:
                product_id = item.get("id", "")
                name = item.get("name", "Unknown")
                mrp_raw = item.get("mrp")
                offer_price_raw = item.get("offer_price")
                available = item.get("available", False)

                # Convert prices to float (API may return strings)
                mrp = float(mrp_raw) if mrp_raw is not None else None
                offer_price = float(offer_price_raw) if offer_price_raw is not None else None

                # Calculate discount
                discount = None
                if mrp and offer_price and mrp > offer_price:
                    discount = mrp - offer_price

                # Parse delivery time
                platform_info = item.get("platform", {})
                sla = platform_info.get("sla", "")
                delivery_minutes = self.parse_delivery_time(sla)

                product = PlatformProduct(
                    platform=platform_name,
                    product_id=product_id,
                    name=name,
                    price=offer_price,
                    mrp=mrp,
                    discount=discount,
                    available=available,
                    delivery_time_minutes=delivery_minutes,
                )
                products.append(product)

                # Print safe summary (no API keys)
                avail_status = "✅" if available else "❌"
                delivery = f"{delivery_minutes} min" if delivery_minutes else sla or "N/A"
                price_str = f"₹{offer_price}" if offer_price else "N/A"
                discount_str = f" (Save ₹{discount})" if discount else ""

                self._print_safe(
                    f"   {avail_status} {name}"
                    f"\n      Price: {price_str}{discount_str}"
                    f"\n      Delivery: {delivery}"
                )

        return products

    async def run_test(self, query: str = "milk") -> bool:
        """
        Run complete test of QuickCommerce API integration.

        Returns:
            True if test passed, False otherwise
        """
        try:
            self._print_safe("=" * 60)
            self._print_safe("QuickCommerce API Integration Test - PHASE 1")
            self._print_safe("=" * 60)

            # Chennai coordinates
            chennai_lat = 13.0827
            chennai_lon = 80.2707

            # Test with all three initial platforms
            platforms = ["BlinkIt", "Zepto", "Swiggy"]

            # Make API call
            response = await self.search_products(
                query=query,
                latitude=chennai_lat,
                longitude=chennai_lon,
                platforms=platforms,
            )

            # Check credits
            credits_remaining = response.get("credits_remaining", 0)
            credit_cost = response.get("data", {}).get("credit_cost", 0)
            self._print_safe(f"\n💰 Credits used: {credit_cost}")
            self._print_safe(f"💰 Credits remaining: {credits_remaining}")

            # Normalize and display results
            products = self.normalize_response(response, query)

            # Summary
            self._print_safe("\n" + "=" * 60)
            self._print_safe("📊 TEST SUMMARY")
            self._print_safe("=" * 60)
            self._print_safe(f"Total products found: {len(products)}")

            # Count by platform
            platform_counts: Dict[str, int] = {}
            for p in products:
                platform_counts[p.platform] = platform_counts.get(p.platform, 0) + 1

            for platform, count in platform_counts.items():
                self._print_safe(f"  {platform}: {count} products")

            # Count availability
            available_count = sum(1 for p in products if p.available)
            self._print_safe(f"\nAvailable products: {available_count}/{len(products)}")

            # Price range
            prices = [p.price for p in products if p.price is not None]
            if prices:
                self._print_safe(f"Price range: ₹{min(prices)} - ₹{max(prices)}")

            # Check for expected data
            if len(products) == 0:
                self._print_safe("\n⚠️  WARNING: No products returned")
                self._print_safe("Possible causes:")
                self._print_safe("  - Query not available in Chennai area")
                self._print_safe("  - Platform availability issues")
                self._print_safe("  - API quota exhausted")
                return False

            self._print_safe("\n✅ PHASE 1 TEST PASSED!")
            self._print_safe("QuickCommerce API integration verified successfully.")
            self._print_safe("\nNext steps:")
            self._print_safe("  1. Build production QuickCommerceClient")
            self._print_safe("  2. Implement product normalization (PHASE 2)")
            self._print_safe("  3. Implement product matching (PHASE 3)")
            self._print_safe("  4. Build price comparison (PHASE 4)")

            return True

        except ValueError as e:
            self._print_safe(f"\n❌ Configuration Error: {e}")
            return False
        except Exception as e:
            self._print_safe(f"\n❌ Test Failed: {str(e)}")
            import traceback

            self._print_safe(traceback.format_exc())
            return False


async def main():
    """Main test runner"""
    tester = QuickCommerceAPITester()
    success = await tester.run_test(query="milk")
    exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
