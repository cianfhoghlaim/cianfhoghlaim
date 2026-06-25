"""Crypteolas AgentOS - Production Runtime for DeFi Protocol Agents.

This is the main entrypoint for the Crypteolas agent service.
It wraps the existing Agno protocol team in AgentOS with:
- A2A protocol endpoints for inter-agent communication
- AG-UI streaming for frontend integration
- TinyAuth for user authentication
- x402 payment middleware for premium endpoints
- Session persistence via SQLite

Usage:
    # Development
    python -m tuatha.crypteolas.agent_os.main

    # Production (via uvicorn)
    uvicorn tuatha.crypteolas.agent_os.main:app --host 0.0.0.0 --port 7771
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from agno.os import AgentOS

# Import existing protocol team and agents
from sruth.tuatha.crypteolas.agents.agno.protocol_team import (
    protocol_team,
    documentation_agent,
    code_analysis_agent,
    graph_agent,
    analytics_agent,
)

# Import shared middleware (shim — see tuatha/crypteolas/_shims/agent_os/)
from sruth.tuatha.crypteolas._shims.agent_os.middleware import (
    TinyAuthMiddleware,
    A2AAuthMiddleware,
)
from sruth.tuatha.crypteolas._shims.agent_os.config import init_config

# Import x402 middleware
from .middleware import X402AgentMiddleware

# Initialize config for this service
config = init_config(service_name="crypteolas", service_port=7771)

# Create AgentOS instance with protocol agents and team
agent_os = AgentOS(
    id="crypteolas-agent-os",
    name="Crypteolas Protocol Analysis AgentOS",
    description=(
        "Production runtime for DeFi protocol analysis agents. "
        "Provides documentation search, smart contract analysis, "
        "temporal knowledge graph queries, and on-chain analytics."
    ),
    agents=[
        documentation_agent,
        code_analysis_agent,
        graph_agent,
        analytics_agent,
    ],
    teams=[protocol_team],
    a2a_interface=True,  # Enable A2A endpoints
    config=os.environ.get("CRYPTEOLAS_CONFIG", str(Path(__file__).parent / "config.yaml")),
)

# Get the FastAPI app
app = agent_os.get_app()

# Add middleware (order matters - last added is first executed)
# 1. x402 payment enforcement (processed first for A2A paths)
app.add_middleware(
    X402AgentMiddleware,
    skip_verification=os.environ.get("X402_SKIP_VERIFICATION", "false").lower() == "true",
)

# 2. A2A auth for inter-service calls
app.add_middleware(A2AAuthMiddleware)

# 3. TinyAuth for user authentication
app.add_middleware(
    TinyAuthMiddleware,
    require_auth=False,
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
        "service": "crypteolas-agent-os",
        "version": "1.0.0",
    }


@app.get("/ready")
async def ready():
    """Readiness check - verifies agent availability."""
    return {
        "status": "ready",
        "agents": [
            "documentation-agent",
            "code-analysis-agent",
            "graph-agent",
            "analytics-agent",
        ],
        "teams": ["protocol-team"],
        "payment_enabled": True,
    }


# Pricing information endpoint
@app.get("/api/pricing")
async def get_pricing():
    """Get pricing information for premium agents."""
    from .middleware import PROTECTED_AGENTS, FREE_AGENTS

    return {
        "protected_agents": {
            path: {
                "price_usd": cfg["price_usd"],
                "description": cfg["description"],
                "free_tier_per_day": cfg.get("free_tier", 0),
            }
            for path, cfg in PROTECTED_AGENTS.items()
        },
        "free_agents": FREE_AGENTS,
        "payment_network": os.environ.get("X402_NETWORK", "base"),
        "payment_asset": "USDC",
    }


# Cross-flow A2A helper endpoint
@app.post("/internal/call-agent")
async def call_remote_agent(request: dict):
    """Internal endpoint for calling agents in other flows.

    This is used when the protocol team needs to call agents
    in oideachais (e.g., for education-related DeFi content)
    or browser (e.g., for scraping protocol docs).
    """
    from fastapi import HTTPException

    from tuatha.crypteolas._shims.agent_os.a2a import call_agent

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
        app="tuatha.crypteolas.agent_os.main:app",
        host="0.0.0.0",
        port=7771,
        reload=True,
    )
