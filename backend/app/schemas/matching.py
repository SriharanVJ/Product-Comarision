"""
Product matching schemas

This module defines schemas for matched products - products that have been
identified as the same across multiple platforms.
"""

from typing import Optional, List, Dict, Set
from pydantic import BaseModel, Field

from app.schemas.product import PlatformOffer, Platform, Unit


class ProductMatchKey(BaseModel):
    """
    The canonical key used to match products across platforms.

    Two products match if they have the same:
    - Brand (normalized)
    - Base name (normalized, variant-agnostic)
    - Variant attributes (toned, full cream, organic, etc.)
    - Equivalent quantity/unit
    """

    brand: Optional[str] = Field(default=None, description="Normalized brand name")
    base_name: str = Field(description="Product name without variant qualifiers")
    variants: Set[str] = Field(default_factory=set, description="Product variant attributes")
    quantity: Optional[float] = Field(default=None, description="Normalized quantity")
    unit: Optional[Unit] = Field(default=None, description="Normalized unit")

    def __hash__(self) -> int:
        """Make hashable for use as dict key"""
        brand_key = (self.brand or "").lower().strip()
        base_name_key = self.base_name.lower().strip()
        variants_key = ",".join(sorted(self.variants))
        quantity_key = f"{self.quantity or 0}:{self.unit or ''}"
        return hash((brand_key, base_name_key, variants_key, quantity_key))

    def __eq__(self, other: object) -> bool:
        """Compare match keys"""
        if not isinstance(other, ProductMatchKey):
            return False
        return (
            (self.brand or "").lower().strip() == (other.brand or "").lower().strip()
            and self.base_name.lower().strip() == other.base_name.lower().strip()
            and self.variants == other.variants
            and self.quantity == other.quantity
            and self.unit == other.unit
        )

    def to_string(self) -> str:
        """Convert to string for debugging"""
        brand_str = self.brand or "Unknown"
        variants_str = " ".join(sorted(self.variants)) if self.variants else ""
        qty_str = f"{self.quantity}{self.unit.value if self.unit else ''}" if self.quantity else ""
        return f"{brand_str} {self.base_name} {variants_str} {qty_str}".strip()


class MatchedProduct(BaseModel):
    """
    A product that has been matched across multiple platforms.

    This is the canonical product representation used by the comparison engine.
    It combines all platform offers for the same logical product.
    """

    # Canonical identity (from match key)
    match_key: ProductMatchKey = Field(description="Key used to match this product")

    # Display information (from first offer, can be enhanced later)
    canonical_name: str = Field(description="Canonical product name for display")
    brand: Optional[str] = Field(default=None, description="Brand name")
    category: Optional[str] = Field(default=None, description="Product category")

    # Quantity information
    quantity: Optional[float] = Field(default=None, description="Quantity value")
    unit: Optional[Unit] = Field(default=None, description="Unit")
    quantity_display: Optional[str] = Field(default=None, description="Human-readable quantity")

    # Visual
    image_url: Optional[str] = Field(default=None, description="Product image URL")

    # Platform offers
    offers: List[PlatformOffer] = Field(default_factory=list, description="All platform offers")

    # Source tracking
    source_product_ids: Set[str] = Field(
        default_factory=set,
        description="IDs of source products that were matched",
    )

    # Comparison metadata
    available_platforms: int = Field(default=0, description="Number of platforms with this product")
    lowest_price: Optional[float] = Field(default=None, description="Lowest price across platforms")
    highest_price: Optional[float] = Field(default=None, description="Highest price across platforms")
    price_difference: Optional[float] = Field(default=None, description="Price difference")
    cheapest_platform: Optional[Platform] = Field(default=None, description="Platform with lowest price")
    fastest_platform: Optional[Platform] = Field(default=None, description="Platform with fastest delivery")

    def add_offer(self, offer: PlatformOffer, source_product_id: str = "") -> None:
        """Add an offer and update metadata"""
        # Check for duplicate platform
        if any(o.platform == offer.platform for o in self.offers):
            return  # Skip duplicate from same platform

        self.offers.append(offer)
        if source_product_id:
            self.source_product_ids.add(source_product_id)

        self._update_comparison_data()

    def _update_comparison_data(self) -> None:
        """Recalculate comparison metadata"""
        if not self.offers:
            return

        # Count available platforms
        self.available_platforms = len(self.offers)

        # Find price range
        prices = [o.price for o in self.offers if o.price is not None]
        if prices:
            self.lowest_price = min(prices)
            self.highest_price = max(prices)
            self.price_difference = self.highest_price - self.lowest_price

            # Find cheapest platform
            for offer in self.offers:
                if offer.price == self.lowest_price:
                    self.cheapest_platform = offer.platform
                    break

        # Find fastest platform
        delivery_times = [
            (o.platform, o.delivery_time_minutes)
            for o in self.offers
            if o.delivery_time_minutes is not None
        ]
        if delivery_times:
            fastest_platform, fastest_time = min(delivery_times, key=lambda x: x[1])
            self.fastest_platform = fastest_platform

    def get_offer_by_platform(self, platform: Platform) -> Optional[PlatformOffer]:
        """Get offer from specific platform"""
        for offer in self.offers:
            if offer.platform == platform:
                return offer
        return None

    def has_offer_from(self, platform: Platform) -> bool:
        """Check if product is available on platform"""
        return any(o.platform == platform for o in self.offers)


class MatchResult(BaseModel):
    """
    Result of product matching operation.

    Contains statistics about the matching process.
    """

    total_input_products: int = Field(description="Number of products input")
    total_matched_products: int = Field(
        default=0,
        description="Number of unique matched products"
    )
    products_with_multiple_offers: int = Field(
        default=0,
        description="Products available on multiple platforms",
    )
    products_with_single_offer: int = Field(
        default=0,
        description="Products available on only one platform",
    )
    duplicate_skipped: int = Field(default=0, description="Duplicate offers skipped")
    matched_products: List[MatchedProduct] = Field(
        default_factory=list,
        description="Final matched products"
    )

    match_rate: float = Field(
        default=0.0,
        description="Percentage of products that matched across platforms",
    )

    def calculate_statistics(self) -> None:
        """Calculate derived statistics"""
        if self.total_input_products == 0:
            self.match_rate = 0.0
            return

        # Count products with multiple vs single offers
        self.products_with_multiple_offers = sum(
            1 for p in self.matched_products if len(p.offers) > 1
        )
        self.products_with_single_offer = sum(
            1 for p in self.matched_products if len(p.offers) == 1
        )

        # Match rate: what percentage of input products were matched
        self.match_rate = (
            (self.total_matched_products / self.total_input_products * 100)
            if self.total_input_products > 0
            else 0.0
        )
