"""Elasticsearch index mappings for users and organizations."""

USERS_INDEX = "users"
ORGANIZATIONS_INDEX = "organizations"

USERS_MAPPING = {
    "mappings": {
        "properties": {
            "user_id": {"type": "keyword"},
            "org_id": {"type": "keyword"},
            "email": {"type": "keyword"},
            "hashed_password": {"type": "keyword"},
            "full_name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            "role": {"type": "keyword"},
            "dashboard_preferences": {"type": "object", "enabled": True},
            "created_at": {"type": "date"},
            "updated_at": {"type": "date"},
        }
    }
}

ORGANIZATIONS_MAPPING = {
    "mappings": {
        "properties": {
            "org_id": {"type": "keyword"},
            "name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            "onboarding_completed": {"type": "boolean"},
            "created_at": {"type": "date"},
            "updated_at": {"type": "date"},
        }
    }
}
