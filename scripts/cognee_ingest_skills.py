#!/usr/bin/env python3
"""Ingest the 57 agent skills into Cognee.

Per the 2026-08-15-knowledge-sync-loop-v1 change (Layer 3).
Creates 1 new Cognee cluster:
  - agent_skills (the 57 skills' SKILL.md files + their frontmatter)

Usage:
  uv run python scripts/cognee_ingest_skills.py
"""
from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

import cognee

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cognee_ingest_skills")


async def main_async() -> int:
    skills_dir = Path(".agents/skills")
    if not skills_dir.is_dir():
        logger.error(f"{skills_dir} not found")
        return 1

    skill_files = sorted(skills_dir.rglob("SKILL.md"))
    total = len(skill_files)
    logger.info(f"Ingesting {total} skill files -> dataset 'agent_skills'")
    ingested = 0
    for i, skill_md in enumerate(skill_files, 1):
        try:
            content = skill_md.read_text()
            if len(content) < 10:
                continue
        except Exception as e:
            logger.warning(f"  SKIP {skill_md.name}: {e}")
            continue
        try:
            await cognee.add(content, dataset_name="agent_skills")
            ingested += 1
        except Exception as e:
            logger.warning(f"  COGNIFY-FAIL {skill_md.name}: {e}")
            continue
        if i % 20 == 0 or i == total:
            logger.info(f"  progress: {i}/{total}")
    logger.info(f"Ingestion complete: {ingested}/{total} skills")
    return 0 if ingested > 0 else 1


def main() -> int:
    return asyncio.run(main_async())


if __name__ == "__main__":
    sys.exit(main())