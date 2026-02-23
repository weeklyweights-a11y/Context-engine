"""Elasticsearch index for product context (wizard data)."""

WIZARD_SECTIONS = [
    "basics",
    "areas",
    "goals",
    "segments",
    "competitors",
    "roadmap",
    "teams",
    "tech_stack",
]


def product_context_index(org_id: str) -> str:
    """Return the product-context index name for an org."""
    return f"{org_id}-product-context"


PRODUCT_CONTEXT_MAPPING = {
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "org_id": {"type": "keyword"},
            "section": {"type": "keyword"},
            "data": {"type": "object", "enabled": True},
            "created_at": {"type": "date"},
            "updated_at": {"type": "date"},
        }
    }
}
