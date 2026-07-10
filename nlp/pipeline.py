"""NLP utilities for rumor extraction, classification, and noise filtering."""
from __future__ import annotations

import re
from collections import Counter

RUMOR_PATTERNS = [
    r"\brumou?r\b", r"\bleak(?:ed)?\b", r"\bhearing that\b", r"\bsources? say\b",
    r"\bunconfirmed\b", r"\btakeover\b", r"\bmerger\b", r"\bcontract\b",
]
CATEGORIES = {
    "contract": ["contract", "deal", "customer", "partnership"],
    "regulation": ["fda", "sec", "doj", "approval", "ban", "probe"],
    "technology": ["ai", "chip", "launch", "patent", "platform"],
    "financial": ["earnings", "guidance", "buyback", "debt", "margin"],
    "personnel": ["ceo", "cfo", "resign", "hire", "layoff"],
}


def extract_keywords(text: str) -> list[str]:
    """Extract rumor-trigger keywords and cashtags from text."""
    lowered = text.lower()
    hits = [pattern.strip(r"\b") for pattern in RUMOR_PATTERNS if re.search(pattern, lowered)]
    cashtags = re.findall(r"\$[A-Z]{1,5}\b", text)
    return sorted(set(hits + cashtags))


def classify_context(text: str) -> str:
    """Classify rumor context into the supported business categories."""
    tokens = re.findall(r"[a-zA-Z]+", text.lower())
    counts = Counter(
        category for category, words in CATEGORIES.items() for token in tokens if token in words
    )
    return counts.most_common(1)[0][0] if counts else "unknown"


def is_noise_or_bot(post: dict, min_text_length: int = 30) -> bool:
    """Flag likely bots, spam, and low-information posts."""
    text = str(post.get("text", ""))
    author = str(post.get("author", "")).lower()
    if len(text) < min_text_length or text.count("🚀") > 5:
        return True
    if any(marker in author for marker in ("bot", "auto", "spam")):
        return True
    return len(set(text.split())) < 5
