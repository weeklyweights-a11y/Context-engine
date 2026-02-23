"""Context Engine v2 — FastAPI application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import agent, analytics, auth, config, customers, feedback, health, product, search, specs, uploads, user
from app.services.elser_service import ensure_elser_deployed
from app.es_client import get_es_client
from app.services.es_service import setup_initial_indexes
from app.utils.logging import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create ES indexes. Shutdown: nothing."""
    logger.info("Starting up...")
    try:
        setup_initial_indexes()
        ensure_elser_deployed(get_es_client())
        logger.info("Initial indexes ready")
    except Exception as e:
        logger.error("Startup failed: %s", str(e))
        raise
    yield
    logger.info("Shutting down")


def create_app() -> FastAPI:
    """Create and configure FastAPI app."""
    settings = get_settings()
    app = FastAPI(
        title="Context Engine v2",
        description="Feedback intelligence platform for Product Managers",
        version="0.1.0",
        lifespan=lifespan,
    )

    origins = [o.strip() for o in settings.backend_cors_origins.split(",")]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, prefix=settings.api_v1_prefix)
    app.include_router(config.router, prefix=settings.api_v1_prefix)
    app.include_router(auth.router, prefix=settings.api_v1_prefix)
    app.include_router(user.router, prefix=settings.api_v1_prefix)
    app.include_router(product.router, prefix=settings.api_v1_prefix)
    app.include_router(feedback.router, prefix=settings.api_v1_prefix)
    app.include_router(search.router, prefix=settings.api_v1_prefix)
    app.include_router(analytics.router, prefix=settings.api_v1_prefix)
    app.include_router(customers.router, prefix=settings.api_v1_prefix)
    app.include_router(uploads.router, prefix=settings.api_v1_prefix)
    app.include_router(specs.router, prefix=settings.api_v1_prefix)
    app.include_router(agent.router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
