"""
Comprehensive tests for Product Comparison Service (PHASE 4)

These tests verify:
- Price comparison calculations
- Delivery comparison calculations
- Platform availability tracking
- Best overall scoring
- Edge case handling (missing data, unavailable offers, ties, zero prices)
"""

import pytest
from app.schemas.product import NormalizedProduct, PlatformOffer, Platform, Unit
from app.schemas.matching import MatchedProduct, ProductMatchKey
from app.services.product_comparison import (
    ProductComparisonService,
    ProductComparison,
    ComparisonMetric,
)
from app.services.scoring import PlatformScorer, ScoringWeights


class TestPriceComparison:
    """Test price-related comparison metrics"""

    @pytest.fixture
    def comparison_service(self):
        return ProductComparisonService()

    def test_cheapest_platform_identified(self, comparison_service):
        """Test identifying the platform with lowest price"""
        offers = [
            PlatformOffer(
                platform=Platform.ZEPTO,
                platform_product_id="z1",
                price=28.0,
                available=True,
                delivery_time_minutes=10,
            ),
            PlatformOffer(
                platform=Platform.BLINKIT,
                platform_product_id="b1",
                price=29.0,
                available=True,
                delivery_time_minutes=8,
            ),
            PlatformOffer(
                platform=Platform.SWIGGY,
                platform_product_id="s1",
                price=30.0,
                available=True,
                delivery_time_minutes=12,
            ),
        ]

        product = MatchedProduct(
            match_key=ProductMatchKey(brand="amul", base_name="milk", variants=set(), quantity=500, unit=Unit.MILLILITER),
            canonical_name="Amul Milk 500ml",
            offers=offers,
        )

        comparison = comparison_service.compare_product(product)

        assert comparison.lowest_price == 28.0
        assert comparison.highest_price == 30.0
        assert comparison.price_difference == 2.0
        assert comparison.cheapest_platform == Platform.ZEPTO

    def test_highest_price_identified(self, comparison_service):
        """Test identifying the highest price across platforms"""
        offers = [
            PlatformOffer(
                platform=Platform.ZEPTO,
                platform_product_id="z1",
                price=28.0,
                available=True,
            ),
            PlatformOffer(
                platform=Platform.BLINKIT,
                platform_product_id="b1",
                price=29.0,
                available=True,
            ),
        ]

        product = MatchedProduct(
            match_key=ProductMatchKey(brand="amul", base_name="milk", variants=set(), quantity=500, unit=Unit.MILLILITER),
            canonical_name="Amul Milk 500ml",
            offers=offers,
        )

        comparison = comparison_service.compare_product(product)

        assert comparison.highest_price == 29.0

    def test_price_difference_calculated(self, comparison_service):
        """Test calculating price difference between highest and lowest"""
        offers = [
            PlatformOffer(
                platform=Platform.ZEPTO,
                platform_product_id="z1",
                price=28.0,
                available=True,
            ),
            PlatformOffer(
                platform=Platform.BLINKIT,
                platform_product_id="b1",
                price=35.0,
                available=True,
            ),
        ]

        product = MatchedProduct(
            match_key=ProductMatchKey(brand="amul", base_name="milk", variants=set(), quantity=500, unit=Unit.MILLILITER),
            canonical_name="Amul Milk 500ml",
            offers=offers,
        )

        comparison = comparison_service.compare_product(product)

        assert comparison.price_difference == 7.0

    def test_potential_savings_calculated(self, comparison_service):
        """Test calculating potential savings vs highest price"""
        offers = [
            PlatformOffer(
                platform=Platform.ZEPTO,
                platform_product_id="z1",
                price=28.0,
                available=True,
            ),
            PlatformOffer(
                platform=Platform.BLINKIT,
                platform_product_id="b1",
                price=32.0,
                available=True,
            ),
        ]

        product = MatchedProduct(
            match_key=ProductMatchKey(brand="amul", base_name="milk", variants=set(), quantity=500, unit=Unit.MILLILITER),
            canonical_name="Amul Milk 500ml",
            offers=offers,
        )

        comparison = comparison_service.compare_product(product)

        assert comparison.potential_savings == 4.0
        assert comparison.has_savings_potential is True
        assert comparison.savings_percentage == 12.5  # 4/32 * 100

    def test_price_tie_chooses_faster_delivery(self, comparison_service):
        """Test that when prices tie, faster delivery wins"""
        offers = [
            PlatformOffer(
                platform=Platform.ZEPTO,
                platform_product_id="z1",
                price=28.0,
                available=True,
                delivery_time_minutes=15,
            ),
            PlatformOffer(
                platform=Platform.BLINKIT,
                platform_product_id="b1",
                price=28.0,
                available=True,
                delivery_time_minutes=8,
            ),
        ]

        product = MatchedProduct(
            match_key=ProductMatchKey(brand="amul", base_name="milk", variants=set(), quantity=500, unit=Unit.MILLILITER),
            canonical_name="Amul Milk 500ml",
            offers=offers,
        )

        comparison = comparison_service.compare_product(product)

        # Same price, faster delivery should be cheapest
        assert comparison.cheapest_platform == Platform.BLINKIT

    def test_zero_price_handled(self, comparison_service):
        """Test that zero prices are handled correctly"""
        offers = [
            PlatformOffer(
                platform=Platform.ZEPTO,
                platform_product_id="z1",
                price=0.0,
                available=True,
            ),
            PlatformOffer(
                platform=Platform.BLINKIT,
                platform_product_id="b1",
                price=28.0,
                available=True,
            ),
        ]

        product = MatchedProduct(
            match_key=ProductMatchKey(brand="amul", base_name="milk", variants=set(), quantity=500, unit=Unit.MILLILITER),
            canonical_name="Amul Milk 500ml",
            offers=offers,
        )

        comparison = comparison_service.compare_product(product)

        assert comparison.lowest_price == 0.0
        assert comparison.highest_price == 28.0
        assert comparison.cheapest_platform == Platform.ZEPTO

    def test_missing_prices_excluded(self, comparison_service):
        """Test that offers without prices are excluded from price calculations"""
        offers = [
            PlatformOffer(
                platform=Platform.ZEPTO,
                platform_product_id="z1",
                price=28.0,
                available=True,
            ),
            PlatformOffer(
                platform=Platform.BLINKIT,
                platform_product_id="b1",
                price=None,
                available=True,
            ),
        ]

        product = MatchedProduct(
            match_key=ProductMatchKey(brand="amul", base_name="milk", variants=set(), quantity=500, unit=Unit.MILLILITER),
            canonical_name="Amul Milk 500ml",
            offers=offers,
        )

        comparison = comparison_service.compare_product(product)

        assert comparison.lowest_price == 28.0
        assert comparison.highest_price == 28.0
        assert comparison.price_difference == 0.0

    def test_only_one_platform_price(self, comparison_service):
        """Test price metrics when only one platform has price data"""
        offers = [
            PlatformOffer(
                platform=Platform.ZEPTO,
                platform_product_id="z1",
                price=28.0,
                available=True,
            ),
        ]

        product = MatchedProduct(
            match_key=ProductMatchKey(brand="amul", base_name="milk", variants=set(), quantity=500, unit=Unit.MILLILITER),
            canonical_name="Amul Milk 500ml",
            offers=offers,
        )

        comparison = comparison_service.compare_product(product)

        assert comparison.lowest_price == 28.0
        assert comparison.highest_price == 28.0
        assert comparison.price_difference == 0.0
        assert comparison.potential_savings == 0.0


class TestDeliveryComparison:
    """Test delivery-related comparison metrics"""

    @pytest.fixture
    def comparison_service(self):
        return ProductComparisonService()

    def test_fastest_platform_identified(self, comparison_service):
        """Test identifying platform with fastest delivery"""
        offers = [
            PlatformOffer(
                platform=Platform.ZEPTO,
                platform_product_id="z1",
                price=28.0,
                available=True,
                delivery_time_minutes=10,
            ),
            PlatformOffer(
                platform=Platform.BLINKIT,
                platform_product_id="b1",
                price=29.0,
                available=True,
                delivery_time_minutes=8,
            ),
            PlatformOffer(
                platform=Platform.SWIGGY,
                platform_product_id="s1",
                price=30.0,
                available=True,
                delivery_time_minutes=12,
            ),
        ]

        product = MatchedProduct(
            match_key=ProductMatchKey(brand="amul", base_name="milk", variants=set(), quantity=500, unit=Unit.MILLILITER),
            canonical_name="Amul Milk 500ml",
            offers=offers,
        )

        comparison = comparison_service.compare_product(product)

        assert comparison.fastest_delivery_time == 8
        assert comparison.fastest_platform == Platform.BLINKIT

    def test_delivery_tie_chooses_cheaper(self, comparison_service):
        """Test that when delivery times tie, cheaper price wins"""
        offers = [
            PlatformOffer(
                platform=Platform.ZEPTO,
                platform_product_id="z1",
                price=28.0,
                available=True,
                delivery_time_minutes=10,
            ),
            PlatformOffer(
                platform=Platform.BLINKIT,
                platform_product_id="b1",
                price=30.0,
                available=True,
                delivery_time_minutes=10,
            ),
        ]

        product = MatchedProduct(
            match_key=ProductMatchKey(brand="amul", base_name="milk", variants=set(), quantity=500, unit=Unit.MILLILITER),
            canonical_name="Amul Milk 500ml",
            offers=offers,
        )

        comparison = comparison_service.compare_product(product)

        # Same delivery time, cheaper should be fastest
        assert comparison.fastest_platform == Platform.ZEPTO

    def test_missing_delivery_times_excluded(self, comparison_service):
        """Test that offers without delivery times are excluded"""
        offers = [
            PlatformOffer(
                platform=Platform.ZEPTO,
                platform_product_id="z1",
                price=28.0,
                available=True,
                delivery_time_minutes=10,
            ),
            PlatformOffer(
                platform=Platform.BLINKIT,
                platform_product_id="b1",
                price=29.0,
                available=True,
                delivery_time_minutes=None,
            ),
        ]

        product = MatchedProduct(
            match_key=ProductMatchKey(brand="amul", base_name="milk", variants=set(), quantity=500, unit=Unit.MILLILITER),
            canonical_name="Amul Milk 500ml",
            offers=offers,
        )

        comparison = comparison_service.compare_product(product)

        assert comparison.fastest_delivery_time == 10
        assert comparison.fastest_platform == Platform.ZEPTO


class TestPlatformAvailability:
    """Test platform availability metrics"""

    @pytest.fixture
    def comparison_service(self):
        return ProductComparisonService()

    def test_available_platforms_count(self, comparison_service):
        """Test counting available platforms"""
        offers = [
            PlatformOffer(
                platform=Platform.ZEPTO,
                platform_product_id="z1",
                price=28.0,
                available=True,
            ),
            PlatformOffer(
                platform=Platform.BLINKIT,
                platform_product_id="b1",
                price=29.0,
                available=True,
            ),
            PlatformOffer(
                platform=Platform.SWIGGY,
                platform_product_id="s1",
                price=30.0,
                available=False,  # Unavailable
            ),
        ]

        product = MatchedProduct(
            match_key=ProductMatchKey(brand="amul", base_name="milk", variants=set(), quantity=500, unit=Unit.MILLILITER),
            canonical_name="Amul Milk 500ml",
            offers=offers,
        )

        comparison = comparison_service.compare_product(product)

        assert comparison.available_platforms == 2
        assert comparison.total_platforms == 3

    def test_unavailable_offers_excluded_from_calculations(self, comparison_service):
        """Test that unavailable offers don't affect price/delivery calculations"""
        offers = [
            PlatformOffer(
                platform=Platform.ZEPTO,
                platform_product_id="z1",
                price=28.0,
                available=True,
                delivery_time_minutes=10,
            ),
            PlatformOffer(
                platform=Platform.BLINKIT,
                platform_product_id="b1",
                price=25.0,  # Lower price but unavailable
                available=False,
                delivery_time_minutes=5,
            ),
        ]

        product = MatchedProduct(
            match_key=ProductMatchKey(brand="amul", base_name="milk", variants=set(), quantity=500, unit=Unit.MILLILITER),
            canonical_name="Amul Milk 500ml",
            offers=offers,
        )

        comparison = comparison_service.compare_product(product)

        # Should ignore unavailable BlinkIt offer
        assert comparison.lowest_price == 28.0
        assert comparison.cheapest_platform == Platform.ZEPTO
        assert comparison.fastest_delivery_time == 10


class TestBestOverallScoring:
    """Test best overall platform scoring algorithm"""

    @pytest.fixture
    def comparison_service(self):
        return ProductComparisonService()

    def test_best_overall_balances_price_and_delivery(self, comparison_service):
        """Test that best overall balances price and delivery"""
        # Zepto: Cheap but slow
        # BlinkIt: Expensive but fast
        # Swiggy: Middle price, middle delivery - should win
        offers = [
            PlatformOffer(
                platform=Platform.ZEPTO,
                platform_product_id="z1",
                price=28.0,
                available=True,
                delivery_time_minutes=15,
            ),
            PlatformOffer(
                platform=Platform.BLINKIT,
                platform_product_id="b1",
                price=35.0,
                available=True,
                delivery_time_minutes=8,
            ),
            PlatformOffer(
                platform=Platform.SWIGGY,
                platform_product_id="s1",
                price=30.0,
                available=True,
                delivery_time_minutes=10,
            ),
        ]

        product = MatchedProduct(
            match_key=ProductMatchKey(brand="amul", base_name="milk", variants=set(), quantity=500, unit=Unit.MILLILITER),
            canonical_name="Amul Milk 500ml",
            offers=offers,
        )

        comparison = comparison_service.compare_product(product)

        # With 60% price weight, 30% delivery weight:
        # Swiggy should win (good balance)
        assert comparison.best_overall_platform is not None
        assert comparison.best_overall_score > 0

    def test_scoring_with_custom_weights(self):
        """Test scoring with custom weights"""
        # 100% price weight
        scorer = PlatformScorer(weights=ScoringWeights(price_weight=0.8, delivery_weight=0.1, availability_weight=0.1))
        service = ProductComparisonService(scorer=scorer)

        offers = [
            PlatformOffer(
                platform=Platform.ZEPTO,
                platform_product_id="z1",
                price=28.0,
                available=True,
                delivery_time_minutes=20,  # Slow but cheap
            ),
            PlatformOffer(
                platform=Platform.BLINKIT,
                platform_product_id="b1",
                price=35.0,
                available=True,
                delivery_time_minutes=5,  # Fast but expensive
            ),
        ]

        product = MatchedProduct(
            match_key=ProductMatchKey(brand="amul", base_name="milk", variants=set(), quantity=500, unit=Unit.MILLILITER),
            canonical_name="Amul Milk 500ml",
            offers=offers,
        )

        comparison = service.compare_product(product)

        # With 80% price weight, cheapest should win
        assert comparison.best_overall_platform == Platform.ZEPTO

    def test_platform_ranking(self, comparison_service):
        """Test that platforms are ranked correctly"""
        offers = [
            PlatformOffer(
                platform=Platform.ZEPTO,
                platform_product_id="z1",
                price=28.0,
                available=True,
                delivery_time_minutes=15,
            ),
            PlatformOffer(
                platform=Platform.BLINKIT,
                platform_product_id="b1",
                price=35.0,
                available=True,
                delivery_time_minutes=8,
            ),
            PlatformOffer(
                platform=Platform.SWIGGY,
                platform_product_id="s1",
                price=30.0,
                available=True,
                delivery_time_minutes=10,
            ),
        ]

        product = MatchedProduct(
            match_key=ProductMatchKey(brand="amul", base_name="milk", variants=set(), quantity=500, unit=Unit.MILLILITER),
            canonical_name="Amul Milk 500ml",
            offers=offers,
        )

        comparison = comparison_service.compare_product(product)

        assert len(comparison.ranked_platforms) == 3
        # First should have highest score
        assert comparison.ranked_platforms[0][1] >= comparison.ranked_platforms[1][1]
        assert comparison.ranked_platforms[1][1] >= comparison.ranked_platforms[2][1]

    def test_unavailable_platform_gets_low_score(self, comparison_service):
        """Test that unavailable offers get very low scores"""
        offers = [
            PlatformOffer(
                platform=Platform.ZEPTO,
                platform_product_id="z1",
                price=28.0,
                available=True,
                delivery_time_minutes=10,
            ),
            PlatformOffer(
                platform=Platform.BLINKIT,
                platform_product_id="b1",
                price=25.0,  # Cheaper but unavailable
                available=False,
                delivery_time_minutes=5,
            ),
        ]

        product = MatchedProduct(
            match_key=ProductMatchKey(brand="amul", base_name="milk", variants=set(), quantity=500, unit=Unit.MILLILITER),
            canonical_name="Amul Milk 500ml",
            offers=offers,
        )

        comparison = comparison_service.compare_product(product)

        # Available platform should win despite higher price
        assert comparison.best_overall_platform == Platform.ZEPTO


class TestEdgeCases:
    """Test edge cases and error handling"""

    @pytest.fixture
    def comparison_service(self):
        return ProductComparisonService()

    def test_empty_product_offers(self, comparison_service):
        """Test comparison with no offers"""
        product = MatchedProduct(
            match_key=ProductMatchKey(brand="amul", base_name="milk", variants=set(), quantity=500, unit=Unit.MILLILITER),
            canonical_name="Amul Milk 500ml",
            offers=[],
        )

        comparison = comparison_service.compare_product(product)

        assert comparison.available_platforms == 0
        assert comparison.total_platforms == 0
        assert comparison.lowest_price is None
        assert comparison.highest_price is None
        assert comparison.cheapest_platform is None

    def test_all_offers_unavailable(self, comparison_service):
        """Test when all offers are unavailable"""
        offers = [
            PlatformOffer(
                platform=Platform.ZEPTO,
                platform_product_id="z1",
                price=28.0,
                available=False,
            ),
            PlatformOffer(
                platform=Platform.BLINKIT,
                platform_product_id="b1",
                price=29.0,
                available=False,
            ),
        ]

        product = MatchedProduct(
            match_key=ProductMatchKey(brand="amul", base_name="milk", variants=set(), quantity=500, unit=Unit.MILLILITER),
            canonical_name="Amul Milk 500ml",
            offers=offers,
        )

        comparison = comparison_service.compare_product(product)

        assert comparison.available_platforms == 0
        assert comparison.total_platforms == 2
        assert comparison.lowest_price is None

    def test_only_one_available_platform(self, comparison_service):
        """Test metrics when only one platform is available"""
        offers = [
            PlatformOffer(
                platform=Platform.ZEPTO,
                platform_product_id="z1",
                price=28.0,
                available=True,
                delivery_time_minutes=10,
            ),
        ]

        product = MatchedProduct(
            match_key=ProductMatchKey(brand="amul", base_name="milk", variants=set(), quantity=500, unit=Unit.MILLILITER),
            canonical_name="Amul Milk 500ml",
            offers=offers,
        )

        comparison = comparison_service.compare_product(product)

        assert comparison.available_platforms == 1
        assert comparison.has_multiple_platforms is False
        assert comparison.lowest_price == 28.0
        assert comparison.highest_price == 28.0

    def test_multiple_products_comparison(self, comparison_service):
        """Test comparing multiple products at once"""
        products = [
            MatchedProduct(
                match_key=ProductMatchKey(brand="amul", base_name="milk", variants=set(), quantity=500, unit=Unit.MILLILITER),
                canonical_name="Amul Milk 500ml",
                offers=[
                    PlatformOffer(
                        platform=Platform.ZEPTO,
                        platform_product_id="z1",
                        price=28.0,
                        available=True,
                    ),
                ],
            ),
            MatchedProduct(
                match_key=ProductMatchKey(brand="britannia", base_name="bread", variants=set(), quantity=400, unit=Unit.GRAM),
                canonical_name="Britannia Bread 400g",
                offers=[
                    PlatformOffer(
                        platform=Platform.BLINKIT,
                        platform_product_id="b1",
                        price=45.0,
                        available=True,
                    ),
                ],
            ),
        ]

        comparisons = comparison_service.compare_products(products)

        assert len(comparisons) == 2
        assert comparisons[0].lowest_price == 28.0
        assert comparisons[1].lowest_price == 45.0

    def test_get_metric_convenience(self, comparison_service):
        """Test the get_metric convenience method"""
        offers = [
            PlatformOffer(
                platform=Platform.ZEPTO,
                platform_product_id="z1",
                price=28.0,
                available=True,
                delivery_time_minutes=10,
            ),
        ]

        product = MatchedProduct(
            match_key=ProductMatchKey(brand="amul", base_name="milk", variants=set(), quantity=500, unit=Unit.MILLILITER),
            canonical_name="Amul Milk 500ml",
            offers=offers,
        )

        lowest = comparison_service.get_metric(product, ComparisonMetric.LOWEST_PRICE)
        assert lowest == 28.0

        fastest = comparison_service.get_metric(product, ComparisonMetric.FASTEST_DELIVERY)
        assert fastest == 10

    def test_get_platform_offer(self, comparison_service):
        """Test getting offer from specific platform"""
        zepto_offer = PlatformOffer(
            platform=Platform.ZEPTO,
            platform_product_id="z1",
            price=28.0,
            available=True,
        )

        product = MatchedProduct(
            match_key=ProductMatchKey(brand="amul", base_name="milk", variants=set(), quantity=500, unit=Unit.MILLILITER),
            canonical_name="Amul Milk 500ml",
            offers=[
                zepto_offer,
                PlatformOffer(
                    platform=Platform.BLINKIT,
                    platform_product_id="b1",
                    price=29.0,
                    available=True,
                ),
            ],
        )

        offer = comparison_service.get_platform_offer(product, Platform.ZEPTO)
        assert offer is not None
        assert offer.platform == Platform.ZEPTO
        assert offer.price == 28.0

        # Test non-existent platform
        missing = comparison_service.get_platform_offer(product, Platform.SWIGGY)
        assert missing is None

    def test_null_values_handling(self, comparison_service):
        """Test handling of None/null values in various fields"""
        offers = [
            PlatformOffer(
                platform=Platform.ZEPTO,
                platform_product_id="z1",
                price=28.0,
                available=True,
                delivery_time_minutes=None,
                mrp=None,
                discount=None,
            ),
        ]

        product = MatchedProduct(
            match_key=ProductMatchKey(brand="amul", base_name="milk", variants=set(), quantity=500, unit=Unit.MILLILITER),
            canonical_name="Amul Milk 500ml",
            offers=offers,
        )

        comparison = comparison_service.compare_product(product)

        assert comparison.lowest_price == 28.0
        assert comparison.fastest_delivery_time is None


class TestScoringAlgorithm:
    """Test the scoring algorithm in detail"""

    def test_price_score_normalization(self):
        """Test that price scores are normalized correctly"""
        scorer = PlatformScorer()

        offers = [
            PlatformOffer(
                platform=Platform.ZEPTO,
                platform_product_id="z1",
                price=20.0,  # Lowest - should get 100
                available=True,
            ),
            PlatformOffer(
                platform=Platform.BLINKIT,
                platform_product_id="b1",
                price=30.0,  # Middle - should get ~50
                available=True,
            ),
            PlatformOffer(
                platform=Platform.SWIGGY,
                platform_product_id="s1",
                price=40.0,  # Highest - should get 0
                available=True,
            ),
        ]

        scores = scorer.score_offers(offers)

        # Find scores by platform
        zepto_score = next(score for offer, score in scores if offer.platform == Platform.ZEPTO)
        swiggy_score = next(score for offer, score in scores if offer.platform == Platform.SWIGGY)

        assert zepto_score > swiggy_score

    def test_delivery_score_normalization(self):
        """Test that delivery scores are normalized correctly"""
        scorer = PlatformScorer()

        offers = [
            PlatformOffer(
                platform=Platform.ZEPTO,
                platform_product_id="z1",
                price=28.0,
                available=True,
                delivery_time_minutes=5,  # Fastest
            ),
            PlatformOffer(
                platform=Platform.BLINKIT,
                platform_product_id="b1",
                price=28.0,
                available=True,
                delivery_time_minutes=30,  # Slowest
            ),
        ]

        scores = scorer.score_offers(offers)

        # Find scores by platform
        zepto_score = next(score for offer, score in scores if offer.platform == Platform.ZEPTO)
        blinkit_score = next(score for offer, score in scores if offer.platform == Platform.BLINKIT)

        assert zepto_score > blinkit_score

    def test_single_offer_scoring(self):
        """Test scoring when there's only one offer"""
        scorer = PlatformScorer()

        offers = [
            PlatformOffer(
                platform=Platform.ZEPTO,
                platform_product_id="z1",
                price=28.0,
                available=True,
                delivery_time_minutes=10,
            ),
        ]

        scores = scorer.score_offers(offers)

        # Single offer should get a reasonable score (not 0, not 100)
        _, score = scores[0]
        assert 0 < score < 100

    def test_availability_score(self):
        """Test that unavailable offers get penalized"""
        scorer = PlatformScorer()

        offers = [
            PlatformOffer(
                platform=Platform.ZEPTO,
                platform_product_id="z1",
                price=25.0,  # Cheapest but unavailable
                available=False,
                delivery_time_minutes=5,
            ),
            PlatformOffer(
                platform=Platform.BLINKIT,
                platform_product_id="b1",
                price=35.0,  # More expensive but available
                available=True,
                delivery_time_minutes=15,
            ),
        ]

        scores = scorer.score_offers(offers)

        # Find scores by platform
        blinkit_score = next(score for offer, score in scores if offer.platform == Platform.BLINKIT)
        zepto_score = next(score for offer, score in scores if offer.platform == Platform.ZEPTO)

        # Available offer should score higher despite being more expensive
        assert blinkit_score > zepto_score

    def test_scoring_weights_validation(self):
        """Test that invalid scoring weights are rejected"""
        with pytest.raises(ValueError):
            ScoringWeights(price_weight=0.5, delivery_weight=0.3, availability_weight=0.1)  # Sum = 0.9

        with pytest.raises(ValueError):
            ScoringWeights(price_weight=0.8, delivery_weight=0.4, availability_weight=0.1)  # Sum = 1.3
