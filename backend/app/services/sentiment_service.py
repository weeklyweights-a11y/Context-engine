"""Keyword-based sentiment analysis for feedback text."""

POSITIVE_KEYWORDS = {
    "great", "love", "excellent", "amazing", "helpful", "easy", "fast",
    "works well", "perfect", "wonderful", "fantastic", "smooth", "intuitive",
}
NEGATIVE_KEYWORDS = {
    "broken", "terrible", "hate", "slow", "confusing", "frustrated",
    "bug", "crash", "error", "issue", "awful", "useless", "worst",
}


def analyze_sentiment(text: str) -> tuple[str, float]:
    """
    Analyze sentiment using keyword matching.

    Returns:
        Tuple of (sentiment_label, sentiment_score).
        sentiment_label: "positive" | "negative" | "neutral"
        sentiment_score: float in [-1.0, 1.0]
    """
    if not text or not isinstance(text, str):
        return ("neutral", 0.0)

    lower = text.lower()
    pos_count = sum(1 for w in POSITIVE_KEYWORDS if w in lower)
    neg_count = sum(1 for w in NEGATIVE_KEYWORDS if w in lower)

    total = pos_count + neg_count
    if total == 0:
        return ("neutral", 0.0)

    score = (pos_count - neg_count) / max(total, 1)
    score = max(-1.0, min(1.0, score))

    if score > 0.1:
        label = "positive"
    elif score < -0.1:
        label = "negative"
    else:
        label = "neutral"

    return (label, round(score, 2))
