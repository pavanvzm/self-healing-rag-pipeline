"""FastAPI application entry point with lifespan and CORS."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.api.routes import queries, metrics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    logger.info("Starting %s...", settings.app_name)
    try:
        await init_db()
        logger.info("Database tables initialized.")
    except Exception as e:
        logger.warning("Database initialization skipped (not available): %s", e)
    yield
    logger.info("Shutting down %s...", settings.app_name)


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="A production-ready Self-Healing RAG Pipeline with autonomous error correction.",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(queries.router)
app.include_router(metrics.router)


@app.get("/health")
async def health_check():
    return {"status": "ok", "app": settings.app_name, "llm_provider": settings.llm_provider}
