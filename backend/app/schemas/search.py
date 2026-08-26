"""
Search API Response Schemas

These schemas define the public API response format for the search endpoint.
They are what the frontend will consume.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class LocationSchema(BaseModel):
    """Location information"""
    latitude: float = Field(description="Location latitude")
    longitude: float = Field(description="Location longitude")
    city: Optional[str] = Field(default=None, description="City name")
    state: Optional[str] = Field(default=None, description="State name")
    country: Optional[str] = Field(default=None, description="Country name")
    formatted_address: Optional[str] = Field(default=None, description="Human-readable location")


class PlatformOfferSchema(BaseModel):
    """Platform offer information"""
    platform: str = Field(description="Platform name")
    price: Optional[float] = Field(default=None, description="Current price")
    mrp: Optional[float] = Field(default=None, description="Maximum retail price")
    discount: Optional[float] = Field(default=None, description="Discount amount")
    available: bool = Field(default=True, description="Product availability")
    delivery_time_minutes: Optional[int] = Field(default=None, description="Delivery time in minutes")
    delivery_time_text: Optional[str] = Field(default=None, description="Raw delivery time string")
    product_url: Optional[str] = Field(default=None, description="Product URL")
    image_url: Optional[str] = Field(default=None, description="Product image URL")


class ComparisonSchema(BaseModel):
    """Comparison metrics for a product"""
    lowest_price: Optional[float] = Field(default=None, description="Lowest price across platforms")
    highest_price: Optional[float] = Field(default=None, description="Highest price across platforms")
    price_difference: Optional[float] = Field(default=None, description="Price difference")
    potential_savings: Optional[float] = Field(default=None, description="Potential savings vs highest price")
    cheapest_platform: Optional[str] = Field(default=None, description="Platform with lowest price")
    fastest_platform: Optional[str] = Field(default=None, description="Platform with fastest delivery")
    fastest_delivery_time: Optional[int] = Field(default=None, description="Fastest delivery time in minutes")
    best_overall_platform: Optional[str] = Field(default=None, description="Best overall platform by scoring")
    best_overall_score: Optional[float] = Field(default=None, description="Best overall platform score")
    available_platforms: int = Field(default=0, description="Number of platforms with this product")
    total_platforms: int = Field(default=0, description="Total number of platforms")


class ProductResultSchema(BaseModel):
    """A single product in search results"""
    name: str = Field(description="Product name")
    brand: Optional[str] = Field(default=None, description="Brand name")
    quantity: Optional[float] = Field(default=None, description="Quantity value")
    unit: Optional[str] = Field(default=None, description="Quantity unit")
    quantity_display: Optional[str] = Field(default=None, description="Human-readable quantity")
    image_url: Optional[str] = Field(default=None, description="Product image URL")
    comparison: ComparisonSchema = Field(description="Comparison metrics")
    offers: List[PlatformOfferSchema] = Field(description="Platform offers")


class SearchResponseSchema(BaseModel):
    """Complete search response"""
    query: str = Field(description="Original search query")
    location: LocationSchema = Field(description="Search location")
    platforms: List[str] = Field(description="Platforms that were searched")
    total_results: int = Field(description="Total number of matched products")
    results: List[ProductResultSchema] = Field(description="Matched products with comparison")
    demo: bool = Field(default=False, description="Whether this is demo/fallback data")
    limit_reached: bool = Field(default=False, description="Whether API key limit was reached")
    message: Optional[str] = Field(default=None, description="Optional message about data source")


class SearchErrorResponse(BaseModel):
    """Error response for search endpoint"""
    error: str = Field(description="Error type")
    message: str = Field(description="Error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")
