#!/usr/bin/env python3
"""Marimo WASM export for BIEP v3 jurisdiction dashboards.

Per the 2026-08-05-marimo-wasm-and-cigrunners-v1 change (closes
GitHub issue #54 — Marimo WASM delta export + manifest publishing + theme).

Exports each BIEP v3 jurisdiction dashboard notebook to a WebAssembly
bundle + a JSON manifest. The bundles are published to
web/apps/cianfhoghlaim-web/public/notebooks/ as static assets.

Usage:
    uv run python scripts/marimo_wasm_export.py
    uv run python scripts/marimo_wasm_export.py --notebooks-root notebooks/leaving_cert/03_leaving_cert
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# The 16 BIEP v3 jurisdiction + grouped dashboards to export
# (per the 2026-08-10-marimo-v14-cascading-effects-verification-v1 change)
DASHBOARD_NOTEBOOKS = [
    "19_ireland_pipeline_dashboard",
    "20_england_pipeline_dashboard",
    "21_sct_wls_ni_pipeline_dashboard",
    "22_crown_dependencies_dashboard",
    "23_8_jurisdiction_overview",
    "24_deployment_control_panel",
    "26_aistear_dashboard",
    "27_primary_dashboard",
    "40_leaving_cert_subject_panel",
    "meaisin_ops_console",
    "celtic_languages",
    "corpus_overview",
    "speedrun_mmo",
    "academic_history",
    "irish_law",
    "sync_health",
]

# The canonical Cianfhoghlaim theme (CSS-only — applied at runtime via a
# <link rel="stylesheet"> tag that the marimo WASM export injects post-build).
CIANFHOGHLAIM_THEME_CSS = """
/* Cianfhoghlaim canonical theme for marimo WASM */
:root {
  --ci-primary: #1e40af;
  --ci-secondary: #059669;
  --ci-bg: #ffffff;
  --ci-text: #1f2937;
  --ci-accent: #f59e0b;
}
body {
  background: var(--ci-bg);
  color: var(--ci-text);
  font-family: -apple-system, system-ui, sans-serif;
}
h1 { color: var(--ci-primary); }
h2 { color: var(--ci-secondary); }
button { background: var(--ci-primary); color: white; }
"""


def export_notebook_to_wasm(notebook_path: Path, output_root: Path) -> dict[str, Any]:
    """Export a single .py notebook to a WASM bundle + manifest.

    Real implementation uses `marimo export wasm` (available in marimo 0.13+).
    Falls back to a placeholder index.html when `marimo` is not on PATH.
    """
    bundle_name = notebook_path.stem
    output_dir = output_root / bundle_name
    output_dir.mkdir(parents=True, exist_ok=True)

    bundle_size = 0
    used_real_export = False
    if shutil.which("marimo"):
        # Run marimo export wasm (marimo 0.13+)
        result = subprocess.run(
            ["marimo", "export", "wasm", str(notebook_path),
             "--output", str(output_dir / "wasm")],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            print(f"WARN: marimo export failed for {notebook_path.name}: {result.stderr[:200]}")
        else:
            used_real_export = True
            wasm_dir = output_dir / "wasm"
            if wasm_dir.exists():
                bundle_size = sum(f.stat().st_size for f in wasm_dir.rglob("*"))

    if not used_real_export:
        # Placeholder: write a minimal index.html with the canonical theme
        placeholder = output_dir / "index.html"
        placeholder.write_text(
            f"<!DOCTYPE html><html><head><title>{bundle_name}</title>"
            f"<style>{CIANFHOGHLAIM_THEME_CSS}</style></head>"
            f"<body><h1>{bundle_name}</h1>"
            f"<p>This is a Marimo WASM placeholder. Run with <code>marimo</code> on "
            f"PATH to generate the real bundle. See scripts/marimo_wasm_export.py "
            f"and openspec/changes/2026-07-14-fix-foundation-v7-flattening-and-baml-drift-v1/.</p>"
            f"</body></html>"
        )
        bundle_size = placeholder.stat().st_size

    manifest = {
        "name": bundle_name,
        "path": str(notebook_path),
        "exported_at": datetime.now(UTC).isoformat(),
        "marimo_version": "0.13+",
        "real_export": used_real_export,
        "bundle_size_kb": bundle_size / 1024,
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="marimo_wasm_export",
        description="Export BIEP v3 jurisdiction dashboard notebooks to Marimo WASM bundles",
    )
    parser.add_argument(
        "--notebooks-root",
        default="notebooks",
        help="Root directory containing the BIEP v3 notebook .py files (default: notebooks — the post-v7 flat layout)",
    )
    parser.add_argument(
        "--output-root",
        default="web/apps/cianfhoghlaim-web/public/notebooks",
        help="Root directory for the WASM bundle output (default: cianfhoghlaim-web/public/notebooks)",
    )
    args = parser.parse_args(argv)

    repo_root = Path.cwd()
    nb_root = repo_root / args.notebooks_root
    out_root = repo_root / args.output_root
    if not nb_root.exists():
        print(f"ERROR: notebooks root not found: {nb_root}", file=sys.stderr)
        return 1
    out_root.mkdir(parents=True, exist_ok=True)

    results = []
    for name in DASHBOARD_NOTEBOOKS:
        nb_path = nb_root / f"{name}.py"
        if not nb_path.exists():
            print(f"WARN: {nb_path} not found, skipping", file=sys.stderr)
            continue
        print(f"Exporting {name}...")
        result = export_notebook_to_wasm(nb_path, out_root)
        results.append(result)
        real = "REAL" if result.get("real_export") else "PLACEHOLDER"
        print(f"  [{real}] {result['bundle_dir']}  size={result['bundle_size_kb']:.1f}KB")

    master_manifest = {
        "exported_at": datetime.now(UTC).isoformat(),
        "count": len(results),
        "real_export_count": sum(1 for r in results if r.get("real_export")),
        "placeholder_count": sum(1 for r in results if not r.get("real_export")),
        "notebooks": results,
    }
    (out_root / "manifest.json").write_text(json.dumps(master_manifest, indent=2))
    print(f"\nExported {len(results)} notebooks to {out_root}")
    print(f"  real={master_manifest['real_export_count']}  placeholder={master_manifest['placeholder_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
