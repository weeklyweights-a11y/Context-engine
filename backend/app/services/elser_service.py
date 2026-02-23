"""ELSER inference endpoint management for semantic search."""

from typing import Any

from app.utils.logging import get_logger

logger = get_logger(__name__)

ELSER_AVAILABLE: bool | None = None


def ensure_elser_deployed(es_client: Any) -> bool:
    """
    Check if ELSER inference endpoint exists; create if not.

    Returns True if ELSER is available, False otherwise.
    Fallback: use FEEDBACK_MAPPING without text_semantic when False.
    """
    global ELSER_AVAILABLE
    if ELSER_AVAILABLE is not None:
        return ELSER_AVAILABLE

    try:
        es_client.inference.get(inference_id="elser-endpoint")
        ELSER_AVAILABLE = True
        logger.info("ELSER inference endpoint already exists")
        return True
    except Exception:
        pass

    try:
        es_client.inference.put(
            inference_id="elser-endpoint",
            body={
                "service": "elser",
                "service_settings": {
                    "num_allocations": 1,
                    "num_threads": 1,
                },
            },
        )
        ELSER_AVAILABLE = True
        logger.info("ELSER inference endpoint created")
        return True
    except Exception as e:
        logger.warning("ELSER not available, using fallback mapping: %s", str(e))
        ELSER_AVAILABLE = False
        return False


def is_elser_available() -> bool:
    """Return whether ELSER is available (after ensure_elser_deployed has been called)."""
    return ELSER_AVAILABLE is True
