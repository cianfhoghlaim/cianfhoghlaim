"""
MCP (Model Context Protocol) server for crypto analytics tools.

Exposes crypto analytics capabilities to LLM clients
(Claude Desktop, other MCP-compatible tools).

Run with: python -m agents.mcp_tools
"""

import json
from typing import Any, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    CallToolResult,
)


# =============================================================================
# MCP Server Setup
# =============================================================================


server = Server("crypto-analytics")


# =============================================================================
# Tool Definitions
# =============================================================================


TOOLS = [
    Tool(
        name="search_knowledge",
        description="Search the crypto knowledge base for protocol documentation",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query",
                },
                "protocol": {
                    "type": "string",
                    "description": "Optional protocol filter (ethena, aave, pendle, etc.)",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results (default 5)",
                    "default": 5,
                },
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="get_funding_rates",
        description="Get funding rate analysis for perpetual contracts",
        inputSchema={
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Trading pair (e.g., ETHUSDT)",
                    "default": "ETHUSDT",
                },
                "days": {
                    "type": "integer",
                    "description": "Lookback period in days",
                    "default": 30,
                },
            },
        },
    ),
    Tool(
        name="compare_yields",
        description="Compare yields across DeFi protocols",
        inputSchema={
            "type": "object",
            "properties": {
                "protocols": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Protocols to compare (default: ethena, aave, pendle, lido)",
                },
            },
        },
    ),
    Tool(
        name="get_stablecoin_metrics",
        description="Get stablecoin supply and peg metrics",
        inputSchema={
            "type": "object",
            "properties": {
                "symbols": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Stablecoins to analyze (default: USDe, USDC, USDT, DAI)",
                },
            },
        },
    ),
    Tool(
        name="query_graph",
        description="Query the crypto knowledge graph for relationships",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Query string",
                },
                "search_type": {
                    "type": "string",
                    "enum": ["insights", "chunks", "graph"],
                    "description": "Type of search",
                    "default": "insights",
                },
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="run_pipeline",
        description="Run a data ingestion pipeline",
        inputSchema={
            "type": "object",
            "properties": {
                "pipeline": {
                    "type": "string",
                    "enum": ["coingecko", "defillama", "binance", "subgraphs", "firecrawl"],
                    "description": "Pipeline to run",
                },
                "config": {
                    "type": "object",
                    "description": "Optional pipeline configuration",
                },
            },
            "required": ["pipeline"],
        },
    ),
    Tool(
        name="get_protocol_summary",
        description="Get a summary of a crypto protocol from the knowledge base",
        inputSchema={
            "type": "object",
            "properties": {
                "protocol": {
                    "type": "string",
                    "description": "Protocol name (ethena, aave, pendle, lido, etc.)",
                },
            },
            "required": ["protocol"],
        },
    ),
]


# =============================================================================
# Tool Implementations
# =============================================================================


def knowledge_search_tool(
    query: str,
    protocol: Optional[str] = None,
    limit: int = 5,
) -> str:
    """Search knowledge base."""
    from pipelines.indexers.cocoindex_flow import query_crypto_knowledge

    results = query_crypto_knowledge(
        query=query,
        protocol_filter=protocol,
        limit=limit,
    )

    if not results:
        return "No relevant documents found."

    formatted = []
    for i, r in enumerate(results, 1):
        formatted.append(
            f"{i}. [{r.get('protocol', 'unknown')}] {r.get('content', '')[:400]}..."
        )

    return "\n\n".join(formatted)


def analytics_tool(tool_name: str, **kwargs) -> str:
    """Run analytics tools."""
    from pipelines.transformations.crypto_analytics import (
        calculate_funding_metrics,
        build_yield_comparison_view,
        calculate_stablecoin_metrics,
        get_connection,
    )

    con = get_connection()

    if tool_name == "funding_rates":
        symbol = kwargs.get("symbol", "ETHUSDT")
        days = kwargs.get("days", 30)

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

{"Favorable for basis trade" if m['positive_rate_pct'] > 70 else "Mixed conditions"}.
"""

    elif tool_name == "yields":
        protocols = kwargs.get("protocols", ["ethena", "aave-v3", "pendle", "lido"])

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

    elif tool_name == "stablecoins":
        metrics = calculate_stablecoin_metrics(con)
        supply_df = metrics["supply_comparison"].execute()

        if len(supply_df) == 0:
            return "No stablecoin data available."

        lines = ["Stablecoin Metrics:", ""]
        for _, row in supply_df.iterrows():
            lines.append(
                f"- {row['symbol']}: ${row['circulating']/1e9:.2f}B supply, "
                f"${row['price']:.4f} price"
            )
        return "\n".join(lines)

    else:
        return f"Unknown analytics tool: {tool_name}"


def pipeline_tool(pipeline: str, config: Optional[dict] = None) -> str:
    """Run data pipeline."""
    config = config or {}

    try:
        if pipeline == "coingecko":
            from pipelines.sources.coingecko import run_coingecko_pipeline

            result = run_coingecko_pipeline(**config)
        elif pipeline == "defillama":
            from pipelines.sources.defillama import run_defillama_pipeline

            result = run_defillama_pipeline(**config)
        elif pipeline == "binance":
            from pipelines.sources.binance import run_binance_pipeline

            result = run_binance_pipeline(**config)
        elif pipeline == "subgraphs":
            from pipelines.sources.subgraphs import run_subgraph_pipeline

            result = run_subgraph_pipeline(**config)
        elif pipeline == "firecrawl":
            from pipelines.scrapers.firecrawl_source import run_firecrawl_pipeline

            result = run_firecrawl_pipeline(**config)
        else:
            return f"Unknown pipeline: {pipeline}"

        return f"Pipeline {pipeline} completed successfully: {result}"

    except Exception as e:
        return f"Pipeline {pipeline} failed: {e}"


def graph_query_tool(query: str, search_type: str = "insights") -> str:
    """Query knowledge graph."""
    from pipelines.knowledge.cognee_pipeline import sync_query

    results = sync_query(query, search_type)

    if not results:
        return "No knowledge graph results found."

    return "\n".join([str(r) for r in results[:5]])


def protocol_summary_tool(protocol: str) -> str:
    """Get protocol summary."""
    from pipelines.indexers.cocoindex_flow import get_protocol_context

    context = get_protocol_context(protocol, limit=20)

    if not context:
        return f"No documentation found for {protocol}."

    return f"# {protocol.upper()} Protocol Summary\n\n{context[:2000]}..."


# =============================================================================
# MCP Handlers
# =============================================================================


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> CallToolResult:
    """Handle tool calls."""
    try:
        if name == "search_knowledge":
            result = knowledge_search_tool(
                query=arguments["query"],
                protocol=arguments.get("protocol"),
                limit=arguments.get("limit", 5),
            )

        elif name == "get_funding_rates":
            result = analytics_tool(
                "funding_rates",
                symbol=arguments.get("symbol", "ETHUSDT"),
                days=arguments.get("days", 30),
            )

        elif name == "compare_yields":
            result = analytics_tool(
                "yields",
                protocols=arguments.get("protocols"),
            )

        elif name == "get_stablecoin_metrics":
            result = analytics_tool("stablecoins")

        elif name == "query_graph":
            result = graph_query_tool(
                query=arguments["query"],
                search_type=arguments.get("search_type", "insights"),
            )

        elif name == "run_pipeline":
            result = pipeline_tool(
                pipeline=arguments["pipeline"],
                config=arguments.get("config"),
            )

        elif name == "get_protocol_summary":
            result = protocol_summary_tool(protocol=arguments["protocol"])

        else:
            result = f"Unknown tool: {name}"

        return CallToolResult(
            content=[TextContent(type="text", text=result)],
            isError=False,
        )

    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: {e}")],
            isError=True,
        )


# =============================================================================
# Server Factory
# =============================================================================


def create_mcp_server() -> Server:
    """Create and return the MCP server instance."""
    return server


async def run_server():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


# =============================================================================
# Entry Point
# =============================================================================


if __name__ == "__main__":
    import asyncio

    asyncio.run(run_server())
