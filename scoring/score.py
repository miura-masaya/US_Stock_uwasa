"""Confidence scoring for stock-rumor candidates."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

BUY_SIGNAL_THRESHOLD = 70

WEIGHTS = {
    "specificity": 20,
    "author_reliability": 20,
    "cross_community": 15,
    "market_anomaly": 20,
    "news_consistency": 15,
    "filing_timing": 10,
}


def clamp(value: float, low: float = 0, high: float = 100) -> float:
    return max(low, min(high, value))


def confidence_score(features: dict[str, float]) -> int:
    """Calculate a 0-100 buy-signal score from the required weighted sub-scores."""
    total = sum(clamp(float(features.get(name, 0)), 0, 1) * weight for name, weight in WEIGHTS.items())
    return int(round(clamp(total)))


def author_reliability_score(post: dict[str, Any]) -> float:
    """Estimate source reliability from explicit metadata and engagement history."""
    if "author_reliability" in post:
        return clamp(float(post["author_reliability"]), 0, 1)
    author = str(post.get("author", "")).lower()
    if any(marker in author for marker in ("analyst", "expert", "insider", "ir", "sec")):
        return 0.75
    metrics = post.get("metrics", {}) or {}
    engagement = sum(float(metrics.get(name, 0) or 0) for name in ("likes", "replies", "reposts", "score"))
    return clamp(engagement / 100, 0.1, 0.6)


def cross_community_score(posts: list[dict[str, Any]]) -> float:
    """Score Reddit + X + Stocktwits style cross-community co-occurrence."""
    sources = {str(post.get("source", "")).lower() for post in posts if post.get("source")}
    return clamp(len(sources) / 3, 0, 1)


def market_anomaly_score(snapshot: dict[str, Any] | None) -> float:
    """Score abnormal volume, options skew, and dark-pool premium."""
    if not snapshot:
        return 0.0
    volume = clamp(float(snapshot.get("volume_zscore", 0) or 0) / 4, 0, 1)
    options = clamp(float(snapshot.get("options_volume_zscore", 0) or 0) / 4, 0, 1)
    put_call = 1 - clamp(abs(float(snapshot.get("put_call_ratio", 1) or 1) - 0.7) / 1.5, 0, 1)
    dark_pool = clamp(float(snapshot.get("dark_pool_premium", 0) or 0) / 0.15, 0, 1)
    return max(volume, options, dark_pool, put_call * 0.5)


def news_consistency_score(news_items: list[dict[str, Any]] | None) -> float:
    """Score whether prior news contains corroborating setup/foreshadowing."""
    if not news_items:
        return 0.0
    if any(item.get("consistent") is True for item in news_items):
        return 1.0
    return clamp(len(news_items) / 3, 0, 0.8)


def filing_timing_score(filings: list[dict[str, Any]] | None, now: datetime | None = None) -> float:
    """Score if 8-K/10-K/13F timing is close to the rumor window."""
    if not filings:
        return 0.0
    now = now or datetime.now(timezone.utc)
    best = 0.0
    for filing in filings:
        form = str(filing.get("form", "")).upper()
        raw_date = filing.get("filed_at") or filing.get("date")
        if form not in {"8-K", "10-K", "10-Q", "13F", "13F-HR"} or not raw_date:
            continue
        filed_at = datetime.fromisoformat(str(raw_date).replace("Z", "+00:00"))
        days = abs((now - filed_at).days)
        best = max(best, 1.0 if days <= 3 else 0.6 if days <= 14 else 0.2 if days <= 45 else 0.0)
    return best
