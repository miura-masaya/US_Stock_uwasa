from datetime import datetime, timezone

from main import analyze_posts
from nlp.pipeline import classify_context, extract_entities, extract_keywords, is_noise_or_bot
from scoring.score import confidence_score, filing_timing_score


def test_extract_keywords_entities_and_context():
    text = "$TSLA rumor: hearing that a major AI contract may be announced"
    assert "$TSLA" in extract_keywords(text)
    assert {entity["ticker"] for entity in extract_entities(text)} == {"TSLA"}
    assert classify_context(text) == "contract"


def test_noise_filter_and_score():
    assert is_noise_or_bot({"author": "spam_bot", "text": "buy 🚀"})
    score = confidence_score({
        "specificity": 1,
        "author_reliability": 1,
        "cross_community": 1,
        "market_anomaly": 1,
        "news_consistency": 1,
        "filing_timing": 1,
    })
    assert score == 100


def test_filing_timing_score_recent_8k():
    score = filing_timing_score(
        [{"form": "8-K", "filed_at": "2026-07-09T00:00:00+00:00"}],
        now=datetime(2026, 7, 10, tzinfo=timezone.utc),
    )
    assert score == 1.0


def test_analyze_posts_returns_buy_signal_json():
    posts = [
        {
            "source": "reddit",
            "symbol": "OKLO",
            "author": "nuclear_analyst",
            "text": "$OKLO rumor: sources say Oklo signed a July 15 contract with Mega Utility for reactor power",
            "url": "https://reddit.example/oklo",
            "metrics": {"score": 120},
        },
        {
            "source": "x",
            "symbol": "OKLO",
            "author": "energy_insider",
            "text": "Hearing that OKLO contract approval with Mega Utility lands 2026-07-15",
            "url": "https://x.example/oklo",
            "metrics": {"likes": 250},
        },
        {
            "source": "stocktwits",
            "symbol": "OKLO",
            "author": "trader123",
            "text": "$OKLO unconfirmed contract leak matches prior utility partnership news",
            "url": "https://stocktwits.example/oklo",
            "metrics": {"likes": 40},
        },
    ]

    results = analyze_posts(
        posts,
        market_provider=lambda _: {"volume_zscore": 4.5, "options_volume_zscore": 3.5, "put_call_ratio": 0.5},
        news_provider=lambda _: [{"title": "Prior utility partnership", "consistent": True}],
        filing_provider=lambda _: [{"form": "8-K", "filed_at": "2026-07-09T00:00:00+00:00"}],
    )

    assert results == [
        {
            "ticker": "OKLO",
            "score": 95,
            "reason": [
                "企業名・契約名・日付など噂の具体性が高い",
                "発信者の信頼度が高い",
                "Reddit・X・Stocktwitsなど複数コミュニティで同時発生",
                "出来高・オプション・ダークプールに異常値",
                "過去ニュースとの整合性がある",
                "8-K・10-K・13Fなど公式書類の提出タイミングが近い",
                "文脈分類: contract",
            ],
            "features": {
                "specificity": 1.0,
                "author_reliability": 0.75,
                "cross_community": 1.0,
                "market_anomaly": 1,
                "news_consistency": 1.0,
                "filing_timing": 1.0,
            },
            "sources": ["reddit", "stocktwits", "x"],
            "urls": ["https://reddit.example/oklo", "https://x.example/oklo", "https://stocktwits.example/oklo"],
        }
    ]
