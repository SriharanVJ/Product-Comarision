"""
Product Matching Service - Balanced Matching Strategy

Uses careful matching that:
1. Requires same base product name
2. Requires same quantity/unit
3. Allows flexible brand matching
4. Groups identical products from different platforms
"""

import re
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict
from difflib import SequenceMatcher

from app.schemas.product import NormalizedProduct, PlatformOffer, Platform, Unit
from app.schemas.matching import ProductMatchKey, MatchedProduct, MatchResult
from app.services.product_normalizer import ProductNormalizer


# Variant terms that should be extracted for matching
VARIANT_TERMS = {
    # Milk variants
    "toned", "full cream", "double toned", "standardized",
    "skimmed", "slim", "fat free", "low fat",
    "pasteurized", "uht", "fresh", "organic",
    "lactose free", "lactose-free", "a2", "cow", "buffalo",

    # Bread variants
    "whole wheat", "whole grain", "multigrain", "brown",
    "white", "milk", "sandwich", "toast", "sourdough",
    "gluten free", "gluten-free", "premium", "classic",

    # Common food variants
    "sugar free", "sugar-free", "diet", "low fat", "fat free",
    "roasted", "fried", "baked", "raw", "organic", "natural",

    # Marketing terms that don't affect the product
    "premium", "gold", "special", "best", "quality", "select",
    "fresh", "delight", "delite", "classic", "traditional",
}


class ProductMatcher:
    """
    Balanced product matcher that groups identical products from different platforms.

    Matching criteria:
    1. Same base product name (after removing variants and quantity)
    2. Same quantity and unit
    3. Compatible brand (exact or similar)
    """

    def __init__(self, normalizer: ProductNormalizer = None, similarity_threshold: float = 0.75):
        self.normalizer = normalizer or ProductNormalizer()
        self.similarity_threshold = similarity_threshold
        self._variant_cache: Dict[str, Set[str]] = {}

    def match_products(
        self, products: List[NormalizedProduct]
    ) -> MatchResult:
        """Match products across platforms"""
        result = MatchResult(total_input_products=len(products))

        if not products:
            return result

        # Group by match key
        match_groups: Dict[str, List[NormalizedProduct]] = defaultdict(list)

        for product in products:
            match_key = self._get_match_key(product)
            match_groups[match_key].append(product)

        # Build matched products
        for group_products in match_groups.values():
            matched_product = self._build_matched_product(group_products)
            result.matched_products.append(matched_product)

        result.total_matched_products = len(match_groups)
        result.calculate_statistics()

        return result

    def _get_match_key(self, product: NormalizedProduct) -> str:
        """Generate match key for grouping"""
        # Normalize brand
        brand = self._normalize_brand(product.brand)

        # Extract base name
        base_name = self._extract_base_name(product.name)

        # Normalize quantity
        quantity, unit = self._normalize_quantity_for_matching(
            product.quantity, product.unit
        )

        # Create key
        qty_str = f"{quantity}{unit.value if unit else ''}" if quantity else ""
        return f"{brand}|{base_name}|{qty_str}"

    def _normalize_brand(self, brand: Optional[str]) -> Optional[str]:
        """Normalize brand name"""
        if not brand:
            return "unknown"
        return brand.lower().strip().replace(" ", "")

    def _extract_base_name(self, name: str) -> str:
        """Extract base product name without variants and quantity"""
        name_lower = name.lower()
        name_lower = name_lower.replace("-", " ")
        name_lower = name_lower.replace("/", " ")

        # Remove quantity indicators
        for unit_pattern in ["ml", "l", "g", "kg", "pc", "pcs", "pack", "doz", "piece", "pieces"]:
            name_lower = re.sub(rf"\d+(\.\d+)?\s*{re.escape(unit_pattern)}\b", "", name_lower)
            name_lower = re.sub(rf"\d+(\.\d+)?{re.escape(unit_pattern)}\b", "", name_lower)

        # Remove standalone numbers
        name_lower = re.sub(r"\b\d+(\.\d+)?\b", "", name_lower)

        # Remove marketing terms that don't affect product identity
        marketing_terms = ["premium", "gold", "special", "best", "quality", "select", "fresh", "delight", "delite"]
        for term in marketing_terms:
            pattern = r"\b" + re.escape(term) + r"\b"
            name_lower = re.sub(pattern, "", name_lower)

        # Clean up separators
        name_lower = re.sub(r"[,\–—|/()]+", " ", name_lower)
        name_lower = " ".join(name_lower.split())

        return name_lower.strip()

    def _normalize_quantity_for_matching(
        self, quantity: Optional[float], unit: Optional[Unit]
    ) -> Tuple[Optional[float], Optional[Unit]]:
        """Normalize quantity to base unit"""
        if quantity is None or unit is None:
            return None, None

        if unit == Unit.LITER:
            return quantity * 1000, Unit.MILLILITER
        if unit == Unit.KILOGRAM:
            return quantity * 1000, Unit.GRAM

        return quantity, unit

    def _build_matched_product(self, products: List[NormalizedProduct]) -> MatchedProduct:
        """Build a MatchedProduct from grouped products"""
        if not products:
            raise ValueError("Cannot build matched product from empty list")

        # Use the first product as template
        first_product = products[0]

        # Create match key
        match_key = ProductMatchKey(
            brand=self._normalize_brand(first_product.brand),
            base_name=self._extract_base_name(first_product.name),
            variants=set(),
            quantity=first_product.quantity,
            unit=first_product.unit,
        )

        # Build matched product
        matched = MatchedProduct(
            match_key=match_key,
            canonical_name=first_product.name,
            brand=first_product.brand,
            quantity=first_product.quantity,
            unit=first_product.unit,
            quantity_display=self.normalizer._format_quantity_display(
                first_product.quantity, first_product.unit
            ),
            image_url=first_product.image_url,
        )

        # Add all offers from all products (this is the key part!)
        for product in products:
            for offer in product.offers:
                # Add offer regardless of platform - we want ALL offers
                if not matched.has_offer_from(offer.platform):
                    matched.add_offer(offer, source_product_id=product.product_id)
                else:
                    # Platform already has an offer - keep the one with better price
                    existing = next(o for o in matched.offers if o.platform == offer.platform)
                    if offer.price < existing.price:
                        # Replace with better price
                        matched.offers.remove(existing)
                        matched.add_offer(offer, source_product_id=product.product_id)

        # Ensure we have all platforms represented
        if len(matched.offers) < len(products):
            # Something went wrong - add missing offers
            for product in products:
                for offer in product.offers:
                    if not matched.has_offer_from(offer.platform):
                        matched.add_offer(offer, source_product_id=product.product_id)

        # Get image from any offer if missing
        if not matched.image_url:
            for offer in matched.offers:
                if offer.image_url:
                    matched.image_url = offer.image_url
                    break

        return matched
