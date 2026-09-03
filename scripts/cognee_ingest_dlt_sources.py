#!/usr/bin/env python3
"""Ingest the 1903 DLT sources into Cognee cluster `dlt_sources`.

Per the 2026-08-15-dlt-sync-loop-v1 change (Layer 3, Day 2).
Creates the 13th Cognee cluster (the 12 existing + dlt_sources).

Usage:
  uv run python scripts/cognee_ingest_dlt_sources.py
"""
from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

import cognee

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cognee_ingest_dlt_sources")


async def main_async() -> int:
    dlt_dir = Path("dlt_sources")
    if not dlt_dir.is_dir():
        logger.error(f"{dlt_dir} not found")
        return 1

    # Get all DLT source files (Python only)
    dlt_files = sorted(dlt_dir.rglob("*.py"))
    total = len(dlt_files)
    logger.info(f"Ingesting {total} DLT source files -> dataset 'dlt_sources'")
    ingested = 0
    for i, dlt_py in enumerate(dlt_files, 1):
        try:
            content = dlt_py.read_text()
            if len(content) < 50:
                continue
        except Exception as e:
            logger.warning(f"  SKIP {dlt_py.name}: {e}")
            continue
        try:
            await cognee.add(content, dataset_name="dlt_sources")
            ingested += 1
        except Exception as e:
            logger.warning(f"  COGNIFY-FAIL {dlt_py.name}: {e}")
            continue
        if i % 100 == 0 or i == total:
            logger.info(f"  progress: {i}/{total}")
    logger.info(f"Ingestion complete: {ingested}/{total} DLT source files")
    return 0 if ingested > 0 else 1


def main() -> int:
    return asyncio.run(main_async())


if __name__ == "__main__":
    sys.exit(main())
