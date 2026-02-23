"""Pydantic schemas for product wizard and context."""

from typing import Any, Literal

from pydantic import BaseModel, Field


# --- Request schemas (one per section) ---


class ProductBasicsRequest(BaseModel):
    """Product basics (step 1)."""

    product_name: str = Field(..., min_length=1)
    description: str | None = None
    industry: str | None = None
    stage: str | None = None
    website_url: str | None = None


class ProductAreaItem(BaseModel):
    """Single product area."""

    name: str = Field(..., min_length=1)
    description: str | None = None
    id: str | None = None
    order: int | None = None


class ProductAreasRequest(BaseModel):
    """Product areas (step 2)."""

    areas: list[ProductAreaItem] = Field(default_factory=list)


class GoalItem(BaseModel):
    """Single goal/OKR."""

    time_period: str | None = None
    title: str = Field(..., min_length=1)
    description: str | None = None
    priority: Literal["P0", "P1", "P2", "P3"] | None = None
    linked_area_id: str | None = None
    id: str | None = None


class ProductGoalsRequest(BaseModel):
    """Business goals (step 3)."""

    goals: list[GoalItem] = Field(default_factory=list)


class SegmentItem(BaseModel):
    """Customer segment."""

    name: str = Field(..., min_length=1)
    description: str | None = None
    revenue_share: float | None = None
    id: str | None = None


class PricingTierItem(BaseModel):
    """Pricing tier."""

    name: str = Field(..., min_length=1)
    price: float = 0
    price_period: str = "month"
    segment_id: str | None = None
    features: str | None = None
    id: str | None = None


class ProductSegmentsRequest(BaseModel):
    """Segments and pricing (step 4)."""

    segments: list[SegmentItem] = Field(default_factory=list)
    pricing_tiers: list[PricingTierItem] = Field(default_factory=list)


class CompetitorItem(BaseModel):
    """Competitor entry."""

    name: str = Field(..., min_length=1)
    website: str | None = None
    strengths: str | None = None
    weaknesses: str | None = None
    differentiation: str | None = None
    id: str | None = None


class ProductCompetitorsRequest(BaseModel):
    """Competitors (step 5)."""

    competitors: list[CompetitorItem] = Field(default_factory=list)


class ExistingFeatureItem(BaseModel):
    """Existing/live feature."""

    name: str = Field(..., min_length=1)
    area_id: str | None = None
    status: Literal["live", "beta", "deprecated"] = "live"
    release_date: str | None = None
    id: str | None = None


class PlannedFeatureItem(BaseModel):
    """Planned feature."""

    name: str = Field(..., min_length=1)
    area_id: str | None = None
    status: Literal["planned", "in_progress", "blocked"] = "planned"
    target_date: str | None = None
    priority: str | None = None
    id: str | None = None


class ProductRoadmapRequest(BaseModel):
    """Roadmap (step 6)."""

    existing_features: list[ExistingFeatureItem] = Field(default_factory=list)
    planned_features: list[PlannedFeatureItem] = Field(default_factory=list)


class TeamItem(BaseModel):
    """Team entry."""

    name: str = Field(..., min_length=1)
    lead: str | None = None
    area_ids: list[str] = Field(default_factory=list)
    size: int | None = None
    slack_channel: str | None = None
    id: str | None = None


class ProductTeamsRequest(BaseModel):
    """Teams (step 7)."""

    teams: list[TeamItem] = Field(default_factory=list)


class TechItem(BaseModel):
    """Tech stack entry."""

    category: Literal[
        "Frontend", "Backend", "Database", "Infrastructure", "Monitoring", "Other"
    ] = "Other"
    technology: str = Field(..., min_length=1)
    notes: str | None = None
    id: str | None = None


class ProductTechStackRequest(BaseModel):
    """Tech stack (step 8)."""

    technologies: list[TechItem] = Field(default_factory=list)


# --- Response schemas ---


class WizardSectionResponse(BaseModel):
    """Single wizard section response."""

    section: str
    data: dict[str, Any]
    updated_at: str


class WizardAllResponse(BaseModel):
    """All wizard sections response."""

    data: dict[str, dict[str, Any]]
    completed_sections: list[str]


class ProductContextResponse(BaseModel):
    """Flattened product context for agent prompt."""

    product_name: str | None = None
    description: str | None = None
    industry: str | None = None
    stage: str | None = None
    website_url: str | None = None
    areas: list[dict[str, Any]] = Field(default_factory=list)
    goals: list[dict[str, Any]] = Field(default_factory=list)
    segments: list[dict[str, Any]] = Field(default_factory=list)
    pricing_tiers: list[dict[str, Any]] = Field(default_factory=list)
    competitors: list[dict[str, Any]] = Field(default_factory=list)
    existing_features: list[dict[str, Any]] = Field(default_factory=list)
    planned_features: list[dict[str, Any]] = Field(default_factory=list)
    teams: list[dict[str, Any]] = Field(default_factory=list)
    technologies: list[dict[str, Any]] = Field(default_factory=list)


class OnboardingStatusResponse(BaseModel):
    """Onboarding status response."""

    completed: bool
    completed_sections: list[str]
    total_sections: int
