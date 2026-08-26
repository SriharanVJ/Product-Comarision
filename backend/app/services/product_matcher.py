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

        # Build matched products from initial grouping
        for group_products in match_groups.values():
            matched_product = self._build_matched_product(group_products)
            result.matched_products.append(matched_product)

        # Fallback: Use fuzzy matching for products that only got single platform offers
        # This helps when products have different names across platforms
        self._apply_fuzzy_matching(result.matched_products)

        result.total_matched_products = len(result.matched_products)
        result.calculate_statistics()

        return result

    def _get_match_key(self, product: NormalizedProduct) -> str:
        """Generate match key for grouping - strict on quantity and brand, lenient on variants"""
        # Normalize brand - this is important, don't group different brands
        brand = self._normalize_brand(product.brand)
        if not brand:
            brand = "unknown"

        # Extract base name (removes variants and quantities)
        base_name = self._extract_base_name(product.name)

        # Normalize quantity - this MUST be strict
        quantity, unit = self._normalize_quantity_for_matching(
            product.quantity, product.unit
        )

        # Create key - quantity is REQUIRED for proper matching
        qty_str = f"{quantity}{unit.value if unit else ''}" if quantity and unit else ""

        # If we have quantity, include it in key (strict matching)
        # If no quantity, be more lenient but use full name
        if qty_str:
            key = f"{brand}|{base_name}|{qty_str}"
        else:
            # No quantity - use more of the name for disambiguation
            key = f"{brand}|{base_name[:30]}"

        return key

    def _normalize_brand(self, brand: Optional[str]) -> Optional[str]:
        """Normalize brand name - be lenient for cross-platform matching"""
        if not brand:
            return None  # Changed from "unknown" to None for better matching

        # Normalize the brand
        normalized = brand.lower().strip().replace(" ", "").replace("-", "")

        # If brand is very generic, don't use it for matching
        generic_brands = {"generic", "unknown", "brand", "local", "store"}
        if normalized in generic_brands or len(normalized) < 3:
            return None

        return normalized

    def _extract_base_name(self, name: str) -> str:
        """Extract base product name without variants and quantity"""
        name_lower = name.lower()
        name_lower = name_lower.replace("-", " ")
        name_lower = name_lower.replace("/", " ")

        # Remove quantity indicators
        for unit_pattern in ["ml", "l", "g", "kg", "pc", "pcs", "pack", "doz", "piece", "pieces", "liter", "litre"]:
            name_lower = re.sub(rf"\d+(\.\d+)?\s*{re.escape(unit_pattern)}\b", "", name_lower)
            name_lower = re.sub(rf"\d+(\.\d+)?{re.escape(unit_pattern)}\b", "", name_lower)

        # Remove standalone numbers
        name_lower = re.sub(r"\b\d+(\.\d+)?\b", "", name_lower)

        # Remove variant terms
        for term in VARIANT_TERMS:
            pattern = r"\b" + re.escape(term) + r"\b"
            name_lower = re.sub(pattern, "", name_lower)

        # Remove marketing terms that don't affect product identity
        marketing_terms = ["premium", "gold", "special", "best", "quality", "select", "fresh", "delight", "delite"]
        for term in marketing_terms:
            pattern = r"\b" + re.escape(term) + r"\b"
            name_lower = re.sub(pattern, "", name_lower)

        # Clean up separators
        name_lower = re.sub(r"[,\–—|/()]+", " ", name_lower)
        name_lower = " ".join(name_lower.split())

        # If base name is too short, keep some more context
        if len(name_lower) < 8:
            # Re-extract with less aggressive cleaning
            name_lower = name.lower()
            name_lower = re.sub(r"\d+(\.\d+)?\s*(ml|l|g|kg|pc|pcs|pack|doz|piece|pieces|liter|litre)\b", "", name_lower)
            name_lower = " ".join(name_lower.split())[:30]  # First 30 chars

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

    def _apply_fuzzy_matching(self, matched_products: List[MatchedProduct]) -> None:
        """
        Apply fuzzy matching to merge products that are similar but didn't match strictly.

        This combines products with:
        - Same brand (or both unknown)
        - Similar names (using string similarity)
        - EXACT same quantity (not approximate)
        - Different platforms (no overlapping platforms)
        """
        # Track which products have been merged
        merged_indices = set()

        for i, product_a in enumerate(matched_products):
            if i in merged_indices:
                continue

            # Check if product_a already has multiple offers
            if len(product_a.offers) > 1:
                continue

            # Look for similar products
            for j, product_b in enumerate(matched_products[i+1:], start=i+1):
                if j in merged_indices:
                    continue

                # Skip if already has multiple offers
                if len(product_b.offers) > 1:
                    continue

                # Skip if they share platforms (means they're already merged properly)
                platforms_a = {offer.platform for offer in product_a.offers}
                platforms_b = {offer.platform for offer in product_b.offers}
                if platforms_a & platforms_b:
                    continue

                # Check brand compatibility - must be same or both unknown
                brand_a = self._normalize_brand(product_a.brand)
                brand_b = self._normalize_brand(product_b.brand)
                if brand_a and brand_b and brand_a != brand_b:
                    continue  # Different brands - don't merge

                # Check name similarity
                name_similarity = SequenceMatcher(
                    None,
                    product_a.canonical_name.lower(),
                    product_b.canonical_name.lower()
                ).ratio()

                # Check quantity EXACT match (not approximate)
                qty_exact_match = self._are_quantities_exact_match(
                    product_a.quantity, product_a.unit,
                    product_b.quantity, product_b.unit
                )

                # Merge if similar name AND exact quantity
                if name_similarity > 0.65 and qty_exact_match:
                    # Merge product_b into product_a
                    for offer in product_b.offers:
                        if not product_a.has_offer_from(offer.platform):
                            product_a.add_offer(offer, source_product_id=str(j))
                    merged_indices.add(j)

    def _are_quantities_exact_match(
        self,
        qty_a: Optional[float],
        unit_a: Optional[Unit],
        qty_b: Optional[float],
        unit_b: Optional[Unit]
    ) -> bool:
        """Check if quantities are EXACT match (not approximate)"""
        # If both missing, consider them match (both no quantity)
        if not qty_a and not qty_b:
            return True

        # If only one has quantity, not a match
        if (not qty_a) or (not qty_b):
            return False

        # If units don't match but we can convert, do so
        if unit_a and unit_b and unit_a != unit_b:
            try:
                # Convert to base units for comparison
                if unit_a in (Unit.LITER, Unit.MILLILITER) and unit_b in (Unit.LITER, Unit.MILLILITER):
                    qty_a_ml = qty_a * 1000 if unit_a == Unit.LITER else qty_a
                    qty_b_ml = qty_b * 1000 if unit_b == Unit.LITER else qty_b
                    return qty_a_ml == qty_b_ml  # EXACT match
                elif unit_a in (Unit.KILOGRAM, Unit.GRAM) and unit_b in (Unit.KILOGRAM, Unit.GRAM):
                    qty_a_g = qty_a * 1000 if unit_a == Unit.KILOGRAM else qty_a
                    qty_b_g = qty_b * 1000 if unit_b == Unit.KILOGRAM else qty_b
                    return qty_a_g == qty_b_g  # EXACT match
                else:
                    return False
            except:
                return False

        # Same units - check exact equality
        return qty_a == qty_b

    def _are_quantities_compatible(
        self,
        qty_a: Optional[float],
        unit_a: Optional[Unit],
        qty_b: Optional[float],
        unit_b: Optional[Unit]
    ) -> bool:
        """Check if quantities are compatible for merging"""
        # If either has no quantity, they're compatible
        if not qty_a or not qty_b:
            return True

        # If units don't match but we can convert, do so
        if unit_a and unit_b and unit_a != unit_b:
            try:
                # Convert to base units for comparison
                if unit_a in (Unit.LITER, Unit.MILLILITER) and unit_b in (Unit.LITER, Unit.MILLILITER):
                    qty_a_ml = qty_a * 1000 if unit_a == Unit.LITER else qty_a
                    qty_b_ml = qty_b * 1000 if unit_b == Unit.LITER else qty_b
                    return abs(qty_a_ml - qty_b_ml) <= 50  # Within 50ml tolerance
                elif unit_a in (Unit.KILOGRAM, Unit.GRAM) and unit_b in (Unit.KILOGRAM, Unit.GRAM):
                    qty_a_g = qty_a * 1000 if unit_a == Unit.KILOGRAM else qty_a
                    qty_b_g = qty_b * 1000 if unit_b == Unit.KILOGRAM else qty_b
                    return abs(qty_a_g - qty_b_g) <= 100  # Within 100g tolerance
                else:
                    return False
            except:
                return False

        # Same units - check if values are close
        return abs(qty_a - qty_b) <= max(qty_a, qty_b) * 0.1  # Within 10%
