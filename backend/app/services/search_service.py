"""
Search Service - Orchestrates the complete search flow

This service connects all components:
QuickCommerceClient → ProductNormalizer → ProductMatcher → ProductComparisonService → API Response

It handles the business logic for product search and comparison.
"""

import logging
from typing import List, Optional, Dict, Any

from app.api.client.quickcommerce_client import (
    QuickCommerceClient,
    QuickCommerceClientError,
    QuickCommerceTimeoutError,
    QuickCommerceAPIError,
)
from app.services.product_normalizer import ProductNormalizer
from app.services.product_matcher import ProductMatcher
from app.services.product_comparison import ProductComparisonService, ProductComparison
from app.schemas.product import Platform
from app.schemas.matching import MatchedProduct, MatchResult
from app.schemas.search import (
    SearchResponseSchema,
    ProductResultSchema,
    PlatformOfferSchema,
    ComparisonSchema,
    LocationSchema,
)

logger = logging.getLogger(__name__)


class SearchValidationError(Exception):
    """Exception raised for search validation errors"""
    pass


class SearchService:
    """
    Orchestrates the complete product search and comparison flow.

    Flow:
    1. Validate input parameters
    2. Call QuickCommerce API
    3. Normalize products from all platforms
    4. Match identical products across platforms
    5. Calculate comparison metrics
    6. Format API response
    """

    def __init__(
        self,
        quickcommerce_client: Optional[QuickCommerceClient] = None,
        normalizer: Optional[ProductNormalizer] = None,
        matcher: Optional[ProductMatcher] = None,
        comparison_service: Optional[ProductComparisonService] = None,
    ):
        """
        Initialize the search service with all required components.

        Args:
            quickcommerce_client: Client for QuickCommerce API
            normalizer: Product normalization service
            matcher: Product matching service
            comparison_service: Product comparison service
        """
        self.quickcommerce_client = quickcommerce_client or QuickCommerceClient()
        self.normalizer = normalizer or ProductNormalizer()
        self.matcher = matcher or ProductMatcher()
        self.comparison_service = comparison_service or ProductComparisonService()

    async def search(
        self,
        query: str,
        latitude: float,
        longitude: float,
        platforms: Optional[List[str]] = None,
    ) -> SearchResponseSchema:
        """
        Perform complete product search and comparison.

        Args:
            query: Search query
            latitude: Location latitude
            longitude: Location longitude
            platforms: Optional list of platforms to search

        Returns:
            SearchResponseSchema with matched products and comparisons

        Raises:
            SearchValidationError: For invalid input parameters
            QuickCommerceClientError: For API communication errors
        """
        # Validate input
        self._validate_search_params(query, latitude, longitude, platforms)

        # Validate that platforms are provided
        if not platforms:
            raise SearchValidationError("At least one platform must be selected")

        # Normalize platform names
        validated_platforms = self._validate_platforms(platforms)

        logger.info(f"Searching for '{query}' at location ({latitude}, {longitude})")

        try:
            # Step 1: Call QuickCommerce API
            api_response = await self.quickcommerce_client.group_search(
                query=query,
                latitude=latitude,
                longitude=longitude,
                platforms=validated_platforms,
            )

            # Step 2: Normalize products from API response
            normalized_products = self.normalizer.normalize_api_response(
                api_response=api_response,
                query=query,
            )

            logger.info(f"Normalized {len(normalized_products)} products")

            # Step 3: Match identical products across platforms
            match_result: MatchResult = self.matcher.match_products(normalized_products)

            logger.info(
                f"Matched into {match_result.total_matched_products} unique products "
                f"({match_result.products_with_multiple_offers} with multiple offers)"
            )

            # Step 4: Calculate comparisons for each matched product
            compared_products = []
            for matched_product in match_result.matched_products:
                comparison = self.comparison_service.compare_product(matched_product)
                compared_products.append((matched_product, comparison))

            # Step 5: Format API response
            return self._format_response(
                query=query,
                latitude=latitude,
                longitude=longitude,
                platforms=validated_platforms,
                compared_products=compared_products,
            )

        except QuickCommerceTimeoutError as e:
            logger.error(f"QuickCommerce API timeout: {e}")
            raise SearchValidationError("Search request timed out. Please try again.")
        except QuickCommerceAPIError as e:
            logger.error(f"QuickCommerce API error: {e}")
            raise SearchValidationError(f"External API error: {e}")
        except QuickCommerceClientError as e:
            logger.error(f"QuickCommerce client error: {e}")
            raise SearchValidationError(f"Search service error: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error during search: {e}")
            raise SearchValidationError(f"An unexpected error occurred: {str(e)}")

    def _validate_search_params(
        self,
        query: str,
        latitude: float,
        longitude: float,
        platforms: Optional[List[str]],
    ) -> None:
        """
        Validate search parameters.

        Raises:
            SearchValidationError: If parameters are invalid
        """
        if not query or not query.strip():
            raise SearchValidationError("Search query cannot be empty")

        if len(query.strip()) < 2:
            raise SearchValidationError("Search query must be at least 2 characters")

        if not (-90 <= latitude <= 90):
            raise SearchValidationError("Latitude must be between -90 and 90")

        if not (-180 <= longitude <= 180):
            raise SearchValidationError("Longitude must be between -180 and 180")

        if platforms is not None and len(platforms) == 0:
            raise SearchValidationError("At least one platform must be specified")

    def _validate_platforms(self, platforms: List[str]) -> List[str]:
        """
        Validate and normalize platform names.

        Args:
            platforms: List of platform names

        Returns:
            List of validated platform names

        Raises:
            SearchValidationError: If platform is not supported
        """
        validated = []
        supported = {p.value.lower(): p.value for p in Platform}

        for platform in platforms:
            # Normalize platform name (case-insensitive)
            platform_normalized = platform.strip().lower()

            if platform_normalized not in supported:
                raise SearchValidationError(
                    f"Unsupported platform: {platform}. "
                    f"Supported platforms: {', '.join(sorted(supported.values()))}"
                )

            validated.append(supported[platform_normalized])

        return validated

    def _format_response(
        self,
        query: str,
        latitude: float,
        longitude: float,
        platforms: List[str],
        compared_products: List[tuple[MatchedProduct, ProductComparison]],
    ) -> SearchResponseSchema:
        """
        Format the final API response.

        Args:
            query: Original search query
            latitude: Location latitude
            longitude: Location longitude
            platforms: Platforms that were searched
            compared_products: List of (matched_product, comparison) tuples

        Returns:
            Formatted SearchResponseSchema
        """
        location = LocationSchema(latitude=latitude, longitude=longitude)

        results = []
        for matched_product, comparison in compared_products:
            # Convert platform offers to API schema
            offers_schemas = [
                PlatformOfferSchema(
                    platform=offer.platform.value,
                    price=offer.price,
                    mrp=offer.mrp,
                    discount=offer.discount,
                    available=offer.available,
                    delivery_time_minutes=offer.delivery_time_minutes,
                    delivery_time_text=offer.delivery_time_text,
                    product_url=offer.product_url,
                    image_url=offer.image_url,
                )
                for offer in matched_product.offers
            ]

            # Convert comparison to API schema
            comparison_schema = ComparisonSchema(
                lowest_price=comparison.lowest_price,
                highest_price=comparison.highest_price,
                price_difference=comparison.price_difference,
                potential_savings=comparison.potential_savings,
                cheapest_platform=comparison.cheapest_platform.value if comparison.cheapest_platform else None,
                fastest_platform=comparison.fastest_platform.value if comparison.fastest_platform else None,
                fastest_delivery_time=comparison.fastest_delivery_time,
                best_overall_platform=comparison.best_overall_platform.value if comparison.best_overall_platform else None,
                best_overall_score=comparison.best_overall_score,
                available_platforms=comparison.available_platforms,
                total_platforms=comparison.total_platforms,
            )

            # Create product result
            product_schema = ProductResultSchema(
                name=matched_product.canonical_name,
                brand=matched_product.brand.title() if matched_product.brand else None,
                quantity=matched_product.quantity,
                unit=matched_product.unit.value if matched_product.unit else None,
                quantity_display=matched_product.quantity_display,
                image_url=matched_product.image_url,
                comparison=comparison_schema,
                offers=offers_schemas,
            )

            results.append(product_schema)

        return SearchResponseSchema(
            query=query,
            location=location,
            platforms=platforms,
            total_results=len(results),
            results=results,
        )
