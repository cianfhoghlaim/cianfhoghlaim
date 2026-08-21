"""
LiteLLM MCP Gateway for Aleyum.

Provides unified access to 25+ MCP servers configured in LiteLLM with
fallback chains for reliability and tool group routing.

The gateway proxies MCP calls through LiteLLM which manages the
underlying MCP server connections (stdio, HTTP, streamable-http).
"""

import asyncio
import httpx
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

from ..config.settings import get_settings

logger = logging.getLogger(__name__)


class MCPServerType(Enum):
    """Type of MCP server connection."""

    STDIO = "stdio"
    HTTP = "streamable-http"


@dataclass
class MCPServerInfo:
    """Information about an MCP server."""

    name: str
    type: MCPServerType
    description: str
    tools: List[str] = field(default_factory=list)
    category: str = "general"


# MCP Server catalog - organized by category
MCP_SERVERS: Dict[str, MCPServerInfo] = {
    # Browser automation
    "browserbase": MCPServerInfo(
        name="browserbase",
        type=MCPServerType.STDIO,
        description="Browser automation via Browserbase",
        tools=["navigate", "click", "fill", "screenshot", "extract"],
        category="browser",
    ),
    "chrome-devtools": MCPServerInfo(
        name="chrome-devtools",
        type=MCPServerType.STDIO,
        description="Chrome DevTools Protocol access",
        tools=["navigate", "evaluate", "screenshot", "network"],
        category="browser",
    ),
    "firecrawl-mcp": MCPServerInfo(
        name="firecrawl-mcp",
        type=MCPServerType.STDIO,
        description="Web scraping via Firecrawl API",
        tools=["scrape", "crawl", "map", "extract"],
        category="browser",
    ),
    # Knowledge/Vector
    "qdrant": MCPServerInfo(
        name="qdrant",
        type=MCPServerType.STDIO,
        description="Qdrant vector database",
        tools=["search", "upsert", "delete", "list_collections"],
        category="knowledge",
    ),
    "cognee-mcp": MCPServerInfo(
        name="cognee-mcp",
        type=MCPServerType.HTTP,
        description="Cognee knowledge graph",
        tools=["search", "add", "query"],
        category="knowledge",
    ),
    # Graph databases
    "memgraph": MCPServerInfo(
        name="memgraph",
        type=MCPServerType.STDIO,
        description="Memgraph graph database",
        tools=["query", "create_node", "create_edge"],
        category="graph",
    ),
    "neo4j": MCPServerInfo(
        name="neo4j",
        type=MCPServerType.STDIO,
        description="Neo4j/FalkorDB graph database",
        tools=["query", "create", "delete"],
        category="graph",
    ),
    # Data flows
    "dagster-mcp": MCPServerInfo(
        name="dagster-mcp",
        type=MCPServerType.STDIO,
        description="Dagster pipeline orchestration",
        tools=["list_jobs", "run_job", "get_job_status"],
        category="dataflows",
    ),
    "dlt-workspace": MCPServerInfo(
        name="dlt-workspace",
        type=MCPServerType.STDIO,
        description="DLT data pipelines",
        tools=["list_sources", "run_pipeline", "get_schema"],
        category="dataflows",
    ),
    # Code search
    "codeolas": MCPServerInfo(
        name="codeolas",
        type=MCPServerType.STDIO,
        description="Códeolas code analysis and search",
        tools=["search", "analyze", "get_relationships"],
        category="code",
    ),
    "chunkhound": MCPServerInfo(
        name="chunkhound",
        type=MCPServerType.STDIO,
        description="ChunkHound semantic code search",
        tools=["search", "index", "explore"],
        category="code",
    ),
    # Infrastructure
    "docker-mcp": MCPServerInfo(
        name="docker-mcp",
        type=MCPServerType.STDIO,
        description="Docker container management",
        tools=["list_containers", "logs", "exec"],
        category="infrastructure",
    ),
    "postgres": MCPServerInfo(
        name="postgres",
        type=MCPServerType.STDIO,
        description="PostgreSQL database",
        tools=["query", "describe"],
        category="infrastructure",
    ),
    # Observability
    "beads": MCPServerInfo(
        name="beads",
        type=MCPServerType.STDIO,
        description="Beads context management",
        tools=["list", "add", "get", "sync"],
        category="observability",
    ),
}

# Tool fallback chains - try tools in order
TOOL_FALLBACK_CHAINS: Dict[str, List[str]] = {
    "browser": ["browserbase", "chrome-devtools", "firecrawl-mcp"],
    "search": ["firecrawl-mcp", "codeolas", "qdrant", "chunkhound"],
    "graph": ["memgraph", "neo4j", "cognee-mcp"],
    "code": ["codeolas", "chunkhound"],
    "knowledge": ["cognee-mcp", "qdrant"],
}


@dataclass
class MCPToolCall:
    """Represents an MCP tool call request."""

    server: str
    tool: str
    arguments: Dict[str, Any] = field(default_factory=dict)
    timeout: float = 30.0


@dataclass
class MCPToolResult:
    """Result from an MCP tool call."""

    success: bool
    data: Any = None
    error: Optional[str] = None
    server: str = ""
    tool: str = ""


class MCPGateway:
    """
    Unified MCP gateway routing through LiteLLM.

    Provides:
    - Single entry point for all MCP tool calls
    - Automatic fallback chains for reliability
    - Tool group routing based on task type
    - Cost tracking integration (via Pydantic AI Gateway patterns)

    Usage:
        gateway = MCPGateway()
        result = await gateway.call_tool("codeolas", "search", {"query": "async function"})
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """
        Initialize the MCP gateway.

        Args:
            base_url: LiteLLM base URL (defaults to settings)
            api_key: LiteLLM API key (defaults to settings)
        """
        settings = get_settings()
        self.base_url = base_url or settings.litellm_base_url
        self.api_key = api_key or settings.litellm_api_key
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=headers,
                timeout=60.0,
            )
        return self._client

    async def call_tool(
        self,
        server: str,
        tool: str,
        arguments: Optional[Dict[str, Any]] = None,
        timeout: float = 30.0,
    ) -> MCPToolResult:
        """
        Call an MCP tool on a specific server.

        Args:
            server: MCP server name (e.g., "codeolas", "browserbase")
            tool: Tool name to call
            arguments: Tool arguments
            timeout: Request timeout

        Returns:
            MCPToolResult with success status and data/error
        """
        arguments = arguments or {}

        if server not in MCP_SERVERS:
            return MCPToolResult(
                success=False,
                error=f"Unknown MCP server: {server}",
                server=server,
                tool=tool,
            )

        try:
            client = await self._get_client()

            # MCP JSON-RPC 2.0 request format
            request_body = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": tool,
                    "arguments": arguments,
                },
            }

            response = await client.post(
                f"/mcp/{server}",
                json=request_body,
                timeout=timeout,
            )

            if response.status_code != 200:
                return MCPToolResult(
                    success=False,
                    error=f"HTTP {response.status_code}: {response.text}",
                    server=server,
                    tool=tool,
                )

            result = response.json()

            if "error" in result:
                return MCPToolResult(
                    success=False,
                    error=result["error"].get("message", str(result["error"])),
                    server=server,
                    tool=tool,
                )

            return MCPToolResult(
                success=True,
                data=result.get("result"),
                server=server,
                tool=tool,
            )

        except httpx.TimeoutException:
            return MCPToolResult(
                success=False,
                error=f"Timeout after {timeout}s",
                server=server,
                tool=tool,
            )
        except Exception as e:
            logger.exception(f"MCP call failed: {server}/{tool}")
            return MCPToolResult(
                success=False,
                error=str(e),
                server=server,
                tool=tool,
            )

    async def call_tool_with_fallback(
        self,
        category: str,
        tool: str,
        arguments: Optional[Dict[str, Any]] = None,
        timeout: float = 30.0,
    ) -> MCPToolResult:
        """
        Call a tool with automatic fallback through the chain.

        Args:
            category: Tool category (e.g., "browser", "search", "graph")
            tool: Tool name
            arguments: Tool arguments
            timeout: Request timeout per attempt

        Returns:
            MCPToolResult from first successful server
        """
        if category not in TOOL_FALLBACK_CHAINS:
            return MCPToolResult(
                success=False,
                error=f"Unknown category: {category}. Available: {list(TOOL_FALLBACK_CHAINS.keys())}",
            )

        chain = TOOL_FALLBACK_CHAINS[category]
        last_error = None

        for server in chain:
            result = await self.call_tool(server, tool, arguments, timeout)
            if result.success:
                logger.info(f"Tool {tool} succeeded on {server}")
                return result
            last_error = result.error
            logger.warning(f"Tool {tool} failed on {server}: {last_error}")

        return MCPToolResult(
            success=False,
            error=f"All servers in {category} chain failed. Last error: {last_error}",
            tool=tool,
        )

    async def list_servers(self) -> List[MCPServerInfo]:
        """List all available MCP servers."""
        return list(MCP_SERVERS.values())

    async def list_tools(self, server: str) -> List[str]:
        """List tools available on a server."""
        if server not in MCP_SERVERS:
            return []
        return MCP_SERVERS[server].tools

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None


# Convenience function for one-off calls
async def call_mcp_tool(
    server: str,
    tool: str,
    arguments: Optional[Dict[str, Any]] = None,
) -> MCPToolResult:
    """
    Quick helper to call an MCP tool.

    Usage:
        result = await call_mcp_tool("codeolas", "search", {"query": "async"})
    """
    gateway = MCPGateway()
    try:
        return await gateway.call_tool(server, tool, arguments)
    finally:
        await gateway.close()
