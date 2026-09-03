#!/usr/bin/env python3
"""Ingest the 320 .baml files into Cognee cluster `baml_schemas`.

Per the 2026-08-15-baml-sync-loop-v1 change (Layer 3, Day 2).
Creates the 11th Cognee cluster (the 10 existing docs/ clusters + the
openspec_changes + openspec_specs + agent_skills clusters from
knowledge-sync-loop-v1 + the new baml_schemas cluster).

Usage:
  uv run python scripts/cognee_ingest_baml_schemas.py
"""
from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

import cognee

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cognee_ingest_baml_schemas")


async def main_async() -> int:
    baml_dir = Path("baml_src")
    if not baml_dir.is_dir():
        logger.error(f"{baml_dir} not found")
        return 1

    baml_files = sorted(baml_dir.rglob("*.baml"))
    total = len(baml_files)
    logger.info(f"Ingesting {total} .baml files -> dataset 'baml_schemas'")
    ingested = 0
    for i, baml_md in enumerate(baml_files, 1):
        try:
            content = baml_md.read_text()
            if len(content) < 10:
                continue
        except Exception as e:
            logger.warning(f"  SKIP {baml_md.name}: {e}")
            continue
        try:
            await cognee.add(content, dataset_name="baml_schemas")
            ingested += 1
        except Exception as e:
            logger.warning(f"  COGNIFY-FAIL {baml_md.name}: {e}")
            continue
        if i % 50 == 0 or i == total:
            logger.info(f"  progress: {i}/{total}")
    logger.info(f"Ingestion complete: {ingested}/{total} .baml files")
    return 0 if ingested > 0 else 1


def main() -> int:
    return asyncio.run(main_async())


if __name__ == "__main__":
    sys.exit(main())