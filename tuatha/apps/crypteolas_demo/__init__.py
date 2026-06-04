"""
Crypteolas Demo — AI-powered DeFi analytics with x402 micropayments.

A standalone demo application that bundles:

- **Crypto agent team** (Agno-based) — research, analysis, and pipeline
  triggering for DeFi protocol questions.
- **MCP server** — exposes crypto analytics tools to Claude Code and
  other MCP-compatible clients.
- **Dagster code-location** — orchestrates the underlying pipelines
  (FIBO/EduVision image generation + Crypteolas crypto data).
- **FIBO/EduVision curriculum** — LanceDB-backed Python Gradio app
  for syllabus → asset generation.
- **TanStack Start frontend** (in ``src/``) — the Web3 / x402 demo
  dashboard, currently a buildable shell of stubs (see ``STATUS.md``).
- **Smart contracts** (in ``anam-contracts/``) — Foundry Solidity for
  the Anam Cara DAO, Cuchulainn NFT, and Tuath Token.

The agent and MCP symbols are imported lazily so that ``import
crypteolas_demo`` does not require the (heavy, optional) Agno +
CocoIndex + BAML runtime to be installed. Callers that actually want
the agents or the MCP server should import them directly::

    from crypteolas_demo.crypto_agents import CryptoResearchAgent
    from crypteolas_demo.mcp_tools import server, TOOLS
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .crypto_agents import (
        CryptoAnalysisAgent,
        CryptoPipelineAgent,
        CryptoResearchAgent,
        chat_with_analyst,
        chat_with_researcher,
        chat_with_team,
        create_crypto_agent_team,
    )
    from .mcp_tools import (
        TOOLS,
        create_mcp_server,
        run_server,
        server,
    )

__all__ = [
    # Agents (lazy)
    "CryptoResearchAgent",
    "CryptoAnalysisAgent",
    "CryptoPipelineAgent",
    "create_crypto_agent_team",
    "chat_with_researcher",
    "chat_with_analyst",
    "chat_with_team",
    # MCP (lazy)
    "server",
    "TOOLS",
    "create_mcp_server",
    "run_server",
]


def __getattr__(name: str):
    """Lazily import the agent and MCP symbols on first access."""
    if name in {
        "CryptoResearchAgent",
        "CryptoAnalysisAgent",
        "CryptoPipelineAgent",
        "create_crypto_agent_team",
        "chat_with_researcher",
        "chat_with_analyst",
        "chat_with_team",
    }:
        from . import crypto_agents

        return getattr(crypto_agents, name)
    if name in {"server", "TOOLS", "create_mcp_server", "run_server"}:
        from . import mcp_tools

        return getattr(mcp_tools, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
