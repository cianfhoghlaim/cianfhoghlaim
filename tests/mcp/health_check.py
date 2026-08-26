"""
MCP Server Health Check Tests.

Tests that all configured MCP servers are reachable and responding.
Validates tool listings and basic functionality for each server.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

logger = logging.getLogger(__name__)

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server."""

    name: str
    command: str
    args: list[str]
    env: dict[str, str] | None = None
    required_tools: list[str] | None = None
    health_tool: str | None = None
    startup_timeout: int = 30


# MCP Server configurations from .mcp.json
MCP_SERVERS: list[MCPServerConfig] = [
    MCPServerConfig(
        name="chunkhound",
        command="uv",
        args=["--directory", str(PROJECT_ROOT), "run", "chunkhound"],
        required_tools=["search_semantic", "code_research", "get_file_chunks"],
    ),
    MCPServerConfig(
        name="firecrawl-mcp",
        command="npx",
        args=["-y", "firecrawl-mcp"],
        env={"FIRECRAWL_API_KEY": os.environ.get("FIRECRAWL_API_KEY", "")},
        required_tools=["firecrawl_scrape", "firecrawl_search", "firecrawl_map"],
    ),
    MCPServerConfig(
        name="browserbase",
        command="npx",
        args=["-y", "@anthropic-ai/browserbase-mcp"],
        env={
            "BROWSERBASE_API_KEY": os.environ.get("BROWSERBASE_API_KEY", ""),
            "BROWSERBASE_PROJECT_ID": os.environ.get("BROWSERBASE_PROJECT_ID", ""),
        },
        required_tools=["browserbase_session_create", "browserbase_stagehand_navigate"],
    ),
    MCPServerConfig(
        name="zai-mcp-server",
        command="uvx",
        args=["zai-mcp-server"],
        required_tools=["ui_to_artifact", "extract_text_from_screenshot"],
    ),
    MCPServerConfig(
        name="qdrant",
        command="uvx",
        args=[
            "qdrant-mcp",
            "--host", os.environ.get("QDRANT_HOST", "localhost"),
            "--port", os.environ.get("QDRANT_PORT", "6333"),
        ],
        required_tools=["search", "upsert"],
    ),
    MCPServerConfig(
        name="memgraph",
        command="uvx",
        args=[
            "memgraph-mcp",
            "--bolt-url", os.environ.get("MEMGRAPH_BOLT_URL", "bolt://localhost:7687"),
        ],
        required_tools=["cypher_query"],
    ),
    MCPServerConfig(
        name="duckdb-mcp",
        command="uvx",
        args=[
            "duckdb-mcp",
            "--db", str(PROJECT_ROOT / "tests" / "fixtures" / "test.duckdb"),
        ],
        required_tools=["query", "schema"],
    ),
    MCPServerConfig(
        name="dagster-mcp",
        command="uvx",
        args=["dagster-mcp"],
        env={"DAGSTER_HOME": str(PROJECT_ROOT / "sruth")},
        required_tools=["materialize_asset", "get_job_status"],
    ),
    MCPServerConfig(
        name="langfuse-mcp",
        command="uvx",
        args=["langfuse-mcp"],
        env={
            "LANGFUSE_PUBLIC_KEY": os.environ.get("LANGFUSE_PUBLIC_KEY", ""),
            "LANGFUSE_SECRET_KEY": os.environ.get("LANGFUSE_SECRET_KEY", ""),
        },
        required_tools=["trace", "score"],
    ),
    MCPServerConfig(
        name="cognee-mcp",
        command="uvx",
        args=["cognee-mcp"],
        required_tools=["add", "search", "cognify"],
    ),
    MCPServerConfig(
        name="beads",
        command="uv",
        args=["--directory", str(PROJECT_ROOT), "run", "beads", "mcp"],
        required_tools=["create_issue", "list_issues"],
    ),
    MCPServerConfig(
        name="letta",
        command="uvx",
        args=["letta-mcp"],
        env={"LETTA_API_KEY": os.environ.get("LETTA_API_KEY", "")},
        required_tools=["send_message", "list_agents"],
    ),
]


class MCPHealthChecker:
    """Health checker for MCP servers using stdio transport."""

    def __init__(self, config: MCPServerConfig):
        self.config = config
        self.process: subprocess.Popen | None = None
        self._request_id = 0

    async def start(self) -> bool:
        """Start the MCP server process."""
        try:
            env = os.environ.copy()
            if self.config.env:
                env.update(self.config.env)

            self.process = subprocess.Popen(
                [self.config.command, *self.config.args],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
            )

            # Wait for server to be ready (simple timeout-based check)
            await asyncio.sleep(2)

            if self.process.poll() is not None:
                stderr = self.process.stderr.read().decode() if self.process.stderr else ""
                logger.error(f"Server {self.config.name} failed to start: {stderr}")
                return False

            return True

        except FileNotFoundError as e:
            logger.error(f"Command not found for {self.config.name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to start {self.config.name}: {e}")
            return False

    async def stop(self):
        """Stop the MCP server process."""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None

    def _send_request(self, method: str, params: dict | None = None) -> dict | None:
        """Send a JSON-RPC request to the MCP server."""
        if not self.process or not self.process.stdin or not self.process.stdout:
            return None

        self._request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": method,
        }
        if params:
            request["params"] = params

        try:
            # Write request
            request_bytes = json.dumps(request).encode() + b"\n"
            self.process.stdin.write(request_bytes)
            self.process.stdin.flush()

            # Read response (with timeout via select or just readline)
            response_line = self.process.stdout.readline()
            if response_line:
                return json.loads(response_line.decode())
            return None

        except Exception as e:
            logger.error(f"Request failed for {self.config.name}: {e}")
            return None

    async def check_health(self) -> dict[str, Any]:
        """Perform health check on the MCP server."""
        result = {
            "name": self.config.name,
            "healthy": False,
            "started": False,
            "tools_available": [],
            "required_tools_present": False,
            "errors": [],
        }

        # Start server
        if not await self.start():
            result["errors"].append("Failed to start server")
            return result

        result["started"] = True

        # Initialize
        init_response = self._send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "health-check", "version": "1.0.0"},
        })

        if not init_response or "error" in init_response:
            result["errors"].append(f"Initialize failed: {init_response}")
            await self.stop()
            return result

        # List tools
        tools_response = self._send_request("tools/list")

        if tools_response and "result" in tools_response:
            tools = tools_response["result"].get("tools", [])
            result["tools_available"] = [t.get("name") for t in tools]

            # Check required tools
            if self.config.required_tools:
                missing = set(self.config.required_tools) - set(result["tools_available"])
                if not missing:
                    result["required_tools_present"] = True
                else:
                    result["errors"].append(f"Missing required tools: {missing}")
        else:
            result["errors"].append(f"Failed to list tools: {tools_response}")

        # Health check tool if specified
        if self.config.health_tool and self.config.health_tool in result["tools_available"]:
            health_response = self._send_request("tools/call", {
                "name": self.config.health_tool,
                "arguments": {},
            })
            if health_response and "error" not in health_response:
                result["healthy"] = True
        elif result["required_tools_present"]:
            # If no specific health tool, consider healthy if required tools present
            result["healthy"] = True

        await self.stop()
        return result


@pytest.fixture
def mcp_checker():
    """Provide MCP health checker factory."""
    checkers = []

    def factory(config: MCPServerConfig) -> MCPHealthChecker:
        checker = MCPHealthChecker(config)
        checkers.append(checker)
        return checker

    yield factory

    # Cleanup
    for checker in checkers:
        asyncio.get_event_loop().run_until_complete(checker.stop())


class TestMCPServerHealth:
    """Test suite for MCP server health checks."""

    @pytest.mark.mcp
    @pytest.mark.asyncio
    async def test_chunkhound_health(self, mcp_checker):
        """Test ChunkHound MCP server health."""
        config = next(c for c in MCP_SERVERS if c.name == "chunkhound")
        checker = mcp_checker(config)
        result = await checker.check_health()

        assert result["started"], f"ChunkHound failed to start: {result['errors']}"
        assert "search_semantic" in result["tools_available"]

    @pytest.mark.mcp
    @pytest.mark.asyncio
    async def test_firecrawl_health(self, mcp_checker):
        """Test Firecrawl MCP server health."""
        if not os.environ.get("FIRECRAWL_API_KEY"):
            pytest.skip("FIRECRAWL_API_KEY not set")

        config = next(c for c in MCP_SERVERS if c.name == "firecrawl-mcp")
        checker = mcp_checker(config)
        result = await checker.check_health()

        assert result["started"], f"Firecrawl failed to start: {result['errors']}"

    @pytest.mark.mcp
    @pytest.mark.asyncio
    async def test_browserbase_health(self, mcp_checker):
        """Test Browserbase MCP server health."""
        if not os.environ.get("BROWSERBASE_API_KEY"):
            pytest.skip("BROWSERBASE_API_KEY not set")

        config = next(c for c in MCP_SERVERS if c.name == "browserbase")
        checker = mcp_checker(config)
        result = await checker.check_health()

        assert result["started"], f"Browserbase failed to start: {result['errors']}"

    @pytest.mark.mcp
    @pytest.mark.asyncio
    async def test_zai_health(self, mcp_checker):
        """Test Z.AI MCP server health."""
        config = next(c for c in MCP_SERVERS if c.name == "zai-mcp-server")
        checker = mcp_checker(config)
        result = await checker.check_health()

        assert result["started"], f"Z.AI failed to start: {result['errors']}"

    @pytest.mark.mcp
    @pytest.mark.asyncio
    async def test_duckdb_health(self, mcp_checker):
        """Test DuckDB MCP server health."""
        config = next(c for c in MCP_SERVERS if c.name == "duckdb-mcp")
        checker = mcp_checker(config)
        result = await checker.check_health()

        assert result["started"], f"DuckDB MCP failed to start: {result['errors']}"

    @pytest.mark.mcp
    @pytest.mark.asyncio
    async def test_beads_health(self, mcp_checker):
        """Test Beads MCP server health."""
        config = next(c for c in MCP_SERVERS if c.name == "beads")
        checker = mcp_checker(config)
        result = await checker.check_health()

        assert result["started"], f"Beads failed to start: {result['errors']}"


async def run_all_health_checks() -> dict[str, Any]:
    """Run health checks on all MCP servers."""
    results = {}

    for config in MCP_SERVERS:
        logger.info(f"Checking {config.name}...")
        checker = MCPHealthChecker(config)
        results[config.name] = await checker.check_health()

    return results


def print_health_report(results: dict[str, Any]):
    """Print a formatted health report."""
    print("\n" + "=" * 60)
    print("MCP Server Health Report")
    print("=" * 60)

    healthy_count = 0
    total_count = len(results)

    for name, result in results.items():
        status = "✅" if result["healthy"] else "❌"
        print(f"\n{status} {name}")

        if result["healthy"]:
            healthy_count += 1
            print(f"   Tools: {len(result['tools_available'])} available")
        else:
            for error in result["errors"]:
                print(f"   ❌ {error}")

    print("\n" + "-" * 60)
    print(f"Summary: {healthy_count}/{total_count} servers healthy")
    print("=" * 60)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    results = asyncio.run(run_all_health_checks())
    print_health_report(results)
