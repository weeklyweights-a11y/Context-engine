"""Product area auto-detection from feedback text."""

import re
from collections import Counter
from typing import Any

from app.services.product_service import get_all_wizard_sections

MIN_OCCURRENCES = 2
MAX_NEW_AREAS = 10


def _get_existing_area_names(org_id: str) -> list[str]:
    """Get existing product area names from wizard."""
    sections = get_all_wizard_sections(org_id)
    areas_data = sections.get("areas", {}).get("data", {})
    areas = areas_data.get("areas", [])
    names = []
    for a in areas:
        if isinstance(a, dict) and a.get("name"):
            names.append(a["name"].lower().strip())
    return names


def _normalize_area_name(name: str) -> str:
    """Normalize area name to lowercase, replace spaces with underscores."""
    s = re.sub(r"[^\w\s]", "", name.lower())
    s = re.sub(r"\s+", "_", s.strip())
    return s or name.lower()


def match_existing_areas(
    texts: list[str],
    existing_areas: list[str],
) -> dict[str, int]:
    """Count mentions of existing areas in texts. Returns area_name -> count."""
    combined = " ".join(t.lower() for t in texts if t)
    counts: dict[str, int] = {}
    for area in existing_areas:
        area_clean = area.lower().replace("_", " ")
        area_words = area_clean.split()
        if len(area_words) >= 2:
            if area_clean in combined:
                counts[area] = combined.count(area_clean)
        else:
            if area in combined or area_clean in combined:
                counts[area] = combined.count(area) + combined.count(area_clean)
    return counts


def find_new_areas(
    texts: list[str],
    existing_areas: list[str],
) -> list[tuple[str, int]]:
    """
    Find frequent terms (potential new areas) not in existing areas.

    Uses simple word extraction; filters common words.
    Returns list of (normalized_name, count) sorted by count desc.
    """
    stop_words = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "is", "it", "this", "that", "we", "i",
        "they", "you", "have", "has", "had", "was", "were", "be", "been",
        "not", "no", "so", "if", "as", "can", "will", "would", "could",
        "should", "may", "might", "must", "need", "get", "got", "like",
    }
    combined = " ".join(t.lower() for t in texts if t)
    words = re.findall(r"\b[a-z]{3,}\b", combined)
    bigrams = [
        f"{words[i]}_{words[i+1]}"
        for i in range(len(words) - 1)
        if words[i] not in stop_words and words[i + 1] not in stop_words
    ]
    existing_set = {_normalize_area_name(a) for a in existing_areas}
    counts: Counter = Counter()
    for w in words:
        if w not in stop_words and len(w) >= 3:
            n = _normalize_area_name(w)
            if n not in existing_set:
                counts[n] += 1
    for b in bigrams:
        if b not in existing_set:
            counts[b] += 1

    result = [(name, c) for name, c in counts.most_common(MAX_NEW_AREAS) if c >= MIN_OCCURRENCES]
    return result


def detect_areas(org_id: str, feedback_texts: list[str]) -> list[dict[str, Any]]:
    """
    Detect product areas from feedback texts.

    Returns list of {name, count, is_new}.
    """
    existing = _get_existing_area_names(org_id)
    result: list[dict[str, Any]] = []

    matched = match_existing_areas(feedback_texts, existing)
    for area, count in sorted(matched.items(), key=lambda x: -x[1]):
        result.append({"name": area, "count": count, "is_new": False})

    new_areas = find_new_areas(feedback_texts, existing)
    for name, count in new_areas:
        result.append({"name": name, "count": count, "is_new": True})

    return result[: 20]
