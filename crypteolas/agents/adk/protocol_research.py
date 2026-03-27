"""
Protocol Research Agent for Crypteolas.

Deep research on DeFi protocols including:
- Architecture analysis
- Tokenomics
- Competitive landscape
- Historical evolution
"""

import datetime

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from ..config import config
from ..tools.document_search import search_documents, search_whitepapers
from ...knowledge_graph.graphiti.temporal_graph import (
    get_protocol_facts,
    query_protocol_timeline,
    find_related_protocols,
)
from ...knowledge_graph.cognee.static_knowledge import (
    search_knowledge,
    compare_protocols,
)


# Define tools
async def research_protocol(
    protocol_name: str,
    include_history: bool = True,
    include_related: bool = True,
) -> dict:
    """
    Comprehensive research on a protocol.

    Args:
        protocol_name: Name of the protocol to research
        include_history: Include temporal evolution
        include_related: Include related protocols
    """
    results = {
        "protocol": protocol_name,
        "facts": [],
        "timeline": [],
        "related": [],
        "documentation": [],
    }

    # Get facts from knowledge graph
    try:
        results["facts"] = await get_protocol_facts(None, protocol_name)
    except Exception:
        pass

    # Get timeline if requested
    if include_history:
        try:
            results["timeline"] = await query_protocol_timeline(None, protocol_name)
        except Exception:
            pass

    # Get related protocols if requested
    if include_related:
        try:
            results["related"] = await find_related_protocols(None, protocol_name)
        except Exception:
            pass

    # Search documentation
    try:
        docs = await search_documents(protocol_name, protocol=protocol_name, limit=5)
        results["documentation"] = docs.results if hasattr(docs, "results") else []
    except Exception:
        pass

    return results


async def compare_protocol_pair(
    protocol_a: str,
    protocol_b: str,
) -> dict:
    """
    Compare two protocols.

    Args:
        protocol_a: First protocol name
        protocol_b: Second protocol name
    """
    try:
        return await compare_protocols(protocol_a, protocol_b)
    except Exception as e:
        return {"error": str(e)}


async def search_protocol_docs(
    query: str,
    protocol: str | None = None,
) -> list[dict]:
    """
    Search protocol documentation.

    Args:
        query: Search query
        protocol: Optional protocol filter
    """
    try:
        results = await search_documents(query, protocol=protocol, limit=10)
        return results.results if hasattr(results, "results") else []
    except Exception:
        return []


async def get_whitepaper_info(
    protocol: str,
    topic: str | None = None,
) -> list[dict]:
    """
    Get information from protocol whitepaper.

    Args:
        protocol: Protocol name
        topic: Optional topic to focus on
    """
    try:
        query = f"{protocol} {topic}" if topic else protocol
        return await search_whitepapers(query, protocol=protocol, limit=5)
    except Exception:
        return []


# Create tools
research_tool = FunctionTool(func=research_protocol)
compare_tool = FunctionTool(func=compare_protocol_pair)
docs_search_tool = FunctionTool(func=search_protocol_docs)
whitepaper_tool = FunctionTool(func=get_whitepaper_info)


# Protocol Research Agent
protocol_research_agent = LlmAgent(
    name="protocol_research_agent",
    model=config.worker_model,
    description="Deep research on DeFi protocols including architecture, tokenomics, and history.",
    instruction=f"""
    You are a Protocol Research specialist for crypto and DeFi.

    **YOUR EXPERTISE:**
    - Protocol architecture analysis
    - Tokenomics and incentive mechanisms
    - Competitive landscape mapping
    - Historical protocol evolution
    - Fork analysis and differentiation

    **AVAILABLE TOOLS:**
    1. research_protocol - Comprehensive protocol research
    2. compare_protocol_pair - Compare two protocols
    3. search_protocol_docs - Search documentation
    4. get_whitepaper_info - Extract whitepaper information

    **RESEARCH APPROACH:**
    1. Start with comprehensive research_protocol call
    2. Use documentation search for specific details
    3. Compare with similar protocols for context
    4. Reference whitepapers for authoritative information

    **OUTPUT FORMAT:**
    - Clear section headings
    - Bullet points for key facts
    - Cite sources (docs, whitepaper, timeline)
    - Note confidence levels

    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    """,
    tools=[research_tool, compare_tool, docs_search_tool, whitepaper_tool],
    output_key="research_findings",
)
