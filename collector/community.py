"""Community rumor collectors for Reddit, Stocktwits, and X.

The functions are dependency-injectable and return normalized dictionaries so
callers can test them without live network credentials.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Callable, Iterable


@dataclass(frozen=True)
class CommunityPost:
    source: str
    symbol: str | None
    author: str
    text: str
    url: str
    created_at: str
    metrics: dict[str, float]


def normalize_post(source: str, raw: dict[str, Any]) -> CommunityPost:
    """Normalize a provider-specific community post payload."""
    return CommunityPost(
        source=source,
        symbol=raw.get("symbol") or raw.get("ticker"),
        author=str(raw.get("author") or raw.get("user") or "unknown"),
        text=str(raw.get("text") or raw.get("body") or raw.get("message") or ""),
        url=str(raw.get("url") or raw.get("permalink") or ""),
        created_at=str(raw.get("created_at") or datetime.now(timezone.utc).isoformat()),
        metrics={k: float(raw.get(k, 0) or 0) for k in ("likes", "replies", "reposts", "score")},
    )


def collect_reddit(fetcher: Callable[[str, int], Iterable[dict[str, Any]]], subreddit: str, limit: int = 100) -> list[dict[str, Any]]:
    """Collect posts from a Reddit fetcher such as PRAW or a Pushshift wrapper."""
    return [asdict(normalize_post("reddit", post)) for post in fetcher(subreddit, limit)]


def collect_stocktwits(fetcher: Callable[[str, int], Iterable[dict[str, Any]]], symbol: str, limit: int = 100) -> list[dict[str, Any]]:
    """Collect messages for a symbol from a Stocktwits-compatible fetcher."""
    return [asdict(normalize_post("stocktwits", post)) for post in fetcher(symbol, limit)]


def collect_x(fetcher: Callable[[str, int], Iterable[dict[str, Any]]], query: str, limit: int = 100) -> list[dict[str, Any]]:
    """Collect X/Twitter posts from an injected API or scraping fetcher."""
    return [asdict(normalize_post("x", post)) for post in fetcher(query, limit)]
