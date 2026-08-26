"""
Fallback Demo Data Service

Provides demo data when the QuickCommerce API is unreachable or limits are reached.
This ensures the frontend remains functional for development/testing purposes.
"""

from typing import List, Dict, Any, Optional
from app.schemas.search import (
    SearchResponseSchema,
    ProductResultSchema,
    PlatformOfferSchema,
    ComparisonSchema,
    LocationSchema,
)


class FallbackDataService:
    """
    Generates demo product data for testing and fallback scenarios.
    """

    # Demo products organized by category
    DEMO_PRODUCTS = {
        "dairy": [
            {
                "name": "Amul Taaza Toned Milk",
                "brand": "Amul",
                "quantity": 500,
                "unit": "ml",
                "quantity_display": "500 ml",
                "image_url": None,
                "offers": {
                    "Zepto": {"price": 28, "mrp": 30, "discount": 7, "delivery_minutes": 8, "available": True},
                    "Swiggy": {"price": 29, "mrp": 30, "discount": 3, "delivery_minutes": 12, "available": True},
                    "BlinkIt": {"price": 28, "mrp": 30, "discount": 7, "delivery_minutes": 10, "available": True},
                }
            },
            {
                "name": "Amul Butter Salted",
                "brand": "Amul",
                "quantity": 100,
                "unit": "g",
                "quantity_display": "100 g",
                "image_url": None,
                "offers": {
                    "Zepto": {"price": 56, "mrp": 60, "discount": 7, "delivery_minutes": 8, "available": True},
                    "Swiggy": {"price": 57, "mrp": 60, "discount": 5, "delivery_minutes": 15, "available": True},
                    "BlinkIt": {"price": 55, "mrp": 60, "discount": 8, "delivery_minutes": 10, "available": True},
                }
            },
            {
                "name": "Gowardhan Fresh Paneer",
                "brand": "Gowardhan",
                "quantity": 200,
                "unit": "g",
                "quantity_display": "200 g",
                "image_url": None,
                "offers": {
                    "Zepto": {"price": 92, "mrp": 100, "discount": 8, "delivery_minutes": 8, "available": True},
                    "Swiggy": {"price": 94, "mrp": 100, "discount": 6, "delivery_minutes": 12, "available": True},
                    "BlinkIt": {"price": 93, "mrp": 100, "discount": 7, "delivery_minutes": 10, "available": True},
                }
            },
        ],
        "bread": [
            {
                "name": "English Oven Premium Whole Wheat Bread",
                "brand": "English Oven",
                "quantity": 400,
                "unit": "g",
                "quantity_display": "400 g",
                "image_url": None,
                "offers": {
                    "Zepto": {"price": 75, "mrp": 80, "discount": 6, "delivery_minutes": 8, "available": True},
                    "Swiggy": {"price": 76, "mrp": 80, "discount": 5, "delivery_minutes": 15, "available": True},
                    "BlinkIt": {"price": 74, "mrp": 80, "discount": 8, "delivery_minutes": 10, "available": True},
                }
            },
            {
                "name": "Britannia Good Day Rich Cashew",
                "brand": "Britannia",
                "quantity": 100,
                "unit": "g",
                "quantity_display": "100 g",
                "image_url": None,
                "offers": {
                    "Zepto": {"price": 40, "mrp": 45, "discount": 11, "delivery_minutes": 8, "available": True},
                    "Swiggy": {"price": 42, "mrp": 45, "discount": 7, "delivery_minutes": 12, "available": True},
                    "BlinkIt": {"price": 41, "mrp": 45, "discount": 9, "delivery_minutes": 10, "available": True},
                }
            },
        ],
        "staples": [
            {
                "name": "Tata Salt",
                "brand": "Tata",
                "quantity": 1,
                "unit": "kg",
                "quantity_display": "1 kg",
                "image_url": None,
                "offers": {
                    "Zepto": {"price": 24, "mrp": 28, "discount": 14, "delivery_minutes": 8, "available": True},
                    "Swiggy": {"price": 25, "mrp": 28, "discount": 11, "delivery_minutes": 15, "available": True},
                    "BlinkIt": {"price": 23, "mrp": 28, "discount": 18, "delivery_minutes": 10, "available": True},
                }
            },
            {
                "name": "India Gate Basmati Rice",
                "brand": "India Gate",
                "quantity": 1,
                "unit": "kg",
                "quantity_display": "1 kg",
                "image_url": None,
                "offers": {
                    "Zepto": {"price": 95, "mrp": 105, "discount": 10, "delivery_minutes": 8, "available": True},
                    "Swiggy": {"price": 98, "mrp": 105, "discount": 7, "delivery_minutes": 12, "available": True},
                    "BlinkIt": {"price": 94, "mrp": 105, "discount": 11, "delivery_minutes": 10, "available": True},
                }
            },
            {
                "name": "Fortune Sunlite Refined Oil",
                "brand": "Fortune",
                "quantity": 1,
                "unit": "l",
                "quantity_display": "1 L",
                "image_url": None,
                "offers": {
                    "Zepto": {"price": 145, "mrp": 165, "discount": 12, "delivery_minutes": 8, "available": True},
                    "Swiggy": {"price": 148, "mrp": 165, "discount": 10, "delivery_minutes": 15, "available": True},
                    "BlinkIt": {"price": 142, "mrp": 165, "discount": 14, "delivery_minutes": 10, "available": True},
                }
            },
        ],
        "snacks": [
            {
                "name": "Lays Classic Salted Chips",
                "brand": "Lays",
                "quantity": 50,
                "unit": "g",
                "quantity_display": "50 g",
                "image_url": None,
                "offers": {
                    "Zepto": {"price": 20, "mrp": 25, "discount": 20, "delivery_minutes": 8, "available": True},
                    "Swiggy": {"price": 22, "mrp": 25, "discount": 12, "delivery_minutes": 15, "available": True},
                    "BlinkIt": {"price": 19, "mrp": 25, "discount": 24, "delivery_minutes": 10, "available": True},
                }
            },
            {
                "name": "Bingo Mad Angles",
                "brand": "Bingo",
                "quantity": 75,
                "unit": "g",
                "quantity_display": "75 g",
                "image_url": None,
                "offers": {
                    "Zepto": {"price": 35, "mrp": 40, "discount": 13, "delivery_minutes": 8, "available": True},
                    "Swiggy": {"price": 36, "mrp": 40, "discount": 10, "delivery_minutes": 12, "available": True},
                    "BlinkIt": {"price": 34, "mrp": 40, "discount": 15, "delivery_minutes": 10, "available": True},
                }
            },
        ],
        "fruits": [
            {
                "name": "Fresh Apple Shimla",
                "brand": None,
                "quantity": 500,
                "unit": "g",
                "quantity_display": "500 g (approx 3-4 pcs)",
                "image_url": None,
                "offers": {
                    "Zepto": {"price": 120, "mrp": 150, "discount": 20, "delivery_minutes": 8, "available": True},
                    "Swiggy": {"price": 125, "mrp": 150, "discount": 17, "delivery_minutes": 15, "available": True},
                    "BlinkIt": {"price": 118, "mrp": 150, "discount": 21, "delivery_minutes": 10, "available": True},
                }
            },
            {
                "name": "Fresh Banana Yelakki",
                "brand": None,
                "quantity": 500,
                "unit": "g",
                "quantity_display": "500 g (approx 5-6 pcs)",
                "image_url": None,
                "offers": {
                    "Zepto": {"price": 35, "mrp": 40, "discount": 13, "delivery_minutes": 8, "available": True},
                    "Swiggy": {"price": 36, "mrp": 40, "discount": 10, "delivery_minutes": 12, "available": True},
                    "BlinkIt": {"price": 34, "mrp": 40, "discount": 15, "delivery_minutes": 10, "available": True},
                }
            },
        ],
        "coffee": [
            {
                "name": "Nescafe Classic Instant Coffee",
                "brand": "Nescafe",
                "quantity": 100,
                "unit": "g",
                "quantity_display": "100 g",
                "image_url": None,
                "offers": {
                    "Zepto": {"price": 145, "mrp": 160, "discount": 9, "delivery_minutes": 8, "available": True},
                    "Swiggy": {"price": 148, "mrp": 160, "discount": 8, "delivery_minutes": 15, "available": True},
                    "BlinkIt": {"price": 142, "mrp": 160, "discount": 11, "delivery_minutes": 10, "available": True},
                }
            },
            {
                "name": "Tata Coffee Grand",
                "brand": "Tata Coffee",
                "quantity": 200,
                "unit": "g",
                "quantity_display": "200 g",
                "image_url": None,
                "offers": {
                    "Zepto": {"price": 220, "mrp": 250, "discount": 12, "delivery_minutes": 8, "available": True},
                    "Swiggy": {"price": 225, "mrp": 250, "discount": 10, "delivery_minutes": 12, "available": True},
                    "BlinkIt": {"price": 218, "mrp": 250, "discount": 13, "delivery_minutes": 10, "available": True},
                }
            },
        ],
    }

    # Category keywords mapping
    CATEGORY_KEYWORDS = {
        "dairy": ["milk", "curd", "yogurt", "paneer", "cheese", "butter", "cream", "ghee", "dairy"],
        "bread": ["bread", "bun", "roti", "naan", "bakery", "biscuit", "cookie", "toast"],
        "staples": ["rice", "wheat", "flour", "atta", "salt", "sugar", "oil", "dal", "lentil", "grain", "staple"],
        "snacks": ["chips", "namkeen", "biscuit", "cookie", "snack", "chocolate", "candy", "munchies"],
        "fruits": ["apple", "banana", "mango", "orange", "fruit", "vegetable", "veg", "carrot", "onion", "potato", "tomato"],
        "coffee": ["coffee", "tea", "nescafe", "bru", "beverage", "green tea", "chai"],
    }

    def get_products_for_query(self, query: str, platforms: List[str]) -> List[Dict[str, Any]]:
        """
        Get relevant demo products based on search query.

        Args:
            query: Search query string
            platforms: List of platforms to include

        Returns:
            List of product dictionaries matching the query
        """
        query_lower = query.lower()

        # Determine which categories match the query
        matched_categories = []
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if any(keyword in query_lower for keyword in keywords):
                matched_categories.append(category)

        # If no specific category matched, return a mix of all
        if not matched_categories:
            matched_categories = list(self.DEMO_PRODUCTS.keys())

        # Collect products from matched categories
        products = []
        for category in matched_categories:
            products.extend(self.DEMO_PRODUCTS.get(category, []))

        # Filter by selected platforms
        platform_set = {p.lower() for p in platforms}
        filtered_products = []

        for product in products:
            # Filter offers by selected platforms
            filtered_offers = {}
            for platform, offer_data in product["offers"].items():
                if platform.lower() in platform_set:
                    filtered_offers[platform] = offer_data

            if filtered_offers:  # Only include if at least one selected platform has it
                product_copy = product.copy()
                product_copy["offers"] = filtered_offers
                filtered_products.append(product_copy)

        return filtered_products[:8]  # Limit to 8 results for demo

    def build_comparison(
        self, offers: Dict[str, Dict[str, Any]]
    ) -> ComparisonSchema:
        """
        Build comparison schema from platform offers.

        Args:
            offers: Dictionary of platform -> offer data

        Returns:
            ComparisonSchema with calculated metrics
        """
        available_offers = {
            p: o for p, o in offers.items() if o.get("available", True)
        }

        prices = [o["price"] for o in available_offers.values() if o.get("price")]
        delivery_times = [
            o["delivery_minutes"]
            for o in available_offers.values()
            if o.get("delivery_minutes")
        ]

        lowest_price = min(prices) if prices else None
        highest_price = max(prices) if prices else None
        price_difference = (
            highest_price - lowest_price
            if lowest_price and highest_price
            else None
        )
        potential_savings = price_difference

        cheapest_platform = (
            min(available_offers.items(), key=lambda x: x[1]["price"])[0]
            if available_offers
            else None
        )
        fastest_platform = (
            min(
                available_offers.items(),
                key=lambda x: x[1].get("delivery_minutes", 999),
            )[0]
            if available_offers
            else None
        )
        fastest_delivery_time = (
            min(delivery_times) if delivery_times else None
        )

        # Simple best overall: prioritize price, then delivery
        best_overall_platform = cheapest_platform
        best_overall_score = 100 - (lowest_price / 10 if lowest_price else 0)

        return ComparisonSchema(
            lowest_price=lowest_price,
            highest_price=highest_price,
            price_difference=price_difference,
            potential_savings=potential_savings,
            cheapest_platform=cheapest_platform,
            fastest_platform=fastest_platform,
            fastest_delivery_time=fastest_delivery_time,
            best_overall_platform=best_overall_platform,
            best_overall_score=best_overall_score,
            available_platforms=len(available_offers),
            total_platforms=len(offers),
        )

    def build_fallback_response(
        self,
        query: str,
        latitude: float,
        longitude: float,
        platforms: List[str],
        limit_reached: bool = False,
        location_info: Optional[Dict[str, Any]] = None,
    ) -> SearchResponseSchema:
        """
        Build a complete fallback search response.

        Args:
            query: Original search query
            latitude: Location latitude
            longitude: Location longitude
            platforms: Platforms that were searched
            limit_reached: Whether this is due to API limit (adds flag)
            location_info: Optional geocoded location information

        Returns:
            SearchResponseSchema with demo data
        """
        products = self.get_products_for_query(query, platforms)

        results = []
        for product in products:
            offers = product["offers"]

            # Build platform offer schemas
            offer_schemas = [
                PlatformOfferSchema(
                    platform=platform.title(),
                    price=offer["price"],
                    mrp=offer["mrp"],
                    discount=offer["discount"],
                    available=offer["available"],
                    delivery_time_minutes=offer["delivery_minutes"],
                    delivery_time_text=f"{offer['delivery_minutes']} mins",
                    product_url=f"https://{platform.lower()}.com/product",
                    image_url=None,
                )
                for platform, offer in offers.items()
            ]

            # Build comparison
            comparison = self.build_comparison(offers)

            # Build product result
            product_schema = ProductResultSchema(
                name=product["name"],
                brand=product.get("brand"),
                quantity=product.get("quantity"),
                unit=product.get("unit"),
                quantity_display=product.get("quantity_display"),
                image_url=product.get("image_url"),
                comparison=comparison,
                offers=offer_schemas,
            )

            results.append(product_schema)

        # Build location with geocoded info if available
        location = LocationSchema(
            latitude=latitude,
            longitude=longitude,
            city=location_info.get("city") if location_info else None,
            state=location_info.get("state") if location_info else None,
            country=location_info.get("country") if location_info else None,
            formatted_address=location_info.get("formatted_address") if location_info else None,
        )

        return SearchResponseSchema(
            query=query,
            location=location,
            platforms=platforms,
            total_results=len(results),
            results=results,
            demo=True,
            limit_reached=limit_reached,
            message="API key limit reached. Showing demo data for preview only." if limit_reached else "Showing demo data.",
        )
