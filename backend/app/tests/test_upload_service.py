"""Upload service tests."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from app.services.upload_service import (
    create_upload,
    get_upload,
    get_upload_temp_path,
    update_upload,
    save_uploaded_file,
)


def test_save_uploaded_file():
    """save_uploaded_file writes content and returns path."""
    content = b"col1,col2\n1,2"
    path = save_uploaded_file(content, "test.csv")
    assert Path(path).exists()
    assert Path(path).read_bytes() == content
    Path(path).unlink(missing_ok=True)


def test_create_upload_returns_id():
    """create_upload returns upload ID."""
    with patch("app.services.upload_service.ensure_index_exists"):
        with patch("app.services.upload_service.index_document") as mock_idx:
            temp = Path(tempfile.gettempdir()) / "test_upload_xyz.csv"
            temp.write_text("x,y\n1,2")
            try:
                uid = create_upload("o1", "feedback", "x.csv", 1, str(temp))
                assert uid
                mock_idx.assert_called_once()
                body = mock_idx.call_args[0][2]
                assert body["org_id"] == "o1"
                assert body["upload_type"] == "feedback"
            finally:
                temp.unlink(missing_ok=True)


def test_get_upload_returns_doc_when_found():
    """get_upload returns document when found."""
    with patch("app.services.upload_service.get_document") as mock_get:
        mock_get.return_value = {
            "id": "u1", "org_id": "o1", "upload_type": "feedback",
            "filename": "x.csv", "status": "pending",
        }
        doc = get_upload("o1", "u1")
        assert doc is not None
        assert doc["org_id"] == "o1"


def test_get_upload_returns_none_wrong_org():
    """get_upload returns None when org does not match."""
    with patch("app.services.upload_service.get_document") as mock_get:
        mock_get.return_value = {"id": "u1", "org_id": "o2"}
        doc = get_upload("o1", "u1")
        assert doc is None


def test_get_upload_temp_path():
    """get_upload_temp_path returns path from document."""
    with patch("app.services.upload_service.get_document") as mock_get:
        mock_get.return_value = {"temp_file_path": "/tmp/abc.csv"}
        path = get_upload_temp_path("u1")
        assert path == "/tmp/abc.csv"


def test_update_upload():
    """update_upload modifies status and column_mapping."""
    with patch("app.services.upload_service.get_document") as mock_get:
        with patch("app.services.upload_service.index_document") as mock_idx:
            mock_get.return_value = {
                "id": "u1", "org_id": "o1", "status": "pending",
                "column_mapping": {}, "temp_file_path": "/tmp/x.csv",
            }
            update_upload("u1", status="completed", column_mapping={"text": "feedback"})
            mock_idx.assert_called_once()
            call_body = mock_idx.call_args[0][2]
            assert call_body["status"] == "completed"
            assert call_body["column_mapping"] == {"text": "feedback"}
