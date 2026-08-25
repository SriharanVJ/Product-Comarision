"""
Comprehensive tests for Product Matching Service (PHASE 3)

These tests verify that the matcher correctly:
- Groups identical products across platforms
- Separates different products
- Handles equivalent quantities (500ml == 0.5l, 1kg == 1000g)
- Distinguishes variants (toned vs full cream, organic vs regular)
- Handles missing fields
- Prevents duplicate offers from same platform
"""

import pytest
from app.schemas.product import NormalizedProduct, PlatformOffer, Platform, Unit
from app.schemas.matching import MatchResult
from app.services.product_matcher import ProductMatcher


class TestProductMatchingBasic:
    """Test basic product matching scenarios"""

    @pytest.fixture
    def matcher(self):
        """Create a fresh matcher for each test"""
        return ProductMatcher()

    def test_exact_same_product_across_platforms(self, matcher):
        """Test matching identical product from all three platforms"""
        products = [
            # Zepto
            NormalizedProduct(
                product_id="zepto_1",
                name="Amul Taaza Toned Milk",
                brand="Amul",
                quantity=500,
                unit=Unit.MILLILITER,
                offers=[
                    PlatformOffer(
                        platform=Platform.ZEPTO,
                        platform_product_id="z1",
                        price=28.0,
                        available=True,
                        delivery_time_minutes=10,
                    )
                ],
            ),
            # BlinkIt
            NormalizedProduct(
                product_id="blinkit_1",
                name="Amul Taaza Toned Milk",
                brand="Amul",
                quantity=500,
                unit=Unit.MILLILITER,
                offers=[
                    PlatformOffer(
                        platform=Platform.BLINKIT,
                        platform_product_id="b1",
                        price=29.0,
                        available=True,
                        delivery_time_minutes=8,
                    )
                ],
            ),
            # Swiggy
            NormalizedProduct(
                product_id="swiggy_1",
                name="Amul Taaza Toned Milk",
                brand="Amul",
                quantity=500,
                unit=Unit.MILLILITER,
                offers=[
                    PlatformOffer(
                        platform=Platform.SWIGGY,
                        platform_product_id="s1",
                        price=30.0,
                        available=True,
                        delivery_time_minutes=12,
                    )
                ],
            ),
        ]

        result = matcher.match_products(products)

        assert result.total_input_products == 3
        assert result.total_matched_products == 1
        assert len(result.matched_products) == 1

        matched = result.matched_products[0]
        assert matched.available_platforms == 3
        assert len(matched.offers) == 3
        assert matched.lowest_price == 28.0
        assert matched.highest_price == 30.0
        assert matched.cheapest_platform == Platform.ZEPTO
        assert matched.fastest_platform == Platform.BLINKIT

    def test_different_capitalization_matches(self, matcher):
        """Test matching handles different capitalization"""
        products = [
            NormalizedProduct(
                product_id="p1",
                name="AMUL TAAZA TONED MILK",
                brand="AMUL",
                quantity=500,
                unit=Unit.MILLILITER,
                offers=[PlatformOffer(platform=Platform.ZEPTO, platform_product_id="z1", price=28)],
            ),
            NormalizedProduct(
                product_id="p2",
                name="amul taaza toned milk",
                brand="amul",
                quantity=500,
                unit=Unit.MILLILITER,
                offers=[PlatformOffer(platform=Platform.BLINKIT, platform_product_id="b1", price=29)],
            ),
        ]

        result = matcher.match_products(products)
        assert result.total_matched_products == 1
        assert len(result.matched_products[0].offers) == 2

    def test_different_punctuation_matches(self, matcher):
        """Test matching handles different punctuation"""
        products = [
            NormalizedProduct(
                product_id="p1",
                name="Amul Taaza Toned Milk - 500 ml",
                brand="Amul",
                quantity=500,
                unit=Unit.MILLILITER,
                offers=[PlatformOffer(platform=Platform.ZEPTO, platform_product_id="z1", price=28)],
            ),
            NormalizedProduct(
                product_id="p2",
                name="Amul Taaza Toned Milk | 500ml",
                brand="Amul",
                quantity=500,
                unit=Unit.MILLILITER,
                offers=[PlatformOffer(platform=Platform.BLINKIT, platform_product_id="b1", price=29)],
            ),
        ]

        result = matcher.match_products(products)
        assert result.total_matched_products == 1

    def test_equivalent_quantities_ml_to_l(self, matcher):
        """Test 500ml matches 0.5l"""
        products = [
            NormalizedProduct(
                product_id="p1",
                name="Amul Taaza Toned Milk",
                brand="Amul",
                quantity=500,
                unit=Unit.MILLILITER,
                offers=[PlatformOffer(platform=Platform.ZEPTO, platform_product_id="z1", price=28)],
            ),
            NormalizedProduct(
                product_id="p2",
                name="Amul Taaza Toned Milk",
                brand="Amul",
                quantity=0.5,
                unit=Unit.LITER,
                offers=[PlatformOffer(platform=Platform.BLINKIT, platform_product_id="b1", price=29)],
            ),
        ]

        result = matcher.match_products(products)
        assert result.total_matched_products == 1
        assert len(result.matched_products[0].offers) == 2

    def test_equivalent_quantities_kg_to_g(self, matcher):
        """Test 1kg matches 1000g"""
        products = [
            NormalizedProduct(
                product_id="p1",
                name="Aashirvaad Atta",
                brand="Aashirvaad",
                quantity=1,
                unit=Unit.KILOGRAM,
                offers=[PlatformOffer(platform=Platform.ZEPTO, platform_product_id="z1", price=280)],
            ),
            NormalizedProduct(
                product_id="p2",
                name="Aashirvaad Atta",
                brand="Aashirvaad",
                quantity=1000,
                unit=Unit.GRAM,
                offers=[PlatformOffer(platform=Platform.BLINKIT, platform_product_id="b1", price=285)],
            ),
        ]

        result = matcher.match_products(products)
        assert result.total_matched_products == 1
        assert len(result.matched_products[0].offers) == 2


class TestProductMatchingDifferentProducts:
    """Test that different products are NOT matched"""

    @pytest.fixture
    def matcher(self):
        return ProductMatcher()

    def test_different_quantities_do_not_match(self, matcher):
        """Test 500ml and 1L are separate products"""
        products = [
            NormalizedProduct(
                product_id="p1",
                name="Amul Taaza Toned Milk",
                brand="Amul",
                quantity=500,
                unit=Unit.MILLILITER,
                offers=[PlatformOffer(platform=Platform.ZEPTO, platform_product_id="z1", price=28)],
            ),
            NormalizedProduct(
                product_id="p2",
                name="Amul Taaza Toned Milk",
                brand="Amul",
                quantity=1000,
                unit=Unit.MILLILITER,
                offers=[PlatformOffer(platform=Platform.BLINKIT, platform_product_id="b1", price=56)],
            ),
        ]

        result = matcher.match_products(products)
        assert result.total_matched_products == 2  # Should be separate products
        assert result.products_with_single_offer == 2
        assert result.products_with_multiple_offers == 0

    def test_different_brands_do_not_match(self, matcher):
        """Test Amul and Britannia are separate products"""
        products = [
            NormalizedProduct(
                product_id="p1",
                name="Taaza Toned Milk",
                brand="Amul",
                quantity=500,
                unit=Unit.MILLILITER,
                offers=[PlatformOffer(platform=Platform.ZEPTO, platform_product_id="z1", price=28)],
            ),
            NormalizedProduct(
                product_id="p2",
                name="Taaza Toned Milk",
                brand="Britannia",
                quantity=500,
                unit=Unit.MILLILITER,
                offers=[PlatformOffer(platform=Platform.BLINKIT, platform_product_id="b1", price=26)],
            ),
        ]

        result = matcher.match_products(products)
        assert result.total_matched_products == 2

    def test_toned_vs_full_cream_do_not_match(self, matcher):
        """Test Toned Milk and Full Cream Milk are separate"""
        products = [
            NormalizedProduct(
                product_id="p1",
                name="Amul Toned Milk",
                brand="Amul",
                quantity=500,
                unit=Unit.MILLILITER,
                offers=[PlatformOffer(platform=Platform.ZEPTO, platform_product_id="z1", price=28)],
            ),
            NormalizedProduct(
                product_id="p2",
                name="Amul Full Cream Milk",
                brand="Amul",
                quantity=500,
                unit=Unit.MILLILITER,
                offers=[PlatformOffer(platform=Platform.BLINKIT, platform_product_id="b1", price=32)],
            ),
        ]

        result = matcher.match_products(products)
        assert result.total_matched_products == 2

    def test_organic_vs_regular_do_not_match(self, matcher):
        """Test Organic and Regular products are separate"""
        products = [
            NormalizedProduct(
                product_id="p1",
                name="Amul Organic Milk",
                brand="Amul",
                quantity=500,
                unit=Unit.MILLILITER,
                offers=[PlatformOffer(platform=Platform.ZEPTO, platform_product_id="z1", price=45)],
            ),
            NormalizedProduct(
                product_id="p2",
                name="Amul Toned Milk",
                brand="Amul",
                quantity=500,
                unit=Unit.MILLILITER,
                offers=[PlatformOffer(platform=Platform.BLINKIT, platform_product_id="b1", price=28)],
            ),
        ]

        result = matcher.match_products(products)
        assert result.total_matched_products == 2

    def test_lactose_free_vs_regular_do_not_match(self, matcher):
        """Test Lactose-Free and Regular are separate"""
        products = [
            NormalizedProduct(
                product_id="p1",
                name="Amul Lactose Free Milk",
                brand="Amul",
                quantity=500,
                unit=Unit.MILLILITER,
                offers=[PlatformOffer(platform=Platform.ZEPTO, platform_product_id="z1", price=38)],
            ),
            NormalizedProduct(
                product_id="p2",
                name="Amul Toned Milk",
                brand="Amul",
                quantity=500,
                unit=Unit.MILLILITER,
                offers=[PlatformOffer(platform=Platform.BLINKIT, platform_product_id="b1", price=28)],
            ),
        ]

        result = matcher.match_products(products)
        assert result.total_matched_products == 2


class TestProductMatchingPartialMatches:
    """Test products available on only some platforms"""

    @pytest.fixture
    def matcher(self):
        return ProductMatcher()

    def test_product_on_two_platforms_only(self, matcher):
        """Test product available on only 2 of 3 platforms"""
        products = [
            NormalizedProduct(
                product_id="p1",
                name="Amul Taaza Toned Milk",
                brand="Amul",
                quantity=500,
                unit=Unit.MILLILITER,
                offers=[PlatformOffer(platform=Platform.ZEPTO, platform_product_id="z1", price=28)],
            ),
            NormalizedProduct(
                product_id="p2",
                name="Amul Taaza Toned Milk",
                brand="Amul",
                quantity=500,
                unit=Unit.MILLILITER,
                offers=[PlatformOffer(platform=Platform.BLINKIT, platform_product_id="b1", price=29)],
            ),
        ]

        result = matcher.match_products(products)

        assert result.total_matched_products == 1
        assert result.products_with_multiple_offers == 1

        matched = result.matched_products[0]
        assert matched.available_platforms == 2
        assert matched.has_offer_from(Platform.ZEPTO)
        assert matched.has_offer_from(Platform.BLINKIT)
        assert not matched.has_offer_from(Platform.SWIGGY)

    def test_product_on_one_platform_only(self, matcher):
        """Test product available on only 1 platform"""
        products = [
            NormalizedProduct(
                product_id="p1",
                name="Amul Taaza Toned Milk",
                brand="Amul",
                quantity=500,
                unit=Unit.MILLILITER,
                offers=[PlatformOffer(platform=Platform.ZEPTO, platform_product_id="z1", price=28)],
            ),
        ]

        result = matcher.match_products(products)

        assert result.total_matched_products == 1
        assert result.products_with_single_offer == 1

        matched = result.matched_products[0]
        assert matched.available_platforms == 1
        assert len(matched.offers) == 1

    def test_multiple_distinct_products(self, matcher):
        """Test multiple different products, each on different platforms"""
        products = [
            NormalizedProduct(
                product_id="p1",
                name="Amul Taaza Toned Milk",
                brand="Amul",
                quantity=500,
                unit=Unit.MILLILITER,
                offers=[PlatformOffer(platform=Platform.ZEPTO, platform_product_id="z1", price=28)],
            ),
            NormalizedProduct(
                product_id="p2",
                name="Britannia Marie Gold",
                brand="Britannia",
                quantity=200,
                unit=Unit.GRAM,
                offers=[PlatformOffer(platform=Platform.BLINKIT, platform_product_id="b1", price=40)],
            ),
        ]

        result = matcher.match_products(products)

        assert result.total_matched_products == 2
        assert result.products_with_single_offer == 2
        assert result.products_with_multiple_offers == 0


class TestProductMatchingDuplicates:
    """Test handling of duplicate products"""

    @pytest.fixture
    def matcher(self):
        return ProductMatcher()

    def test_duplicate_from_same_platform_skipped(self, matcher):
        """Test that duplicate offers from same platform are skipped"""
        products = [
            NormalizedProduct(
                product_id="p1",
                name="Amul Taaza Toned Milk",
                brand="Amul",
                quantity=500,
                unit=Unit.MILLILITER,
                offers=[PlatformOffer(platform=Platform.ZEPTO, platform_product_id="z1", price=28)],
            ),
            NormalizedProduct(
                product_id="p2",
                name="Amul Taaza Toned Milk",
                brand="Amul",
                quantity=500,
                unit=Unit.MILLILITER,
                offers=[PlatformOffer(platform=Platform.ZEPTO, platform_product_id="z2", price=29)],
            ),
        ]

        result = matcher.match_products(products)

        assert result.total_matched_products == 1
        matched = result.matched_products[0]
        # Only one Zepto offer should be kept
        zepto_offers = [o for o in matched.offers if o.platform == Platform.ZEPTO]
        assert len(zepto_offers) == 1

    def test_same_product_multiple_identical_entries(self, matcher):
        """Test completely duplicate product entries"""
        products = [
            NormalizedProduct(
                product_id="p1",
                name="Amul Taaza Toned Milk",
                brand="Amul",
                quantity=500,
                unit=Unit.MILLILITER,
                offers=[PlatformOffer(platform=Platform.ZEPTO, platform_product_id="z1", price=28)],
            ),
            NormalizedProduct(
                product_id="p2",
                name="Amul Taaza Toned Milk",
                brand="Amul",
                quantity=500,
                unit=Unit.MILLILITER,
                offers=[PlatformOffer(platform=Platform.ZEPTO, platform_product_id="z1", price=28)],
            ),
        ]

        result = matcher.match_products(products)

        # Should match but not duplicate
        assert result.total_matched_products == 1
        assert len(result.matched_products[0].offers) == 1


class TestProductMatchingMissingFields:
    """Test handling of missing/optional fields"""

    @pytest.fixture
    def matcher(self):
        return ProductMatcher()

    def test_missing_brand_still_matches_same_product(self, matcher):
        """Test products without brand can match if names are equivalent"""
        products = [
            NormalizedProduct(
                product_id="p1",
                name="Taaza Toned Milk",
                brand=None,
                quantity=500,
                unit=Unit.MILLILITER,
                offers=[PlatformOffer(platform=Platform.ZEPTO, platform_product_id="z1", price=28)],
            ),
            NormalizedProduct(
                product_id="p2",
                name="Taaza Toned Milk",
                brand=None,
                quantity=500,
                unit=Unit.MILLILITER,
                offers=[PlatformOffer(platform=Platform.BLINKIT, platform_product_id="b1", price=29)],
            ),
        ]

        result = matcher.match_products(products)
        # Products with missing brand but same name should still match
        assert result.total_matched_products >= 1

    def test_missing_quantity_cannot_match(self, matcher):
        """Test products without quantity are treated as different"""
        products = [
            NormalizedProduct(
                product_id="p1",
                name="Amul Taaza Toned Milk",
                brand="Amul",
                quantity=None,
                unit=None,
                offers=[PlatformOffer(platform=Platform.ZEPTO, platform_product_id="z1", price=28)],
            ),
            NormalizedProduct(
                product_id="p2",
                name="Amul Taaza Toned Milk",
                brand="Amul",
                quantity=500,
                unit=Unit.MILLILITER,
                offers=[PlatformOffer(platform=Platform.BLINKIT, platform_product_id="b1", price=29)],
            ),
        ]

        result = matcher.match_products(products)
        # Missing quantity means these cannot be confidently matched
        # They should remain separate
        assert result.total_matched_products == 2


class TestProductMatchingComplexScenarios:
    """Test complex real-world scenarios"""

    @pytest.fixture
    def matcher(self):
        return ProductMatcher()

    def test_multiple_products_with_various_combinations(self, matcher):
        """Test matching with many products across platforms"""
        products = [
            # Same product on all 3 platforms
            NormalizedProduct(
                product_id="milk1_zepto",
                name="Amul Taaza Toned Milk",
                brand="Amul",
                quantity=500,
                unit=Unit.MILLILITER,
                offers=[PlatformOffer(platform=Platform.ZEPTO, platform_product_id="z1", price=28)],
            ),
            NormalizedProduct(
                product_id="milk1_blinkit",
                name="Amul Taaza Toned Milk",
                brand="Amul",
                quantity=500,
                unit=Unit.MILLILITER,
                offers=[PlatformOffer(platform=Platform.BLINKIT, platform_product_id="b1", price=29)],
            ),
            NormalizedProduct(
                product_id="milk1_swiggy",
                name="Amul Taaza Toned Milk",
                brand="Amul",
                quantity=0.5,
                unit=Unit.LITER,
                offers=[PlatformOffer(platform=Platform.SWIGGY, platform_product_id="s1", price=30)],
            ),
            # Different quantity - separate product
            NormalizedProduct(
                product_id="milk2_zepto",
                name="Amul Taaza Toned Milk",
                brand="Amul",
                quantity=1000,
                unit=Unit.MILLILITER,
                offers=[PlatformOffer(platform=Platform.ZEPTO, platform_product_id="z2", price=56)],
            ),
            # Different variant - separate product
            NormalizedProduct(
                product_id="milk3_blinkit",
                name="Amul Full Cream Milk",
                brand="Amul",
                quantity=500,
                unit=Unit.MILLILITER,
                offers=[PlatformOffer(platform=Platform.BLINKIT, platform_product_id="b2", price=32)],
            ),
            # Completely different product
            NormalizedProduct(
                product_id="bread1_zepto",
                name="Britannia Toast Bread",
                brand="Britannia",
                quantity=400,
                unit=Unit.GRAM,
                offers=[PlatformOffer(platform=Platform.ZEPTO, platform_product_id="z3", price=45)],
            ),
        ]

        result = matcher.match_products(products)

        # Should have 4 distinct products:
        # 1. Amul Taaza Toned 500ml (3 platforms)
        # 2. Amul Taaza Toned 1000ml (1 platform)
        # 3. Amul Full Cream 500ml (1 platform)
        # 4. Britannia Toast (1 platform)
        assert result.total_input_products == 6
        assert result.total_matched_products == 4
        assert result.products_with_multiple_offers == 1
        assert result.products_with_single_offer == 3

        # Find the matched product with 3 offers
        three_offer_product = next(
            (p for p in result.matched_products if len(p.offers) == 3),
            None
        )
        assert three_offer_product is not None
        assert three_offer_product.available_platforms == 3
        assert three_offer_product.lowest_price == 28
        assert three_offer_product.highest_price == 30


class TestProductMatchingHelperMethods:
    """Test helper methods for debugging and inspection"""

    @pytest.fixture
    def matcher(self):
        return ProductMatcher()

    def test_are_products_matchable(self, matcher):
        """Test the are_products_matchable helper method"""
        product1 = NormalizedProduct(
            product_id="p1",
            name="Amul Taaza Toned Milk",
            brand="Amul",
            quantity=500,
            unit=Unit.MILLILITER,
            offers=[PlatformOffer(platform=Platform.ZEPTO, platform_product_id="z1", price=28)],
        )

        product2_same = NormalizedProduct(
            product_id="p2",
            name="Amul Taaza Toned Milk",
            brand="Amul",
            quantity=500,
            unit=Unit.MILLILITER,
            offers=[PlatformOffer(platform=Platform.BLINKIT, platform_product_id="b1", price=29)],
        )

        product3_diff_qty = NormalizedProduct(
            product_id="p3",
            name="Amul Taaza Toned Milk",
            brand="Amul",
            quantity=1000,
            unit=Unit.MILLILITER,
            offers=[PlatformOffer(platform=Platform.SWIGGY, platform_product_id="s1", price=56)],
        )

        assert matcher.are_products_matchable(product1, product2_same) is True
        assert matcher.are_products_matchable(product1, product3_diff_qty) is False

    def test_get_match_key_string(self, matcher):
        """Test the get_match_key_string helper for debugging"""
        product = NormalizedProduct(
            product_id="p1",
            name="Amul Taaza Toned Milk",
            brand="Amul",
            quantity=500,
            unit=Unit.MILLILITER,
            offers=[PlatformOffer(platform=Platform.ZEPTO, platform_product_id="z1", price=28)],
        )

        match_key_str = matcher.get_match_key_string(product)

        # Should contain relevant parts
        assert "amul" in match_key_str.lower()
        assert "toned" in match_key_str.lower()
        assert "500" in match_key_str or "ml" in match_key_str

    def test_match_result_statistics(self, matcher):
        """Test that MatchResult calculates correct statistics"""
        products = [
            NormalizedProduct(
                product_id="p1",
                name="Amul Taaza Toned Milk",
                brand="Amul",
                quantity=500,
                unit=Unit.MILLILITER,
                offers=[PlatformOffer(platform=Platform.ZEPTO, platform_product_id="z1", price=28)],
            ),
            NormalizedProduct(
                product_id="p2",
                name="Amul Taaza Toned Milk",
                brand="Amul",
                quantity=500,
                unit=Unit.MILLILITER,
                offers=[PlatformOffer(platform=Platform.BLINKIT, platform_product_id="b1", price=29)],
            ),
            NormalizedProduct(
                product_id="p3",
                name="Britannia Bread",
                brand="Britannia",
                quantity=400,
                unit=Unit.GRAM,
                offers=[PlatformOffer(platform=Platform.ZEPTO, platform_product_id="z2", price=40)],
            ),
        ]

        result = matcher.match_products(products)

        assert result.total_input_products == 3
        assert result.total_matched_products == 2
        assert result.products_with_multiple_offers == 1  # Milk
        assert result.products_with_single_offer == 1  # Bread
        assert result.match_rate > 0  # Should be calculated
        assert len(result.matched_products) == 2


class TestProductMatchingVariantExtraction:
    """Test extraction and matching of product variants"""

    @pytest.fixture
    def matcher(self):
        return ProductMatcher()

    def test_extract_milk_variants(self, matcher):
        """Test extraction of milk-specific variants"""
        # Toned milk
        p1 = NormalizedProduct(
            product_id="p1",
            name="Amul Toned Milk 500ml",
            brand="Amul",
            quantity=500,
            unit=Unit.MILLILITER,
            offers=[PlatformOffer(platform=Platform.ZEPTO, platform_product_id="z1", price=28)],
        )
        key1 = matcher._extract_match_key(p1)
        assert "toned" in key1.variants

        # Full cream milk
        p2 = NormalizedProduct(
            product_id="p2",
            name="Amul Full Cream Milk 500ml",
            brand="Amul",
            quantity=500,
            unit=Unit.MILLILITER,
            offers=[PlatformOffer(platform=Platform.BLINKIT, platform_product_id="b1", price=32)],
        )
        key2 = matcher._extract_match_key(p2)
        assert "full cream" in key2.variants

        # Lactose-free
        p3 = NormalizedProduct(
            product_id="p3",
            name="Amul Lactose-Free Milk 500ml",
            brand="Amul",
            quantity=500,
            unit=Unit.MILLILITER,
            offers=[PlatformOffer(platform=Platform.SWIGGY, platform_product_id="s1", price=38)],
        )
        key3 = matcher._extract_match_key(p3)
        assert "lactose free" in key3.variants or "lactose-free" in key3.variants

        # All three should be different products
        assert key1 != key2
        assert key2 != key3
        assert key1 != key3

    def test_extract_base_name(self, matcher):
        """Test extraction of base name without variants"""
        product = NormalizedProduct(
            product_id="p1",
            name="Amul Taaza Toned Milk 500ml",
            brand="Amul",
            quantity=500,
            unit=Unit.MILLILITER,
            offers=[PlatformOffer(platform=Platform.ZEPTO, platform_product_id="z1", price=28)],
        )

        base_name = matcher._extract_base_name(product.name, matcher._extract_variants(product.name, product.brand))

        # Should have "milk" but not "toned"
        assert "milk" in base_name.lower()
        assert "toned" not in base_name.lower()

    def test_variants_with_hyphen_and_space(self, matcher):
        """Test that lactose-free and lactose free are treated as same"""
        products = [
            NormalizedProduct(
                product_id="p1",
                name="Amul Lactose-Free Milk",
                brand="Amul",
                quantity=500,
                unit=Unit.MILLILITER,
                offers=[PlatformOffer(platform=Platform.ZEPTO, platform_product_id="z1", price=38)],
            ),
            NormalizedProduct(
                product_id="p2",
                name="Amul Lactose Free Milk",
                brand="Amul",
                quantity=500,
                unit=Unit.MILLILITER,
                offers=[PlatformOffer(platform=Platform.BLINKIT, platform_product_id="b1", price=39)],
            ),
        ]

        result = matcher.match_products(products)

        # Should match despite different spelling
        assert result.total_matched_products == 1
        assert len(result.matched_products[0].offers) == 2
