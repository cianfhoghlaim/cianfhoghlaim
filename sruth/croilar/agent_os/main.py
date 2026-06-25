"""Croilar AgentOS — generic, stream-driven runtime.

The legacy `aleyum-agent-os` runtime is replaced by a generic factory
that builds one AgentOS instance per registered Stream. Each stream
gets its own port (from `Stream.agent_port`) and its own service id
(`croilar-{stream.id}-agent-os`).

Usage (per stream):

    # Music stream (port 7774)
    python -m sruth.croilar.agent_os.main --stream music

    # Teaching stream (port 7775)
    python -m sruth.croilar.agent_os.main --stream teaching

    # CV stream (port 7776)
    python -m sruth.croilar.agent_os.main --stream cv

    # Research stream (port 7777)
    python -m sruth.croilar.agent_os.main --stream research

Production (via uvicorn):

    uvicorn sruth.croilar.agent_os.main:app --host 0.0.0.0 --port 7774
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import List

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.anthropic import Claude
from agno.models.openai import OpenAIChat
from agno.os import AgentOS
from agno.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.newspaper4k import Newspaper4kTools
from pydantic import BaseModel, Field

from _shared.streams import Stream, get_stream, list_streams
from sruth.shared.agent_os.config import init_config
from sruth.shared.agent_os.middleware import A2AAuthMiddleware, TinyAuthMiddleware

# Resolve default stream from CLI / env
_DEFAULT_STREAM_ID = os.getenv("CROILAR_STREAM_ID", "music")


def _resolve_stream(stream_id: str) -> Stream:
    try:
        return get_stream(stream_id)
    except KeyError as e:
        available = [s.id for s in list_streams()]
        raise SystemExit(
            f"Unknown stream {stream_id!r}; available: {available}"
        ) from e


# Initialize config for this service (stream-specific).
# Done after stream resolution so we can pass the right port.
stream: Stream = _resolve_stream(_DEFAULT_STREAM_ID)
config = init_config(service_name=stream.id, service_port=stream.agent_port)

# Storage
STORAGE_DIR = Path(os.getenv("AGNO_STORAGE_DIR", "./storage/sessions"))
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

team_storage = SqliteDb(
    session_table="research_team_sessions",
    db_file=str(STORAGE_DIR / f"research_team_{stream.id}.db"),
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
    role=(
        "Performs comprehensive web research using search and article extraction. "
        "Synthesizes information from multiple sources with proper citations."
    ),
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
    role=(
        "Analyzes research findings and synthesizes coherent reports. "
        "Identifies patterns, contradictions, and insights across sources."
    ),
    tools=[],
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


# Cross-Stream Integration Agent
integrator = Agent(
    name="Cross-Stream Integrator",
    model=OpenAIChat(id=DEFAULT_MODEL),
    role=(
        "Integrates research with data from other streams (oideachais, crypteolas, browser). "
        "Calls remote agents via A2A for domain-specific information."
    ),
    tools=[],
    instructions=[
        "Identify when domain-specific expertise is needed.",
        "Call appropriate agents in other streams via A2A:",
        "  - Education topics → oideachais/curriculum",
        "  - DeFi/crypto topics → crypteolas/protocol-team",
        "  - Web automation needs → browser/orchestrator",
        "Integrate cross-stream responses into research.",
        "Note which streams contributed to the response.",
    ],
    add_datetime_to_context=True,
    markdown=True,
)


# Research Team
research_team = Team(
    name="Research Team",
    model=OpenAIChat(id=DEFAULT_MODEL),
    members=[web_researcher, analyst, integrator],
    db=team_storage,
    description=(
        "A coordinated research team for deep investigation and analysis. "
        "Combines web research, analysis, and cross-stream integration "
        "for comprehensive research reports."
    ),
    instructions=[
        "Follow structured research process:",
        "1. Clarify research scope and objectives",
        "2. Conduct web research with multiple sources",
        "3. Analyze and synthesize findings",
        "4. Integrate cross-stream data if relevant",
        "5. Produce comprehensive report",
        "",
        "Prioritize accuracy over speed.",
        "Include confidence levels in conclusions.",
        "Note limitations and gaps in research.",
        "Provide actionable follow-up questions.",
        "",
        "Use cross-stream calls for domain expertise:",
        "  - Irish education → oideachais agents",
        "  - DeFi protocols → crypteolas agents",
        "  - Web scraping → browser agents",
    ],
    output_schema=ResearchResponse,
    share_member_interactions=True,
    markdown=True,
    debug_mode=os.getenv("AGNO_DEBUG", "false").lower() == "true",
)


# Create AgentOS instance — one per stream.
_SVC_ID = f"croilar-{stream.id}-agent-os"
_SVC_NAME = f"Croilar {stream.owner_display_name} ({stream.id}) AgentOS"

agent_os = AgentOS(
    id=_SVC_ID,
    name=_SVC_NAME,
    description=(
        f"Production runtime for the {stream.id!r} stream "
        f"(owner={stream.owner_display_name}). "
        f"Provides web research, analysis, and cross-stream integration."
    ),
    agents=[web_researcher, analyst, integrator],
    teams=[research_team],
    a2a_interface=True,
    config=os.environ.get("CROILAR_AGENTOS_CONFIG", str(Path(__file__).parent / "config.yaml")),
)

# FastAPI app
app = agent_os.get_app()

app.add_middleware(A2AAuthMiddleware)
app.add_middleware(
    TinyAuthMiddleware,
    require_auth=False,
    skip_paths=["/health", "/healthz", "/ready", "/metrics", "/.well-known", "/docs", "/openapi.json"],
)


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": _SVC_ID,
        "stream_id": stream.id,
        "owner": stream.owner_display_name,
        "version": "1.0.0",
    }


@app.get("/ready")
async def ready():
    return {
        "status": "ready",
        "stream_id": stream.id,
        "agents": ["web-researcher", "analyst", "integrator"],
        "teams": ["research-team"],
    }


# Cross-stream research endpoint
@app.post("/research")
async def deep_research(request: dict):
    """Perform deep research with cross-stream integration."""
    from fastapi import HTTPException

    query = request.get("query")
    if not query:
        raise HTTPException(400, "query required")

    include_streams = request.get("include_streams", [])
    session_id = request.get("session_id")

    result = research_team.run(query, session_id=session_id, stream=False)

    if include_streams:
        from sruth.shared.agent_os.a2a import A2AClient

        client = A2AClient()
        cross_stream_data: dict = {}

        for s in include_streams:
            try:
                if s == "oideachais":
                    response = await client.send_message("curriculum", query)
                    cross_stream_data["oideachais"] = response.content
                elif s == "crypteolas":
                    response = await client.send_message("protocol_research", query)
                    cross_stream_data["crypteolas"] = response.content
                elif s == "browser":
                    response = await client.send_message("browser_orchestrator", query)
                    cross_stream_data["browser"] = response.content
            except Exception as e:
                cross_stream_data[s] = f"Error: {str(e)}"

        result.cross_flow_data = cross_stream_data

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Croilar AgentOS (stream-driven)")
    parser.add_argument(
        "--stream",
        default=_DEFAULT_STREAM_ID,
        choices=[s.id for s in list_streams()],
        help="Stream id to serve (default: %(default)s; can also be set via CROILAR_STREAM_ID env var).",
    )
    parser.add_argument(
        "--host", default=os.getenv("CROILAR_AGENTOS_HOST", "0.0.0.0"),
        help="Bind host (default: %(default)s).",
    )
    parser.add_argument(
        "--port", type=int, default=None,
        help="Bind port (default: Stream.agent_port from the registry).",
    )
    parser.add_argument(
        "--reload", action="store_true",
        help="Enable auto-reload for development.",
    )
    args = parser.parse_args()

    target = _resolve_stream(args.stream)
    bind_port = args.port or target.agent_port

    agent_os.serve(
        app="sruth.croilar.agent_os.main:app",
        host=args.host,
        port=bind_port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()
