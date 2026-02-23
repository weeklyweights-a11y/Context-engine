"""Elasticsearch index for agent conversations (UI listing and message display)."""


def conversations_index(org_id: str) -> str:
    """Return the conversations index name for an org."""
    return f"{org_id}-conversations"


CONVERSATIONS_MAPPING = {
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "org_id": {"type": "keyword"},
            "user_id": {"type": "keyword"},
            "kibana_conversation_id": {"type": "keyword"},
            "title": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            "messages": {
                "type": "nested",
                "properties": {
                    "role": {"type": "keyword"},
                    "content": {"type": "text"},
                    "timestamp": {"type": "date"},
                },
            },
            "created_at": {"type": "date"},
            "updated_at": {"type": "date"},
        }
    }
}
