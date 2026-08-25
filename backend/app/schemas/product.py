"""
Normalized product schemas

This module defines our internal product schema that abstracts away
differences between BlinkIt, Zepto, Swiggy, and other platforms.

All external API responses are normalized to these schemas.
"""

from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum


class Platform(str, Enum):
    """Supported quick-commerce platforms"""

    BLINKIT = "BlinkIt"
    ZEPTO = "Zepto"
    SWIGGY = "Swiggy"
    BIGBASKET = "BigBasket"
    DMART = "DMart"
    JIOMART = "JioMart"
    MINUTES = "Minutes"
    AMAZON = "Amazon"
    NYKAA = "Nykaa"
    MYNTRA = "Myntra"
    FLIPKART = "Flipkart"


class Unit(str, Enum):
    """Standardized product units"""

    GRAM = "g"
    KILOGRAM = "kg"
    MILLILITER = "ml"
    LITER = "l"
    PIECE = "pc"
    PACK = "pack"
    DOZEN = "doz"
    UNIT = "unit"


class PlatformOffer(BaseModel):
    """
    A single product offering from a specific platform.

    This represents how a product is listed on one platform.
    """

    platform: Platform = Field(description="Platform name")
    platform_product_id: str = Field(description="Product ID on this platform")

    # Price information
    price: Optional[float] = Field(default=None, description="Current selling price")
    mrp: Optional[float] = Field(default=None, description="Maximum Retail Price")
    discount: Optional[float] = Field(default=None, description="Discount amount (MRP - price)")

    # Availability
    available: bool = Field(default=True, description="Whether product is currently available")

    # Delivery
    delivery_time_minutes: Optional[int] = Field(default=None, description="Estimated delivery time in minutes")
    delivery_time_text: Optional[str] = Field(default=None, description="Raw delivery time string from platform")

    # Links
    product_url: Optional[str] = Field(default=None, description="Deep link to product on platform")
    image_url: Optional[str] = Field(default=None, description="Product image URL")

    # Metadata
    raw_data: Optional[dict] = Field(default=None, exclude=True, description="Raw API response for debugging")

    @field_validator("price", "mrp", "discount", mode="before")
    @classmethod
    def parse_float(cls, v):
        """Parse string/float values safely"""
        if v is None:
            return None
        if isinstance(v, (int, float)):
            return float(v)
        if isinstance(v, str):
            # Remove currency symbols, commas, whitespace
            cleaned = (
                v.replace("₹", "")
                .replace("Rs.", "")
                .replace("INR", "")
                .replace(",", "")
                .strip()
            )
            if cleaned == "":
                return None
            try:
                result = float(cleaned)
                return result  # Return result even if 0
            except ValueError:
                return None
        return None

    @model_validator(mode="after")
    def calculate_discount(self):
        """Calculate discount if not provided"""
        if self.discount is None and self.mrp is not None and self.price is not None:
            self.discount = max(0, self.mrp - self.price)
        return self


class NormalizedProduct(BaseModel):
    """
    Our internal product schema with normalized fields.

    A single logical product can have multiple PlatformOffers
    from different platforms.

    Example:
        "Amul Taaza Toned Milk 500ml" might have offers from:
        - BlinkIt (₹28, 10 min)
        - Zepto (₹27, 8 min)
        - Swiggy (₹29, 12 min)
    """

    # Core identity
    product_id: str = Field(description="Internal product ID (generated)")
    name: str = Field(description="Product name (normalized)")
    brand: Optional[str] = Field(default=None, description="Brand name (extracted)")
    category: Optional[str] = Field(default=None, description="Product category")

    # Quantity information
    quantity: Optional[float] = Field(default=None, description="Numeric quantity value")
    unit: Optional[Unit] = Field(default=None, description="Standardized unit")
    quantity_display: Optional[str] = Field(default=None, description="Human-readable quantity string")

    # Visual
    image_url: Optional[str] = Field(default=None, description="Primary product image")

    # Platform offerings - the key comparison data
    offers: List[PlatformOffer] = Field(default_factory=list, description="Platform-specific offerings")

    # Comparison metadata (computed)
    available_on_platforms: int = Field(default=0, description="Number of platforms with this product")
    lowest_price: Optional[float] = Field(default=None, description="Lowest price across all platforms")
    highest_price: Optional[float] = Field(default=None, description="Highest price across all platforms")
    price_difference: Optional[float] = Field(default=None, description="Difference between highest and lowest price")

    @field_validator("quantity", mode="before")
    @classmethod
    def parse_quantity(cls, v):
        """Parse quantity from string/float"""
        if v is None:
            return None
        if isinstance(v, (int, float)):
            return float(v)
        if isinstance(v, str):
            try:
                return float(v)
            except ValueError:
                return None
        return None

    def add_offer(self, offer: PlatformOffer) -> None:
        """Add a platform offer and update comparison metadata"""
        self.offers.append(offer)

        # Update comparison metadata
        self._update_comparison_data()

    def _update_comparison_data(self) -> None:
        """Recalculate comparison metadata from current offers"""
        if not self.offers:
            return

        # Count available platforms
        self.available_on_platforms = sum(1 for o in self.offers if o.available)

        # Find price range
        available_prices = [o.price for o in self.offers if o.available and o.price is not None]

        if available_prices:
            self.lowest_price = min(available_prices)
            self.highest_price = max(available_prices)
            self.price_difference = self.highest_price - self.lowest_price

    def get_cheapest_offer(self) -> Optional[PlatformOffer]:
        """Get the offer with the lowest price"""
        available_offers = [o for o in self.offers if o.available and o.price is not None]
        if not available_offers:
            return None
        return min(available_offers, key=lambda o: o.price)

    def get_fastest_offer(self) -> Optional[PlatformOffer]:
        """Get the offer with fastest delivery"""
        available_offers = [
            o for o in self.offers if o.available and o.delivery_time_minutes is not None
        ]
        if not available_offers:
            return None
        return min(available_offers, key=lambda o: o.delivery_time_minutes)

    def get_offer_by_platform(self, platform: Platform) -> Optional[PlatformOffer]:
        """Get offer from a specific platform"""
        for offer in self.offers:
            if offer.platform == platform:
                return offer
        return None


class ProductList(BaseModel):
    """Container for a list of products with metadata"""

    query: str = Field(description="Original search query")
    total: int = Field(description="Total number of products")
    products: List[NormalizedProduct] = Field(description="List of normalized products")

    # Search metadata
    platforms_searched: List[Platform] = Field(description="Platforms that were searched")
    location: Optional["SearchLocation"] = Field(default=None, description="Search location")


class SearchLocation(BaseModel):
    """Location information for search"""

    latitude: float
    longitude: float
    city: Optional[str] = None
    pincode: Optional[str] = None


# Update forward reference
ProductList.model_rebuild()
