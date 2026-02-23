"""Sentiment service tests."""

import pytest

from app.services.sentiment_service import analyze_sentiment


def test_positive_sentiment():
    """Positive words produce positive label and score."""
    label, score = analyze_sentiment("This is amazing and excellent!")
    assert label == "positive"
    assert score > 0


def test_negative_sentiment():
    """Negative words produce negative label and score."""
    label, score = analyze_sentiment("This is terrible and frustrating.")
    assert label == "negative"
    assert score < 0


def test_neutral_sentiment():
    """No strong sentiment words produce neutral."""
    label, score = analyze_sentiment("The button was clicked.")
    assert label == "neutral"
    assert -0.5 <= score <= 0.5


def test_empty_string():
    """Empty string returns neutral."""
    label, score = analyze_sentiment("")
    assert label == "neutral"
