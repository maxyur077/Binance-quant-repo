from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import __app_name__, __version__
from app.api.middleware.audit_middleware import setup_audit_middleware
from app.api.middleware.cors_middleware import setup_cors
from app.api.middleware.rate_limit_middleware import setup_rate_limiting
from app.api.v1.router import api_v1_router
from app.db.supabase_client import get_supabase_client
from app.settings import get_settings

logger = logging.getLogger(__name__)


from app.workers import (
    scanner_worker,
    position_worker,
    subscription_worker,
    payment_worker,
    notification_worker
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info(f"Starting {__app_name__} v{__version__}")
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
        logger.warning("Supabase credentials missing from environment.")
    else:
        # Initialize singleton
        get_supabase_client()
        logger.info("Supabase client initialized.")
        
    logger.info("Starting background workers...")
    scanner_worker.start()
    position_worker.start()
    subscription_worker.start()
    payment_worker.start()
    notification_worker.start()
    
    yield
    
    logger.info("Stopping background workers...")
    scanner_worker.stop()
    position_worker.stop()
    subscription_worker.stop()
    payment_worker.stop()
    notification_worker.stop()
    logger.info(f"Shutting down {__app_name__}")


def create_app() -> FastAPI:
    app = FastAPI(
        title=__app_name__,
        version=__version__,
        lifespan=lifespan,
    )

    setup_cors(app)
    setup_rate_limiting(app)
    setup_audit_middleware(app)

    app.include_router(api_v1_router)

    @app.get("/")
    async def root() -> dict:
        return {
            "name": __app_name__,
            "version": __version__,
            "docs_url": "/docs",
        }

    return app


app = create_app()
