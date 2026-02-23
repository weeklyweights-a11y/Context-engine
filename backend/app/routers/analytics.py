"""Analytics endpoints for dashboard widgets."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.dependencies import get_current_user
from app.services.analytics_service import (
    get_area_breakdown,
    get_at_risk_customers,
    get_segment_breakdown,
    get_sentiment_breakdown,
    get_source_distribution,
    get_summary,
    get_top_issues,
    get_volume,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _get_org_id(current_user: dict) -> str:
    return current_user["org_id"]


@router.get("/summary")
def analytics_summary(
    current_user: Annotated[dict, Depends(get_current_user)],
    period: str = Query("30d", description="7d, 30d, 90d, or custom"),
    from_date: str | None = Query(None, alias="from"),
    to_date: str | None = Query(None, alias="to"),
) -> dict:
    """Return 4 summary metrics with trends."""
    return get_summary(
        org_id=_get_org_id(current_user),
        period=period,
        from_date=from_date,
        to_date=to_date,
    )


@router.get("/volume")
def analytics_volume(
    current_user: Annotated[dict, Depends(get_current_user)],
    period: str = Query("30d"),
    from_date: str | None = Query(None, alias="from"),
    to_date: str | None = Query(None, alias="to"),
    areas: str | None = Query(None, description="Comma-separated product areas"),
) -> dict:
    """Return feedback volume over time."""
    area_list = [a.strip() for a in (areas or "").split(",") if a.strip()]
    return get_volume(
        org_id=_get_org_id(current_user),
        period=period,
        from_date=from_date,
        to_date=to_date,
        areas=area_list if area_list else None,
    )


@router.get("/sentiment")
def analytics_sentiment(
    current_user: Annotated[dict, Depends(get_current_user)],
    period: str = Query("30d"),
    from_date: str | None = Query(None, alias="from"),
    to_date: str | None = Query(None, alias="to"),
) -> dict:
    """Return sentiment breakdown."""
    return get_sentiment_breakdown(
        org_id=_get_org_id(current_user),
        period=period,
        from_date=from_date,
        to_date=to_date,
    )


@router.get("/top-issues")
def analytics_top_issues(
    current_user: Annotated[dict, Depends(get_current_user)],
    period: str = Query("30d"),
    from_date: str | None = Query(None, alias="from"),
    to_date: str | None = Query(None, alias="to"),
    limit: int = Query(5, ge=1, le=20),
) -> dict:
    """Return top issues ranked by impact."""
    return get_top_issues(
        org_id=_get_org_id(current_user),
        period=period,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
    )


@router.get("/areas")
def analytics_areas(
    current_user: Annotated[dict, Depends(get_current_user)],
    period: str = Query("30d"),
    from_date: str | None = Query(None, alias="from"),
    to_date: str | None = Query(None, alias="to"),
) -> dict:
    """Return product area breakdown."""
    return get_area_breakdown(
        org_id=_get_org_id(current_user),
        period=period,
        from_date=from_date,
        to_date=to_date,
    )


@router.get("/at-risk")
def analytics_at_risk(
    current_user: Annotated[dict, Depends(get_current_user)],
    period: str = Query("30d"),
    from_date: str | None = Query(None, alias="from"),
    to_date: str | None = Query(None, alias="to"),
    limit: int = Query(5, ge=1, le=20),
) -> dict:
    """Return at-risk customers."""
    return get_at_risk_customers(
        org_id=_get_org_id(current_user),
        period=period,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
    )


@router.get("/sources")
def analytics_sources(
    current_user: Annotated[dict, Depends(get_current_user)],
    period: str = Query("30d"),
    from_date: str | None = Query(None, alias="from"),
    to_date: str | None = Query(None, alias="to"),
) -> dict:
    """Return source distribution."""
    return get_source_distribution(
        org_id=_get_org_id(current_user),
        period=period,
        from_date=from_date,
        to_date=to_date,
    )


@router.get("/segments")
def analytics_segments(
    current_user: Annotated[dict, Depends(get_current_user)],
    period: str = Query("30d"),
    from_date: str | None = Query(None, alias="from"),
    to_date: str | None = Query(None, alias="to"),
) -> dict:
    """Return segment breakdown."""
    return get_segment_breakdown(
        org_id=_get_org_id(current_user),
        period=period,
        from_date=from_date,
        to_date=to_date,
    )
