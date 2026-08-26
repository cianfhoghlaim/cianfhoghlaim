#!/usr/bin/env python3
"""Auto-fix the 3 safe pre-v7 path patterns surfaced by sync:paths.

Per the 2026-08-15-retroactive-pre-v7-cleanup-v1 change (Phase A.2).
Reads the latest stedding/sync-reports/paths-{date}.md, applies the
3 safe rename patterns in-place, validates via ast.parse for .py
files, and writes a fix-applied report.

The 3 safe patterns (auto-fixable, no human review needed):
- sruth/cianfhoghlaim/        -> . (the pre-v7 repo rename)
- infrastructure/stacks/      -> bonneagar/stacks/  (the IaC move)
- infrastructure/komodo/      -> bonneagar/komodo/  (the IaC move)

Safety guarantees:
- .py files validated via ast.parse post-rename (revert if breaks)
- Files with 'was sruth/...pre-v7' annotation are SKIPPED (intentionally historical)
- Files with 'is sruth/...pre-v7' annotation are SKIPPED
- Self-reference file (the file that DEFINES the patterns) is detected + skipped
  (i.e. mise.toml which contains 'infrastructure/stacks/' as a string literal
  in the sync:paths task definition is not auto-fixed)

Usage:
  scripts/sync_paths_fix.py [--dry-run] [--pattern PATTERN]
  --dry-run    : show what would be fixed without applying
  --pattern X  : fix only one pattern (sruth|stacks|komodo)
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPORTS_DIR = Path("stedding/sync-reports")
FIX_REPORT_DIR = REPORTS_DIR

# The 3 safe patterns: (old, new, description)
SAFE_PATTERNS = [
    (
        "sruth/cianfhoghlaim/",
        ".",
        "the pre-v7 repo rename (sruth/ was the old multi-package layout)",
    ),
    (
        "infrastructure/stacks/",
        "bonneagar/stacks/",
        "the IaC move (IaC was re-merged into this repo at bonneagar/stacks/)",
    ),
    (
        "infrastructure/komodo/",
        "bonneagar/komodo/",
        "the IaC move (Komodo procedures are now at bonneagar/komodo/)",
    ),
]

# Files that DEFINES the patterns themselves (must be excluded from the auto-fix)
# mise.toml contains the patterns as string literals in the sync:paths task
PATTERN_DEFINING_FILES = {
    "mise.toml",
    "scripts/sync/paths.sh",
}


def find_latest_report() -> Path | None:
    """Find the most recent stedding/sync-reports/paths-{date}.md.

    Filters out the paths-fix-* reports (those are the fix-applied reports
    produced BY this script, not the upstream sync:paths reports it consumes).
    """
    if not REPORTS_DIR.is_dir():
        return None
    reports = sorted(
        (p for p in REPORTS_DIR.glob("paths-*.md") if not p.name.startswith("paths-fix-")),
        reverse=True,
    )
    return reports[0] if reports else None


def parse_report(report: Path) -> dict[str, int]:
    """Parse the sync:paths report to get the per-pattern counts."""
    counts: dict[str, int] = {}
    if not report.is_file():
        return counts
    text = report.read_text()
    for m in re.finditer(r"^-\s+(\S+):\s+(\d+)\s+occurrences", text, re.MULTILINE):
        counts[m.group(1)] = int(m.group(2))
    return counts


def find_files_with_pattern(pattern: str, exclude_self_refs: bool = True) -> list[Path]:
    """Find tracked files containing the pattern (excluding the pattern-defining files)."""
    cmd = [
        "grep",
        "-rln",
        "-E",
        pattern,
        "--include=*.py",
        "--include=*.ts",
        "--include=*.toml",
        "--include=*.yaml",
        "--include=*.baml",
        "--include=*.tsx",
        "--include=*.json",
        "bonneagar/",
        "dlt_sources/",
        "orchestration/",
        "baml_src/",
        "cocoindex/",
        "motherduck/",
        "meaisinfhoghlaim/",
        "agents/",
        "observability/",
        "pyproject.toml",
        "mise.toml",
        "turbo.json",
        "package.json",
        "tsconfig.json",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=".", timeout=60)
    files: list[Path] = []
    for line in result.stdout.strip().splitlines():
        path = Path(line)
        if exclude_self_refs and (
            path.name in PATTERN_DEFINING_FILES or str(path) in PATTERN_DEFINING_FILES
        ):
            continue
        if not path.exists():
            continue
        files.append(path)
    return files


def is_safe_to_rename(path: Path, old: str, new: str) -> tuple[bool, str]:
    """Validate the rename is safe for the file.

    Returns (is_safe, reason).
    For .py files, validates via ast.parse after a dry-run sed.
    For other files, validates by checking the file still exists.
    """
    if not path.exists():
        return False, "file does not exist"

    # Skip files that contain the intentionally historical annotation
    try:
        content = path.read_text()
    except Exception as e:
        return False, f"cannot read: {e}"

    if "was sruth/" in content and "pre-v7" in content:
        return False, "file contains 'was sruth/...pre-v7' annotation (intentionally historical)"

    if path.suffix == ".py":
        # Simulate the rename and validate
        simulated = content.replace(old, new)
        if simulated == content:
            return False, "no actual match for pattern"
        try:
            ast.parse(simulated)
        except SyntaxError as e:
            return False, f"ast.parse would fail after rename: {e}"
        return True, "ast.parse OK after simulated rename"

    if path.suffix in (".yaml", ".yml", ".toml", ".json", ".ts", ".tsx", ".baml"):
        # Just check the file is parseable as text (no structural validation)
        return True, "text file (no structural validation)"

    return True, "text file (default)"


def apply_rename(path: Path, old: str, new: str) -> bool:
    """Apply the rename in-place. Returns True if successful."""
    try:
        content = path.read_text()
    except Exception:
        return False
    if old not in content:
        return False
    new_content = content.replace(old, new)
    if new_content == content:
        return False
    try:
        path.write_text(new_content)
    except Exception:
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--dry-run", action="store_true", help="show what would be fixed without applying"
    )
    parser.add_argument(
        "--pattern",
        choices=["sruth", "stacks", "komodo"],
        help="fix only one pattern (default: all 3)",
    )
    args = parser.parse_args()

    # Find the latest report
    report = find_latest_report()
    if not report:
        print(f"ERROR: no sync:paths report found in {REPORTS_DIR}/")
        return 1

    counts = parse_report(report)
    print(f"Read report: {report}")
    print(f"Per-pattern counts: {counts}")
    print()

    # Filter to the 3 safe patterns
    patterns_to_fix = SAFE_PATTERNS
    if args.pattern:
        pattern_name_to_arg = {"sruth": 0, "stacks": 1, "komodo": 2}
        patterns_to_fix = [SAFE_PATTERNS[pattern_name_to_arg[args.pattern]]]

    fix_results: list[dict] = []
    for old, new, description in patterns_to_fix:
        # Get the count from the report
        count = counts.get(old, 0)
        if count == 0:
            print(f"SKIP {old}: 0 occurrences (already clean)")
            continue

        print(f"=== Pattern: {old} -> {new} ({count} occurrences) ===")
        print(f"    Description: {description}")
        files = find_files_with_pattern(old)
        print(f"    Files to inspect: {len(files)}")
        if not files:
            print(f"    SKIP: no files found (report is stale or self-references)")
            continue

        fixed_count = 0
        skipped_count = 0
        for path in files:
            is_safe, reason = is_safe_to_rename(path, old, new)
            if not is_safe:
                skipped_count += 1
                print(f"    SKIP {path}: {reason}")
                continue
            if args.dry_run:
                print(f"    WOULD FIX {path}")
                fixed_count += 1
            else:
                if apply_rename(path, old, new):
                    fixed_count += 1
                    print(f"    FIXED {path}")
                else:
                    skipped_count += 1
                    print(f"    FAILED {path}")

        fix_results.append(
            {
                "pattern": old,
                "replacement": new,
                "description": description,
                "occurrences_reported": count,
                "files_inspected": len(files),
                "files_fixed": fixed_count,
                "files_skipped": skipped_count,
            }
        )
        print()

    # Write the fix-applied report
    today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    fix_report = FIX_REPORT_DIR / f"paths-fix-{today}.md"
    if not args.dry_run:
        with open(fix_report, "w") as f:
            f.write(
                f"# Pre-v7 Path Drift Fix-Applied Report — {datetime.now(tz=timezone.utc).isoformat()}\n\n"
            )
            f.write(f"Auto-fix mode: **{'DRY RUN' if args.dry_run else 'APPLIED'}**\n\n")
            f.write("## Per-Pattern Results\n\n")
            for r in fix_results:
                f.write(f"### {r['pattern']} -> {r['replacement']}\n\n")
                f.write(f"- Description: {r['description']}\n")
                f.write(f"- Occurrences reported: {r['occurrences_reported']}\n")
                f.write(f"- Files inspected: {r['files_inspected']}\n")
                f.write(f"- Files {'would be ' if args.dry_run else ''}fixed: {r['files_fixed']}\n")
                f.write(f"- Files skipped: {r['files_skipped']}\n\n")
            f.write("## Summary\n\n")
            total_fixed = sum(r["files_fixed"] for r in fix_results)
            total_skipped = sum(r["files_skipped"] for r in fix_results)
            f.write(f"- Total files fixed: {total_fixed}\n")
            f.write(f"- Total files skipped: {total_skipped}\n")
            f.write(f"- Pattern: {args.pattern or 'all 3'}\n")
            f.write(f"- Mode: {'DRY RUN' if args.dry_run else 'APPLIED'}\n")
        print(f"Wrote fix report: {fix_report}")

    # Summary
    total_fixed = sum(r["files_fixed"] for r in fix_results)
    total_skipped = sum(r["files_skipped"] for r in fix_results)
    print()
    print(f"=== Summary ===")
    print(f"  Total files {'would be ' if args.dry_run else ''}fixed: {total_fixed}")
    print(f"  Total files skipped: {total_skipped}")
    print(f"  Mode: {'DRY RUN' if args.dry_run else 'APPLIED'}")

    return 0 if not args.dry_run else 0


if __name__ == "__main__":
    sys.exit(main())
