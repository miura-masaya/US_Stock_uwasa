"""NLP utilities for rumor extraction, classification, and noise filtering."""
from __future__ import annotations

import re
from collections import Counter
from typing import Iterable

RUMOR_PATTERNS = [
    r"\brumou?r\b", r"\bleak(?:ed)?\b", r"\bhearing that\b", r"\bsources? say\b",
    r"\bunconfirmed\b", r"\btakeover\b", r"\bmerger\b", r"\bcontract\b",
    r"\bapproval\b", r"\bpartnership\b", r"\bacquisition\b", r"\bbuyout\b",
]
CATEGORIES = {
    "contract": ["contract", "deal", "customer", "partnership", "supplier", "award"],
    "regulation": ["fda", "sec", "doj", "approval", "ban", "probe", "clearance"],
    "technology": ["ai", "chip", "launch", "patent", "platform", "trial", "prototype"],
    "financial": ["earnings", "guidance", "buyback", "debt", "margin", "financing"],
    "personnel": ["ceo", "cfo", "resign", "hire", "layoff", "chairman"],
}
CONTEXT_SPECIFICITY_PATTERNS = [
    r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{1,2}\b",
    r"\b\d{4}-\d{2}-\d{2}\b",
    r"\b(?:q[1-4]|h[12])\s*\d{4}\b",
    r"\b(?:contract|agreement|mou|loi|approval|filing|8-k|10-k|13f)\b",
    r"\b(?:with|from|by)\s+[A-Z][A-Za-z&. -]{2,}\b",
]
KNOWN_COMPANIES = {
    "TESLA": "TSLA",
    "TESLA INC": "TSLA",
    "OKLO": "OKLO",
    "OKLO INC": "OKLO",
    "NVIDIA": "NVDA",
    "NVIDIA CORP": "NVDA",
    "APPLE": "AAPL",
    "MICROSOFT": "MSFT",
}


def extract_entities(text: str, symbol_hint: str | None = None) -> list[dict[str, str]]:
    """Extract cashtags, ticker-looking symbols, and known company names."""
    entities: dict[str, dict[str, str]] = {}
    if symbol_hint:
        ticker = symbol_hint.upper().lstrip("$")
        entities[ticker] = {"ticker": ticker, "name": ticker, "source": "symbol_hint"}
    for cashtag in re.findall(r"\$([A-Z]{1,5})\b", text):
        entities[cashtag] = {"ticker": cashtag, "name": cashtag, "source": "cashtag"}
    for name, ticker in KNOWN_COMPANIES.items():
        if re.search(rf"\b{re.escape(name)}\b", text, flags=re.IGNORECASE):
            entities[ticker] = {"ticker": ticker, "name": name.title(), "source": "company_name"}
    return sorted(entities.values(), key=lambda item: item["ticker"])


def extract_keywords(text: str) -> list[str]:
    """Extract rumor-trigger keywords and cashtags from text."""
    lowered = text.lower()
    hits = [re.sub(r"[^a-z ?]", "", pattern).strip() for pattern in RUMOR_PATTERNS if re.search(pattern, lowered)]
    cashtags = re.findall(r"\$[A-Z]{1,5}\b", text)
    return sorted(set(hits + cashtags))


def classify_context(text: str) -> str:
    """Classify rumor context into the supported business categories."""
    tokens = re.findall(r"[a-zA-Z0-9-]+", text.lower())
    counts = Counter(
        category for category, words in CATEGORIES.items() for token in tokens if token in words
    )
    return counts.most_common(1)[0][0] if counts else "unknown"


def specificity_score(text: str, entities: Iterable[dict[str, str]] | None = None) -> float:
    """Return 0-1 specificity based on named entities, dates, and concrete deal terms."""
    score = 0.0
    entity_count = len(list(entities or []))
    if entity_count:
        score += 0.35
    if entity_count > 1:
        score += 0.15
    matches = sum(1 for pattern in CONTEXT_SPECIFICITY_PATTERNS if re.search(pattern, text, re.IGNORECASE))
    score += min(matches, 3) * 0.2
    if len(re.findall(r"\b[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)+\b", text)):
        score += 0.1
    return min(score, 1.0)


def is_noise_or_bot(post: dict, min_text_length: int = 30) -> bool:
    """Flag likely bots, spam, and low-information posts."""
    text = str(post.get("text", ""))
    author = str(post.get("author", "")).lower()
    if len(text) < min_text_length or text.count("🚀") > 5:
        return True
    if any(marker in author for marker in ("bot", "auto", "spam")):
        return True
    urls = len(re.findall(r"https?://", text))
    if urls > 3 or text.lower().count("buy now") > 1:
        return True
    return len(set(text.split())) < 5
