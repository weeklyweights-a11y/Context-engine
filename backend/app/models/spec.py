"""Elasticsearch index and constants for spec documents."""


def specs_index(org_id: str) -> str:
    """Return the specs index name for an org."""
    return f"{org_id}-specs"


SPECS_MAPPING = {
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "org_id": {"type": "keyword"},
            "title": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            "topic": {"type": "keyword"},
            "product_area": {"type": "keyword"},
            "status": {"type": "keyword"},
            "prd": {"type": "text"},
            "architecture": {"type": "text"},
            "rules": {"type": "text"},
            "plan": {"type": "text"},
            "feedback_count": {"type": "integer"},
            "customer_count": {"type": "integer"},
            "total_arr": {"type": "float"},
            "feedback_ids": {"type": "keyword"},
            "customer_ids": {"type": "keyword"},
            "linked_goal_id": {"type": "keyword"},
            "generated_by": {"type": "keyword"},
            "generated_by_name": {"type": "keyword"},
            "data_brief": {"type": "object", "enabled": True},
            "data_freshness_date": {"type": "date"},
            "created_at": {"type": "date"},
            "updated_at": {"type": "date"},
        }
    }
}
