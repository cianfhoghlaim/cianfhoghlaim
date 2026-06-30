"""Agent Registry Dagster assets — materialise the 2 new agent discovery
v1 Apps (`agent_registry` + `agents_md`).

Added in the `2026-06-30-agent-platform-cluster-hermes-cocoindex` change.
"""
from __future__ import annotations

import subprocess
from collections.abc import Iterator

import structlog
from dagster import AssetExecutionContext, asset

logger = structlog.get_logger(__name__)


@asset(
    group_name="agent_registry",
    compute_kind="embedding",
    description="Materialise the agent_registry v1 App (BAAI/bge-m3 1024-dim over opencode.json agents + mcp servers).",
)
def agent_registry_index(context: AssetExecutionContext) -> Iterator[str]:
    """Run `mise run cocoindex:update agent_registry`."""
    context.log.info("[agent_registry_index] starting")
    result = subprocess.run(
        ["mise", "run", "cocoindex:update-agent_registry"],
        capture_output=True,
        text=True,
        timeout=600,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"cocoindex:update-agent_registry failed: {result.stderr}"
        )
    context.log.info(f"[agent_registry_index] done: {result.stdout[:200]}")
    yield result.stdout


@asset(
    group_name="agent_registry",
    compute_kind="embedding",
    description="Materialise the agents_md v1 App (BAAI/bge-m3 1024-dim over the 6 AGENTS.md files).",
)
def agents_md_index(context: AssetExecutionContext) -> Iterator[str]:
    """Run `mise run cocoindex:update agents_md`."""
    context.log.info("[agents_md_index] starting")
    result = subprocess.run(
        ["mise", "run", "cocoindex:update-agents_md"],
        capture_output=True,
        text=True,
        timeout=600,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"cocoindex:update-agents_md failed: {result.stderr}"
        )
    context.log.info(f"[agents_md_index] done: {result.stdout[:200]}")
    yield result.stdout
