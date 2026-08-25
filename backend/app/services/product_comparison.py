"""
Product Comparison Service (PHASE 4)

This service implements comprehensive product comparison across platforms.
It uses the matched products from Phase 3 and calculates:
- Price comparisons (lowest, highest, difference, savings)
- Delivery comparisons (fastest, slowest)
- Platform availability
- Best overall platform (using configurable scoring)

All calculations only consider offers marked as available.
"""

from typing import Optional, List, Dict
from dataclasses import dataclass
from enum import Enum

from app.schemas.product import PlatformOffer, Platform
from app.schemas.matching import MatchedProduct
from app.services.scoring import PlatformScorer, ScoringWeights, ScoringResult


class ComparisonMetric(str, Enum):
    """Types of comparison metrics available"""

    LOWEST_PRICE = "lowest_price"
    HIGHEST_PRICE = "highest_price"
    PRICE_DIFFERENCE = "price_difference"
    POTENTIAL_SAVINGS = "potential_savings"
    CHEAPEST_PLATFORM = "cheapest_platform"
    FASTEST_DELIVERY = "fastest_delivery"
    FASTEST_PLATFORM = "fastest_platform"
    AVAILABLE_PLATFORMS = "available_platforms"
    TOTAL_PLATFORMS = "total_platforms"
    BEST_OVERALL = "best_overall"


@dataclass
class ProductComparison:
    """
    Comprehensive comparison data for a single matched product.

    All metrics are calculated based on available offers only.
    """

    # Input product
    product: MatchedProduct

    # Price metrics
    lowest_price: Optional[float] = None
    highest_price: Optional[float] = None
    price_difference: Optional[float] = None
    cheapest_platform: Optional[Platform] = None
    potential_savings: Optional[float] = None  # Savings compared to highest price

    # Delivery metrics
    fastest_delivery_time: Optional[int] = None
    fastest_platform: Optional[Platform] = None

    # Availability metrics
    available_platforms: int = 0
    total_platforms: int = 0

    # Best overall (from scoring algorithm)
    best_overall_platform: Optional[Platform] = None
    best_overall_score: Optional[float] = None

    # Detailed scoring breakdown (optional)
    scoring_result: Optional[ScoringResult] = None

    # Rankings
    ranked_platforms: List[tuple[Platform, float]] = None  # [(platform, score), ...]

    def __post_init__(self):
        """Initialize derived fields"""
        if self.ranked_platforms is None:
            self.ranked_platforms = []

    @property
    def has_multiple_platforms(self) -> bool:
        """Check if product is available on multiple platforms"""
        return self.available_platforms > 1

    @property
    def has_savings_potential(self) -> bool:
        """Check if there's potential for savings"""
        return (
            self.price_difference is not None
            and self.price_difference > 0
            and self.has_multiple_platforms
        )

    @property
    def savings_percentage(self) -> Optional[float]:
        """Calculate savings as percentage of highest price"""
        if not self.highest_price or self.highest_price == 0:
            return None
        if self.potential_savings is None:
            return None
        return round((self.potential_savings / self.highest_price) * 100, 2)


class ProductComparisonService:
    """
    Service for calculating product comparisons across platforms.

    This service:
    1. Analyzes price differences across platforms
    2. Identifies cheapest and fastest options
    3. Calculates potential savings
    4. Uses scoring algorithm to determine best overall platform
    5. Handles edge cases (missing data, unavailable offers, ties)
    """

    def __init__(self, scorer: Optional[PlatformScorer] = None):
        """
        Initialize the comparison service.

        Args:
            scorer: Optional custom scorer, defaults to 60/30/10 weights
        """
        self.scorer = scorer or PlatformScorer()

    def compare_product(self, product: MatchedProduct) -> ProductComparison:
        """
        Perform comprehensive comparison on a single matched product.

        Args:
            product: The matched product to analyze

        Returns:
            ProductComparison with all calculated metrics
        """
        if not product.offers:
            return self._create_empty_comparison(product)

        # Get only available offers
        available_offers = [o for o in product.offers if o.available]

        if not available_offers:
            return self._create_empty_comparison(product)

        # Calculate price metrics
        price_metrics = self._calculate_price_metrics(available_offers)

        # Calculate delivery metrics
        delivery_metrics = self._calculate_delivery_metrics(available_offers)

        # Calculate availability metrics
        total_platforms = len(product.offers)
        available_platforms = len(available_offers)

        # Calculate best overall using scoring
        scoring_result = self._score_offers(available_offers)
        best_overall_platform = scoring_result.get_best_platform() if scoring_result else None
        best_overall_score = scoring_result.get_best_score() if scoring_result else None

        # Get ranked platforms from scoring result
        ranked_platforms = scoring_result.get_ranked_platforms() if scoring_result else []

        return ProductComparison(
            product=product,
            lowest_price=price_metrics["lowest_price"],
            highest_price=price_metrics["highest_price"],
            price_difference=price_metrics["price_difference"],
            cheapest_platform=price_metrics["cheapest_platform"],
            potential_savings=price_metrics["potential_savings"],
            fastest_delivery_time=delivery_metrics["fastest_time"],
            fastest_platform=delivery_metrics["fastest_platform"],
            available_platforms=available_platforms,
            total_platforms=total_platforms,
            best_overall_platform=best_overall_platform,
            best_overall_score=best_overall_score,
            scoring_result=scoring_result,
            ranked_platforms=ranked_platforms,
        )

    def _create_empty_comparison(self, product: MatchedProduct) -> ProductComparison:
        """Create comparison for product with no available offers"""
        return ProductComparison(
            product=product,
            available_platforms=0,
            total_platforms=len(product.offers),
        )

    def _calculate_price_metrics(self, offers: List[PlatformOffer]) -> Dict:
        """
        Calculate price-related metrics from available offers.

        Returns dict with:
        - lowest_price: Minimum price
        - highest_price: Maximum price
        - price_difference: Difference between highest and lowest
        - cheapest_platform: Platform with lowest price
        - potential_savings: Amount saved by choosing cheapest
        """
        # Filter offers with prices
        offers_with_prices = [o for o in offers if o.price is not None]

        if not offers_with_prices:
            return {
                "lowest_price": None,
                "highest_price": None,
                "price_difference": None,
                "cheapest_platform": None,
                "potential_savings": None,
            }

        # Find lowest and highest prices
        prices = [(o.price, o) for o in offers_with_prices]
        lowest_price, cheapest_offer = min(prices, key=lambda x: x[0])
        highest_price, _ = max(prices, key=lambda x: x[0])

        price_difference = highest_price - lowest_price
        potential_savings = price_difference if price_difference > 0 else 0

        # Handle ties: if multiple offers have same lowest price, prefer faster delivery
        cheapest_offers = [o for o in offers_with_prices if o.price == lowest_price]
        if len(cheapest_offers) > 1:
            # Pick the one with fastest delivery
            cheapest_offer = min(
                cheapest_offers,
                key=lambda o: o.delivery_time_minutes if o.delivery_time_minutes else float("inf"),
            )

        return {
            "lowest_price": lowest_price,
            "highest_price": highest_price,
            "price_difference": price_difference,
            "cheapest_platform": cheapest_offer.platform,
            "potential_savings": potential_savings,
        }

    def _calculate_delivery_metrics(self, offers: List[PlatformOffer]) -> Dict:
        """
        Calculate delivery-related metrics from available offers.

        Returns dict with:
        - fastest_time: Minimum delivery time
        - fastest_platform: Platform with fastest delivery
        """
        # Filter offers with delivery times
        offers_with_delivery = [o for o in offers if o.delivery_time_minutes is not None]

        if not offers_with_delivery:
            return {
                "fastest_time": None,
                "fastest_platform": None,
            }

        # Find fastest delivery
        delivery_times = [(o.delivery_time_minutes, o) for o in offers_with_delivery]
        fastest_time, fastest_offer = min(delivery_times, key=lambda x: x[0])

        # Handle ties: if multiple offers have same delivery time, prefer lower price
        fastest_offers = [o for o in offers_with_delivery if o.delivery_time_minutes == fastest_time]
        if len(fastest_offers) > 1:
            # Pick the one with lowest price
            fastest_offer = min(
                fastest_offers,
                key=lambda o: o.price if o.price is not None else float("inf"),
            )

        return {
            "fastest_time": fastest_time,
            "fastest_platform": fastest_offer.platform,
        }

    def _score_offers(self, offers: List[PlatformOffer]) -> Optional[ScoringResult]:
        """
        Score offers using the scoring algorithm.

        Returns:
            ScoringResult with detailed breakdowns
        """
        if not offers:
            return None

        scores = self.scorer.score_offers(offers)

        return ScoringResult(
            offers=offers,
            scores=scores,
            weights=self.scorer.weights,
        )

    def compare_products(self, products: List[MatchedProduct]) -> List[ProductComparison]:
        """
        Compare multiple products.

        Args:
            products: List of matched products to compare

        Returns:
            List of ProductComparison objects
        """
        return [self.compare_product(product) for product in products]

    def get_metric(self, product: MatchedProduct, metric: ComparisonMetric) -> Optional:
        """
        Get a specific metric for a product.

        Convenience method for single metric access.

        Args:
            product: The matched product
            metric: The metric to retrieve

        Returns:
            The metric value (type depends on metric)
        """
        comparison = self.compare_product(product)

        metric_map = {
            ComparisonMetric.LOWEST_PRICE: comparison.lowest_price,
            ComparisonMetric.HIGHEST_PRICE: comparison.highest_price,
            ComparisonMetric.PRICE_DIFFERENCE: comparison.price_difference,
            ComparisonMetric.POTENTIAL_SAVINGS: comparison.potential_savings,
            ComparisonMetric.CHEAPEST_PLATFORM: comparison.cheapest_platform,
            ComparisonMetric.FASTEST_DELIVERY: comparison.fastest_delivery_time,
            ComparisonMetric.FASTEST_PLATFORM: comparison.fastest_platform,
            ComparisonMetric.AVAILABLE_PLATFORMS: comparison.available_platforms,
            ComparisonMetric.TOTAL_PLATFORMS: comparison.total_platforms,
            ComparisonMetric.BEST_OVERALL: comparison.best_overall_platform,
        }

        return metric_map.get(metric)

    def get_platform_offer(
        self,
        product: MatchedProduct,
        platform: Platform,
    ) -> Optional[PlatformOffer]:
        """
        Get the offer from a specific platform.

        Args:
            product: The matched product
            platform: The platform to get offer from

        Returns:
            The PlatformOffer if found, None otherwise
        """
        return product.get_offer_by_platform(platform)
