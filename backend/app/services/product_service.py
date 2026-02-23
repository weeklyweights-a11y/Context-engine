"""Product wizard and context service."""

import uuid
from datetime import datetime
from typing import Any

from app.models.product import (
    PRODUCT_CONTEXT_MAPPING,
    WIZARD_SECTIONS,
    product_context_index,
)
from app.models.user import ORGANIZATIONS_INDEX
from app.schemas.product import ProductContextResponse
from app.services.es_service import (
    delete_document,
    ensure_index_exists,
    get_document,
    index_document,
    search_documents,
)
from app.utils.logging import get_logger

logger = get_logger(__name__)


def _ensure_ids(data: dict[str, Any], list_keys: list[str]) -> dict[str, Any]:
    """Ensure list items have UUIDs. Mutates and returns data."""
    result = dict(data)
    for key in list_keys:
        if key in result and isinstance(result[key], list):
            items = []
            for item in result[key]:
                if isinstance(item, dict):
                    copy = dict(item)
                    if "id" not in copy or not copy["id"]:
                        copy["id"] = str(uuid.uuid4())
                    items.append(copy)
                else:
                    items.append(item)
            result[key] = items
    return result


def _add_ids_for_section(section: str, data: dict[str, Any]) -> dict[str, Any]:
    """Add UUIDs to list items per section."""
    if section == "areas":
        return _ensure_ids(data, ["areas"])
    if section == "goals":
        return _ensure_ids(data, ["goals"])
    if section == "segments":
        return _ensure_ids(data, ["segments", "pricing_tiers"])
    if section == "competitors":
        return _ensure_ids(data, ["competitors"])
    if section == "roadmap":
        return _ensure_ids(data, ["existing_features", "planned_features"])
    if section == "teams":
        return _ensure_ids(data, ["teams"])
    if section == "tech_stack":
        return _ensure_ids(data, ["technologies"])
    return data


def save_wizard_section(org_id: str, section: str, data: dict[str, Any]) -> dict[str, Any]:
    """
    Upsert a wizard section document.

    Creates index if needed. Uses section as document id for upsert.
    """
    if section not in WIZARD_SECTIONS:
        raise ValueError(f"Invalid section: {section}")

    idx = product_context_index(org_id)
    ensure_index_exists(idx, PRODUCT_CONTEXT_MAPPING)

    data_with_ids = _add_ids_for_section(section, data)
    now = datetime.utcnow().isoformat() + "Z"

    existing = get_document(idx, section)
    created_at = existing["created_at"] if existing else now

    body = {
        "id": str(uuid.uuid4()),
        "org_id": org_id,
        "section": section,
        "data": data_with_ids,
        "created_at": created_at,
        "updated_at": now,
    }

    index_document(idx, section, body)
    logger.info("Saved wizard section %s for org %s", section, org_id[:8])
    return body


def get_wizard_section(org_id: str, section: str) -> dict[str, Any] | None:
    """Get one wizard section. Returns None if not found."""
    if section not in WIZARD_SECTIONS:
        return None

    idx = product_context_index(org_id)
    doc = get_document(idx, section)
    return doc


def get_all_wizard_sections(org_id: str) -> dict[str, dict[str, Any]]:
    """Get all wizard sections for org. Returns dict of section -> doc."""
    idx = product_context_index(org_id)
    try:
        hits = search_documents(
            idx,
            {"term": {"org_id": org_id}},
            size=100,
        )
    except Exception:
        return {}

    result: dict[str, dict[str, Any]] = {}
    for doc in hits:
        sec = doc.get("section")
        if sec:
            result[sec] = doc
    return result


def delete_wizard_section(org_id: str, section: str) -> bool:
    """Delete a wizard section. Returns True if deleted."""
    if section not in WIZARD_SECTIONS:
        return False

    idx = product_context_index(org_id)
    return delete_document(idx, section)


def get_product_context(org_id: str) -> ProductContextResponse:
    """
    Build flattened product context from all sections.

    Returns empty structure if no data. Used for agent system prompt.
    """
    sections = get_all_wizard_sections(org_id)

    product_name = None
    description = None
    industry = None
    stage = None
    website_url = None
    areas = []
    goals = []
    segments = []
    pricing_tiers = []
    competitors = []
    existing_features = []
    planned_features = []
    teams = []
    technologies = []

    basics = sections.get("basics", {}).get("data", {})
    if basics:
        product_name = basics.get("product_name")
        description = basics.get("description")
        industry = basics.get("industry")
        stage = basics.get("stage")
        website_url = basics.get("website_url")

    areas_data = sections.get("areas", {}).get("data", {})
    if areas_data:
        areas = areas_data.get("areas", [])

    goals_data = sections.get("goals", {}).get("data", {})
    if goals_data:
        goals = goals_data.get("goals", [])

    segments_data = sections.get("segments", {}).get("data", {})
    if segments_data:
        segments = segments_data.get("segments", [])
        pricing_tiers = segments_data.get("pricing_tiers", [])

    competitors_data = sections.get("competitors", {}).get("data", {})
    if competitors_data:
        competitors = competitors_data.get("competitors", [])

    roadmap_data = sections.get("roadmap", {}).get("data", {})
    if roadmap_data:
        existing_features = roadmap_data.get("existing_features", [])
        planned_features = roadmap_data.get("planned_features", [])

    teams_data = sections.get("teams", {}).get("data", {})
    if teams_data:
        teams = teams_data.get("teams", [])

    tech_data = sections.get("tech_stack", {}).get("data", {})
    if tech_data:
        technologies = tech_data.get("technologies", [])

    return ProductContextResponse(
        product_name=product_name,
        description=description,
        industry=industry,
        stage=stage,
        website_url=website_url,
        areas=areas,
        goals=goals,
        segments=segments,
        pricing_tiers=pricing_tiers,
        competitors=competitors,
        existing_features=existing_features,
        planned_features=planned_features,
        teams=teams,
        technologies=technologies,
    )


def get_onboarding_status(org_id: str) -> dict[str, Any]:
    """
    Check onboarding_completed flag and count completed sections.

    Treats missing onboarding_completed as False (no migration needed).
    """
    org = get_document(ORGANIZATIONS_INDEX, org_id)
    completed = False
    if org:
        completed = org.get("onboarding_completed", False) or False

    sections = get_all_wizard_sections(org_id)
    completed_sections = list(sections.keys())

    return {
        "completed": completed,
        "completed_sections": completed_sections,
        "total_sections": len(WIZARD_SECTIONS),
    }


def mark_onboarding_complete(org_id: str) -> None:
    """Set onboarding_completed = true on the organization."""
    org = get_document(ORGANIZATIONS_INDEX, org_id)
    if not org:
        raise ValueError("Organization not found")

    now = datetime.utcnow().isoformat() + "Z"
    updated = dict(org)
    updated["onboarding_completed"] = True
    updated["updated_at"] = now

    index_document(ORGANIZATIONS_INDEX, org_id, updated)
    logger.info("Marked onboarding complete for org %s", org_id[:8])
