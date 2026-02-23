"""ES service tests."""

from unittest.mock import MagicMock, patch

import pytest

from app.services.es_service import (
    ensure_index_exists,
    get_document,
    index_document,
    search_documents,
)


def test_ensure_index_exists_creates_when_missing():
    """ensure_index_exists creates index when it does not exist."""
    mock_es = MagicMock()
    mock_es.indices.exists.return_value = False

    with patch("app.services.es_service.get_es_client", return_value=mock_es):
        ensure_index_exists("test-index", {"mappings": {}})

    mock_es.indices.create.assert_called_once()
    call_args = mock_es.indices.create.call_args
    assert call_args[1]["index"] == "test-index"


def test_ensure_index_exists_skips_when_exists():
    """ensure_index_exists skips creation when index exists."""
    mock_es = MagicMock()
    mock_es.indices.exists.return_value = True

    with patch("app.services.es_service.get_es_client", return_value=mock_es):
        ensure_index_exists("test-index", {"mappings": {}})

    mock_es.indices.create.assert_not_called()


def test_index_document_stores_correctly():
    """index_document stores document in index."""
    mock_es = MagicMock()
    mock_es.index.return_value = {"result": "created"}

    with patch("app.services.es_service.get_es_client", return_value=mock_es):
        index_document("idx", "doc1", {"name": "test"})

    mock_es.index.assert_called_once_with(
        index="idx", id="doc1", document={"name": "test"}
    )


def test_search_documents_returns_results():
    """search_documents returns _source from hits."""
    mock_es = MagicMock()
    mock_es.search.return_value = {
        "hits": {
            "hits": [
                {"_source": {"id": "1", "name": "a"}},
                {"_source": {"id": "2", "name": "b"}},
            ]
        }
    }

    with patch("app.services.es_service.get_es_client", return_value=mock_es):
        result = search_documents("idx", {"match_all": {}}, size=10)

    assert len(result) == 2
    assert result[0]["name"] == "a"
    assert result[1]["name"] == "b"
