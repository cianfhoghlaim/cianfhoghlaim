#!/usr/bin/env python3
"""Ingest the 87 Docker Compose stacks at `bonneagar/stacks/` into Cognee cluster `stacks_catalog`.

Per the 2026-08-15-stacks-sync-loop-v1 change (Layer 8, Day 2).
Creates the 12th Cognee cluster (the 11 existing docs/openspec/skills/baml
clusters + the new stacks_catalog cluster).

For each stack at `bonneagar/stacks/<name>/`, the ingestor reads the 6
GOLD_STANDARD files (compose.yaml + sidecar.yaml + secrets.env +
pangolin.yaml + blueprint.yaml + .env.example) + assembles a per-stack
catalog entry + adds it to Cognee.

Usage:
  uv run python scripts/cognee_ingest_stacks_catalog.py
"""
from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

import cognee

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cognee_ingest_stacks_catalog")


GOLD_STANDARD_FILES = (
    "compose.yaml",
    "sidecar.yaml",
    "secrets.env",
    "pangolin.yaml",
    "blueprint.yaml",
    ".env.example",
)


def _build_catalog_entry(stack_dir: Path) -> str | None:
    """Build a markdown catalog entry for one stack.

    Returns None if the stack is missing the mandatory compose.yaml.
    """
    if not (stack_dir / "compose.yaml").is_file():
        return None

    parts: list[str] = [
        f"# Stack: {stack_dir.name}",
        "",
        f"Path: {stack_dir}",
        "",
    ]

    # GOLD_STANDARD status
    present = [f for f in GOLD_STANDARD_FILES if (stack_dir / f).is_file()]
    missing = [f for f in GOLD_STANDARD_FILES if f not in present]
    parts.append("## GOLD_STANDARD Status")
    parts.append("")
    parts.append(f"- Present ({len(present)}/6): {', '.join(present)}")
    if missing:
        parts.append(f"- Missing ({len(missing)}/6): {', '.join(missing)}")
    parts.append("")

    # Per-file excerpts (compose.yaml is the most informative)
    for fname in GOLD_STANDARD_FILES:
        path = stack_dir / fname
        if not path.is_file():
            continue
        try:
            content = path.read_text()
        except Exception as exc:
            parts.append(f"## {fname}")
            parts.append("")
            parts.append(f"(read error: {exc})")
            parts.append("")
            continue
        excerpt = content[:1500]
        parts.append(f"## {fname}")
        parts.append("")
        parts.append("```")
        parts.append(excerpt)
        if len(content) > 1500:
            parts.append("... (truncated)")
        parts.append("```")
        parts.append("")

    return "\n".join(parts)


async def main_async() -> int:
    stacks_root = Path("bonneagar/stacks")
    if not stacks_root.is_dir():
        logger.error(f"{stacks_root} not found")
        return 1

    stack_dirs = sorted(p for p in stacks_root.iterdir() if p.is_dir())
    total = len(stack_dirs)
    # Per the 2026-08-24-dlt-sources-to-multi-repo-scaffold-v1 change Phase 0.8:
    # the canonical cluster name is `stacks` (per the v2 plan §C.8). We also
    # write to the legacy `stacks_catalog` cluster for backward compat with
    # the 2026-08-15-stacks-sync-loop-v1 sync chain.
    datasets = ("stacks", "stacks_catalog")
    logger.info(
        f"Ingesting {total} stack catalogs -> datasets {list(datasets)}"
    )

    ingested = 0
    skipped = 0
    for i, stack_dir in enumerate(stack_dirs, 1):
        try:
            entry = _build_catalog_entry(stack_dir)
        except Exception as exc:
            logger.warning(f"  SKIP {stack_dir.name}: {exc}")
            skipped += 1
            continue
        if entry is None:
            skipped += 1
            continue
        try:
            for ds in datasets:
                await cognee.add(entry, dataset_name=ds)
            ingested += 1
        except Exception as exc:
            logger.warning(f"  COGNIFY-FAIL {stack_dir.name}: {exc}")
            continue
        if i % 10 == 0 or i == total:
            logger.info(f"  progress: {i}/{total}")

    logger.info(
        f"Ingestion complete: {ingested}/{total} stacks "
        f"({skipped} skipped)"
    )
    return 0 if ingested > 0 else 1


def main() -> int:
    return asyncio.run(main_async())


if __name__ == "__main__":
    sys.exit(main())
