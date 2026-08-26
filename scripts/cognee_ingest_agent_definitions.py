#!/usr/bin/env python3
"""Ingest the 188 agent files into Cognee cluster `agent_definitions`.

Per the 2026-08-15-agent-definitions-sync-loop-v1 change (Layer 3, Day 2).
Creates the 14th Cognee cluster (the 13 existing + agent_definitions).

Usage:
  uv run python scripts/cognee_ingest_agent_definitions.py
"""
from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

import cognee

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cognee_ingest_agent_definitions")


async def main_async() -> int:
    agents_dir = Path("agents")
    if not agents_dir.is_dir():
        logger.error(f"{agents_dir} not found")
        return 1

    agent_files = sorted(agents_dir.rglob("*.py"))
    total = len(agent_files)
    # Per the 2026-08-24-dlt-sources-to-multi-repo-scaffold-v1 change Phase 0.8:
    # the canonical cluster name is `agents` (per the v2 plan §C.8). We also
    # write to the legacy `agent_definitions` cluster for backward compat
    # with the 2026-08-15-agent-definitions-sync-loop-v1 sync chain.
    datasets = ("agents", "agent_definitions")
    logger.info(
        f"Ingesting {total} agent files -> datasets {list(datasets)}"
    )
    ingested = 0
    for i, agent_py in enumerate(agent_files, 1):
        try:
            content = agent_py.read_text()
            if len(content) < 50:
                continue
        except Exception as e:
            logger.warning(f"  SKIP {agent_py.name}: {e}")
            continue
        try:
            for ds in datasets:
                await cognee.add(content, dataset_name=ds)
            ingested += 1
        except Exception as e:
            logger.warning(f"  COGNIFY-FAIL {agent_py.name}: {e}")
            continue
        if i % 50 == 0 or i == total:
            logger.info(f"  progress: {i}/{total}")
    logger.info(f"Ingestion complete: {ingested}/{total} agent files")
    return 0 if ingested > 0 else 1


def main() -> int:
    return asyncio.run(main_async())


if __name__ == "__main__":
    sys.exit(main())
