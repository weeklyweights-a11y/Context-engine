"""Product wizard and context endpoints."""

from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends, HTTPException, status

from app.dependencies import get_current_user
from app.models.product import WIZARD_SECTIONS
from app.schemas.product import (
    ProductBasicsRequest,
    ProductAreasRequest,
    ProductCompetitorsRequest,
    ProductGoalsRequest,
    ProductRoadmapRequest,
    ProductSegmentsRequest,
    ProductTechStackRequest,
    ProductTeamsRequest,
)
from app.services.product_service import (
    delete_wizard_section,
    get_all_wizard_sections,
    get_onboarding_status,
    get_product_context,
    get_wizard_section,
    mark_onboarding_complete,
    save_wizard_section,
)

router = APIRouter(prefix="/product", tags=["product"])

SECTION_SCHEMAS = {
    "basics": ProductBasicsRequest,
    "areas": ProductAreasRequest,
    "goals": ProductGoalsRequest,
    "segments": ProductSegmentsRequest,
    "competitors": ProductCompetitorsRequest,
    "roadmap": ProductRoadmapRequest,
    "teams": ProductTeamsRequest,
    "tech_stack": ProductTechStackRequest,
}


def _validate_section_data(section: str, data: dict[str, Any]) -> dict[str, Any]:
    """Validate body against section schema, return model_dump()."""
    schema = SECTION_SCHEMAS.get(section)
    if not schema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invalid section: {section}",
        )
    try:
        model = schema.model_validate(data)
        return model.model_dump(exclude_none=False)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        ) from e


@router.put("/wizard/{section}", response_model=dict)
def put_wizard_section(
    section: str,
    body: dict[str, Any] = Body(...),
    current_user: Annotated[dict, Depends(get_current_user)] = None,
) -> dict:
    """Save or update one wizard section."""
    org_id = current_user["org_id"]
    validated = _validate_section_data(section, body)
    try:
        doc = save_wizard_section(org_id, section, validated)
        return {"data": doc}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get("/wizard", response_model=dict)
def get_wizard_all(
    current_user: Annotated[dict, Depends(get_current_user)] = None,
) -> dict:
    """Get all wizard sections for current org."""
    org_id = current_user["org_id"]
    sections = get_all_wizard_sections(org_id)
    data = {sec: doc.get("data", {}) for sec, doc in sections.items()}
    return {
        "data": data,
        "completed_sections": list(sections.keys()),
    }


@router.get("/wizard/{section}", response_model=dict)
def get_wizard_one(
    section: str,
    current_user: Annotated[dict, Depends(get_current_user)] = None,
) -> dict:
    """Get one wizard section."""
    if section not in WIZARD_SECTIONS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invalid section: {section}",
        )
    org_id = current_user["org_id"]
    doc = get_wizard_section(org_id, section)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found",
        )
    return {"data": doc}


@router.delete("/wizard/{section}", response_model=dict)
def delete_wizard(
    section: str,
    current_user: Annotated[dict, Depends(get_current_user)] = None,
) -> dict:
    """Delete one wizard section."""
    if section not in WIZARD_SECTIONS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invalid section: {section}",
        )
    org_id = current_user["org_id"]
    deleted = delete_wizard_section(org_id, section)
    return {"data": {"deleted": deleted}}


@router.get("/context", response_model=dict)
def get_context(
    current_user: Annotated[dict, Depends(get_current_user)] = None,
) -> dict:
    """Get flattened product context (for agent prompt)."""
    org_id = current_user["org_id"]
    ctx = get_product_context(org_id)
    return {"data": ctx.model_dump()}


@router.get("/onboarding-status", response_model=dict)
def get_onboarding(
    current_user: Annotated[dict, Depends(get_current_user)] = None,
) -> dict:
    """Get onboarding completion status."""
    org_id = current_user["org_id"]
    status_data = get_onboarding_status(org_id)
    return {"data": status_data}


@router.post("/onboarding-complete", response_model=dict)
def post_onboarding_complete(
    current_user: Annotated[dict, Depends(get_current_user)] = None,
) -> dict:
    """Mark onboarding as complete."""
    org_id = current_user["org_id"]
    try:
        mark_onboarding_complete(org_id)
        return {"data": {"completed": True}}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
