"""Lint the .cocoindex_code/guides.yml file.

Walks every entry in the YAML file, extracts the `files:`
list, and verifies each path resolves on disk (file OR
directory). Emits a JSON report to
stedding/sync-reports/guides-yml-{date}.json.

Exits 0 if all paths resolve; exits 1 if any path is missing.

Per the 2026-08-13-guides-yml-repair-and-docs-integrations-index-v1
openspec change (the indexing-and-cognition spec delta).
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required. Install with: uv add pyyaml", file=sys.stderr)
    sys.exit(2)


GUIDES_PATH = Path(".cocoindex_code/guides.yml")
REPORTS_DIR = Path("stedding/sync-reports")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--guides",
        type=Path,
        default=GUIDES_PATH,
        help="Path to guides.yml (default: .cocoindex_code/guides.yml)",
    )
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=REPORTS_DIR,
        help="Directory to write the JSON report (default: stedding/sync-reports/)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the report and always exit 0 (do not fail)",
    )
    args = parser.parse_args()

    guides_path: Path = args.guides
    report_dir: Path = args.report_dir

    if not guides_path.exists():
        print(f"ERROR: {guides_path} does not exist", file=sys.stderr)
        return 2

    with guides_path.open() as f:
        guides = yaml.safe_load(f)

    if not isinstance(guides, list):
        print(f"ERROR: {guides_path} must contain a YAML list at the top level", file=sys.stderr)
        return 2

    total_entries = len(guides)
    total_files = 0
    missing_paths: list[dict[str, object]] = []
    entries_summary: list[dict[str, object]] = []

    for i, g in enumerate(guides, 1):
        title = g.get("title", "?")
        domain = g.get("domain", "?")
        files = g.get("files", []) or []
        entry_missing: list[str] = []
        for f in files:
            path = str(f).lstrip("/")
            total_files += 1
            if not os.path.exists(path):
                entry_missing.append(path)
                missing_paths.append({
                    "entry_index": i,
                    "title": title,
                    "domain": domain,
                    "missing_path": path,
                })
        entries_summary.append({
            "entry_index": i,
            "title": title,
            "domain": domain,
            "file_count": len(files),
            "missing_count": len(entry_missing),
            "missing_paths": entry_missing,
            "status": "ok" if not entry_missing else "fail",
        })

    today = _dt.datetime.now(_dt.UTC).strftime("%Y-%m-%d")
    report = {
        "generated_at": _dt.datetime.now(_dt.UTC).isoformat(),
        "guides_path": str(guides_path),
        "total_entries": total_entries,
        "total_file_references": total_files,
        "missing_count": len(missing_paths),
        "status": "ok" if not missing_paths else "fail",
        "entries": entries_summary,
        "missing_paths": missing_paths,
    }

    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"guides-yml-{today}.json"
    with report_path.open("w") as f:
        json.dump(report, f, indent=2)

    # Print the summary
    print(f"lint:guides-yml: {total_entries} entries, {total_files} file references")
    if missing_paths:
        print(f"lint:guides-yml: FAIL — {len(missing_paths)} missing path(s):")
        for m in missing_paths:
            print(f"  [{m['entry_index']}] {m['title']} -> {m['missing_path']}")
        print(f"lint:guides-yml: Report: {report_path}")
        if args.dry_run:
            return 0
        return 1
    else:
        print(f"lint:guides-yml: All {total_entries} guides have valid paths")
        print(f"lint:guides-yml: Report: {report_path}")
        return 0


if __name__ == "__main__":
    sys.exit(main())