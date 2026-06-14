"""
Simple Celtic Education API.

Minimal FastAPI application for curriculum data and AG-UI streaming.
No external observability dependencies required.

Usage:
    cd sruth/oideachais
    python -m uvicorn api.main_simple:app --reload --port 8000
"""
from __future__ import annotations

import logging
import os
import sys
from contextlib import asynccontextmanager

# Ensure the correct directories are on the Python path
# This allows imports like 'from storage.curriculum_vectors import ...'
# and 'from sruth.shared.storage import ...'
_oideachais_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_sruth_dir = os.path.dirname(_oideachais_dir)  # sruth/
_root_dir = os.path.dirname(_sruth_dir)  # Parent of sruth/ (for 'from sruth.X import')

for _path in [_oideachais_dir, _root_dir]:
    if _path not in sys.path:
        sys.path.insert(0, _path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Celtic Education API starting...")
    yield
    logger.info("Celtic Education API shutting down...")


app = FastAPI(
    title="Celtic Education API",
    description="""
API for Celtic education content with AG-UI streaming support.

## Features
- **AG-UI Agent**: SSE streaming chat endpoint
- **Curriculum Search**: Query curriculum pages and learning outcomes
- **Cross-Nation**: Compare curricula across Celtic nations

## Endpoints
- `POST /api/agent` - AG-UI streaming agent
- `GET /api/curriculum/pages` - List curriculum pages
- `GET /api/curriculum/outcomes` - List learning outcomes
- `GET /api/curriculum/stats` - Get statistics
    """,
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from .routes.agent import agui_router
from .routes.agent import router as agent_router
from .routes.curriculum import router as curriculum_router

app.include_router(curriculum_router)
app.include_router(agent_router)
app.include_router(agui_router)  # AG-UI protocol endpoints


@app.get("/")
async def root():
    """API root."""
    return {
        "name": "Celtic Education API",
        "version": "0.1.0",
        "endpoints": {
            "agent": "POST /api/agent",
            "curriculum_pages": "GET /api/curriculum/pages",
            "learning_outcomes": "GET /api/curriculum/outcomes",
            "subjects": "GET /api/curriculum/subjects",
            "stats": "GET /api/curriculum/stats",
            "health": "GET /api/health",
        },
    }


@app.get("/health")
async def health():
    """Global health check."""
    return {"status": "healthy", "version": "0.1.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
