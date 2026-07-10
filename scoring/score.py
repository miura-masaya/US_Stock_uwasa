"""Confidence scoring for stock-rumor candidates."""
from __future__ import annotations


def clamp(value: float, low: float = 0, high: float = 100) -> float:
    return max(low, min(high, value))


def confidence_score(features: dict[str, float]) -> int:
    """Calculate a 0-100 rumor confidence score from weighted sub-scores."""
    weights = {
        "author_reliability": 20,
        "cross_community": 20,
        "news_consistency": 15,
        "market_anomaly": 20,
        "filing_timing": 10,
        "context_specificity": 15,
    }
    total = sum(clamp(float(features.get(name, 0)), 0, 1) * weight for name, weight in weights.items())
    return int(round(clamp(total)))
