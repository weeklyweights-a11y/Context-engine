"""Wizard schema validation tests."""

import pytest
from pydantic import ValidationError

from app.schemas.product import (
    ProductAreasRequest,
    ProductBasicsRequest,
    ProductCompetitorsRequest,
    ProductGoalsRequest,
    ProductRoadmapRequest,
    ProductSegmentsRequest,
    ProductTechStackRequest,
    ProductTeamsRequest,
)


def test_basics_product_name_required():
    """Basics: product_name required, others optional."""
    ProductBasicsRequest(product_name="Acme")
    ProductBasicsRequest(product_name="Acme", description="B2B")
    with pytest.raises(ValidationError):
        ProductBasicsRequest(description="B2B")
    with pytest.raises(ValidationError):
        ProductBasicsRequest(product_name="")


def test_areas_each_area_needs_name():
    """Areas: each area needs a name."""
    ProductAreasRequest(areas=[{"name": "A1"}, {"name": "A2"}])
    with pytest.raises(ValidationError):
        ProductAreasRequest(areas=[{"name": "A1"}, {"description": "D2"}])


def test_goals_each_goal_needs_title():
    """Goals: each goal needs a title."""
    ProductGoalsRequest(goals=[{"title": "Reduce churn"}])
    with pytest.raises(ValidationError):
        ProductGoalsRequest(goals=[{"time_period": "Q1", "description": "X"}])


def test_segments_name_required():
    """Segments: name required on each segment."""
    ProductSegmentsRequest(segments=[{"name": "Enterprise"}])
    with pytest.raises(ValidationError):
        ProductSegmentsRequest(segments=[{"description": "Big companies"}])


def test_competitors_name_required():
    """Competitors: name required on each competitor."""
    ProductCompetitorsRequest(competitors=[{"name": "Mixpanel"}])
    with pytest.raises(ValidationError):
        ProductCompetitorsRequest(competitors=[{"website": "https://x.com"}])


def test_roadmap_feature_name_required():
    """Roadmap: feature name required on each item."""
    ProductRoadmapRequest(
        existing_features=[{"name": "Dashboard"}],
        planned_features=[{"name": "Filtering"}],
    )
    with pytest.raises(ValidationError):
        ProductRoadmapRequest(existing_features=[{"status": "live"}])


def test_teams_team_name_required():
    """Teams: team name required."""
    ProductTeamsRequest(teams=[{"name": "Payments"}])
    with pytest.raises(ValidationError):
        ProductTeamsRequest(teams=[{"lead": "John"}])


def test_tech_stack_technology_required():
    """Tech stack: technology name and category required (category has default)."""
    ProductTechStackRequest(technologies=[{"technology": "React"}])
    with pytest.raises(ValidationError):
        ProductTechStackRequest(technologies=[{"category": "Frontend"}])
