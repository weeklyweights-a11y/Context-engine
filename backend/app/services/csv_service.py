"""CSV parsing and column detection for feedback and customer uploads."""

import csv
from pathlib import Path
from typing import Any

FEEDBACK_HEADER_MAP: dict[str, list[str]] = {
    "text": [
        "feedback", "message", "text", "description", "content", "body",
        "comment", "note", "review", "request",
    ],
    "source": ["source", "source_type", "channel", "origin", "type"],
    "product_area": ["area", "product_area", "module", "feature", "category", "topic"],
    "customer_name": ["company", "customer", "organization", "org", "account", "company_name"],
    "author_name": ["name", "author", "user", "reviewer", "submitter"],
    "author_email": ["email", "customer_email", "user_email", "contact_email"],
    "date": ["date", "created", "created_at", "timestamp", "time", "submitted"],
    "sentiment": ["sentiment", "tone", "feeling"],
    "rating": ["rating", "score", "stars", "nps"],
}

CUSTOMER_HEADER_MAP: dict[str, list[str]] = {
    "company_name": [
        "company", "company_name", "customer", "organization", "org",
        "account", "name",
    ],
    "customer_id_external": ["id", "customer_id", "account_id", "external_id"],
    "segment": ["segment", "tier", "type", "plan_type", "customer_type"],
    "plan": ["plan", "plan_name", "subscription", "product"],
    "mrr": ["mrr", "monthly_revenue", "monthly"],
    "arr": ["arr", "annual_revenue", "annual", "revenue"],
    "account_manager": ["manager", "account_manager", "owner", "csm", "am"],
    "renewal_date": ["renewal", "renewal_date", "contract_end", "expiry"],
    "health_score": ["health", "health_score", "score", "nps"],
    "industry": ["industry", "vertical", "sector"],
    "employee_count": ["employees", "employee_count", "company_size", "size"],
}


def _match_header(our_field: str, headers: list[str], mapping: dict[str, list[str]]) -> str | None:
    """Match CSV header to our field using keyword mapping. Case-insensitive.
    Tries exact match first, then partial (header contains keyword or keyword in header words).
    """
    keywords = mapping.get(our_field, [])
    keywords_lower = {k.lower() for k in keywords}
    for h in headers:
        if not h:
            continue
        h_clean = h.strip().lower()
        if h_clean in keywords_lower:
            return h.strip()
        # Partial match: header contains keyword, or any header word matches a keyword
        for kw in keywords_lower:
            if kw in h_clean:
                return h.strip()
        words = h_clean.replace("-", " ").replace("_", " ").split()
        if any(w in keywords_lower for w in words):
            return h.strip()
    return None


def detect_feedback_columns(headers: list[str]) -> dict[str, str | None]:
    """Auto-map CSV headers to feedback fields. Returns dict of our_field -> csv_column."""
    result: dict[str, str | None] = {}
    for our_field in FEEDBACK_HEADER_MAP:
        matched = _match_header(our_field, headers, FEEDBACK_HEADER_MAP)
        result[our_field] = matched
    # Fallback: use first column for text if nothing matched (avoids stuck pending uploads)
    first = next((h.strip() for h in headers if h and h.strip()), None)
    if first and not result.get("text"):
        result["text"] = first
    return result


def detect_customer_columns(headers: list[str]) -> dict[str, str | None]:
    """Auto-map CSV headers to customer fields. Returns dict of our_field -> csv_column."""
    result: dict[str, str | None] = {}
    for our_field in CUSTOMER_HEADER_MAP:
        matched = _match_header(our_field, headers, CUSTOMER_HEADER_MAP)
        result[our_field] = matched
    # Fallback: use first column for company_name if nothing matched
    first = next((h.strip() for h in headers if h and h.strip()), None)
    if first and not result.get("company_name"):
        result["company_name"] = first
    return result


def parse_csv_file(
    file_path: str | Path,
    column_mapping: dict[str, str | None],
    required_fields: list[str] | None = None,
) -> list[dict[str, Any]]:
    """
    Parse CSV file using column mapping.

    Args:
        file_path: Path to CSV file.
        column_mapping: Dict of our_field -> csv_column name.
        required_fields: Fields that must be mapped and non-empty (optional).

    Returns:
        List of dicts, each with our field names as keys.
    """
    path = Path(file_path)
    if not path.exists():
        return []

    our_to_csv = {k: v for k, v in column_mapping.items() if v}
    csv_to_our = {v: k for k, v in our_to_csv.items()}

    rows: list[dict[str, Any]] = []
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            out: dict[str, Any] = {}
            for csv_col, our_field in csv_to_our.items():
                val = row.get(csv_col, "").strip() if row.get(csv_col) else ""
                if val:
                    out[our_field] = val
            rows.append(out)

    return rows


def validate_row(
    row: dict[str, Any],
    required_fields: list[str],
) -> tuple[bool, str | None]:
    """
    Validate a row has required fields.

    Returns:
        Tuple of (is_valid, error_message).
    """
    for field in required_fields:
        val = row.get(field)
        if val is None or (isinstance(val, str) and not val.strip()):
            return (False, f"Missing required field: {field}")
    return (True, None)
