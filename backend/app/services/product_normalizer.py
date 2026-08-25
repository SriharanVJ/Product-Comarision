"""
Product Normalization Service

This service handles normalization of products from different platforms.
It handles:
- Product name normalization
- Brand extraction
- Quantity/unit parsing and normalization
- Price normalization
- Delivery time parsing
- Image URL extraction

The goal is to convert platform-specific data into our normalized schema.
"""

import re
import hashlib
from typing import Optional, Dict, List, Tuple
from app.schemas.product import NormalizedProduct, PlatformOffer, Platform, Unit


# Unit conversion constants
UNIT_CONVERSIONS: Dict[Tuple[Unit, Unit], float] = {
    # Milliliters to Liters
    (Unit.MILLILITER, Unit.LITER): 0.001,
    # Liters to Milliliters
    (Unit.LITER, Unit.MILLILITER): 1000.0,
    # Grams to Kilograms
    (Unit.GRAM, Unit.KILOGRAM): 0.001,
    # Kilograms to Grams
    (Unit.KILOGRAM, Unit.GRAM): 1000.0,
}


# Common Indian grocery brands
COMMON_BRANDS = {
    "amul", "britannia", "nestle", "hindustan unilever", "itc", "cadbury",
    "parle", "sunfeast", "goodlife", "aashirvaad", "tata", "fortune",
    "saffola", "monsieur", "danone", "yogabar", "kellogg", "quaker",
    "heinz", "maggie", "knorr", "chings", "mdh", "everest", "catch",
    "badshah", "tatamonte", "coca-cola", "pepsi", "sprite", "thums up",
    "maaza", "slice", "frooti", "appy", "sting", "red bull", "monster",
    "lays", "kurkure", "bingo", "balaji", "haldiram", "bikaji", "itarial",
    "mothers recipe", "chitale", "bambino", "mithai", "peda", "barfi",
    "amrutha", "heritage", "nandini", "milma", "verka", "vitagen", "milky Mist",
    "nice", "delite", "heritage", "karuna", "akshayakalpa", "sudha", "a+",
    "saras", "gokul", "mahaprofit", " Dynamix", "creamica", "hatsun",
}


# Unit patterns with their normalized values
UNIT_PATTERNS: List[Tuple[List[str], Unit]] = [
    (["ml", "millilitre", "milliliter", "millilitres", "milliliters"], Unit.MILLILITER),
    (["l", "litre", "liter", "litres", "liters"], Unit.LITER),
    (["g", "gram", "grams", "gramme", "grammes"], Unit.GRAM),
    (["kg", "kilogram", "kilograms", "kilogramme", "kilogrammes"], Unit.KILOGRAM),
    (["pc", "piece", "pieces", "pcs"], Unit.PIECE),
    (["pack", "packs", "pkt"], Unit.PACK),
    (["doz", "dozen"], Unit.DOZEN),
]


class ProductNormalizer:
    """
    Normalizes products from different platforms into our unified schema.

    This service handles the differences in how platforms represent products,
    such as:
    - Different naming conventions
    - Different unit representations
    - Different quantity formats
    - Different price representations
    """

    def __init__(self):
        """Initialize the normalizer"""
        self._brand_cache: Dict[str, Optional[str]] = {}

    def normalize_api_response(
        self,
        api_response: Dict,
        query: str,
    ) -> List[NormalizedProduct]:
        """
        Normalize the complete API response into a list of NormalizedProduct.

        Args:
            api_response: Raw response from QuickCommerce API
            query: Original search query

        Returns:
            List of normalized products
        """
        if api_response.get("status") != "success":
            return []

        data = api_response.get("data", {})
        results = data.get("results", {})

        normalized_products: List[NormalizedProduct] = []

        for platform_name, platform_results in results.items():
            try:
                platform = Platform(platform_name)
            except ValueError:
                # Skip unknown platforms
                continue

            for item in platform_results:
                try:
                    offer = self._normalize_platform_item(item, platform)
                    # For now, create one product per offer
                    # Product matching (merging same product across platforms) is Phase 3
                    product = self._create_product_from_offer(offer, query)
                    normalized_products.append(product)
                except Exception as e:
                    # Log error but continue processing other items
                    print(f"Error normalizing item from {platform_name}: {e}")
                    continue

        return normalized_products

    def _normalize_platform_item(self, item: Dict, platform: Platform) -> PlatformOffer:
        """
        Normalize a single item from a platform into a PlatformOffer.

        This extracts all relevant fields and handles type conversions.
        """
        # Basic fields
        platform_product_id = str(item.get("id", ""))
        name = str(item.get("name", "Unknown"))

        # Price fields - handle various types
        # Check offer_price first, fall back to price, but handle 0 correctly
        price_raw = item.get("offer_price")
        if price_raw is None:
            price_raw = item.get("price")
        mrp_raw = item.get("mrp")

        # Availability
        available = bool(item.get("available", True))

        # Platform info
        platform_info = item.get("platform", {})
        delivery_time_text = platform_info.get("sla", "")
        delivery_time_minutes = self._parse_delivery_time(delivery_time_text)

        # Image URL - might be at different levels or as an array
        images_array = item.get("images")
        if images_array and isinstance(images_array, list) and len(images_array) > 0:
            image_url = images_array[0]
        else:
            image_url = (
                item.get("image_url")
                or item.get("image")
                or item.get("img")
                or platform_info.get("image_url")
            )

        # Product URL - might be at different levels
        product_url = (
            item.get("product_url")
            or item.get("url")
            or item.get("link")
            or platform_info.get("product_url")
        )

        # Store raw data for debugging
        raw_data = {"original_item": item}

        return PlatformOffer(
            platform=platform,
            platform_product_id=platform_product_id,
            price=price_raw,  # Will be parsed by Pydantic validator
            mrp=mrp_raw,
            available=available,
            delivery_time_minutes=delivery_time_minutes,
            delivery_time_text=delivery_time_text,
            product_url=product_url,
            image_url=image_url,
            raw_data=raw_data,
        )

    def _create_product_from_offer(self, offer: PlatformOffer, query: str) -> NormalizedProduct:
        """Create a NormalizedProduct from a single PlatformOffer"""

        # Extract actual product name from raw data - preserve canonical name
        raw_item = offer.raw_data.get("original_item", {}) if offer.raw_data else {}
        product_name = self._normalize_product_name(raw_item.get("name", offer.platform_product_id))
        brand = self._extract_brand(product_name)

        # Try to get quantity from API's quantity field first, then parse from name
        quantity_field = raw_item.get("quantity")
        if quantity_field:
            quantity, unit = self._parse_quantity_and_unit(str(quantity_field))
        else:
            quantity, unit = self._parse_quantity_and_unit(product_name)
        quantity_display = self._format_quantity_display(quantity, unit)

        # Store canonical name separately to preserve full product name
        canonical_name = raw_item.get("name", offer.platform_product_id)

        # Generate stable product ID
        product_id = self._generate_product_id(
            brand or "",
            product_name,
            quantity or 0,
            unit or Unit.UNIT,
        )

        # Use offer image URL if available
        image_url = offer.image_url

        product = NormalizedProduct(
            product_id=product_id,
            name=canonical_name,  # Use canonical name instead of normalized name
            brand=brand,
            quantity=quantity,
            unit=unit,
            quantity_display=quantity_display,
            image_url=image_url,
            offers=[offer],
        )

        # Trigger comparison metadata update
        product._update_comparison_data()

        return product

    def _normalize_product_name(self, name: str) -> str:
        """
        Normalize product name for consistency.

        This:
        - Removes extra whitespace
        - Standardizes separators
        - Removes special characters
        - Normalizes case
        """
        if not name:
            return ""

        # Remove extra whitespace
        name = " ".join(name.split())

        # Standardize separators (| -> -, etc)
        name = re.sub(r"\s*[|–—]\s*", " - ", name)

        return name.strip()

    def _extract_brand(self, product_name: str) -> Optional[str]:
        """
        Extract brand name from product name.

        Uses a list of known brands and heuristics to find the brand.
        """
        if not product_name or product_name in self._brand_cache:
            return self._brand_cache.get(product_name)

        # Lowercase for matching
        name_lower = product_name.lower()

        # Check for known brands
        for brand in COMMON_BRANDS:
            if brand in name_lower:
                self._brand_cache[product_name] = brand.title()
                return brand.title()

        # Try to find brand at start of name (often first word)
        words = product_name.split()
        if words:
            first_word = words[0]
            # If first word is capitalized and longer than 2 chars, might be brand
            if len(first_word) > 2 and first_word[0].isupper():
                self._brand_cache[product_name] = first_word
                return first_word

        self._brand_cache[product_name] = None
        return None

    def _parse_quantity_and_unit(self, text: str) -> Tuple[Optional[float], Optional[Unit]]:
        """
        Parse quantity and unit from product name.

        Examples:
            "500ml" -> (500.0, Unit.MILLILITER)
            "1 kg" -> (1.0, Unit.KILOGRAM)
            "0.5L" -> (0.5, Unit.LITER)
            "2 pcs" -> (2.0, Unit.PIECE)
            "500 ml x 4" -> (2000.0, Unit.MILLILITER)  # Multi-pack

        Returns:
            Tuple of (quantity, unit) or (None, None) if not found
        """
        if not text:
            return None, None

        text_lower = text.lower()

        # Handle multi-pack quantities first (e.g., "500 ml x 4")
        multi_pack_match = re.search(r"(\d+(?:\.\d+)?)\s*ml\s*x\s*(\d+)", text_lower)
        if multi_pack_match:
            quantity = float(multi_pack_match.group(1)) * float(multi_pack_match.group(2))
            return quantity, Unit.MILLILITER

        multi_pack_match_g = re.search(r"(\d+(?:\.\d+)?)\s*g\s*x\s*(\d+)", text_lower)
        if multi_pack_match_g:
            quantity = float(multi_pack_match_g.group(1)) * float(multi_pack_match_g.group(2))
            return quantity, Unit.GRAM

        # Try each unit pattern
        for patterns, unit in UNIT_PATTERNS:
            for pattern in patterns:
                # Build regex to find quantity before unit
                # Handles: "500ml", "500 ml", "500.5ml", "500.5 ml"
                regex = rf"(\d+(?:\.\d+)?)\s*(?:{re.escape(pattern)}s?)\b"
                match = re.search(regex, text_lower)

                if match:
                    quantity = float(match.group(1))
                    return quantity, unit

        # Try decimal format for liters (0.5 = 500ml)
        # Look for patterns like "0.5 l" or ".5 l"
        decimal_match = re.search(r"(\d*\.?\d+)\s*l\b", text_lower)
        if decimal_match:
            quantity = float(decimal_match.group(1))
            if quantity < 1:
                # Convert to ml for small quantities
                return quantity * 1000, Unit.MILLILITER
            return quantity, Unit.LITER

        return None, None

    def _format_quantity_display(
        self,
        quantity: Optional[float],
        unit: Optional[Unit],
    ) -> Optional[str]:
        """
        Format quantity and unit for human display.

        Uses "natural" units for display (e.g., 500ml instead of 0.5l)
        """
        if quantity is None or unit is None:
            return None

        # Normalize to human-friendly units
        display_quantity = quantity
        display_unit = unit

        # Convert to smaller unit for readability
        if unit == Unit.LITER and quantity < 1:
            display_quantity = quantity * 1000
            display_unit = Unit.MILLILITER
        elif unit == Unit.KILOGRAM and quantity < 1:
            display_quantity = quantity * 1000
            display_unit = Unit.GRAM

        # Format nicely
        if isinstance(display_quantity, int) or display_quantity.is_integer():
            return f"{int(display_quantity)}{display_unit.value}"
        else:
            return f"{display_quantity:g}{display_unit.value}"

    def _parse_delivery_time(self, sla_text: Optional[str]) -> Optional[int]:
        """
        Parse delivery time from SLA string.

        Handles various formats:
            "8 mins" -> 8
            "10-15 mins" -> 10
            "30 min" -> 30
            "1 hour" -> 60
        """
        if not sla_text:
            return None

        # First, replace hours if present
        sla_lower = sla_text.lower()

        # Handle hours (1 hour = 60 mins)
        hour_match = re.search(r"(\d+)\s*hour", sla_lower)
        if hour_match:
            return int(hour_match.group(1)) * 60

        # Remove spaces and handle minutes
        sla_lower = sla_lower.replace(" ", "").replace("minutes", "").replace("mins", "").replace("min", "")

        try:
            if "-" in sla_lower:
                # Take lower bound for ranges
                return int(sla_lower.split("-")[0])
            return int(sla_lower)
        except (ValueError, IndexError):
            return None

    def _generate_product_id(
        self,
        brand: str,
        name: str,
        quantity: float,
        unit: Unit,
    ) -> str:
        """
        Generate a stable, unique product ID.

        Uses hash of product identity fields for consistency.
        """
        # Normalize input
        identifier = f"{brand}|{name}|{quantity}|{unit.value}".lower().strip()

        # Generate hash
        hash_obj = hashlib.md5(identifier.encode())
        return hash_obj.hexdigest()[:16]

    def normalize_unit(self, quantity: float, from_unit: Unit, to_unit: Unit) -> float:
        """
        Convert quantity from one unit to another.

        Args:
            quantity: The quantity value
            from_unit: Source unit
            to_unit: Target unit

        Returns:
            Converted quantity

        Raises:
            ValueError: If conversion is not supported
        """
        if from_unit == to_unit:
            return quantity

        conversion_key = (from_unit, to_unit)
        if conversion_key in UNIT_CONVERSIONS:
            return quantity * UNIT_CONVERSIONS[conversion_key]

        raise ValueError(f"Cannot convert from {from_unit} to {to_unit}")

    def are_quantities_equal(
        self,
        q1: Optional[float],
        u1: Optional[Unit],
        q2: Optional[float],
        u2: Optional[Unit],
        tolerance: float = 0.01,
    ) -> bool:
        """
        Check if two quantities are the same, accounting for unit differences.

        Examples:
            (500, ml) == (0.5, l) -> True
            (1, kg) == (1000, g) -> True
        """
        if None in (q1, u1, q2, u2):
            return False

        if u1 == u2:
            return abs(q1 - q2) <= tolerance

        # Try converting q1 to u2
        try:
            converted = self.normalize_unit(q1, u1, u2)
            return abs(converted - q2) < tolerance
        except ValueError:
            return False
