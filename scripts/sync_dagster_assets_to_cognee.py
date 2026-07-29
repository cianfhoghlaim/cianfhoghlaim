#!/usr/bin/env python3
"""Ingest the Dagster asset graph into Cognee.

Per the 2026-08-15-retroactive-pre-v7-cleanup-v1 change (Phase 6 — Cognee ingestion).
Creates 1 new Cognee cluster:
  - dagster_assets (the 5-layer defs/ tree: per-group @asset + @asset_check
    + @sensor counts + asset names + their group paths)

Walks orchestration/defs/ + parses each .py file via `ast` to extract
@asset / @asset_check / @sensor decorator usage, then ingests a
per-layer summary into Cognee.

Usage:
  uv run python scripts/sync_dagster_assets_to_cognee.py
"""
from __future__ import annotations

import ast
import asyncio
import logging
import sys
from pathlib import Path

import cognee

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sync_dagster_assets_to_cognee")

DEFS_ROOT = Path("orchestration/defs")
LAYER_NAMES = [
    "1_ingestion",
    "2_materials",
    "3_model_lifecycle",
    "4_asset_generation",
    "5_agent_ops",
]
DATASET_NAME = "dagster_assets"


def extract_decorators(py_path: Path) -> dict[str, list[str]]:
    """Parse a .py file and return the list of decorator types used.

    Returns a dict like {"asset": ["my_asset", "..."], "sensor": [...]}.
    """
    try:
        source = py_path.read_text()
        tree = ast.parse(source, filename=str(py_path))
    except (SyntaxError, OSError) as e:
        logger.warning(f"  SKIP {py_path}: {e}")
        return {"asset": [], "asset_check": [], "sensor": []}

    decorators: dict[str, list[str]] = {"asset": [], "asset_check": [], "sensor": []}

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            name: str | None = None
            if isinstance(decorator, ast.Name):
                name = decorator.id
            elif isinstance(decorator, ast.Attribute):
                name = decorator.attr
            elif isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name):
                    name = decorator.func.id
                elif isinstance(decorator.func, ast.Attribute):
                    name = decorator.func.attr
            if name in decorators:
                decorators[name].append(node.name)

    return decorators


def walk_defs_tree() -> dict[str, dict[str, int]]:
    """Walk orchestration/defs/ + return per-layer decorator counts.

    Returns: {layer_name: {"asset": N, "asset_check": N, "sensor": N, "files": N}}
    """
    summary: dict[str, dict[str, int]] = {}

    for layer in LAYER_NAMES:
        layer_dir = DEFS_ROOT / layer
        if not layer_dir.is_dir():
            continue
        totals = {"asset": 0, "asset_check": 0, "sensor": 0, "files": 0}
        for py_path in sorted(layer_dir.rglob("*.py")):
            totals["files"] += 1
            decorators = extract_decorators(py_path)
            totals["asset"] += len(decorators["asset"])
            totals["asset_check"] += len(decorators["asset_check"])
            totals["sensor"] += len(decorators["sensor"])
        summary[layer] = totals

    return summary


def render_per_layer_summary(summary: dict[str, dict[str, int]]) -> str:
    """Render a markdown summary of the per-layer decorator counts."""
    lines = [
        "# Dagster Asset Graph — 5-Layer defs/ Tree Summary",
        "",
        "Per the 2026-08-15-retroactive-pre-v7-cleanup-v1 change (Phase 6).",
        "This summary is ingested into the `dagster_assets` Cognee cluster.",
        "",
        "| Layer | @asset | @asset_check | @sensor | .py files |",
        "|:--|--:|--:|--:|--:|",
    ]
    grand_total = {"asset": 0, "asset_check": 0, "sensor": 0, "files": 0}
    for layer, counts in summary.items():
        lines.append(
            f"| `{layer}` | {counts['asset']} | {counts['asset_check']} | "
            f"{counts['sensor']} | {counts['files']} |"
        )
        for key in grand_total:
            grand_total[key] += counts[key]
    lines.append(
        f"| **TOTAL** | **{grand_total['asset']}** | "
        f"**{grand_total['asset_check']}** | **{grand_total['sensor']}** | "
        f"**{grand_total['files']}** |"
    )
    lines.extend([
        "",
        "## Canonical 5-Layer Convention",
        "",
        "The 5 layers (per the dagster-5-layer-component-architecture spec) are:",
        "1. `1_ingestion/` — DLT pipelines + Firecrawl monitors + Ireland/England BAML",
        "2. `2_materials/` — Per-jurisdiction asset wrappers (Ireland, England, JC, etc.)",
        "3. `3_model_lifecycle/` — Model registry + sync_health (this asset lives here)",
        "4. `4_asset_generation/` — Education asset assets (curriculum, exams)",
        "5. `5_agent_ops/` — Agent operations (heritage agents)",
        "",
        "## KCG Components",
        "",
        "The 5 canonical KCG Components live at `orchestration/components/`:",
        "- `layer1_ingestion.py`",
        "- `layer2_materials.py`",
        "- `layer3_model_lifecycle.py`",
        "- `layer4_asset_generation.py`",
        "- `layer5_agent_ops.py`",
        "",
        "Plus 4 derived components:",
        "- `biep_subject_component.py`",
        "- `junior_cycle_subject_component.py`",
        "- `england_board_subject_component.py`",
        "- `england_cross_board_comparator_component.py`",
    ])
    return "\n".join(lines)


async def ingest_to_cognee(summary_text: str) -> int:
    """Ingest the summary into Cognee as the dagster_assets cluster."""
    try:
        await cognee.add(summary_text, dataset_name=DATASET_NAME)
    except Exception as e:
        logger.error(f"  COGNEE-FAIL: {e}")
        return 0
    return 1


async def main_async() -> int:
    summary = walk_defs_tree()
    if not summary:
        logger.error(f"No layers found under {DEFS_ROOT}")
        return 1

    summary_text = render_per_layer_summary(summary)
    logger.info(f"Walked {len(summary)} layers + rendered summary ({len(summary_text)} chars)")

    ingested = await ingest_to_cognee(summary_text)
    logger.info(
        f"Ingestion complete: {ingested} summary ingested into '{DATASET_NAME}' cluster"
    )
    return 0 if ingested > 0 else 1


def main() -> int:
    return asyncio.run(main_async())


if __name__ == "__main__":
    sys.exit(main())
