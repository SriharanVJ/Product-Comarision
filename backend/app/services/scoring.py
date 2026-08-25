"""
Product Scoring Algorithm (PHASE 4)

This module implements the scoring algorithm for determining the "best" platform.
The scoring is configurable and isolated so it can be easily modified.

Initial scoring weights:
- Price: 60%
- Delivery: 30%
- Availability: 10%
"""

from typing import Optional, List
from dataclasses import dataclass
from app.schemas.product import PlatformOffer, Platform


@dataclass
class ScoringWeights:
    """
    Configurable weights for scoring algorithm.

    All weights should sum to 1.0 (100%).
    """

    price_weight: float = 0.60
    delivery_weight: float = 0.30
    availability_weight: float = 0.10

    def __post_init__(self):
        """Validate that weights sum to 1.0"""
        total = self.price_weight + self.delivery_weight + self.availability_weight
        if not (0.99 <= total <= 1.01):  # Allow small floating point errors
            raise ValueError(f"Scoring weights must sum to 1.0, got {total}")

    @classmethod
    def default(cls) -> "ScoringWeights":
        """Get default scoring weights"""
        return cls()


class PlatformScorer:
    """
    Scores platforms based on price, delivery, and availability.

    The scoring algorithm:
    1. Price Score: Lower prices get higher scores
    2. Delivery Score: Faster delivery gets higher scores
    3. Availability Score: Available offers get full points, unavailable get zero

    Final Score = (Price Score × Price Weight) +
                  (Delivery Score × Delivery Weight) +
                  (Availability Score × Availability Weight)
    """

    def __init__(self, weights: Optional[ScoringWeights] = None):
        """
        Initialize the scorer with optional custom weights.

        Args:
            weights: Custom scoring weights, defaults to 60/30/10
        """
        self.weights = weights or ScoringWeights.default()

    def score_offers(
        self,
        offers: List[PlatformOffer],
    ) -> List[tuple[PlatformOffer, float]]:
        """
        Score all offers and return a list of (offer, score) tuples.

        Args:
            offers: List of platform offers to score

        Returns:
            List of (offer, score) tuples with calculated scores (0-100)
        """
        if not offers:
            return []

        # Extract price and delivery data for normalization
        prices = [o.price for o in offers if o.price is not None and o.available]
        delivery_times = [
            o.delivery_time_minutes
            for o in offers
            if o.delivery_time_minutes is not None and o.available
        ]

        # Get min/max for normalization
        min_price = min(prices) if prices else None
        max_price = max(prices) if prices else None

        min_delivery = min(delivery_times) if delivery_times else None
        max_delivery = max(delivery_times) if delivery_times else None

        scores = []

        for offer in offers:
            score = self._calculate_offer_score(
                offer,
                min_price,
                max_price,
                min_delivery,
                max_delivery,
            )
            scores.append((offer, score))

        return scores

    def _calculate_offer_score(
        self,
        offer: PlatformOffer,
        min_price: Optional[float],
        max_price: Optional[float],
        min_delivery: Optional[int],
        max_delivery: Optional[int],
    ) -> float:
        """
        Calculate score for a single offer.

        Price Score (0-100):
        - If available with price: inversely proportional to price
        - Lower price = higher score
        - If unavailable or no price: 0

        Delivery Score (0-100):
        - If available with delivery time: inversely proportional to time
        - Faster delivery = higher score
        - If unavailable or no delivery time: 0

        Availability Score (0-100):
        - If available: 100
        - If unavailable: 0
        """
        price_score = self._calculate_price_score(offer.price, offer.available, min_price, max_price)
        delivery_score = self._calculate_delivery_score(
            offer.delivery_time_minutes,
            offer.available,
            min_delivery,
            max_delivery,
        )
        availability_score = self._calculate_availability_score(offer.available)

        # Weighted sum
        final_score = (
            (price_score * self.weights.price_weight)
            + (delivery_score * self.weights.delivery_weight)
            + (availability_score * self.weights.availability_weight)
        )

        return round(final_score, 2)

    def _calculate_price_score(
        self,
        price: Optional[float],
        available: bool,
        min_price: Optional[float],
        max_price: Optional[float],
    ) -> float:
        """
        Calculate price score (0-100).

        Lower prices get higher scores using inverse normalization.
        Score = 100 - ((price - min) / (max - min)) * 100

        If only one price available, give it a moderate score (80).
        """
        if not available or price is None:
            return 0.0

        if min_price is None or max_price is None:
            return 0.0

        # Handle edge case: only one price point
        if min_price == max_price:
            return 80.0  # Good score but not perfect (allows for delivery/availability to differentiate)

        # Calculate normalized score
        # Lowest price gets 100, highest gets 0
        price_range = max_price - min_price
        if price_range == 0:
            return 80.0

        relative_position = (price - min_price) / price_range
        score = 100.0 - (relative_position * 100.0)

        return max(0.0, min(100.0, score))

    def _calculate_delivery_score(
        self,
        delivery_time: Optional[int],
        available: bool,
        min_delivery: Optional[int],
        max_delivery: Optional[int],
    ) -> float:
        """
        Calculate delivery score (0-100).

        Faster delivery gets higher scores using inverse normalization.
        Score = 100 - ((time - min) / (max - min)) * 100

        If only one delivery time available, give it a moderate score (80).
        """
        if not available or delivery_time is None:
            return 0.0

        if min_delivery is None or max_delivery is None:
            return 0.0

        # Handle edge case: only one delivery time
        if min_delivery == max_delivery:
            return 80.0

        # Calculate normalized score
        # Fastest gets 100, slowest gets 0
        time_range = max_delivery - min_delivery
        if time_range == 0:
            return 80.0

        relative_position = (delivery_time - min_delivery) / time_range
        score = 100.0 - (relative_position * 100.0)

        return max(0.0, min(100.0, score))

    def _calculate_availability_score(self, available: bool) -> float:
        """
        Calculate availability score (0-100).

        Available = 100
        Unavailable = 0
        """
        return 100.0 if available else 0.0

    def get_best_offer(
        self,
        offers: List[PlatformOffer],
        scores: Optional[List[tuple[PlatformOffer, float]]] = None,
    ) -> Optional[PlatformOffer]:
        """
        Get the offer with the highest score.

        Args:
            offers: List of offers to choose from
            scores: Optional pre-calculated scores (will be calculated if not provided)

        Returns:
            The offer with the highest score, or None if no offers available
        """
        if not offers:
            return None

        if scores is None:
            scores = self.score_offers(offers)

        if not scores:
            return None

        # Find offer with highest score
        best_offer, _ = max(scores, key=lambda x: x[1])

        return best_offer

    def get_ranked_offers(
        self,
        offers: List[PlatformOffer],
    ) -> List[tuple[PlatformOffer, float]]:
        """
        Get offers ranked by score (highest to lowest).

        Args:
            offers: List of offers to rank

        Returns:
            List of (offer, score) tuples sorted by score descending
        """
        if not offers:
            return []

        scores = self.score_offers(offers)

        # Sort by score descending
        ranked = sorted(scores, key=lambda x: x[1], reverse=True)

        return ranked


class ScoringResult:
    """
    Result of scoring operation with detailed breakdowns.
    """

    def __init__(
        self,
        offers: List[PlatformOffer],
        scores: List[tuple[PlatformOffer, float]],
        weights: ScoringWeights,
    ):
        self.offers = offers
        self.scores = scores  # List of (offer, score) tuples
        self.weights = weights
        self.best_offer = max(scores, key=lambda x: x[1])[0] if scores else None

    def get_best_platform(self) -> Optional[Platform]:
        """Get the platform with the highest score"""
        return self.best_offer.platform if self.best_offer else None

    def get_best_score(self) -> Optional[float]:
        """Get the highest score"""
        if not self.scores:
            return None
        return max(score for _, score in self.scores)

    def get_ranked_platforms(self) -> List[tuple[Platform, float]]:
        """Get platforms ranked by score"""
        ranked = sorted(
            self.scores,
            key=lambda x: x[1],
            reverse=True,
        )
        return [(offer.platform, score) for offer, score in ranked]

    def get_score_for_platform(self, platform: Platform) -> Optional[float]:
        """Get score for a specific platform"""
        for offer, score in self.scores:
            if offer.platform == platform:
                return score
        return None

    def get_score_for_offer(self, offer: PlatformOffer) -> Optional[float]:
        """Get score for a specific offer"""
        for scored_offer, score in self.scores:
            if scored_offer == offer:
                return score
        return None
