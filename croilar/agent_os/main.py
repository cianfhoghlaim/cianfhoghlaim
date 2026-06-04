"""Aleyum AgentOS - Production Runtime for Research Agents.

This is the main entrypoint for the Aleyum research agent service.
Provides deep research capabilities with multi-hop reasoning.

Usage:
    # Development
    python -m sruth.aleyum.agent_os.main

    # Production (via uvicorn)
    uvicorn sruth.aleyum.agent_os.main:app --host 0.0.0.0 --port 7774
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import List, Optional

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.anthropic import Claude
from agno.os import AgentOS
from agno.db.sqlite import SqliteDb
from agno.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.newspaper4k import Newspaper4kTools
from pydantic import BaseModel, Field

# Import shared middleware
from sruth.shared.agent_os.middleware import TinyAuthMiddleware, A2AAuthMiddleware
from sruth.shared.agent_os.config import init_config

# Initialize config for this service
config = init_config(service_name="aleyum", service_port=7774)

# Storage
STORAGE_DIR = Path(os.getenv("AGNO_STORAGE_DIR", "./storage/sessions"))
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

team_storage = SqliteDb(
    session_table="research_team_sessions",
    db_file=str(STORAGE_DIR / "research_team.db"),
)


# =============================================================================
# Structured Output Models
# =============================================================================

class ResearchSource(BaseModel):
    """A source from research."""

    title: str
    url: str
    snippet: str
    relevance_score: float = 1.0


class ResearchReport(BaseModel):
    """A research report."""

    topic: str
    summary: str
    key_findings: List[str] = Field(default_factory=list)
    sources: List[ResearchSource] = Field(default_factory=list)
    follow_up_questions: List[str] = Field(default_factory=list)
    confidence: float = 0.8


class ResearchResponse(BaseModel):
    """Response from research team."""

    query: str
    report: ResearchReport
    cross_flow_data: dict = Field(default_factory=dict)  # Data from other flows


# =============================================================================
# Agent Definitions
# =============================================================================

DEFAULT_MODEL = os.getenv("AGNO_DEFAULT_MODEL", "gpt-4o")
CLAUDE_MODEL = os.getenv("AGNO_CLAUDE_MODEL", "claude-sonnet-4-20250514")


# Web Research Agent
web_researcher = Agent(
    name="Web Researcher",
    model=OpenAIChat(id=DEFAULT_MODEL),
    role="Performs comprehensive web research using search and article extraction. "
    "Synthesizes information from multiple sources with proper citations.",
    tools=[DuckDuckGoTools(), Newspaper4kTools()],
    instructions=[
        "Search for authoritative and recent sources.",
        "Cross-reference multiple sources for accuracy.",
        "Extract key facts and insights.",
        "Include proper citations with URLs.",
        "Note source credibility and recency.",
        "Identify gaps in available information.",
    ],
    add_datetime_to_context=True,
    markdown=True,
)


# Analysis Agent
analyst = Agent(
    name="Research Analyst",
    model=Claude(id=CLAUDE_MODEL),
    role="Analyzes research findings and synthesizes coherent reports. "
    "Identifies patterns, contradictions, and insights across sources.",
    tools=[],  # Analysis only, no external tools
    instructions=[
        "Synthesize findings from multiple sources.",
        "Identify key patterns and trends.",
        "Note contradictions between sources.",
        "Provide balanced, evidence-based conclusions.",
        "Suggest areas for further investigation.",
        "Quantify confidence in conclusions.",
    ],
    markdown=True,
)


# Cross-Flow Integration Agent
integrator = Agent(
    name="Cross-Flow Integrator",
    model=OpenAIChat(id=DEFAULT_MODEL),
    role="Integrates research with data from other flows (oideachais, crypteolas, browser). "
    "Calls remote agents via A2A for domain-specific information.",
    tools=[],  # Will use A2A client
    instructions=[
        "Identify when domain-specific expertise is needed.",
        "Call appropriate agents in other flows via A2A:",
        "  - Education topics → oideachais/curriculum",
        "  - DeFi/crypto topics → crypteolas/protocol-team",
        "  - Web automation needs → browser/orchestrator",
        "Integrate cross-flow responses into research.",
        "Note which flows contributed to the response.",
    ],
    add_datetime_to_context=True,
    markdown=True,
)


# Research Team
research_team = Team(
    name="Research Team",
    model=OpenAIChat(id=DEFAULT_MODEL),
    members=[
        web_researcher,
        analyst,
        integrator,
    ],
    db=team_storage,
    description=(
        "A coordinated research team for deep investigation and analysis. "
        "Combines web research, analysis, and cross-flow integration "
        "for comprehensive research reports."
    ),
    instructions=[
        # Research process
        "Follow structured research process:",
        "1. Clarify research scope and objectives",
        "2. Conduct web research with multiple sources",
        "3. Analyze and synthesize findings",
        "4. Integrate cross-flow data if relevant",
        "5. Produce comprehensive report",
        "",
        # Quality standards
        "Prioritize accuracy over speed.",
        "Include confidence levels in conclusions.",
        "Note limitations and gaps in research.",
        "Provide actionable follow-up questions.",
        "",
        # Cross-flow integration
        "Use cross-flow calls for domain expertise:",
        "  - Irish education → oideachais agents",
        "  - DeFi protocols → crypteolas agents",
        "  - Web scraping → browser agents",
    ],
    output_schema=ResearchResponse,
    share_member_interactions=True,
    markdown=True,
    debug_mode=os.getenv("AGNO_DEBUG", "false").lower() == "true",
)


# Create AgentOS instance
agent_os = AgentOS(
    id="aleyum-agent-os",
    name="Aleyum Research AgentOS",
    description=(
        "Production runtime for deep research agents. "
        "Provides web research, analysis, and cross-flow integration "
        "for comprehensive research capabilities."
    ),
    agents=[
        web_researcher,
        analyst,
        integrator,
    ],
    teams=[research_team],
    a2a_interface=True,
    config=os.environ.get("ALEYUM_CONFIG", str(Path(__file__).parent / "config.yaml")),
)

# Get the FastAPI app
app = agent_os.get_app()

# Add middleware
app.add_middleware(A2AAuthMiddleware)
app.add_middleware(
    TinyAuthMiddleware,
    require_auth=False,
    skip_paths=["/health", "/healthz", "/ready", "/metrics", "/.well-known", "/docs", "/openapi.json"],
)


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "aleyum-agent-os", "version": "1.0.0"}


@app.get("/ready")
async def ready():
    return {
        "status": "ready",
        "agents": ["web-researcher", "analyst", "integrator"],
        "teams": ["research-team"],
    }


# Cross-flow research endpoint
@app.post("/research")
async def deep_research(request: dict):
    """Perform deep research with cross-flow integration."""
    from fastapi import HTTPException

    query = request.get("query")
    if not query:
        raise HTTPException(400, "query required")

    include_flows = request.get("include_flows", [])
    session_id = request.get("session_id")

    # Run research team
    result = research_team.run(
        query,
        session_id=session_id,
        stream=False,
    )

    # If cross-flow integration requested, call other flows
    if include_flows:
        from sruth.shared.agent_os.a2a import A2AClient

        client = A2AClient()
        cross_flow_data = {}

        for flow in include_flows:
            try:
                if flow == "oideachais":
                    response = await client.send_message("curriculum", query)
                    cross_flow_data["oideachais"] = response.content
                elif flow == "crypteolas":
                    response = await client.send_message("protocol_research", query)
                    cross_flow_data["crypteolas"] = response.content
                elif flow == "browser":
                    response = await client.send_message("browser_orchestrator", query)
                    cross_flow_data["browser"] = response.content
            except Exception as e:
                cross_flow_data[flow] = f"Error: {str(e)}"

        result.cross_flow_data = cross_flow_data

    return result


if __name__ == "__main__":
    agent_os.serve(
        app="sruth.aleyum.agent_os.main:app",
        host="0.0.0.0",
        port=7774,
        reload=True,
    )
