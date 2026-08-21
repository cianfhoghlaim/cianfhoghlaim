"""
FastAPI Backend for Crypteolas.

Provides:
- AG-UI SSE streaming for CopilotKit
- Code search endpoints
- DeFi analytics endpoints
- Documentation search endpoints
- x402 payment protocol support
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog

from .routes import agent, search, analytics, github, payments
from .lib.pricing_config import PRICING_CONFIG

# Import x402 payment middleware from local lib
from .lib.x402 import X402Middleware

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Starting Crypteolas API")
    yield
    logger.info("Shutting down Crypteolas API")


# Create FastAPI app
app = FastAPI(
    title="Crypteolas API",
    description="GitHub Intelligence + DeFi Analytics API",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get(
        "CORS_ORIGINS", "http://localhost:3000,http://localhost:5173"
    ).split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add x402 payment middleware
# Set X402_SKIP_VERIFICATION=true for development without blockchain
app.add_middleware(
    X402Middleware,
    protected_paths=list(PRICING_CONFIG.keys()) if PRICING_CONFIG else [],
    skip_verification=os.environ.get("X402_SKIP_VERIFICATION", "true").lower() == "true",
)

# Include routers
app.include_router(agent.router, prefix="/api/agent", tags=["agent"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(github.router, prefix="/api/github", tags=["github"])
app.include_router(payments.router, prefix="/api/payments", tags=["payments"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "crypteolas"}


@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "service": "crypteolas",
        "version": "0.1.0",
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error("Unhandled exception", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
