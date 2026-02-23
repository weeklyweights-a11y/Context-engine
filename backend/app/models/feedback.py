"""Elasticsearch index and constants for feedback items."""

FEEDBACK_SOURCES = [
    "app_store_review",
    "g2_capterra",
    "support_ticket",
    "nps_csat",
    "customer_email",
    "sales_call_note",
    "slack_message",
    "internal_team_feedback",
    "user_interview",
    "bug_report",
    "community_forum",
]

FEEDBACK_SOURCE_LABELS = {
    "app_store_review": "App Store Review",
    "g2_capterra": "G2 / Capterra",
    "support_ticket": "Support Ticket",
    "nps_csat": "NPS / CSAT Survey",
    "customer_email": "Customer Email",
    "sales_call_note": "Sales Call Note",
    "slack_message": "Slack Message",
    "internal_team_feedback": "Internal Team Feedback",
    "user_interview": "User Interview / Research",
    "bug_report": "Bug Report (Jira/Linear)",
    "community_forum": "Community Forum / Discord",
}


def feedback_index(org_id: str) -> str:
    """Return the feedback index name for an org."""
    return f"{org_id}-feedback"


FEEDBACK_MAPPING = {
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "org_id": {"type": "keyword"},
            "text": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            "source": {"type": "keyword"},
            "sentiment": {"type": "keyword"},
            "sentiment_score": {"type": "float"},
            "rating": {"type": "integer"},
            "product_area": {"type": "keyword"},
            "customer_id": {"type": "keyword"},
            "customer_name": {"type": "keyword"},
            "customer_segment": {"type": "keyword"},
            "author_name": {"type": "keyword"},
            "author_email": {"type": "keyword"},
            "tags": {"type": "keyword"},
            "source_file": {"type": "keyword"},
            "ingestion_method": {"type": "keyword"},
            "created_at": {"type": "date"},
            "ingested_at": {"type": "date"},
            "metadata": {"type": "object", "enabled": True},
        }
    }
}

FEEDBACK_MAPPING_WITH_ELSER = {
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "org_id": {"type": "keyword"},
            "text": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            "text_semantic": {
                "type": "semantic_text",
                "inference_id": "elser-endpoint",
            },
            "source": {"type": "keyword"},
            "sentiment": {"type": "keyword"},
            "sentiment_score": {"type": "float"},
            "rating": {"type": "integer"},
            "product_area": {"type": "keyword"},
            "customer_id": {"type": "keyword"},
            "customer_name": {"type": "keyword"},
            "customer_segment": {"type": "keyword"},
            "author_name": {"type": "keyword"},
            "author_email": {"type": "keyword"},
            "tags": {"type": "keyword"},
            "source_file": {"type": "keyword"},
            "ingestion_method": {"type": "keyword"},
            "created_at": {"type": "date"},
            "ingested_at": {"type": "date"},
            "metadata": {"type": "object", "enabled": True},
        }
    }
}
