"""
Integration tests for SearchService (PHASE 5)

These tests verify the complete search flow using mocked QuickCommerce API responses.
No real API calls are made - all external responses are mocked to avoid consuming credits.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.services.search_service import SearchService, SearchValidationError
from app.api.client.quickcommerce_client import (
    QuickCommerceClient,
    QuickCommerceTimeoutError,
    QuickCommerceAPIError,
)
from app.services.product_normalizer import ProductNormalizer
from app.services.product_matcher import ProductMatcher
from app.services.product_comparison import ProductComparisonService
from app.schemas.search import SearchResponseSchema


# Mock QuickCommerce API response for milk search
MOCK_MILK_API_RESPONSE = {
    "status": "success",
    "data": {
        "credit_cost": 1,
        "results": {
            "Zepto": [
                {
                    "id": "z_milk_1",
                    "name": "Amul Taaza Toned Milk 500ml",
                    "offer_price": 28,
                    "mrp": 30,
                    "available": True,
                    "platform": {
                        "sla": "10 mins",
                        "image_url": "https://example.com/zepto-milk.jpg",
                    },
                    "product_url": "https://zepto.com/p/amul-milk",
                }
            ],
            "BlinkIt": [
                {
                    "id": "b_milk_1",
                    "name": "Amul Taaza Toned Milk 500ml",
                    "offer_price": 29,
                    "mrp": 31,
                    "available": True,
                    "platform": {
                        "sla": "8 mins",
                        "image_url": "https://example.com/blinkit-milk.jpg",
                    },
                    "product_url": "https://blinkit.com/p/amul-milk",
                }
            ],
            "Swiggy": [
                {
                    "id": "s_milk_1",
                    "name": "Amul Taaza Toned Milk 500ml",
                    "offer_price": 30,
                    "mrp": 32,
                    "available": True,
                    "platform": {
                        "sla": "15 mins",
                        "image_url": "https://example.com/swiggy-milk.jpg",
                    },
                    "product_url": "https://swiggy.com/p/amul-milk",
                }
            ],
        },
    },
}


# Mock response with multiple different products
MOCK_MULTIPLE_PRODUCTS_RESPONSE = {
    "status": "success",
    "data": {
        "credit_cost": 1,
        "results": {
            "Zepto": [
                {
                    "id": "z_milk_1",
                    "name": "Amul Taaza Toned Milk 500ml",
                    "offer_price": 28,
                    "mrp": 30,
                    "available": True,
                    "platform": {"sla": "10 mins"},
                },
                {
                    "id": "z_bread_1",
                    "name": "Britannia Toast Bread 400g",
                    "offer_price": 45,
                    "mrp": 50,
                    "available": True,
                    "platform": {"sla": "12 mins"},
                },
            ],
            "BlinkIt": [
                {
                    "id": "b_milk_1",
                    "name": "Amul Taaza Toned Milk 500ml",
                    "offer_price": 29,
                    "mrp": 31,
                    "available": True,
                    "platform": {"sla": "8 mins"},
                },
                {
                    "id": "b_bread_1",
                    "name": "Britannia Toast Bread 400g",
                    "offer_price": 44,
                    "mrp": 49,
                    "available": True,
                    "platform": {"sla": "10 mins"},
                },
            ],
        },
    },
}


# Mock empty response
MOCK_EMPTY_RESPONSE = {
    "status": "success",
    "data": {
        "credit_cost": 0,
        "results": {
            "Zepto": [],
            "BlinkIt": [],
            "Swiggy": [],
        },
    },
}


# Mock error response
MOCK_ERROR_RESPONSE = {
    "status": "error",
    "message": "Invalid API key",
}


class TestSearchServiceSuccess:
    """Test successful search scenarios"""

    @pytest.fixture
    def search_service(self):
        """Create SearchService with mocked QuickCommerce client"""
        mock_client = Mock(spec=QuickCommerceClient)
        mock_client.group_search = AsyncMock(return_value=MOCK_MILK_API_RESPONSE)

        return SearchService(quickcommerce_client=mock_client)

    @pytest.mark.asyncio
    async def test_successful_milk_search(self, search_service):
        """Test successful milk search returns matched products"""
        result = await search_service.search(
            query="milk",
            latitude=13.0827,
            longitude=80.2707,
            platforms=["Zepto", "BlinkIt", "Swiggy"],
        )

        assert isinstance(result, SearchResponseSchema)
        assert result.query == "milk"
        assert result.location.latitude == 13.0827
        assert result.location.longitude == 80.2707
        assert len(result.platforms) == 3
        assert result.total_results == 1

        # Check the matched product
        product = result.results[0]
        assert "Amul" in product.name or "milk" in product.name.lower()
        assert product.brand == "Amul"
        assert product.quantity == 500
        assert product.unit == "ml"

    @pytest.mark.asyncio
    async def test_multiple_platforms_returned(self, search_service):
        """Test that offers from all platforms are returned"""
        result = await search_service.search(
            query="milk",
            latitude=13.0827,
            longitude=80.2707,
            platforms=["Zepto", "BlinkIt", "Swiggy"],
        )

        product = result.results[0]
        assert len(product.offers) == 3

        platforms = {offer.platform for offer in product.offers}
        assert platforms == {"Zepto", "BlinkIt", "Swiggy"}

    @pytest.mark.asyncio
    async def test_same_product_matched_across_platforms(self, search_service):
        """Test that same product from different platforms is matched correctly"""
        result = await search_service.search(
            query="milk",
            latitude=13.0827,
            longitude=80.2707,
            platforms=["Zepto", "BlinkIt", "Swiggy"],
        )

        # Should have 1 matched product (not 3 separate ones)
        assert result.total_results == 1

        product = result.results[0]
        assert len(product.offers) == 3  # 3 platforms

    @pytest.mark.asyncio
    async def test_cheapest_platform_correctly_returned(self, search_service):
        """Test that cheapest platform is correctly identified"""
        result = await search_service.search(
            query="milk",
            latitude=13.0827,
            longitude=80.2707,
            platforms=["Zepto", "BlinkIt", "Swiggy"],
        )

        product = result.results[0]
        assert product.comparison.cheapest_platform == "Zepto"  # Price: 28
        assert product.comparison.lowest_price == 28.0
        assert product.comparison.highest_price == 30.0

    @pytest.mark.asyncio
    async def test_fastest_platform_correctly_returned(self, search_service):
        """Test that fastest platform is correctly identified"""
        result = await search_service.search(
            query="milk",
            latitude=13.0827,
            longitude=80.2707,
            platforms=["Zepto", "BlinkIt", "Swiggy"],
        )

        product = result.results[0]
        assert product.comparison.fastest_platform == "BlinkIt"  # 8 mins
        assert product.comparison.fastest_delivery_time is not None

    @pytest.mark.asyncio
    async def test_best_overall_platform_calculated(self, search_service):
        """Test that best overall platform is calculated"""
        result = await search_service.search(
            query="milk",
            latitude=13.0827,
            longitude=80.2707,
            platforms=["Zepto", "BlinkIt", "Swiggy"],
        )

        product = result.results[0]
        # Best overall should be one of the platforms
        assert product.comparison.best_overall_platform in ["Zepto", "BlinkIt", "Swiggy"]
        assert product.comparison.best_overall_score is not None
        assert product.comparison.best_overall_score > 0

    @pytest.mark.asyncio
    async def test_multiple_products_search(self):
        """Test search with multiple different products"""
        mock_client = Mock(spec=QuickCommerceClient)
        mock_client.group_search = AsyncMock(return_value=MOCK_MULTIPLE_PRODUCTS_RESPONSE)

        service = SearchService(quickcommerce_client=mock_client)

        result = await service.search(
            query="groceries",
            latitude=13.0827,
            longitude=80.2707,
            platforms=["Zepto", "BlinkIt"],
        )

        # Should have 2 matched products (milk and bread)
        assert result.total_results == 2
        assert len(result.results) == 2


class TestSearchServiceValidation:
    """Test input validation"""

    @pytest.fixture
    def search_service(self):
        mock_client = Mock(spec=QuickCommerceClient)
        mock_client.group_search = AsyncMock(return_value=MOCK_MILK_API_RESPONSE)
        return SearchService(quickcommerce_client=mock_client)

    @pytest.mark.asyncio
    async def test_empty_search_query_rejected(self, search_service):
        """Test that empty search query is rejected"""
        with pytest.raises(SearchValidationError, match="cannot be empty"):
            await search_service.search(
                query="",
                latitude=13.0827,
                longitude=80.2707,
            )

    @pytest.mark.asyncio
    async def test_short_search_query_rejected(self, search_service):
        """Test that search query under 2 characters is rejected"""
        with pytest.raises(SearchValidationError, match="at least 2 characters"):
            await search_service.search(
                query="a",
                latitude=13.0827,
                longitude=80.2707,
            )

    @pytest.mark.asyncio
    async def test_invalid_latitude_rejected(self, search_service):
        """Test that invalid latitude is rejected"""
        with pytest.raises(SearchValidationError, match="Latitude must be between"):
            await search_service.search(
                query="milk",
                latitude=91,
                longitude=80.2707,
            )

    @pytest.mark.asyncio
    async def test_invalid_longitude_rejected(self, search_service):
        """Test that invalid longitude is rejected"""
        with pytest.raises(SearchValidationError, match="Longitude must be between"):
            await search_service.search(
                query="milk",
                latitude=13.0827,
                longitude=181,
            )

    @pytest.mark.asyncio
    async def test_unsupported_platform_rejected(self, search_service):
        """Test that unsupported platform is rejected"""
        with pytest.raises(SearchValidationError, match="Unsupported platform"):
            await search_service.search(
                query="milk",
                latitude=13.0827,
                longitude=80.2707,
                platforms=["InvalidPlatform"],
            )


class TestSearchServiceErrors:
    """Test error handling"""

    @pytest.mark.asyncio
    async def test_empty_search_results(self):
        """Test handling of empty search results"""
        mock_client = Mock(spec=QuickCommerceClient)
        mock_client.group_search = AsyncMock(return_value=MOCK_EMPTY_RESPONSE)

        service = SearchService(quickcommerce_client=mock_client)

        result = await service.search(
            query="nonexistent",
            latitude=13.0827,
            longitude=80.2707,
            platforms=["Zepto", "BlinkIt", "Swiggy"],
        )

        assert result.total_results == 0
        assert len(result.results) == 0

    @pytest.mark.asyncio
    async def test_external_api_timeout(self):
        """Test handling of API timeout"""
        mock_client = Mock(spec=QuickCommerceClient)
        mock_client.group_search = AsyncMock(
            side_effect=QuickCommerceTimeoutError("Request timed out")
        )

        service = SearchService(quickcommerce_client=mock_client)

        with pytest.raises(SearchValidationError, match="timed out|Search request timed out"):
            await service.search(
                query="milk",
                latitude=13.0827,
                longitude=80.2707,
                platforms=["Zepto"],  # Use valid platform
            )

    @pytest.mark.asyncio
    async def test_external_api_failure(self):
        """Test handling of API failure"""
        mock_client = Mock(spec=QuickCommerceClient)
        mock_client.group_search = AsyncMock(
            side_effect=QuickCommerceAPIError("API error", status_code=500)
        )

        service = SearchService(quickcommerce_client=mock_client)

        with pytest.raises(SearchValidationError, match="External API error|Search service error"):
            await service.search(
                query="milk",
                latitude=13.0827,
                longitude=80.2707,
                platforms=["Zepto"],  # Use valid platform
            )


class TestSearchServiceEdgeCases:
    """Test edge cases and partial failures"""

    @pytest.mark.asyncio
    async def test_missing_product_fields(self):
        """Test handling of products with missing fields"""
        # Response with missing optional fields
        response_with_missing = {
            "status": "success",
            "data": {
                "credit_cost": 1,
                "results": {
                    "Zepto": [
                        {
                            "id": "z_milk_1",
                            "name": "Amul Milk",
                            # Missing offer_price, mrp, etc.
                            "available": True,
                            "platform": {},
                        }
                    ],
                },
            },
        }

        mock_client = Mock(spec=QuickCommerceClient)
        mock_client.group_search = AsyncMock(return_value=response_with_missing)

        service = SearchService(quickcommerce_client=mock_client)

        result = await service.search(
            query="milk",
            latitude=13.0827,
            longitude=80.2707,
            platforms=["Zepto"],
        )

        # Should handle missing fields gracefully
        assert isinstance(result, SearchResponseSchema)

    @pytest.mark.asyncio
    async def test_custom_platforms(self):
        """Test search with custom platform selection"""
        mock_client = Mock(spec=QuickCommerceClient)

        # Response with only Zepto results
        zepto_only_response = {
            "status": "success",
            "data": {
                "credit_cost": 1,
                "results": {
                    "Zepto": [
                        {
                            "id": "z_milk_1",
                            "name": "Amul Milk",
                            "offer_price": 28,
                            "available": True,
                            "platform": {"sla": "10 mins"},
                        }
                    ],
                },
            },
        }

        mock_client.group_search = AsyncMock(return_value=zepto_only_response)

        service = SearchService(quickcommerce_client=mock_client)

        result = await service.search(
            query="milk",
            latitude=13.0827,
            longitude=80.2707,
            platforms=["Zepto"],
        )

        # Should only search Zepto
        assert "Zepto" in result.platforms
        assert len(result.results) >= 0

    @pytest.mark.asyncio
    async def test_case_insensitive_platform_names(self):
        """Test that platform names are case-insensitive"""
        mock_client = Mock(spec=QuickCommerceClient)
        mock_client.group_search = AsyncMock(return_value=MOCK_MILK_API_RESPONSE)

        service = SearchService(quickcommerce_client=mock_client)

        # Test lowercase platform names
        result = await service.search(
            query="milk",
            latitude=13.0827,
            longitude=80.2707,
            platforms=["zepto", "blinkit"],
        )

        # Should normalize to proper casing
        assert "Zepto" in result.platforms
        assert "BlinkIt" in result.platforms

        # The platforms list should have the properly cased versions
        assert "zepto" not in result.platforms
        assert "blinkit" not in result.platforms


class TestSearchResponseStructure:
    """Test API response structure matches specification"""

    @pytest.fixture
    def search_service(self):
        mock_client = Mock(spec=QuickCommerceClient)
        mock_client.group_search = AsyncMock(return_value=MOCK_MILK_API_RESPONSE)
        return SearchService(quickcommerce_client=mock_client)

    @pytest.mark.asyncio
    async def test_response_has_all_required_fields(self, search_service):
        """Test that response contains all required fields"""
        result = await search_service.search(
            query="milk",
            latitude=13.0827,
            longitude=80.2707,
        )

        # Top-level fields
        assert hasattr(result, "query")
        assert hasattr(result, "location")
        assert hasattr(result, "platforms")
        assert hasattr(result, "total_results")
        assert hasattr(result, "results")

        # Location fields
        assert hasattr(result.location, "latitude")
        assert hasattr(result.location, "longitude")

    @pytest.mark.asyncio
    async def test_product_result_has_all_required_fields(self, search_service):
        """Test that product result contains all required fields"""
        result = await search_service.search(
            query="milk",
            latitude=13.0827,
            longitude=80.2707,
        )

        product = result.results[0]

        # Product fields
        assert hasattr(product, "name")
        assert hasattr(product, "brand")
        assert hasattr(product, "quantity")
        assert hasattr(product, "unit")
        assert hasattr(product, "comparison")
        assert hasattr(product, "offers")

    @pytest.mark.asyncio
    async def test_comparison_schema_has_all_metrics(self, search_service):
        """Test that comparison schema contains all metrics"""
        result = await search_service.search(
            query="milk",
            latitude=13.0827,
            longitude=80.2707,
        )

        comparison = result.results[0].comparison

        # Comparison fields
        assert hasattr(comparison, "lowest_price")
        assert hasattr(comparison, "highest_price")
        assert hasattr(comparison, "potential_savings")
        assert hasattr(comparison, "cheapest_platform")
        assert hasattr(comparison, "fastest_platform")
        assert hasattr(comparison, "best_overall_platform")
        assert hasattr(comparison, "available_platforms")
        assert hasattr(comparison, "total_platforms")

    @pytest.mark.asyncio
    async def test_offer_schema_has_all_required_fields(self, search_service):
        """Test that offer schema contains all required fields"""
        result = await search_service.search(
            query="milk",
            latitude=13.0827,
            longitude=80.2707,
        )

        offer = result.results[0].offers[0]

        # Offer fields
        assert hasattr(offer, "platform")
        assert hasattr(offer, "price")
        assert hasattr(offer, "available")
        assert hasattr(offer, "delivery_time_minutes")
