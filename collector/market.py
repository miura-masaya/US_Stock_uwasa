"""Market-data collectors for volume, options, dark-pool, and EDGAR signals."""
from __future__ import annotations

from typing import Any, Callable


def get_market_snapshot(symbol: str, provider: Callable[[str], dict[str, Any]]) -> dict[str, Any]:
    """Return normalized market anomaly inputs for a ticker."""
    raw = provider(symbol)
    return {
        "symbol": symbol.upper(),
        "volume_zscore": float(raw.get("volume_zscore", 0) or 0),
        "options_volume_zscore": float(raw.get("options_volume_zscore", 0) or 0),
        "put_call_ratio": float(raw.get("put_call_ratio", 0) or 0),
        "dark_pool_premium": float(raw.get("dark_pool_premium", 0) or 0),
    }


def get_edgar_filings(symbol: str, provider: Callable[[str, list[str]], list[dict[str, Any]]]) -> list[dict[str, Any]]:
    """Fetch recent SEC filings relevant to rumor timing."""
    forms = ["8-K", "10-K", "10-Q", "13F-HR"]
    return provider(symbol.upper(), forms)
