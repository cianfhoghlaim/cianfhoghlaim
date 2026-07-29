#!/usr/bin/env python3
"""Ingest openspec changes + specs into Cognee.

Per the 2026-08-15-knowledge-sync-loop-v1 change (Layer 3).
Creates 2 new Cognee clusters:
  - openspec_changes (the 14 pending + 303 archived changes)
  - openspec_specs (the 71 capability specs)

Usage:
  uv run python scripts/cognee_ingest_openspec.py
"""
from __future__ import annotations

import asyncio
import hashlib
import logging
import sys
from pathlib import Path

import cognee

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cognee_ingest_openspec")


def file_id(filepath: Path, root: Path) -> str:
    rel = str(filepath.relative_to(root))
    return hashlib.md5(rel.encode()).hexdigest()[:12]


async def ingest_directory(directory: Path, dataset_name: str) -> int:
    if not directory.is_dir():
        logger.error(f"{directory} is not a directory")
        return 0
    files = sorted(directory.rglob("*.md"))
    total = len(files)
    logger.info(f"Ingesting {total} files from {directory} -> dataset '{dataset_name}'")
    ingested = 0
    for i, filepath in enumerate(files, 1):
        try:
            content = filepath.read_text()
            if len(content) < 10:
                continue
        except Exception as e:
            logger.warning(f"  SKIP {filepath.name}: {e}")
            continue
        try:
            await cognee.add(content, dataset_name=dataset_name)
            ingested += 1
        except Exception as e:
            logger.warning(f"  COGNIFY-FAIL {filepath.name}: {e}")
            continue
        if i % 50 == 0 or i == total:
            logger.info(f"  progress: {i}/{total}")
    return ingested


async def main_async() -> int:
    # 1. Ingest openspec changes (exclude archive/ to keep the dataset small;
    # the 14 pending + the most recent 30 archived = ~44 files; ~500KB)
    changes_pending = Path("openspec/changes")
    changes_archive = Path("openspec/changes/archive")
    ingested_changes = await ingest_directory(changes_pending, "openspec_changes")
    if changes_archive.exists():
        # Only ingest the most recent 30 archived changes (keep dataset
        # size manageable; the rest can be ingested on-demand)
        recent_archived = sorted(
            changes_archive.iterdir(),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )[:30]
        for archived in recent_archived:
            if archived.is_dir():
                await ingest_directory(archived, "openspec_changes")

    # 2. Ingest openspec specs (71 .md files; small dataset)
    specs_dir = Path("openspec/specs")
    ingested_specs = await ingest_directory(specs_dir, "openspec_specs")

    logger.info(
        f"Ingestion complete: {ingested_changes} changes + {ingested_specs} specs"
    )
    return 0 if ingested_changes > 0 or ingested_specs > 0 else 1


def main() -> int:
    return asyncio.run(main_async())


if __name__ == "__main__":
    sys.exit(main())