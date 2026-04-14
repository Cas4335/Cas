"""
PHX API — Main application entry point.

FastAPI backend for the offline AI knowledge appliance.
Handles authentication, authorization, retrieval, RAG, and audit logging.
"""

import logging
import structlog
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine
from app.routers import auth, chat, sources, sync, admin, health
from app.core.qdrant_client import init_qdrant_collection


# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("phx-api starting", tenant_id=settings.TENANT_ID)
    # Ensure Qdrant collection exists with correct schema
    await init_qdrant_collection()
    logger.info("phx-api ready")
    yield
    logger.info("phx-api shutting down")


app = FastAPI(
    title="PHX API",
    description="Offline AI Knowledge Appliance — API",
    version="1.0.0",
    # Disable docs in production if desired (keep enabled for v1 ops convenience)
    docs_url="/docs",
    redoc_url=None,
    lifespan=lifespan,
)

# CORS — restrict to internal origins only.
# In production, restrict origins to the known UI hostname.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

# Register routers
app.include_router(health.router, tags=["health"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(sources.router, prefix="/sources", tags=["sources"])
app.include_router(sync.router, prefix="/sync", tags=["sync"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
