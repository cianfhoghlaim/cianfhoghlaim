"""
Protocol Analysis Team - Agno Multi-Agent Coordination.

A coordinated team of specialized agents for DeFi protocol analysis:
- Documentation Agent: Search protocol docs and whitepapers
- Code Analysis Agent: Smart contract and implementation analysis
- Graph Agent: Temporal knowledge graph queries
- Analytics Agent: DeFi metrics and on-chain analytics

Uses Agno Team with share_member_interactions for context sharing.
Supports session persistence via SqliteDb.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.models.openai import OpenAIChat
from agno.db.sqlite import SqliteDb
from agno.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from pydantic import BaseModel, Field


# Session storage configuration
STORAGE_DIR = Path(os.getenv("AGNO_STORAGE_DIR", "./storage/sessions"))
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

team_storage = SqliteDb(
    session_table="protocol_team_sessions",
    db_file=str(STORAGE_DIR / "protocol_team.db"),
)


# =============================================================================
# Custom Tools - Import from MCP server tools
# =============================================================================

class ProtocolDocTools:
    """Tools for protocol documentation search."""

    def search_docs(
        self,
        query: str,
        protocol: Optional[str] = None,
        source_type: Optional[str] = None,
        limit: int = 10,
    ) -> List[dict]:
        """Search protocol documentation."""
        import asyncio
        from ...mcp_server.tools import search_protocol_docs_impl
        return asyncio.get_event_loop().run_until_complete(
            search_protocol_docs_impl(query, protocol, source_type, limit)
        )

    def sync_docs(
        self,
        protocol_name: str,
        force_refresh: bool = False,
    ) -> dict:
        """Sync latest documentation for a protocol."""
        import asyncio
        from ...mcp_server.tools import sync_protocol_docs_impl
        return asyncio.get_event_loop().run_until_complete(
            sync_protocol_docs_impl(protocol_name, force_refresh)
        )


class ProtocolCodeTools:
    """Tools for protocol code analysis."""

    def search_code(
        self,
        query: str,
        protocol: Optional[str] = None,
        language: Optional[str] = None,
        limit: int = 10,
    ) -> List[dict]:
        """Search protocol code."""
        import asyncio
        from ...mcp_server.tools import search_protocol_code_impl
        return asyncio.get_event_loop().run_until_complete(
            search_protocol_code_impl(query, protocol, language, limit)
        )


class ProtocolGraphTools:
    """Tools for protocol knowledge graph queries."""

    def get_entity(
        self,
        protocol_name: str,
        entity_type: Optional[str] = None,
        point_in_time: Optional[str] = None,
    ) -> dict:
        """Get protocol entity with temporal awareness."""
        import asyncio
        from ...mcp_server.tools import get_protocol_entity_impl
        return asyncio.get_event_loop().run_until_complete(
            get_protocol_entity_impl(protocol_name, entity_type, point_in_time)
        )

    def get_relationships(
        self,
        protocol_name: str,
        relationship_types: Optional[List[str]] = None,
        direction: str = "both",
        limit: int = 20,
    ) -> dict:
        """Get protocol relationships."""
        import asyncio
        from ...mcp_server.tools import get_protocol_relationships_impl
        return asyncio.get_event_loop().run_until_complete(
            get_protocol_relationships_impl(protocol_name, relationship_types, direction, limit)
        )

    def get_timeline(
        self,
        protocol_name: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> dict:
        """Get protocol timeline."""
        import asyncio
        from ...mcp_server.tools import get_protocol_timeline_impl
        return asyncio.get_event_loop().run_until_complete(
            get_protocol_timeline_impl(protocol_name, start_date, end_date)
        )

    def compare_protocols(
        self,
        protocol_a: str,
        protocol_b: str,
        aspects: Optional[List[str]] = None,
    ) -> dict:
        """Compare two protocols."""
        import asyncio
        from ...mcp_server.tools import compare_protocols_impl
        return asyncio.get_event_loop().run_until_complete(
            compare_protocols_impl(protocol_a, protocol_b, aspects)
        )


class DeFiAnalyticsTools:
    """Tools for DeFi analytics."""

    def get_protocol_metrics(
        self,
        protocol_name: str,
        metrics: Optional[List[str]] = None,
    ) -> dict:
        """Get protocol metrics (TVL, volume, users)."""
        # Placeholder - would integrate with DeFiLlama, Dune, etc.
        return {
            "protocol": protocol_name,
            "metrics": metrics or ["tvl", "volume", "users"],
            "data": {},
        }

    def get_historical_data(
        self,
        protocol_name: str,
        metric: str,
        start_date: str,
        end_date: str,
    ) -> dict:
        """Get historical metric data."""
        return {
            "protocol": protocol_name,
            "metric": metric,
            "period": f"{start_date} to {end_date}",
            "data": [],
        }


# =============================================================================
# Structured Output Models
# =============================================================================

class ProtocolSearchResult(BaseModel):
    """Result from protocol documentation search."""

    query: str
    protocol: Optional[str] = None
    results: List[dict] = Field(default_factory=list)
    source_types: List[str] = Field(default_factory=list)
    total_matches: int = 0


class CodeAnalysisResult(BaseModel):
    """Result from code analysis."""

    protocol: str
    contracts: List[dict] = Field(default_factory=list)
    functions: List[dict] = Field(default_factory=list)
    security_notes: List[str] = Field(default_factory=list)
    patterns_identified: List[str] = Field(default_factory=list)


class ProtocolEntity(BaseModel):
    """Protocol entity from knowledge graph."""

    id: str
    entity_type: str
    name: str
    properties: dict = Field(default_factory=dict)
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None
    relationships: List[dict] = Field(default_factory=list)


class ProtocolAnalysis(BaseModel):
    """Comprehensive protocol analysis."""

    protocol: str
    summary: str
    architecture: Optional[str] = None
    key_contracts: List[dict] = Field(default_factory=list)
    integrations: List[dict] = Field(default_factory=list)
    audits: List[dict] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    metrics: dict = Field(default_factory=dict)


class ProtocolResponse(BaseModel):
    """Unified response from protocol team."""

    query: str
    summary: str
    documentation: Optional[ProtocolSearchResult] = None
    code_analysis: Optional[CodeAnalysisResult] = None
    graph_data: Optional[ProtocolEntity] = None
    analytics: Optional[dict] = None
    protocol_analysis: Optional[ProtocolAnalysis] = None
    follow_up_suggestions: List[str] = Field(default_factory=list)


# =============================================================================
# Agent Definitions
# =============================================================================

DEFAULT_MODEL = os.getenv("AGNO_DEFAULT_MODEL", "gpt-4o")
CLAUDE_MODEL = os.getenv("AGNO_CLAUDE_MODEL", "claude-sonnet-4-20250514")


def get_model(model_type: str = "default"):
    """Get the appropriate model."""
    if model_type == "claude":
        return Claude(id=CLAUDE_MODEL)
    else:
        return OpenAIChat(id=DEFAULT_MODEL)


# Documentation Agent
documentation_agent = Agent(
    name="Protocol Documentation Agent",
    model=get_model("default"),
    role="Searches and synthesizes DeFi protocol documentation. "
    "Covers whitepapers, technical docs, governance proposals, "
    "and audit reports for protocols like Uniswap, Aave, Compound, etc.",
    tools=[ProtocolDocTools(), DuckDuckGoTools()],
    instructions=[
        "Search indexed documentation first, then web if needed.",
        "Prioritize official documentation over third-party sources.",
        "Include links to source documents.",
        "Note the recency of documentation.",
        "Highlight version-specific information.",
        "Cross-reference with audit reports when security is relevant.",
        "Explain technical concepts in accessible terms.",
    ],
    add_datetime_to_context=True,
    markdown=True,
)


# Code Analysis Agent
code_analysis_agent = Agent(
    name="Smart Contract Agent",
    model=get_model("claude"),  # Claude for code understanding
    role="Analyzes smart contracts and protocol implementations. "
    "Reviews Solidity, Vyper, and off-chain code. Identifies "
    "patterns, security considerations, and integration points.",
    tools=[ProtocolCodeTools()],
    instructions=[
        "Search for relevant contracts and implementations.",
        "Identify common patterns (proxies, vaults, AMMs, oracles).",
        "Note access control and privilege patterns.",
        "Highlight potential security considerations.",
        "Explain complex logic step by step.",
        "Cross-reference with protocol documentation.",
        "Note gas optimization patterns.",
    ],
    add_datetime_to_context=True,
    markdown=True,
)


# Graph Agent
graph_agent = Agent(
    name="Protocol Graph Agent",
    model=get_model("default"),
    role="Queries the temporal knowledge graph for protocol relationships. "
    "Tracks integrations, dependencies, oracle connections, and "
    "historical changes using bi-temporal data model.",
    tools=[ProtocolGraphTools()],
    instructions=[
        "Use temporal queries for historical protocol states.",
        "Map integration relationships between protocols.",
        "Track governance and version changes over time.",
        "Identify shared dependencies (oracles, liquidity).",
        "Compare protocols across multiple dimensions.",
        "Note timeline of key events (launches, upgrades, incidents).",
        "Provide point-in-time analysis when requested.",
    ],
    add_datetime_to_context=True,
    markdown=True,
)


# Analytics Agent
analytics_agent = Agent(
    name="DeFi Analytics Agent",
    model=get_model("default"),
    role="Provides on-chain analytics and metrics for DeFi protocols. "
    "Covers TVL, volume, user metrics, and cross-protocol comparisons "
    "using DeFiLlama, Dune, and other data sources.",
    tools=[DeFiAnalyticsTools(), DuckDuckGoTools()],
    instructions=[
        "Provide current metrics with timestamps.",
        "Include trend analysis when relevant.",
        "Compare against market benchmarks.",
        "Note data source and methodology.",
        "Highlight anomalies or significant changes.",
        "Consider chain-specific differences.",
        "Relate metrics to protocol events when possible.",
    ],
    add_datetime_to_context=True,
    markdown=True,
)


# =============================================================================
# Protocol Team
# =============================================================================

protocol_team = Team(
    name="Protocol Analysis Team",
    model=get_model("default"),
    members=[
        documentation_agent,
        code_analysis_agent,
        graph_agent,
        analytics_agent,
    ],
    db=team_storage,
    description=(
        "A coordinated team of AI agents specialized in DeFi protocol analysis. "
        "Covers documentation, smart contracts, protocol relationships, and "
        "on-chain analytics. Routes queries to appropriate specialists and "
        "synthesizes comprehensive protocol insights."
    ),
    instructions=[
        # Query routing
        "Analyze the query to identify which agents are needed.",
        "For documentation/how-to → Documentation Agent",
        "For code/contracts → Smart Contract Agent",
        "For relationships/history → Protocol Graph Agent",
        "For metrics/analytics → Analytics Agent",
        "",
        # Multi-agent coordination
        "Complex queries often need multiple agents:",
        "  - 'How does X work?' → Documentation + Code",
        "  - 'Compare X and Y' → Graph + Analytics",
        "  - 'Is X secure?' → Code + Documentation (audits)",
        "  - 'X integrations' → Graph + Documentation",
        "",
        # Response format
        "Always include protocol names and versions.",
        "Link to source materials.",
        "Note temporal context (when was this true?).",
        "Highlight risks and security considerations.",
        "",
        # Protocol categories
        "Consider protocol categories:",
        "  - DEXes: Uniswap, Curve, Balancer, SushiSwap",
        "  - Lending: Aave, Compound, MakerDAO, Morpho",
        "  - Oracles: Chainlink, UMA, Band, API3",
        "  - Bridges: Across, Stargate, LayerZero",
        "  - Liquid Staking: Lido, Rocket Pool, Frax",
        "",
        # Risk awareness
        "Always note potential risks:",
        "  - Smart contract risk (unaudited, upgradeable)",
        "  - Oracle dependencies",
        "  - Governance centralization",
        "  - Liquidity and market risks",
    ],
    # output_schema=ProtocolResponse,  # Disabled: OpenAI structured output has strict schema requirements
    share_member_interactions=True,
    markdown=True,
    debug_mode=os.getenv("AGNO_DEBUG", "false").lower() == "true",
    show_members_responses=True,
)


# =============================================================================
# Convenience Functions
# =============================================================================

def ask_protocol_team(
    query: str,
    stream: bool = True,
    session_id: Optional[str] = None,
) -> ProtocolResponse:
    """
    Query the Protocol Analysis Team.

    Args:
        query: The user's question about DeFi protocols.
        stream: Whether to stream the response.
        session_id: Optional session ID for conversation continuity.

    Returns:
        Structured ProtocolResponse with analysis from relevant agents.
    """
    run_kwargs = {"stream": stream}
    if session_id:
        run_kwargs["session_id"] = session_id

    return protocol_team.run(query, **run_kwargs)


def search_protocol_docs(
    query: str,
    protocol: Optional[str] = None,
    source_type: Optional[str] = None,
) -> ProtocolSearchResult:
    """
    Direct protocol documentation search.

    Args:
        query: Search query.
        protocol: Filter by protocol name.
        source_type: Filter by source type (docs, whitepaper, audit).

    Returns:
        ProtocolSearchResult with matching documentation.
    """
    search_query = query
    if protocol:
        search_query = f"[{protocol}] {query}"
    if source_type:
        search_query += f" type:{source_type}"

    return documentation_agent.run(search_query)


def get_protocol_info(
    protocol_name: str,
    point_in_time: Optional[str] = None,
) -> ProtocolEntity:
    """
    Get protocol entity information.

    Args:
        protocol_name: Name of the protocol.
        point_in_time: Optional ISO datetime for historical query.

    Returns:
        ProtocolEntity with protocol details and relationships.
    """
    query = f"Get information about {protocol_name}"
    if point_in_time:
        query += f" as of {point_in_time}"

    return graph_agent.run(query)


def analyze_protocol(
    protocol_name: str,
    aspects: Optional[List[str]] = None,
) -> ProtocolAnalysis:
    """
    Comprehensive protocol analysis.

    Args:
        protocol_name: Name of the protocol to analyze.
        aspects: Specific aspects to analyze (architecture, security, metrics).

    Returns:
        ProtocolAnalysis with comprehensive assessment.
    """
    aspects = aspects or ["architecture", "security", "integrations", "metrics"]
    return protocol_team.run(
        f"Provide comprehensive analysis of {protocol_name} "
        f"covering: {', '.join(aspects)}"
    )


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    print("Protocol Analysis Team - Interactive Mode")
    print("=" * 50)
    print("Ask questions about DeFi protocols: docs, contracts,")
    print("relationships, metrics, and comparisons.")
    print("Type 'exit' to quit.")
    print("=" * 50)

    while True:
        try:
            query = input("\nYou: ").strip()
            if query.lower() in ("exit", "quit", "q"):
                print("Goodbye!")
                break
            if not query:
                continue

            print("\nProtocol Team:")
            protocol_team.print_response(query, stream=True)

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
