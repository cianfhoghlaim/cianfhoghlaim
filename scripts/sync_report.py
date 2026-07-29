#!/usr/bin/env python3
"""Generate the per-layer + unified sync report.

Per the 2026-08-15-knowledge-sync-loop-v1 change (orchestrator).

Runs the 5 layer sync scripts (paths / ccc / cognee / skills / mcp),
captures each one's stdout, and writes a unified `all-{date}.md` to
`stedding/sync-reports/`. Each layer section includes a pass/fail
status and the per-layer report excerpt.

Usage:
  uv run python scripts/sync_report.py              # run all 5 layers
  uv run python scripts/sync_report.py --layers paths,skills  # subset
  uv run python scripts/sync_report.py --dry-run    # show plan, don't run
"""
from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPORT_DIR = Path("stedding/sync-reports")
LAYER_SCRIPTS = {
    "paths": "scripts/sync/paths.sh",
    "ccc": "scripts/sync/ccc.sh",
    "cognee": "scripts/sync/cognee.sh",
    "skills": "scripts/sync/skills.sh",
    "mcp": "scripts/sync/mcp.sh",
}


def run_layer(name: str, script: Path) -> tuple[int, str]:
    """Run a single layer sync script and return (exit_code, stdout)."""
    if not script.exists():
        return 1, f"(script not found: {script})"
    proc = subprocess.run(
        ["bash", str(script)],
        capture_output=True,
        text=True,
        check=False,
    )
    out = proc.stdout or ""
    if proc.stderr:
        out += "\n[stderr]\n" + proc.stderr
    return proc.returncode, out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--layers",
        default=",".join(LAYER_SCRIPTS.keys()),
        help="Comma-separated layer names (default: all 5)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the plan without running the layer scripts",
    )
    args = parser.parse_args()

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    layers = [name.strip() for name in args.layers.split(",") if name.strip()]
    unknown = [name for name in layers if name not in LAYER_SCRIPTS]
    if unknown:
        print(f"ERROR: unknown layer(s): {', '.join(unknown)}", file=sys.stderr)
        print(f"Available: {', '.join(LAYER_SCRIPTS.keys())}", file=sys.stderr)
        return 2

    if args.dry_run:
        print(f"Plan: would run {len(layers)} layer(s)")
        for name in layers:
            print(f"  - {name}: bash {LAYER_SCRIPTS[name]}")
        return 0

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    date_slug = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    report_path = REPORT_DIR / f"all-{date_slug}.md"

    lines: list[str] = [
        "# Knowledge Sync Loop — Full Report",
        f"Generated: {timestamp}",
        "",
        "Per the 2026-08-15-knowledge-sync-loop-v1 change. Pull-based.",
        "",
        "---",
        "",
    ]

    overall_fail = 0
    for name in layers:
        script = Path(LAYER_SCRIPTS[name])
        print(f"[sync_report] Running layer '{name}' ({shlex.quote(str(script))})")
        code, output = run_layer(name, script)
        status = "PASS" if code == 0 else f"FAIL (exit {code})"
        lines.append(f"## Layer: sync:{name} — {status}")
        lines.append("")
        lines.append("```")
        lines.append(output.rstrip())
        lines.append("```")
        lines.append("")
        if code != 0:
            overall_fail += 1

    lines.append("---")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(
        f"{len(layers) - overall_fail}/{len(layers)} layers passed. "
        "The deployment control panel (notebooks/24_deployment_control_panel.py) "
        "reads this report."
    )

    report_path.write_text("\n".join(lines) + "\n")
    print(f"[sync_report] Wrote {report_path}")

    return 1 if overall_fail > 0 else 0


if __name__ == "__main__":
    sys.exit(main())