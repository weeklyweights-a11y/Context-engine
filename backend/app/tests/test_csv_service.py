"""CSV service tests."""

import tempfile
from pathlib import Path

import pytest

from app.services.csv_service import (
    detect_customer_columns,
    detect_feedback_columns,
    parse_csv_file,
    validate_row,
)


def test_detect_feedback_columns_matches_known_headers():
    """Feedback column detection maps known headers."""
    headers = ["feedback", "source", "date", "rating", "company"]
    result = detect_feedback_columns(headers)
    assert result.get("text") == "feedback"
    assert result.get("source") == "source"
    assert result.get("date") == "date"
    assert result.get("rating") == "rating"
    assert result.get("customer_name") == "company"


def test_detect_customer_columns_matches_known_headers():
    """Customer column detection maps known headers."""
    headers = ["company_name", "segment", "mrr", "customer_id"]
    result = detect_customer_columns(headers)
    assert result.get("company_name") is not None
    assert result.get("segment") == "segment"
    assert result.get("mrr") == "mrr"


def test_parse_csv_file():
    """parse_csv_file produces rows with our field names."""
    path = Path(tempfile.gettempdir()) / "test_feedback.csv"
    path.write_text(
        "feedback,source,rating\n"
        "Great product,support_ticket,5\n"
        "Needs improvement,app_store,2\n",
        encoding="utf-8",
    )
    try:
        mapping = {"text": "feedback", "source": "source", "rating": "rating"}
        rows = parse_csv_file(path, mapping)
        assert len(rows) == 2
        assert rows[0]["text"] == "Great product"
        assert rows[0]["source"] == "support_ticket"
        assert rows[0]["rating"] == "5"
    finally:
        path.unlink(missing_ok=True)


def test_validate_row_required_fields():
    """validate_row rejects rows missing required fields."""
    valid, _ = validate_row({"text": "ok"}, ["text"])
    assert valid
    valid, err = validate_row({}, ["text"])
    assert not valid
    assert "text" in (err or "")
    valid, err = validate_row({"text": "  "}, ["text"])
    assert not valid
