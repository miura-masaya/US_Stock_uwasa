from nlp.pipeline import classify_context, extract_keywords, is_noise_or_bot
from scoring.score import confidence_score


def test_extract_keywords_and_context():
    text = "$TSLA rumor: hearing that a major AI contract may be announced"
    assert "$TSLA" in extract_keywords(text)
    assert classify_context(text) == "contract"


def test_noise_filter_and_score():
    assert is_noise_or_bot({"author": "spam_bot", "text": "buy 🚀"})
    score = confidence_score({
        "author_reliability": 1,
        "cross_community": 1,
        "news_consistency": 1,
        "market_anomaly": 1,
        "filing_timing": 1,
        "context_specificity": 1,
    })
    assert score == 100
