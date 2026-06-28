"""
agents_graph.py — Agents & MCP cluster graph model.

Cluster: docs-agents
Entities: McpServer, AgentTool, LlmAgent, BamlSchema, BrowserSession
"""

from __future__ import annotations

GRAPH_NODE_TYPES: tuple[str, ...] = (
    "McpServer",
    "AgentTool",
    "LlmAgent",
    "BamlSchema",
    "BrowserSession",
)

GRAPH_EDGE_TYPES: tuple[str, ...] = (
    "LlmAgent USES AgentTool",
    "McpServer EXPOSES AgentTool",
    "LlmAgent CALLS McpServer",
    "BamlSchema DEFINES AgentTool",
    "BrowserSession SESSIONED_BY LlmAgent",
)

CLUSTER_NAME = "docs-agents"
CLUSTER_DESCRIPTION = (
    "The 12-agent fleet + 10 MCP servers + BAML extraction schemas "
    "that drive every OpenCode sruth-subagent in the cianfhoghlaim "
    "monorepo."
)


def get_graph_model() -> dict[str, tuple[str, ...]]:
    return {"nodes": GRAPH_NODE_TYPES, "edges": GRAPH_EDGE_TYPES}
