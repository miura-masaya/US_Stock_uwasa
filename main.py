"""End-to-end orchestration for the US stock rumor monitoring skeleton."""
from __future__ import annotations

from collector.community import collect_reddit
from nlp.pipeline import classify_context, extract_keywords, is_noise_or_bot
from scoring.score import confidence_score
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


def analyze_posts(posts: list[dict]) -> list[dict]:
    results = []
    for post in posts:
        if is_noise_or_bot(post):
            continue
        keywords = extract_keywords(post["text"])
        context = classify_context(post["text"])
        score = confidence_score(
            {
                "author_reliability": 0.4,
                "cross_community": 0.2,
                "news_consistency": 0.3,
                "market_anomaly": 0.1,
                "filing_timing": 0.0,
                "context_specificity": 0.6 if context != "unknown" else 0.2,
            }
        )
        results.append({**post, "keywords": keywords, "context": context, "confidence_score": score})
    return results


def main() -> None:
    posts = collect_reddit(demo_fetcher, "wallstreetbets", limit=10)
    results = analyze_posts(posts)
    save_json(results, "data/results.json")
    for result in results:
        if result["confidence_score"] >= 70:
            print(f"通知対象: {result['symbol']} score={result['confidence_score']}")


if __name__ == "__main__":
    main()
