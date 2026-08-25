"""
Search API Routes

FastAPI routes for product search and comparison.
"""

import logging
from typing import Optional, List
from fastapi import APIRouter, Query, HTTPException, status

from app.services.search_service import SearchService, SearchValidationError
from app.schemas.search import SearchResponseSchema, SearchErrorResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["search"])


# Initialize search service (will be injected in production via dependency injection)
search_service = SearchService()


@router.get("/search", response_model=SearchResponseSchema)
async def search_products(
    q: str = Query(..., min_length=2, description="Search query"),
    latitude: float = Query(..., ge=-90, le=90, description="Location latitude"),
    longitude: float = Query(..., ge=-180, le=180, description="Location longitude"),
    platforms: str = Query(..., description="Comma-separated platform names (required - at least one)"),
) -> SearchResponseSchema:
    """
    Search for products across quick-commerce platforms.

    This endpoint searches for products and compares prices, delivery times,
    and availability across selected platforms.

    ## Parameters
    - **q**: Search query (e.g., "milk", "bread", "amul")
    - **latitude**: Location latitude (Chennai: ~13.08)
    - **longitude**: Location longitude (Chennai: ~80.27)
    - **platforms**: Required comma-separated platforms (at least one must be selected)

    ## Returns
    Matched products with:
    - Canonical product information
    - Platform-specific offers
    - Price comparisons
    - Delivery time comparisons
    - Best overall platform recommendations

    ## Example
    ```
    GET /api/v1/search?q=milk&latitude=13.0827&longitude=80.2707
    ```
    """
    # Parse platforms parameter
    platform_list = None
    if platforms:
        platform_list = [p.strip() for p in platforms.split(",")]

    try:
        result = await search_service.search(
            query=q,
            latitude=latitude,
            longitude=longitude,
            platforms=platform_list,
        )

        return result

    except SearchValidationError as e:
        logger.warning(f"Search validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except Exception as e:
        logger.exception(f"Unexpected error in search endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later.",
        )


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "product-comparison-api",
        "version": "1.0.0"
    }
