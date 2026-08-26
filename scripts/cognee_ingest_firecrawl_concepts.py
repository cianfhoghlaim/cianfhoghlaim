#!/usr/bin/env python3
"""Ingest the .cocoindex_code/guides.yml concept guides into the 8th Cognee cluster `firecrawl_concepts`.

Per the 2026-08-24-dlt-sources-to-multi-repo-scaffold-v1 change Phase 0.8.
Per the 2026-08-14-firecrawl-mcp-ccc-dual-search-v1 change (Layer 12).

The .cocoindex_code/guides.yml file holds the canonical concept guides
that back the ccc (CocoIndex Code) semantic search. Each guide maps a
high-level concept to the canonical files that describe it.

For each guide (the YAML's `- title:` entries), this script assembles a
per-guide markdown entry + adds it to Cognee.

Usage:
  uv run python scripts/cognee_ingest_firecrawl_concepts.py
"""
from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

import cognee

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cognee_ingest_firecrawl_concepts")


GUIDES_PATH = Path(".cocoindex_code/guides.yml")


def _build_guide_entry(guide_title: str, raw_block: str) -> str:
    """Build a markdown catalog entry for one concept guide.

    The raw_block is the YAML excerpt starting from `- title:` to the
    next `- title:` or EOF.
    """
    parts: list[str] = [
        f"# Concept Guide: {guide_title}",
        "",
        "Source: .cocoindex_code/guides.yml",
        "",
        "```yaml",
        raw_block.rstrip(),
        "```",
        "",
    ]
    return "\n".join(parts)


def _parse_guides(path: Path) -> list[tuple[str, str]]:
    """Parse guides.yml into a list of (title, raw_block) tuples."""
    if not path.is_file():
        logger.error(f"{path} not found")
        return []
    text = path.read_text()
    guides: list[tuple[str, str]] = []
    current_title: str | None = None
    current_lines: list[str] = []
    for line in text.splitlines():
        if line.startswith("- title:"):
            if current_title is not None:
                guides.append((current_title, "\n".join(current_lines)))
            current_title = line.split(":", 1)[1].strip().strip('"').strip("'")
            current_lines = [line]
        elif current_title is not None:
            current_lines.append(line)
    if current_title is not None:
        guides.append((current_title, "\n".join(current_lines)))
    return guides


async def main_async() -> int:
    if not GUIDES_PATH.is_file():
        logger.error(f"{GUIDES_PATH} not found")
        return 1

    guides = _parse_guides(GUIDES_PATH)
    total = len(guides)
    logger.info(
        f"Ingesting {total} concept guides from {GUIDES_PATH} -> dataset 'firecrawl_concepts'"
    )

    ingested = 0
    for i, (title, block) in enumerate(guides, 1):
        try:
            entry = _build_guide_entry(title, block)
            await cognee.add(entry, dataset_name="firecrawl_concepts")
            ingested += 1
        except Exception as exc:
            logger.warning(f"  COGNIFY-FAIL {title}: {exc}")
            continue
        if i % 10 == 0 or i == total:
            logger.info(f"  progress: {i}/{total}")

    logger.info(f"Ingestion complete: {ingested}/{total} concept guides")
    return 0 if ingested > 0 else 1


def main() -> int:
    return asyncio.run(main_async())


if __name__ == "__main__":
    sys.exit(main())