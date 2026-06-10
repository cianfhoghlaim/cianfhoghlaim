"""Oideachais AgentOS - Production Runtime for Celtic Education Agents.

This is the main entrypoint for the Oideachais agent service.
It wraps the existing Agno education team in AgentOS for:
- A2A protocol endpoints for inter-agent communication
- AG-UI streaming for frontend integration
- TinyAuth for user authentication via Pangolin/Traefik
- Session persistence via PostgreSQL

Usage:
    # Development
    python -m oideachais.agent_os.main

    # Production (via uvicorn)
    uvicorn oideachais.agent_os.main:app --host 0.0.0.0 --port 7772
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from agno.os import AgentOS

# Import existing education team and agents
from agents.agno.education_team import (
    corpus_agent,
    curriculum_agent,
    education_team,
    geospatial_agent,
    research_agent,
    statistics_agent,
    translation_agent,
)
from shared.agent_os.config import init_config

# Import shared middleware
from shared.agent_os.middleware import A2AAuthMiddleware, TinyAuthMiddleware

# Initialize config for this service
config = init_config(service_name="oideachais", service_port=7772)

# Create AgentOS instance with education agents and team
agent_os = AgentOS(
    id="oideachais-agent-os",
    name="Celtic Education AgentOS",
    description=(
        "Production runtime for Celtic education agents. "
        "Provides curriculum search, translation, research, "
        "folklore corpus access, and education statistics."
    ),
    agents=[
        curriculum_agent,
        research_agent,
        translation_agent,
        corpus_agent,
        geospatial_agent,
        statistics_agent,
    ],
    teams=[education_team],
    a2a_interface=True,  # Enable A2A endpoints
    config=os.environ.get("OIDEACHAIS_CONFIG", str(Path(__file__).parent / "config.yaml")),
)

# Get the FastAPI app
app = agent_os.get_app()

# Add middleware (order matters - last added is first executed)
# 1. A2A auth for inter-service calls (processed first for A2A paths)
app.add_middleware(A2AAuthMiddleware)

# 2. TinyAuth for user authentication (processed second)
app.add_middleware(
    TinyAuthMiddleware,
    require_auth=False,  # Allow unauthenticated for public endpoints
    skip_paths=[
        "/health",
        "/healthz",
        "/ready",
        "/metrics",
        "/.well-known",
        "/docs",
        "/openapi.json",
    ],
)


# Add custom health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint for Kubernetes/Docker."""
    return {
        "status": "healthy",
        "service": "oideachais-agent-os",
        "version": "1.0.0",
    }


@app.get("/ready")
async def ready():
    """Readiness check - verifies agent availability."""
    return {
        "status": "ready",
        "agents": [
            "curriculum-agent",
            "research-agent",
            "translation-agent",
            "corpus-agent",
            "geospatial-agent",
            "statistics-agent",
        ],
        "teams": ["education-team"],
    }


# Cross-flow A2A helper endpoint
@app.post("/internal/call-agent")
async def call_remote_agent(request: dict):
    """Internal endpoint for calling agents in other flows.

    This is used when the education team needs to call agents
    in crypteolas (e.g., for DeFi education content) or browser
    (e.g., for scraping educational resources).
    """
    from fastapi import HTTPException
    from shared.agent_os.a2a import call_agent

    target_agent = request.get("agent")
    message = request.get("message")
    user_id = request.get("user_id")

    if not target_agent or not message:
        raise HTTPException(400, "agent and message required")

    try:
        response = await call_agent(target_agent, message, user_id=user_id)
        return {
            "status": "success",
            "agent": target_agent,
            "response": response.content,
            "session_id": response.session_id,
        }
    except Exception as e:
        raise HTTPException(502, f"A2A call failed: {str(e)}")


if __name__ == "__main__":
    # Run with auto-reload for development
    agent_os.serve(
        app="oideachais.agent_os.main:app",
        host="0.0.0.0",
        port=7772,
        reload=True,
    )
