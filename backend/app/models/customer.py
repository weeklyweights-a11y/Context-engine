"""Elasticsearch index for customer profiles."""


def customers_index(org_id: str) -> str:
    """Return the customers index name for an org."""
    return f"{org_id}-customers"


CUSTOMERS_MAPPING = {
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "org_id": {"type": "keyword"},
            "company_name": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword"}},
            },
            "customer_id_external": {"type": "keyword"},
            "segment": {"type": "keyword"},
            "plan": {"type": "keyword"},
            "mrr": {"type": "float"},
            "arr": {"type": "float"},
            "account_manager": {"type": "keyword"},
            "renewal_date": {"type": "date"},
            "health_score": {"type": "integer"},
            "industry": {"type": "keyword"},
            "employee_count": {"type": "integer"},
            "created_at": {"type": "date"},
            "updated_at": {"type": "date"},
            "metadata": {"type": "object", "enabled": True},
        }
    }
}
