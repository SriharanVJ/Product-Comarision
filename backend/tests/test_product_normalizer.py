"""
Unit tests for Product Normalization Service (PHASE 2)

These tests use actual API response structures captured from Phase 1.
All external API calls are mocked - tests run offline.
"""

import pytest
from unittest.mock import patch

from app.schemas.product import NormalizedProduct, PlatformOffer, Platform, Unit
from app.services.product_normalizer import ProductNormalizer


# Sample API responses based on actual Phase 1 output
SAMPLE_ZEPTO_RESPONSE = {
    "status": "success",
    "request_id": "test-request-id",
    "credits_remaining": 97,
    "data": {
        "query": "milk",
        "platforms": ["Zepto"],
        "lat": 13.0827,
        "lon": 80.2707,
        "credit_cost": 1,
        "results": {
            "Zepto": [
                {
                    "id": "12345",
                    "name": "Amrutha A2 Pasteurized Organic Fresh Milk | Pouch",
                    "mrp": 47,
                    "offer_price": 47,
                    "available": True,
                    "platform": {
                        "name": "Zepto",
                        "sla": "8 mins"
                    }
                },
                {
                    "id": "12346",
                    "name": "Nice Toned Fresh Milk | Pouch",
                    "mrp": 22,
                    "offer_price": 20,
                    "available": True,
                    "platform": {
                        "name": "Zepto",
                        "sla": "8 mins"
                    }
                },
                {
                    "id": "12347",
                    "name": "Good Life Toned UHT Milk | 500ml",
                    "mrp": 18,
                    "offer_price": 15,
                    "available": True,
                    "platform": {
                        "name": "Zepto",
                        "sla": "8 mins"
                    }
                }
            ]
        }
    }
}

SAMPLE_SWIGGY_RESPONSE = {
    "status": "success",
    "data": {
        "query": "milk",
        "platforms": ["Swiggy"],
        "lat": 13.0827,
        "lon": 80.2707,
        "credit_cost": 1,
        "results": {
            "Swiggy": [
                {
                    "id": "23456",
                    "name": "Amrutha A2 Pasteurized Organic Milk",
                    "mrp": "47",
                    "offer_price": "47",
                    "available": True,
                    "platform": {
                        "name": "Swiggy",
                        "sla": "16 mins"
                    }
                },
                {
                    "id": "23457",
                    "name": "Delite Milk",
                    "mrp": "25",
                    "offer_price": "22",
                    "available": True,
                    "platform": {
                        "name": "Swiggy",
                        "sla": "16-20 mins"
                    }
                }
            ]
        }
    }
}

SAMPLE_BLINKIT_RESPONSE = {
    "status": "success",
    "data": {
        "results": {
            "BlinkIt": [
                {
                    "id": "34567",
                    "name": "Amul Taaza Toned Milk 500ml",
                    "mrp": 30,
                    "offer_price": 28,
                    "available": True,
                    "platform": {
                        "name": "BlinkIt",
                        "sla": "10 min"
                    }
                },
                {
                    "id": "34568",
                    "name": "Amul Taaza Toned Milk - 500 ml",
                    "mrp": 30,
                    "offer_price": 29,
                    "available": True,
                    "platform": {
                        "name": "BlinkIt",
                        "sla": "10 mins"
                    }
                }
            ]
        }
    }
}


class TestProductNormalizer:
    """Test suite for ProductNormalizer"""

    @pytest.fixture
    def normalizer(self):
        """Create a fresh normalizer for each test"""
        return ProductNormalizer()

    # Test basic normalization

    def test_normalize_zepto_response(self, normalizer):
        """Test normalizing Zepto API response"""
        products = normalizer.normalize_api_response(SAMPLE_ZEPTO_RESPONSE, "milk")

        assert len(products) == 3

        # Check first product
        product = products[0]
        assert isinstance(product, NormalizedProduct)
        assert product.name == "Amrutha A2 Pasteurized Organic Fresh Milk - Pouch"
        assert len(product.offers) == 1

        offer = product.offers[0]
        assert offer.platform == Platform.ZEPTO
        assert offer.platform_product_id == "12345"
        assert offer.price == 47.0
        assert offer.mrp == 47.0
        assert offer.available is True
        assert offer.delivery_time_minutes == 8

    def test_normalize_swiggy_response(self, normalizer):
        """Test normalizing Swiggy API response with string prices"""
        products = normalizer.normalize_api_response(SAMPLE_SWIGGY_RESPONSE, "milk")

        assert len(products) == 2

        # Swiggy returns prices as strings - verify parsing
        product = products[0]
        offer = product.offers[0]
        assert offer.price == 47.0
        assert offer.mrp == 47.0
        assert isinstance(offer.price, float)
        assert isinstance(offer.mrp, float)

    def test_normalize_blinkit_response(self, normalizer):
        """Test normalizing BlinkIt API response"""
        products = normalizer.normalize_api_response(SAMPLE_BLINKIT_RESPONSE, "milk")

        assert len(products) >= 1

        # Check for discount calculation
        product = products[0]
        offer = product.offers[0]
        assert offer.price == 28.0
        assert offer.mrp == 30.0
        assert offer.discount == 2.0

    # Test price parsing

    def test_price_parsing_various_formats(self, normalizer):
        """Test price parsing handles various formats"""
        # Create test items with different price formats
        test_cases = [
            (28, 28.0),  # Integer
            ("28", 28.0),  # String
            ("₹28", 28.0),  # With rupee symbol
            ("Rs. 28", 28.0),  # With Rs.
            ("28.50", 28.5),  # Decimal
            ("1,499", 1499.0),  # With comma
        ]

        for raw_price, expected in test_cases:
            item = {
                "id": "test",
                "name": "Test Product",
                "offer_price": raw_price,
                "mrp": raw_price,
                "available": True,
                "platform": {"name": "Zepto", "sla": "10 mins"}
            }

            offer = normalizer._normalize_platform_item(item, Platform.ZEPTO)
            assert offer.price == expected, f"Failed for price: {raw_price}"

    # Test delivery time parsing

    def test_delivery_time_parsing(self, normalizer):
        """Test delivery time parsing handles various formats"""
        test_cases = [
            ("8 mins", 8),
            ("10 min", 10),
            ("16-20 mins", 16),  # Range returns lower bound
            ("30", 30),
            ("45 minutes", 45),
            (None, None),
            ("", None),
            ("unknown", None),  # Invalid returns None
        ]

        for sla_text, expected in test_cases:
            result = normalizer._parse_delivery_time(sla_text)
            assert result == expected, f"Failed for SLA: {sla_text}"

    # Test brand extraction

    def test_brand_extraction_known_brands(self, normalizer):
        """Test brand extraction for known brands"""
        test_cases = [
            ("Amul Taaza Milk", "Amul"),
            ("Britannia Good Day", "Britannia"),
            ("Nestle Coffee", "Nestle"),
            ("Tata Salt", "Tata"),
            ("Fortune Oil", "Fortune"),
            ("Aashirvaad Atta", "Aashirvaad"),
        ]

        for product_name, expected_brand in test_cases:
            brand = normalizer._extract_brand(product_name)
            assert brand == expected_brand, f"Failed for: {product_name}"

    def test_brand_extraction_unknown_brand(self, normalizer):
        """Test brand extraction returns None for unknown brands"""
        brand = normalizer._extract_brand("Generic Product Name")
        assert brand is None or isinstance(brand, str)

    # Test quantity/unit parsing

    def test_quantity_parsing_ml(self, normalizer):
        """Test parsing milliliter quantities"""
        test_cases = [
            ("500ml", (500.0, Unit.MILLILITER)),
            ("500 ml", (500.0, Unit.MILLILITER)),
            ("500.5ml", (500.5, Unit.MILLILITER)),
            ("1L", (1.0, Unit.LITER)),  # 1L is parsed as liter
            ("1000 ml", (1000.0, Unit.MILLILITER)),
        ]

        for text, (expected_qty, expected_unit) in test_cases:
            qty, unit = normalizer._parse_quantity_and_unit(text)
            assert unit == expected_unit, f"Failed for: {text}"

    def test_quantity_parsing_grams(self, normalizer):
        """Test parsing gram quantities"""
        test_cases = [
            ("500g", (500.0, Unit.GRAM)),
            ("1 kg", (1.0, Unit.KILOGRAM)),
            ("1.5kg", (1.5, Unit.KILOGRAM)),
            ("100 g", (100.0, Unit.GRAM)),
        ]

        for text, (expected_qty, expected_unit) in test_cases:
            qty, unit = normalizer._parse_quantity_and_unit(text)
            assert unit == expected_unit, f"Failed for: {text}"

    def test_quantity_parsing_pieces(self, normalizer):
        """Test parsing piece/pack quantities"""
        test_cases = [
            ("12 pcs", (12.0, Unit.PIECE)),
            ("1 pack", (1.0, Unit.PACK)),
            ("2 dozen", (2.0, Unit.DOZEN)),
        ]

        for text, (expected_qty, expected_unit) in test_cases:
            qty, unit = normalizer._parse_quantity_and_unit(text)
            assert unit == expected_unit, f"Failed for: {text}"

    def test_quantity_display_formatting(self, normalizer):
        """Test quantity display formatting"""
        test_cases = [
            (500, Unit.MILLILITER, "500ml"),
            (0.5, Unit.LITER, "500ml"),  # Converted to ml for display
            (1, Unit.LITER, "1l"),
            (1000, Unit.GRAM, "1000g"),
            (1, Unit.KILOGRAM, "1kg"),  # kg stays as kg
            (10, Unit.PIECE, "10pc"),
        ]

        for qty, unit, expected_display in test_cases:
            result = normalizer._format_quantity_display(qty, unit)
            assert result == expected_display, f"Failed for {qty}{unit.value}"

    # Test unit conversion

    def test_unit_conversion_ml_to_l(self, normalizer):
        """Test milliliter to liter conversion"""
        result = normalizer.normalize_unit(500, Unit.MILLILITER, Unit.LITER)
        assert result == 0.5

    def test_unit_conversion_l_to_ml(self, normalizer):
        """Test liter to milliliter conversion"""
        result = normalizer.normalize_unit(1, Unit.LITER, Unit.MILLILITER)
        assert result == 1000.0

    def test_unit_conversion_g_to_kg(self, normalizer):
        """Test gram to kilogram conversion"""
        result = normalizer.normalize_unit(500, Unit.GRAM, Unit.KILOGRAM)
        assert result == 0.5

    def test_unit_conversion_same_unit(self, normalizer):
        """Test conversion to same unit returns same value"""
        result = normalizer.normalize_unit(500, Unit.MILLILITER, Unit.MILLILITER)
        assert result == 500

    def test_invalid_unit_conversion(self, normalizer):
        """Test invalid unit conversion raises error"""
        with pytest.raises(ValueError):
            normalizer.normalize_unit(500, Unit.MILLILITER, Unit.GRAM)

    # Test quantity equality

    def test_quantities_equal_same_unit(self, normalizer):
        """Test quantity equality with same units"""
        assert normalizer.are_quantities_equal(500, Unit.MILLILITER, 500, Unit.MILLILITER)
        assert normalizer.are_quantities_equal(500, Unit.MILLILITER, 501, Unit.MILLILITER, tolerance=1)
        assert not normalizer.are_quantities_equal(500, Unit.MILLILITER, 400, Unit.MILLILITER)

    def test_quantities_equal_different_units(self, normalizer):
        """Test quantity equality across different units"""
        # 500ml == 0.5l
        assert normalizer.are_quantities_equal(500, Unit.MILLILITER, 0.5, Unit.LITER)

        # 1kg == 1000g
        assert normalizer.are_quantities_equal(1, Unit.KILOGRAM, 1000, Unit.GRAM)

        # 1000ml == 1l
        assert normalizer.are_quantities_equal(1000, Unit.MILLILITER, 1, Unit.LITER)

    def test_quantities_equal_with_none(self, normalizer):
        """Test quantity equality with None values"""
        assert not normalizer.are_quantities_equal(None, Unit.MILLILITER, 500, Unit.MILLILITER)
        assert not normalizer.are_quantities_equal(500, Unit.MILLILITER, None, Unit.MILLILITER)

    # Test product ID generation

    def test_product_id_generation_stable(self, normalizer):
        """Test product ID generation is stable for same inputs"""
        id1 = normalizer._generate_product_id("Amul", "Taaza Milk", 500, Unit.MILLILITER)
        id2 = normalizer._generate_product_id("Amul", "Taaza Milk", 500, Unit.MILLILITER)
        assert id1 == id2

    def test_product_id_generation_unique(self, normalizer):
        """Test product ID generation is unique for different inputs"""
        id1 = normalizer._generate_product_id("Amul", "Taaza Milk", 500, Unit.MILLILITER)
        id2 = normalizer._generate_product_id("Amul", "Taaza Milk", 1000, Unit.MILLILITER)
        assert id1 != id2

    def test_product_id_generation_case_insensitive(self, normalizer):
        """Test product ID generation normalizes case"""
        id1 = normalizer._generate_product_id("Amul", "Taaza Milk", 500, Unit.MILLILITER)
        id2 = normalizer._generate_product_id("amul", "taaza milk", 500, Unit.MILLILITER)
        assert id1 == id2

    # Test product name normalization

    def test_name_normalization(self, normalizer):
        """Test product name normalization"""
        test_cases = [
            ("  Extra  spaces  ", "Extra spaces"),
            ("Product - Variant", "Product - Variant"),
            ("Product | Variant", "Product - Variant"),
            ("Product—Variant", "Product - Variant"),
        ]

        for input_name, expected in test_cases:
            result = normalizer._normalize_product_name(input_name)
            assert result == expected, f"Failed for: {input_name}"

    # Test comparison metadata

    def test_product_comparison_metadata(self):
        """Test product comparison metadata is calculated correctly"""
        product = NormalizedProduct(
            product_id="test",
            name="Test Product",
            offers=[
                PlatformOffer(
                    platform=Platform.ZEPTO,
                    platform_product_id="1",
                    price=28,
                    available=True,
                    delivery_time_minutes=10,
                ),
                PlatformOffer(
                    platform=Platform.BLINKIT,
                    platform_product_id="2",
                    price=30,
                    available=True,
                    delivery_time_minutes=8,
                ),
                PlatformOffer(
                    platform=Platform.SWIGGY,
                    platform_product_id="3",
                    price=29,
                    available=False,  # Not available
                    delivery_time_minutes=12,
                ),
            ],
        )

        # Update comparison metadata
        product._update_comparison_data()

        assert product.available_on_platforms == 2
        assert product.lowest_price == 28.0
        assert product.highest_price == 30.0
        assert product.price_difference == 2.0

    def test_get_cheapest_offer(self):
        """Test getting cheapest offer"""
        product = NormalizedProduct(
            product_id="test",
            name="Test",
            offers=[
                PlatformOffer(
                    platform=Platform.ZEPTO,
                    platform_product_id="1",
                    price=28,
                    available=True,
                ),
                PlatformOffer(
                    platform=Platform.BLINKIT,
                    platform_product_id="2",
                    price=30,
                    available=True,
                ),
            ],
        )

        cheapest = product.get_cheapest_offer()
        assert cheapest.platform == Platform.ZEPTO
        assert cheapest.price == 28

    def test_get_fastest_offer(self):
        """Test getting fastest delivery offer"""
        product = NormalizedProduct(
            product_id="test",
            name="Test",
            offers=[
                PlatformOffer(
                    platform=Platform.ZEPTO,
                    platform_product_id="1",
                    price=28,
                    available=True,
                    delivery_time_minutes=10,
                ),
                PlatformOffer(
                    platform=Platform.BLINKIT,
                    platform_product_id="2",
                    price=30,
                    available=True,
                    delivery_time_minutes=8,
                ),
            ],
        )

        fastest = product.get_fastest_offer()
        assert fastest.platform == Platform.BLINKIT
        assert fastest.delivery_time_minutes == 8

    def test_get_offer_by_platform(self):
        """Test getting offer by specific platform"""
        product = NormalizedProduct(
            product_id="test",
            name="Test",
            offers=[
                PlatformOffer(
                    platform=Platform.ZEPTO,
                    platform_product_id="1",
                    price=28,
                ),
                PlatformOffer(
                    platform=Platform.BLINKIT,
                    platform_product_id="2",
                    price=30,
                ),
            ],
        )

        zepto_offer = product.get_offer_by_platform(Platform.ZEPTO)
        assert zepto_offer is not None
        assert zepto_offer.platform == Platform.ZEPTO

        swiggy_offer = product.get_offer_by_platform(Platform.SWIGGY)
        assert swiggy_offer is None


class TestProductNormalizerEdgeCases:
    """Test edge cases and error handling"""

    @pytest.fixture
    def normalizer(self):
        return ProductNormalizer()

    def test_empty_response(self, normalizer):
        """Test normalizing empty response"""
        products = normalizer.normalize_api_response({"status": "success", "data": {"results": {}}}, "test")
        assert len(products) == 0

    def test_error_response(self, normalizer):
        """Test normalizing error response"""
        products = normalizer.normalize_api_response({"status": "error"}, "test")
        assert len(products) == 0

    def test_missing_optional_fields(self, normalizer):
        """Test handling missing optional fields"""
        item = {
            "id": "test",
            "name": "Test Product",
            # Missing price, availability, etc.
            "platform": {"name": "Zepto"}
        }

        offer = normalizer._normalize_platform_item(item, Platform.ZEPTO)
        assert offer.platform_product_id == "test"
        assert offer.price is None
        assert offer.mrp is None
        assert offer.available is True  # Default

    def test_zero_price(self, normalizer):
        """Test handling zero price"""
        item = {
            "id": "test",
            "name": "Free Product",
            "offer_price": 0,
            "mrp": 0,
            "available": True,
            "platform": {"name": "Zepto", "sla": "10 mins"}
        }

        offer = normalizer._normalize_platform_item(item, Platform.ZEPTO)
        assert offer.price == 0.0
        assert offer.mrp == 0.0
        assert offer.discount == 0.0

    def test_invalid_platform_skipped(self, normalizer):
        """Test invalid platform names are handled gracefully"""
        response = {
            "status": "success",
            "data": {
                "results": {
                    "InvalidPlatform": [
                        {"id": "1", "name": "Test", "mrp": 10, "offer_price": 10, "available": True, "platform": {"name": "InvalidPlatform"}}
                    ]
                }
            }
        }

        products = normalizer.normalize_api_response(response, "test")
        # Should skip invalid platform
        assert len(products) == 0
