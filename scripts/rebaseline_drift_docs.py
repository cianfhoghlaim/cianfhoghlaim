"""rebaseline_drift_docs.py — auto-fix the stale count claims reported by lint:drift-docs.

The `mise run lint:drift-docs` gate (added by the
2026-07-29-repo-hygiene change) reports count claims that
don't match ground truth. This script walks every claim
and rewrites it to match ground truth.

Per the 2026-08-13-count-drift-rebase-and-indexing-cognition-cleanup-v1
change (the retrospective-cleanup spec delta).

Usage:
    uv run python scripts/rebaseline_drift_docs.py           # dry-run (default)
    uv run python scripts/rebaseline_drift_docs.py --apply   # write the fixes
    uv run python scripts/rebaseline_drift_docs.py --json    # JSON report to stdout
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
from pathlib import Path

# Lazily re-use the existing lint_drift_docs.py machinery.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lint_drift_docs import (
    AGENTS_FILES,
    CLAIM_PATTERN,
    REPO_ROOT,
    REPORT_DIR,
    ground_truth,
)


def find_violations() -> list[dict]:
    """Walk every in-scope AGENTS.md file and return the violations.

    Returns:
        list of dicts: { file, line, category, claimed, actual, context }
    """
    truth = ground_truth()
    violations: list[dict] = []
    for agents_path in AGENTS_FILES:
        if not agents_path.exists():
            continue
        text = agents_path.read_text()
        for line_no, line in enumerate(text.splitlines(), start=1):
            for match in CLAIM_PATTERN.finditer(line):
                claimed = int(match.group(1))
                category = match.group(2).lower()
                actual = truth.get(category)
                if actual is None or claimed == actual:
                    continue
                ctx_start = max(0, match.start() - 10)
                ctx_end = min(len(line), match.end() + 10)
                context = line[ctx_start:ctx_end].strip()
                violations.append({
                    "file": str(agents_path.relative_to(REPO_ROOT)),
                    "line": line_no,
                    "category": category,
                    "claimed": claimed,
                    "actual": actual,
                    "context": context,
                })
    return violations


def apply_fixes(violations: list[dict]) -> list[dict]:
    """Apply the fixes to disk. Returns a list of planned/applied fixes.

    Args:
        violations: list of violation dicts from find_violations()

    Returns:
        list of dicts: { file, line, category, old, new, status }
    """
    by_file: dict[str, list[dict]] = {}
    for v in violations:
        by_file.setdefault(v["file"], []).append(v)

    applied: list[dict] = []
    for file_rel, file_violations in by_file.items():
        path = REPO_ROOT / file_rel
        text = path.read_text()
        lines = text.splitlines()
        # Sort violations by line number in descending order so we
        # can iterate without invalidating upstream indices.
        file_violations_sorted = sorted(file_violations, key=lambda v: v["line"], reverse=True)
        for v in file_violations_sorted:
            line_idx = v["line"] - 1
            line = lines[line_idx]
            match = None
            for m in CLAIM_PATTERN.finditer(line):
                if int(m.group(1)) == v["claimed"] and m.group(2).lower() == v["category"]:
                    match = m
                    break
            if match is None:
                continue
            old_text = match.group(0)
            new_text = f"{v['actual']} {v['category']}"
            new_line = line[:match.start()] + new_text + line[match.end():]
            lines[line_idx] = new_line
            applied.append({
                "file": file_rel,
                "line": v["line"],
                "category": v["category"],
                "old": v["claimed"],
                "new": v["actual"],
                "old_text": old_text,
                "new_text": new_text,
                "status": "applied",
            })
        new_text = "\n".join(lines)
        # Preserve trailing newline if the original had one
        if text.endswith("\n") and not new_text.endswith("\n"):
            new_text += "\n"
        path.write_text(new_text)
    return applied


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write the fixes to disk (default: dry-run)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the JSON report to stdout",
    )
    args = parser.parse_args()

    violations = find_violations()
    truth = ground_truth()

    today = _dt.datetime.now(_dt.UTC).strftime("%Y-%m-%d")
    report: dict = {
        "generated_at": _dt.datetime.now(_dt.UTC).isoformat(),
        "ground_truth": truth,
        "mode": "apply" if args.apply else "dry-run",
        "violation_count": len(violations),
        "fixes": [],
    }

    if not violations:
        report["status"] = "clean"
        if not args.json:
            print(f"lint:drift-docs:rebaseline: 0 changes needed (already clean)")
        # Still write the report
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        report_path = REPORT_DIR / f"drift-docs-rebaseline-{today}.json"
        with report_path.open("w") as f:
            json.dump(report, f, indent=2)
        if not args.json:
            print(f"lint:drift-docs:rebaseline: Report: {report_path}")
        return 0

    if args.apply:
        report["fixes"] = apply_fixes(violations)
        report["status"] = "applied"
    else:
        # Dry-run: just list the planned fixes
        for v in violations:
            report["fixes"].append({
                "file": v["file"],
                "line": v["line"],
                "category": v["category"],
                "old": v["claimed"],
                "new": v["actual"],
                "old_text": f"{v['claimed']} {v['category']}",
                "new_text": f"{v['actual']} {v['category']}",
                "status": "planned",
            })
        report["status"] = "planned"

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / f"drift-docs-rebaseline-{today}.json"
    with report_path.open("w") as f:
        json.dump(report, f, indent=2)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        mode = "apply" if args.apply else "dry-run"
        print(f"lint:drift-docs:rebaseline: {len(violations)} change(s) ({mode} mode)")
        for f in report["fixes"]:
            print(f"  [{f['file']}:{f['line']}] {f['category']} {f['old']} -> {f['new']}  ({f['status']})")
        print(f"lint:drift-docs:rebaseline: Report: {report_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())