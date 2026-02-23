"""Low-level Elasticsearch operations."""

from typing import Any

from app.es_client import get_es_client
from app.models.upload import (
    UPLOAD_HISTORY_INDEX,
    UPLOAD_HISTORY_MAPPING,
)
from app.models.user import (
    ORGANIZATIONS_INDEX,
    ORGANIZATIONS_MAPPING,
    USERS_INDEX,
    USERS_MAPPING,
)
from app.utils.logging import get_logger

logger = get_logger(__name__)


def ensure_index_exists(index_name: str, mappings: dict[str, Any]) -> None:
    """Create index if it does not exist."""
    es = get_es_client()
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name, body=mappings)
        logger.info("Created index: %s", index_name)


def setup_initial_indexes() -> None:
    """Create users, organizations, and upload-history indexes on startup."""
    ensure_index_exists(USERS_INDEX, USERS_MAPPING)
    ensure_index_exists(ORGANIZATIONS_INDEX, ORGANIZATIONS_MAPPING)
    ensure_index_exists(UPLOAD_HISTORY_INDEX, UPLOAD_HISTORY_MAPPING)


def index_document(index: str, doc_id: str, body: dict[str, Any]) -> None:
    """Store a document in the given index."""
    es = get_es_client()
    es.index(index=index, id=doc_id, document=body)


def update_document(
    index: str, doc_id: str, partial: dict[str, Any]
) -> None:
    """Partial update of a document."""
    es = get_es_client()
    es.update(index=index, id=doc_id, doc=partial)


def get_document(index: str, doc_id: str) -> dict[str, Any] | None:
    """Get a document by ID. Returns None if not found."""
    es = get_es_client()
    try:
        resp = es.get(index=index, id=doc_id)
        return resp.get("_source")
    except Exception:
        return None


def search_documents(
    index: str, query: dict[str, Any], size: int = 20
) -> list[dict[str, Any]]:
    """Run search and return list of _source documents."""
    es = get_es_client()
    resp = es.search(index=index, query=query, size=size)
    hits = resp.get("hits", {}).get("hits", [])
    return [h["_source"] for h in hits]


def search_document_ids(index: str, query: dict[str, Any], size: int = 10000) -> list[str]:
    """Run search and return list of document IDs."""
    es = get_es_client()
    resp = es.search(index=index, query=query, size=size, _source=False)
    hits = resp.get("hits", {}).get("hits", [])
    return [h["_id"] for h in hits]


def delete_document(index: str, doc_id: str) -> bool:
    """Delete a document by ID. Returns True if deleted."""
    es = get_es_client()
    try:
        es.delete(index=index, id=doc_id)
        return True
    except Exception:
        return False


def bulk_index_documents(
    index: str,
    documents: list[dict[str, Any]],
    id_field: str = "id",
    batch_size: int = 500,
) -> tuple[int, int]:
    """
    Index documents via ES Bulk API in batches.

    Args:
        index: Target index name.
        documents: List of documents to index. Each must have id_field.
        id_field: Field name containing document ID.
        batch_size: Max documents per bulk request.

    Returns:
        Tuple of (success_count, failed_count).
    """
    from elasticsearch.helpers import BulkIndexError, bulk

    es = get_es_client()
    success_count = 0
    failed_count = 0

    for i in range(0, len(documents), batch_size):
        batch = documents[i : i + batch_size]
        actions = []
        for doc in batch:
            if id_field not in doc:
                failed_count += 1
                continue
            actions.append({
                "_op_type": "index",
                "_index": index,
                "_id": str(doc[id_field]),
                "_source": doc,
            })
        if not actions:
            continue
        try:
            ok, failed = bulk(
                es,
                actions,
                raise_on_error=False,
                raise_on_exception=False,
                stats_only=True,
            )
            success_count += ok
            failed_count += failed
        except BulkIndexError as e:
            success_count += e.successful
            failed_count += len(e.errors)
            for err in e.errors:
                logger.warning("Bulk index error: %s", err)
        except Exception as e:
            failed_count += len(actions)
            logger.error("Bulk index failed: %s", str(e))

    return (success_count, failed_count)
