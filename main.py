"""End-to-end orchestration for the US stock rumor monitoring skeleton."""
from __future__ import annotations

from collections import defaultdict
from typing import Any, Callable

from collector.community import collect_reddit
from nlp.pipeline import (
    classify_context,
    extract_entities,
    extract_keywords,
    is_noise_or_bot,
    specificity_score,
)
from scoring.score import (
    BUY_SIGNAL_THRESHOLD,
    author_reliability_score,
    confidence_score,
    cross_community_score,
    filing_timing_score,
    market_anomaly_score,
    news_consistency_score,
)
from storage import save_json


def demo_fetcher(_: str, __: int):
    return [
        {
            "symbol": "TSLA",
            "author": "example_trader",
            "text": "$TSLA rumor: hearing that strategic AI/space partnership details may be announced soon",
            "url": "https://example.com/rumor/tsla",
            "score": 12,
        }
    ]


def _empty_provider(_: str) -> dict[str, Any]:
    return {}


def _empty_news_provider(_: str) -> list[dict[str, Any]]:
    return []


def _empty_filing_provider(_: str) -> list[dict[str, Any]]:
    return []


def analyze_posts(
    posts: list[dict[str, Any]],
    market_provider: Callable[[str], dict[str, Any]] = _empty_provider,
    news_provider: Callable[[str], list[dict[str, Any]]] = _empty_news_provider,
    filing_provider: Callable[[str], list[dict[str, Any]]] = _empty_filing_provider,
) -> list[dict[str, Any]]:
    """Analyze rumor posts and return JSON-ready buy-signal candidates scoring 70+."""
    enriched: list[dict[str, Any]] = []
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for post in posts:
        if is_noise_or_bot(post):
            continue
        entities = extract_entities(post.get("text", ""), post.get("symbol"))
        keywords = extract_keywords(post.get("text", ""))
        context = classify_context(post.get("text", ""))
        base = {**post, "entities": entities, "keywords": keywords, "context": context}
        enriched.append(base)
        for entity in entities:
            grouped[entity["ticker"]].append(base)

    results: list[dict[str, Any]] = []
    for ticker, ticker_posts in grouped.items():
        market = market_provider(ticker)
        news = news_provider(ticker)
        filings = filing_provider(ticker)
        specificity = max(specificity_score(post["text"], post["entities"]) for post in ticker_posts)
        author = max(author_reliability_score(post) for post in ticker_posts)
        features = {
            "specificity": specificity,
            "author_reliability": author,
            "cross_community": cross_community_score(ticker_posts),
            "market_anomaly": market_anomaly_score(market),
            "news_consistency": news_consistency_score(news),
            "filing_timing": filing_timing_score(filings),
        }
        score = confidence_score(features)
        if score < BUY_SIGNAL_THRESHOLD:
            continue
        reasons = build_reasons(features, ticker_posts)
        results.append(
            {
                "ticker": ticker,
                "score": score,
                "reason": reasons,
                "features": features,
                "sources": sorted({post.get("source", "unknown") for post in ticker_posts}),
                "urls": [post.get("url", "") for post in ticker_posts if post.get("url")],
            }
        )
    return sorted(results, key=lambda item: item["score"], reverse=True)


def build_reasons(features: dict[str, float], posts: list[dict[str, Any]]) -> list[str]:
    """Create concise Japanese reasons for the buy-signal JSON output."""
    reasons: list[str] = []
    if features["specificity"] >= 0.7:
        reasons.append("企業名・契約名・日付など噂の具体性が高い")
    if features["author_reliability"] >= 0.7:
        reasons.append("発信者の信頼度が高い")
    if features["cross_community"] >= 0.67:
        reasons.append("Reddit・X・Stocktwitsなど複数コミュニティで同時発生")
    if features["market_anomaly"] >= 0.7:
        reasons.append("出来高・オプション・ダークプールに異常値")
    if features["news_consistency"] >= 0.7:
        reasons.append("過去ニュースとの整合性がある")
    if features["filing_timing"] >= 0.6:
        reasons.append("8-K・10-K・13Fなど公式書類の提出タイミングが近い")
    contexts = sorted({post["context"] for post in posts if post["context"] != "unknown"})
    if contexts:
        reasons.append("文脈分類: " + ", ".join(contexts))
    return reasons


def main() -> None:
    posts = collect_reddit(demo_fetcher, "wallstreetbets", limit=10)
    results = analyze_posts(posts)
    save_json(results, "data/results.json")
    for result in results:
        print(result)


if __name__ == "__main__":
    main()
