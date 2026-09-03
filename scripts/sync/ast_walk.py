"""ast_walk.py — the AST walker that powers `scripts/sync/dagster.sh` Layer 6.

Per the 2026-07-29-repo-hygiene-agent-routing-and-sync-wiring-v1 change
(see specs/knowledge-sync-loop/spec.md Layer 6 requirement) + the
2026-08-15-retroactive-pre-v7-cleanup-v1 change (the dagster layer).

Walks `orchestration/defs/`, parses each `.py` file with `ast`, and
counts the @asset / @sensor / @schedule / @job / @asset_check decorators
+ the group_name= kwargs.

Usage:
    python3 ast_walk.py
    python3 ast_walk.py --json
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from collections import Counter
from pathlib import Path

DEFS_ROOT = Path("orchestration/defs")
DECORATOR_NAMES = {
    "asset",
    "asset_check",
    "sensor",
    "schedule",
    "job",
    "resources",
    "resource",
}


def walk() -> dict:
    """Walk DEFS_ROOT and count decorators + collect metadata."""
    total_decorators: Counter = Counter()
    total_assets: int = 0
    total_sensors: int = 0
    total_schedules: int = 0
    total_jobs: int = 0
    total_asset_checks: int = 0
    broken_files: list[str] = []
    group_names: Counter = Counter()
    per_layer: dict[str, Counter] = {}

    layer_dirs = (
        sorted(DEFS_ROOT.iterdir())
        if DEFS_ROOT.is_dir()
        else []
    )

    for layer_dir in layer_dirs:
        if not layer_dir.is_dir():
            continue
        layer_name = layer_dir.name
        layer_counts: Counter = Counter()
        for py_file in layer_dir.rglob("*.py"):
            if "__pycache__" in py_file.parts:
                continue
            if py_file.name == "__init__.py":
                continue
            try:
                tree = ast.parse(py_file.read_text())
            except SyntaxError as e:
                broken_files.append(f"{py_file}: {e}")
                continue
            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                for dec in node.decorator_list:
                    name: str | None = None
                    if isinstance(dec, ast.Call):
                        func = dec.func
                        if isinstance(func, ast.Name):
                            name = func.id
                        elif isinstance(func, ast.Attribute):
                            name = func.attr
                        # Pull group_name= kwarg
                        for kw in dec.keywords:
                            if kw.arg == "group_name" and isinstance(kw.value, ast.Constant):
                                group_names[kw.value.value] += 1
                    elif isinstance(dec, ast.Name):
                        name = dec.id
                    elif isinstance(dec, ast.Attribute):
                        name = dec.attr
                    if name in DECORATOR_NAMES:
                        layer_counts[name] += 1
                        total_decorators[name] += 1
        per_layer[layer_name] = layer_counts

    return {
        "per_layer": {k: dict(v) for k, v in per_layer.items()},
        "totals": {
            "asset": total_decorators.get("asset", 0),
            "sensor": total_decorators.get("sensor", 0),
            "schedule": total_decorators.get("schedule", 0),
            "job": total_decorators.get("job", 0),
            "asset_check": total_decorators.get("asset_check", 0),
        },
        "group_count": len(group_names),
        "broken_files": broken_files,
    }


def render_markdown(data: dict) -> str:
    """Render the walk() result as a Markdown report."""
    lines = ["# Dagster Defs Sync Report", ""]
    lines.append("## Per-layer decorator counts")
    lines.append("")
    lines.append("| Layer | @asset | @sensor | @schedule | @job | @asset_check |")
    lines.append("|:--|--:|--:|--:|--:|--:|")
    for layer_name, counts in data["per_layer"].items():
        lines.append(
            f"| `{layer_name}` | {counts.get('asset', 0)} | {counts.get('sensor', 0)} | "
            f"{counts.get('schedule', 0)} | {counts.get('job', 0)} | "
            f"{counts.get('asset_check', 0)} |"
        )
    lines.append("")
    lines.append("## Totals")
    lines.append("")
    for key, value in data["totals"].items():
        lines.append(f"- Total @{key}: {value}")
    lines.append(f"- Unique group_name values: {data['group_count']}")
    lines.append("")
    if data["broken_files"]:
        lines.append("## Broken files")
        lines.append("")
        for f in data["broken_files"]:
            lines.append(f"- `{f}`")
        lines.append("")
        lines.append(f"FAIL: {len(data['broken_files'])} file(s) failed to parse")
    else:
        lines.append("OK: all defs/*.py files parse cleanly via ast")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Walk orchestration/defs/ via AST.")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of Markdown")
    args = parser.parse_args()

    data = walk()
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print(render_markdown(data))

    return 1 if data["broken_files"] else 0


if __name__ == "__main__":
    sys.exit(main())
