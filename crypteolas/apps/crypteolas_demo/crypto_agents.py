"""
Agno agent definitions for crypto analytics.

Provides specialized agents for:
- Research: Knowledge graph queries, documentation search
- Analysis: Data analysis, yield comparisons, risk assessment
- Coordination: Multi-agent task orchestration
"""

from typing import Any, Optional

from agno import Agent, Team, Tool, RunResponse
from agno.models.litellm import LiteLLM

from foinse.llm import get_model_id, LITELLM_BASE_URL


# =============================================================================
# Agent Tools
# =============================================================================


def search_knowledge_base(
    query: str,
    protocol_filter: Optional[str] = None,
    limit: int = 5,
) -> str:
    """
    Search the crypto knowledge base.

    Args:
        query: Search query
        protocol_filter: Optional protocol filter (ethena, aave, pendle, etc.)
        limit: Max results

    Returns:
        Formatted search results
    """
    from pipelines.indexers.cocoindex_flow import query_crypto_knowledge

    results = query_crypto_knowledge(
        query=query,
        protocol_filter=protocol_filter,
        limit=limit,
    )

    if not results:
        return "No relevant documents found."

    formatted = []
    for i, r in enumerate(results, 1):
        formatted.append(
            f"{i}. [{r.get('protocol', 'unknown')}] {r.get('content', '')[:300]}..."
        )

    return "\n\n".join(formatted)


def get_protocol_context(protocol: str) -> str:
    """
    Get comprehensive context for a protocol.

    Args:
        protocol: Protocol name

    Returns:
        Protocol documentation context
    """
    from pipelines.indexers.cocoindex_flow import get_protocol_context as _get_context

    return _get_context(protocol, limit=30)


def query_knowledge_graph(query: str, search_type: str = "insights") -> str:
    """
    Query Cognee knowledge graph.

    Args:
        query: Query string
        search_type: Type of search (insights, chunks, graph)

    Returns:
        Knowledge graph results
    """
    from pipelines.knowledge.cognee_pipeline import sync_query

    results = sync_query(query, search_type)

    if not results:
        return "No knowledge graph results found."

    return "\n".join([str(r) for r in results[:5]])


def get_funding_rate_analysis(symbol: str = "ETHUSDT", days: int = 30) -> str:
    """
    Get funding rate analysis.

    Args:
        symbol: Trading pair
        days: Lookback period

    Returns:
        Funding rate metrics
    """
    from pipelines.transformations.crypto_analytics import (
        calculate_funding_metrics,
        get_connection,
    )

    con = get_connection()
    metrics = calculate_funding_metrics(con, symbol=symbol, lookback_days=days)
    df = metrics.execute()

    if len(df) == 0:
        return "No funding data available."

    m = df.iloc[0]
    return f"""
Funding Rate Analysis for {symbol} (last {days} days):

- Average Rate: {m['avg_funding_rate']*100:.4f}% per 8h
- Annualized APR: {m['annualized_apr_avg']:.2f}%
- Positive Rate Periods: {m['positive_rate_pct']:.1f}%
- Observations: {int(m['count'])}

Interpretation: {"Favorable for basis trade" if m['positive_rate_pct'] > 70 else "Mixed conditions"}.
"""


def get_yield_comparison(protocols: Optional[list[str]] = None) -> str:
    """
    Compare yields across protocols.

    Args:
        protocols: Protocols to compare

    Returns:
        Yield comparison table
    """
    from pipelines.transformations.crypto_analytics import (
        build_yield_comparison_view,
        get_connection,
    )

    if protocols is None:
        protocols = ["ethena", "aave-v3", "pendle", "lido"]

    con = get_connection()
    comparison = build_yield_comparison_view(con, protocols=protocols)
    df = comparison.execute()

    if len(df) == 0:
        return "No yield data available."

    lines = ["Protocol Yield Comparison:", ""]
    for _, row in df.iterrows():
        lines.append(
            f"- {row['project']}: {row['weighted_avg_apy']:.2f}% weighted APY "
            f"(TVL: ${row['total_tvl']/1e9:.2f}B)"
        )

    return "\n".join(lines)


def get_stablecoin_metrics() -> str:
    """
    Get stablecoin supply and peg metrics.

    Returns:
        Stablecoin comparison
    """
    from pipelines.transformations.crypto_analytics import (
        calculate_stablecoin_metrics,
        get_connection,
    )

    con = get_connection()
    metrics = calculate_stablecoin_metrics(con)

    supply_df = metrics["supply_comparison"].execute()
    share_df = metrics["market_share"].execute()

    if len(supply_df) == 0:
        return "No stablecoin data available."

    lines = ["Stablecoin Metrics:", ""]
    for _, row in supply_df.iterrows():
        share = share_df[share_df["symbol"] == row["symbol"]]
        share_pct = share["market_share_pct"].iloc[0] if len(share) > 0 else 0

        lines.append(
            f"- {row['symbol']}: ${row['circulating']/1e9:.2f}B supply, "
            f"${row['price']:.4f} price, {share_pct:.1f}% market share"
        )

    return "\n".join(lines)


def run_pipeline(
    pipeline_type: str,
    config: Optional[dict] = None,
) -> str:
    """
    Trigger a data pipeline.

    Args:
        pipeline_type: Type of pipeline (coingecko, defillama, binance, firecrawl)
        config: Pipeline configuration

    Returns:
        Pipeline result
    """
    config = config or {}

    if pipeline_type == "coingecko":
        from pipelines.sources.coingecko import run_coingecko_pipeline

        result = run_coingecko_pipeline(**config)
    elif pipeline_type == "defillama":
        from pipelines.sources.defillama import run_defillama_pipeline

        result = run_defillama_pipeline(**config)
    elif pipeline_type == "binance":
        from pipelines.sources.binance import run_binance_pipeline

        result = run_binance_pipeline(**config)
    elif pipeline_type == "subgraphs":
        from pipelines.sources.subgraphs import run_subgraph_pipeline

        result = run_subgraph_pipeline(**config)
    else:
        return f"Unknown pipeline type: {pipeline_type}"

    return f"Pipeline {pipeline_type} completed: {result}"


# =============================================================================
# Research Agent
# =============================================================================


class CryptoResearchAgent(Agent):
    """
    Research agent for crypto documentation and knowledge graph queries.

    Capabilities:
    - Search protocol documentation
    - Query knowledge graph
    - Summarize protocol mechanics
    """

    def __init__(self, model: Optional[str] = None):
        model_instance = LiteLLM(
            id=get_model_id(model),
            api_base=LITELLM_BASE_URL,
        )

        super().__init__(
            name="CryptoResearcher",
            model=model_instance,
            description="Research agent for crypto protocol documentation and knowledge",
            instructions=[
                "You are a crypto research specialist with access to protocol documentation.",
                "Use the knowledge base tools to find accurate information.",
                "Always cite sources when providing information.",
                "Focus on explaining complex DeFi concepts clearly.",
            ],
            tools=[
                Tool(
                    name="search_knowledge_base",
                    function=search_knowledge_base,
                    description="Search crypto knowledge base for documentation",
                ),
                Tool(
                    name="get_protocol_context",
                    function=get_protocol_context,
                    description="Get full documentation context for a protocol",
                ),
                Tool(
                    name="query_knowledge_graph",
                    function=query_knowledge_graph,
                    description="Query Cognee knowledge graph for relationships",
                ),
            ],
            show_tool_calls=True,
            markdown=True,
        )


# =============================================================================
# Analysis Agent
# =============================================================================


class CryptoAnalysisAgent(Agent):
    """
    Analysis agent for crypto market data and metrics.

    Capabilities:
    - Funding rate analysis
    - Yield comparisons
    - Protocol health assessment
    - Stablecoin metrics
    """

    def __init__(self, model: Optional[str] = None):
        model_instance = LiteLLM(
            id=get_model_id(model),
            api_base=LITELLM_BASE_URL,
        )

        super().__init__(
            name="CryptoAnalyst",
            model=model_instance,
            description="Analysis agent for crypto market data and DeFi metrics",
            instructions=[
                "You are a DeFi analyst specializing in yield strategies.",
                "Provide data-driven insights using the analytics tools.",
                "Explain the implications of metrics for investment decisions.",
                "Always consider risk factors alongside returns.",
                "For Ethena specifically, focus on funding rate dynamics.",
            ],
            tools=[
                Tool(
                    name="get_funding_rate_analysis",
                    function=get_funding_rate_analysis,
                    description="Analyze funding rates for basis trade",
                ),
                Tool(
                    name="get_yield_comparison",
                    function=get_yield_comparison,
                    description="Compare yields across DeFi protocols",
                ),
                Tool(
                    name="get_stablecoin_metrics",
                    function=get_stablecoin_metrics,
                    description="Get stablecoin supply and peg metrics",
                ),
            ],
            show_tool_calls=True,
            markdown=True,
        )


# =============================================================================
# Pipeline Agent
# =============================================================================


class CryptoPipelineAgent(Agent):
    """
    Agent for managing data pipelines.

    Capabilities:
    - Trigger data ingestion
    - Monitor pipeline status
    - Refresh data sources
    """

    def __init__(self, model: Optional[str] = None):
        model_instance = LiteLLM(
            id=get_model_id(model),
            api_base=LITELLM_BASE_URL,
        )

        super().__init__(
            name="PipelineManager",
            model=model_instance,
            description="Agent for managing crypto data pipelines",
            instructions=[
                "You manage data pipelines for the crypto analytics platform.",
                "Only run pipelines when explicitly requested.",
                "Report pipeline status and any errors.",
            ],
            tools=[
                Tool(
                    name="run_pipeline",
                    function=run_pipeline,
                    description="Run a data pipeline (coingecko, defillama, binance, subgraphs)",
                ),
            ],
            show_tool_calls=True,
            markdown=True,
        )


# =============================================================================
# Agent Team
# =============================================================================


def create_crypto_agent_team(
    model: Optional[str] = None,
    include_pipeline_agent: bool = False,
) -> Team:
    """
    Create a crypto analytics agent team.

    The team coordinates:
    - Research agent for documentation queries
    - Analysis agent for data insights

    Args:
        model: LLM model to use
        include_pipeline_agent: Whether to include pipeline management

    Returns:
        Configured Agno Team
    """
    agents = [
        CryptoResearchAgent(model=model),
        CryptoAnalysisAgent(model=model),
    ]

    if include_pipeline_agent:
        agents.append(CryptoPipelineAgent(model=model))

    model_instance = LiteLLM(
        id=get_model_id(model),
        api_base=LITELLM_BASE_URL,
    )

    team = Team(
        name="CryptoAnalyticsTeam",
        model=model_instance,
        agents=agents,
        instructions=[
            "You coordinate crypto research and analysis.",
            "Route research questions to CryptoResearcher.",
            "Route data analysis requests to CryptoAnalyst.",
            "Synthesize information from multiple agents when needed.",
            "Focus on Ethena ecosystem but support other protocols.",
        ],
        show_tool_calls=True,
        markdown=True,
    )

    return team


# =============================================================================
# Convenience Functions
# =============================================================================


def chat_with_researcher(message: str) -> RunResponse:
    """Quick chat with research agent."""
    agent = CryptoResearchAgent()
    return agent.run(message)


def chat_with_analyst(message: str) -> RunResponse:
    """Quick chat with analysis agent."""
    agent = CryptoAnalysisAgent()
    return agent.run(message)


def chat_with_team(message: str) -> RunResponse:
    """Chat with the full crypto team."""
    team = create_crypto_agent_team()
    return team.run(message)


# =============================================================================
# CLI
# =============================================================================


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "What is Ethena and how does it generate yield?"

    print(f"Query: {query}\n")

    # Use the team for comprehensive response
    team = create_crypto_agent_team()
    response = team.run(query)

    print(response.content)
