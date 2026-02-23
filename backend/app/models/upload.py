"""Elasticsearch index for upload history."""

UPLOAD_HISTORY_INDEX = "upload-history"

UPLOAD_HISTORY_MAPPING = {
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "org_id": {"type": "keyword"},
            "upload_type": {"type": "keyword"},
            "filename": {"type": "keyword"},
            "total_rows": {"type": "integer"},
            "imported_rows": {"type": "integer"},
            "failed_rows": {"type": "integer"},
            "status": {"type": "keyword"},
            "column_mapping": {"type": "object", "enabled": True},
            "error_message": {"type": "text"},
            "temp_file_path": {"type": "keyword"},
            "imported_ids": {"type": "keyword"},
            "created_at": {"type": "date"},
            "completed_at": {"type": "date"},
        }
    }
}
