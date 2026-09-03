"""
Python bridge for the web UI control panel.

Per the `deployment-control-panel` openspec capability (2026-08-15).
This module is invoked by `web/hono-api/control-panel/index.ts` via
subprocess to fetch data from the canonical registries.

The bridge exposes 5 subcommands (one per tab):
  - models          → list every MODEL_REGISTRY entry
  - models set      → toggle a model on/off in deployment-choice.yaml
  - pipelines       → list every DLT source + CocoIndex App
  - pipelines set   → toggle a pipeline on/off
  - datasets        → list every BIEP DuckDB table + LanceDB mount + BAML class
  - stacks          → list every Docker Compose stack
  - stacks set      → toggle a stack on/off
  - registry        → full MODEL_REGISTRY summary + drift count

Each subcommand emits JSON to stdout. Errors go to stderr with
non-zero exit code.

Reference: openspec/specs/deployment-control-panel/spec.md
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

# Repo root — the parent of notebooks/_shared/
_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


# ─── Subcommands ─────────────────────────────────────────────────────────


def cmd_models(args: argparse.Namespace) -> int:
    """Tab 1: every MODEL_REGISTRY entry with the deployment-choice enabled flag."""
    from meaisinfhoghlaim.models import MODEL_REGISTRY, filter_models
    from notebooks._shared.schema import read_deployment_choice

    state = read_deployment_choice()
    enabled_models = state.get("enabled_models", {})

    models = []
    for entry in MODEL_REGISTRY.entries():
        models.append({
            "enabled": bool(enabled_models.get(entry.key, entry.available)),
            "key": entry.key,
            "family": entry.family,
            "role": entry.role,
            "display_name": entry.display_name,
            "upstream_id": entry.upstream_id,
            "backend": entry.backend,
            "available": entry.available,
            "litellm_alias": entry.litellm_alias or "",
            "languages": ",".join(entry.languages) if entry.languages else "",
        })
    print(json.dumps({"models": models}))
    return 0


def cmd_models_set(args: argparse.Namespace) -> int:
    """Toggle a model on/off in deployment-choice.yaml."""
    from notebooks._shared.schema import read_deployment_choice, write_deployment_choice

    state = read_deployment_choice()
    state.setdefault("enabled_models", {})[args.key] = bool(args.enabled)
    write_deployment_choice(state)
    print(json.dumps({"ok": True, "key": args.key, "enabled": bool(args.enabled)}))
    return 0


def cmd_pipelines(args: argparse.Namespace) -> int:
    """Tab 2: every DLT source + CocoIndex App."""
    from notebooks._shared.schema import list_dlt_sources, list_cocoindex_apps, read_deployment_choice

    state = read_deployment_choice()
    enabled_pipelines = state.get("enabled_pipelines", {})

    pipelines = []
    for src in list_dlt_sources():
        pipelines.append({
            "source_name": src["source_name"],
            "file_path": src["file_path"],
            "primary_key": str(src["primary_key"]),
            "destinations": src["destinations"],
            "enabled": bool(enabled_pipelines.get(src["source_name"], True)),
        })
    for app in list_cocoindex_apps():
        pipelines.append({
            "source_name": app["app_name"],
            "file_path": app["file_path"],
            "primary_key": app.get("embedder") or "(n/a)",
            "destinations": [app["lance_mount"]] if app.get("lance_mount") else [],
            "enabled": bool(enabled_pipelines.get(app["app_name"], True)),
        })
    print(json.dumps({"pipelines": pipelines}))
    return 0


def cmd_pipelines_set(args: argparse.Namespace) -> int:
    """Toggle a pipeline on/off in deployment-choice.yaml."""
    from notebooks._shared.schema import read_deployment_choice, write_deployment_choice

    state = read_deployment_choice()
    state.setdefault("enabled_pipelines", {})[args.source_name] = bool(args.enabled)
    write_deployment_choice(state)
    print(json.dumps({"ok": True, "source_name": args.source_name, "enabled": bool(args.enabled)}))
    return 0


def cmd_datasets(args: argparse.Namespace) -> int:
    """Tab 3: every BIEP DuckDB table + LanceDB mount + BAML class."""
    from notebooks._shared.schema import _lance_introspect, list_baml_classes

    datasets = []
    # LanceDB mounts (table-level)
    for row in _lance_introspect():
        datasets.append({
            "table_name": row["table_name"],
            "schema_name": row["schema_name"],
            "column_count": 1,
            "source": "lance",
        })
    # BAML classes
    for cls in list_baml_classes():
        datasets.append({
            "table_name": f"{cls['class_name']} (BAML)",
            "schema_name": cls["parent_baml"],
            "column_count": 1,
            "source": "baml",
        })
    print(json.dumps({"datasets": datasets}))
    return 0


def cmd_stacks(args: argparse.Namespace) -> int:
    """Tab 4: every Docker Compose stack in bonneagar/stacks/."""
    from notebooks._shared.schema import read_deployment_choice

    state = read_deployment_choice()
    enabled_stacks = state.get("enabled_stacks", {})

    stacks_dir = _REPO_ROOT / "bonneagar" / "stacks"
    stacks = []
    if stacks_dir.exists():
        for entry in sorted(stacks_dir.iterdir()):
            if not entry.is_dir() or entry.name.startswith("_"):
                continue
            category = "infra"
            if any((entry / sub).exists() for sub in ("lance", "cognee", "langfuse")):
                category = "ml"
            elif any((entry / sub).exists() for sub in ("web", "convex")):
                category = "web"
            stacks.append({
                "name": entry.name,
                "enabled": bool(enabled_stacks.get(entry.name, True)),
                "category": category,
            })
    print(json.dumps({"stacks": stacks}))
    return 0


def cmd_stacks_set(args: argparse.Namespace) -> int:
    """Toggle a stack on/off in deployment-choice.yaml."""
    from notebooks._shared.schema import read_deployment_choice, write_deployment_choice

    state = read_deployment_choice()
    state.setdefault("enabled_stacks", {})[args.name] = bool(args.enabled)
    write_deployment_choice(state)
    print(json.dumps({"ok": True, "name": args.name, "enabled": bool(args.enabled)}))
    return 0


def cmd_registry(args: argparse.Namespace) -> int:
    """Tab 5: full MODEL_REGISTRY summary + drift count."""
    from meaisinfhoghlaim.models import MODEL_REGISTRY

    summary = MODEL_REGISTRY.summary()
    # Drift count — run scripts/registry_audit.py
    drift_count = 0
    try:
        import subprocess
        proc = subprocess.run(
            ["python3", str(_REPO_ROOT / "scripts" / "registry_audit.py")],
            cwd=str(_REPO_ROOT),
            capture_output=True,
            text=True,
        )
        # The audit script reports "Found 0 hardcoded..." or "Found N potential..."
        for line in proc.stdout.splitlines():
            if line.startswith("Found ") and "potential" in line:
                drift_count = int(line.split()[1])
    except Exception:
        pass

    return {
        "total": summary["total"],
        "available": summary["available"],
        "deprecated": summary["deprecated"],
        "by_family": summary["by_family"],
        "drift_count": drift_count,
        "last_audit": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


# ─── Main ────────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(description="Web UI control panel Python bridge")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    p_models = subparsers.add_parser("models", help="List every MODEL_REGISTRY entry (or toggle one with --key/--enabled)")
    p_models.add_argument("--key", required=False, help="Toggle this model")
    p_models.add_argument("--enabled", required=False, help="Set enabled to true/false")
    p_models.set_defaults(func=cmd_models_dispatch)

    p_pipelines = subparsers.add_parser("pipelines", help="List every DLT source + CocoIndex App (or toggle one with --source_name/--enabled)")
    p_pipelines.add_argument("--source_name", required=False, help="Toggle this pipeline")
    p_pipelines.add_argument("--enabled", required=False, help="Set enabled to true/false")
    p_pipelines.set_defaults(func=cmd_pipelines_dispatch)

    subparsers.add_parser("datasets", help="List every BIEP DuckDB table + LanceDB mount + BAML class").set_defaults(func=cmd_datasets)

    p_stacks = subparsers.add_parser("stacks", help="List every Docker Compose stack (or toggle one with --name/--enabled)")
    p_stacks.add_argument("--name", required=False, help="Toggle this stack")
    p_stacks.add_argument("--enabled", required=False, help="Set enabled to true/false")
    p_stacks.set_defaults(func=cmd_stacks_dispatch)

    subparsers.add_parser("registry", help="Full MODEL_REGISTRY summary + drift count").set_defaults(func=cmd_registry)

    args = parser.parse_args()
    try:
        result = args.func(args)
        if isinstance(result, int):
            return result
        if isinstance(result, dict):
            print(json.dumps(result))
            return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


def cmd_models_dispatch(args: argparse.Namespace) -> int:
    """Dispatch the models subcommand to list or toggle."""
    if args.key is not None and args.enabled is not None:
        return cmd_models_set(args)
    return cmd_models(args)


def cmd_pipelines_dispatch(args: argparse.Namespace) -> int:
    """Dispatch the pipelines subcommand to list or toggle."""
    if args.source_name is not None and args.enabled is not None:
        return cmd_pipelines_set(args)
    return cmd_pipelines(args)


def cmd_stacks_dispatch(args: argparse.Namespace) -> int:
    """Dispatch the stacks subcommand to list or toggle."""
    if args.name is not None and args.enabled is not None:
        return cmd_stacks_set(args)
    return cmd_stacks(args)


if __name__ == "__main__":
    sys.exit(main())
