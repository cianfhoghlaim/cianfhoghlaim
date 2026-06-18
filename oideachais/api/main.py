"""
Celtic Education Platform API.

FastAPI application providing:
- Semantic search across all domains
- Geospatial queries and map data
- Translation between Celtic languages
- Agent streaming for conversational AI

Endpoints:
    /search/* - Semantic search
    /geo/* - Geospatial data
    /translate/* - Celtic translation
    /agent/* - AI agent streaming
    /health - Health check

Observability:
    - Datadog APM + LLM Observability
    - MLflow experiment tracking
    - Langfuse LLM tracing
    - Ragas RAG evaluation
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Initialize observability BEFORE any other imports that might use tracing
from oideachais.observability import (
    init_langfuse,
    init_mlflow,
    init_observability,
    langfuse_flush,
    langfuse_shutdown,
    setup_datadog_apm,
    setup_logging,
)

logger = logging.getLogger(__name__)


# ============================================================================
# Application Lifecycle
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager with observability initialization."""
    # Startup - Initialize observability stack
    logger.info("Celtic Education Platform API starting...")

    # 1. Initialize logging with Datadog correlation
    setup_logging()

    # 2. Initialize Datadog APM + LLM Observability
    dd_enabled = init_observability()
    if dd_enabled:
        logger.info("Datadog APM + LLMObs initialized")
    else:
        logger.warning("Datadog disabled (DD_API_KEY not set)")

    # 3. Initialize MLflow for experiment tracking
    init_mlflow(experiment_name="oideachais-celtic-education")
    logger.info("MLflow initialized")

    # 4. Initialize Langfuse for LLM tracing
    init_langfuse()
    logger.info("Langfuse initialized")

    logger.info("All observability services initialized")

    yield

    # Shutdown - Flush and cleanup
    logger.info("Celtic Education Platform API shutting down...")

    # Flush Langfuse traces
    langfuse_flush()
    langfuse_shutdown()
    logger.info("Langfuse shutdown complete")


# ============================================================================
# Application Setup
# ============================================================================

app = FastAPI(
    title="Celtic Education Platform API",
    description="""
Unified API for Celtic education content across Ireland, Scotland, Wales, and more.

## Features
- **Search**: Semantic search across curriculum, folklore, terminology
- **Geospatial**: Map data for Gaeltacht, dialect regions, school locations
- **Translation**: Translate between 6 Celtic languages
- **Agents**: Conversational AI for education queries

## Languages
- English (en)
- Irish (ga)
- Scottish Gaelic (gd)
- Welsh (cy)
- Manx (gv)
- Cornish (kw)
- Breton (br)

## Nations
- Ireland
- Scotland
- Wales
- Northern Ireland
- England
- Crown Dependencies
    """,
    version="0.1.0",
    lifespan=lifespan,
)

# Datadog APM middleware (must be added before other middleware)
setup_datadog_apm(app)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth middleware - validates BetterAuth sessions from web app
from .middleware import AuthMiddleware

app.add_middleware(AuthMiddleware)


# ============================================================================
# Route Registration
# ============================================================================

from .routes import (
    agent,
    cross_archive_graph,
    curriculum,
    geospatial,
    official_media,
    search,
)
app.include_router(search.router)
app.include_router(geospatial.router)
app.include_router(curriculum.router)
app.include_router(agent.router)
app.include_router(cross_archive_graph.router)
# Official-media pipeline (Phase 6 of the official-media-pipeline change)
app.include_router(official_media.router)


# ============================================================================
# Health Check
# ============================================================================

class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    services: dict[str, str]
    observability: dict[str, str]


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns status of API, dependent services, and observability stack.
    """
    from oideachais.observability import get_langfuse_client, is_initialized, is_llmobs_enabled

    services = {
        "api": "healthy",
        "duckdb": "unknown",
        "lancedb": "unknown",
    }

    observability = {
        "datadog_apm": "disabled",
        "datadog_llmobs": "disabled",
        "mlflow": "unknown",
        "langfuse": "unknown",
    }

    # Check DuckDB
    try:
        import duckdb
        conn = duckdb.connect("./storage/data/celtic_education.duckdb", read_only=True)
        conn.execute("SELECT 1").fetchone()
        conn.close()
        services["duckdb"] = "healthy"
    except Exception:
        services["duckdb"] = "unavailable"

    # Check LanceDB
    try:
        import lancedb
        db = lancedb.connect("./storage/data/lancedb")
        services["lancedb"] = "healthy"
    except Exception:
        services["lancedb"] = "unavailable"

    # Check Datadog
    if is_initialized():
        observability["datadog_apm"] = "enabled"
    if is_llmobs_enabled():
        observability["datadog_llmobs"] = "enabled"

    # Check MLflow
    try:
        import mlflow
        if mlflow.active_run() is not None or mlflow.get_tracking_uri():
            observability["mlflow"] = "connected"
        else:
            observability["mlflow"] = "configured"
    except Exception:
        observability["mlflow"] = "unavailable"

    # Check Langfuse
    try:
        client = get_langfuse_client()
        if client is not None:
            observability["langfuse"] = "connected"
        else:
            observability["langfuse"] = "disabled"
    except Exception:
        observability["langfuse"] = "unavailable"

    overall_status = "healthy" if all(
        v in ("healthy", "enabled", "connected", "configured")
        for v in list(services.values()) + list(observability.values())
    ) else "degraded"

    return HealthResponse(
        status=overall_status,
        version="0.1.0",
        services=services,
        observability=observability,
    )


# ============================================================================
# Root Endpoint
# ============================================================================

@app.get("/")
async def root() -> dict[str, Any]:
    """API root - returns basic info."""
    return {
        "name": "Celtic Education Platform API",
        "version": "0.1.0",
        "docs": "/docs",
        "endpoints": {
            "search": "/search",
            "geospatial": "/geo",
            "agent": "/agent",
            "health": "/health",
        },
    }


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    return HTTPException(
        status_code=500,
        detail=f"Internal server error: {str(exc)}",
    )


# ============================================================================
# CLI Entry Point
# ============================================================================

def main():
    """Run the API server."""
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()
