#!/usr/bin/env python3
"""Ingest the 104 notebook files into Cognee cluster `notebooks`.

Per the 2026-08-15-notebooks-sync-loop-v1 change (Layer 3, Day 2).
Creates the 15th Cognee cluster (the 14 existing + notebooks).

Usage:
  uv run python scripts/cognee_ingest_notebooks.py
"""
from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

import cognee

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cognee_ingest_notebooks")


async def main_async() -> int:
    nb_dir = Path("notebooks")
    if not nb_dir.is_dir():
        logger.error(f"{nb_dir} not found")
        return 1

    # Get all numeric-prefix notebook files
    nb_files = sorted([f for f in nb_dir.glob("[0-9]*_*.py") if f.is_file()])
    total = len(nb_files)
    logger.info(f"Ingesting {total} notebook files -> dataset 'notebooks'")
    ingested = 0
    for i, nb_py in enumerate(nb_files, 1):
        try:
            content = nb_py.read_text()
            if len(content) < 50:
                continue
        except Exception as e:
            logger.warning(f"  SKIP {nb_py.name}: {e}")
            continue
        try:
            await cognee.add(content, dataset_name="notebooks")
            ingested += 1
        except Exception as e:
            logger.warning(f"  COGNIFY-FAIL {nb_py.name}: {e}")
            continue
        if i % 20 == 0 or i == total:
            logger.info(f"  progress: {i}/{total}")
    logger.info(f"Ingestion complete: {ingested}/{total} notebook files")
    return 0 if ingested > 0 else 1


def main() -> int:
    return asyncio.run(main_async())


if __name__ == "__main__":
    sys.exit(main())
