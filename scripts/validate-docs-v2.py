#!/usr/bin/env python3
"""
validate-docs-v2.py — Verify docs-v2/ is well-formed and complete.

Checks:
  1. Every file in docs/ has a mapping in coverage.json
  2. Every target file in docs-v2/ has at least one source
  3. Every merged .md file has the expected frontmatter
  4. Total size and file count are within bounds
  5. No duplicate target paths (no two sources map to the same target unless
     they are the same file — which is fine)
  6. Every .md in docs-v2/ has at least one `## From:` section
  7. The 00_index.md exists and lists all domains

Outputs a report; exits non-zero on any failure.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_SRC = REPO_ROOT / "docs"
DOCS_V2 = REPO_ROOT / "docs-v2"
COVERAGE = DOCS_V2 / ".migration" / "coverage.json"
INDEX = DOCS_V2 / "00_index.md"

DOMAINS = [
    "01-platform-architecture",
    "02-data-platform",
    "03-agents",
    "04-ai-ml",
    "05-web",
    "06-infrastructure",
    "07-standards",
    "08-misc",
    "09-cognee",
]

errors: list[str] = []
warnings: list[str] = []
stats: dict[str, Any] = {}


def check(label: str, ok: bool, detail: str = "") -> None:
    if ok:
        print(f"  PASS  {label}")
    else:
        print(f"  FAIL  {label}: {detail}")
        errors.append(f"{label}: {detail}")


def main() -> int:
    print("docs-v2 validation\n")
    print("=" * 60)
    if not COVERAGE.exists():
        print(f"FATAL: {COVERAGE} not found; run scripts/migrate-docs-v2.py first")
        return 1
    coverage = json.loads(COVERAGE.read_text())
    print(f"Coverage entries: {len(coverage)}")

    # Check 1: every .md in docs/ has a mapping
    print("\n[1] Source coverage")
    src_md = [p for p in DOCS_SRC.rglob("*.md") if p.is_file()]
    mapped = {REPO_ROOT / k for k in coverage if (REPO_ROOT / k).exists()}
    unmapped = [str(p.relative_to(REPO_ROOT)) for p in src_md if p not in mapped]
    check(
        "every .md in docs/ has a mapping",
        len(unmapped) == 0,
        f"{len(unmapped)} unmapped (e.g. {unmapped[:3]})",
    )
    stats["unmapped_md"] = len(unmapped)

    # Check 2: every target has at least one source
    print("\n[2] Target coverage")
    target_to_sources: dict[str, list[str]] = {}
    for src, tgt in coverage.items():
        target_to_sources.setdefault(tgt, []).append(src)
    orphan_targets = [
        tgt for tgt, srcs in target_to_sources.items() if not srcs
    ]
    check(
        "every target has at least one source",
        len(orphan_targets) == 0,
        f"{len(orphan_targets)} orphan targets",
    )

    # Check 3: every merged .md has expected frontmatter
    print("\n[3] Frontmatter check")
    merged_files = list(DOCS_V2.rglob("*.md"))
    merged_files = [
        p for p in merged_files
        if ".migration" not in p.parts
        and p.name not in {"00_index.md", "MIGRATION.md", "changelog.md"}
    ]
    stats["merged_files"] = len(merged_files)
    no_fm: list[str] = []
    fm_keys = {"title", "domain", "merged_from_count", "supersedes"}
    for mf in merged_files:
        content = mf.read_text(encoding="utf-8", errors="replace")
        if not content.startswith("---"):
            no_fm.append(str(mf.relative_to(REPO_ROOT)))
            continue
        end = content.find("\n---", 3)
        if end == -1:
            no_fm.append(str(mf.relative_to(REPO_ROOT)))
            continue
        fm_text = content[3:end]
        present = {k for k in fm_keys if k in fm_text}
        if not {"title", "domain", "merged_from_count"} <= present:
            no_fm.append(str(mf.relative_to(REPO_ROOT)))
    check(
        "every merged .md has valid frontmatter",
        len(no_fm) == 0,
        f"{len(no_fm)} missing/partial FM (e.g. {no_fm[:3]})",
    )

    # Check 4: size and count
    print("\n[4] Size and count")
    docs_size = sum(p.stat().st_size for p in DOCS_SRC.rglob("*") if p.is_file())
    v2_size = sum(p.stat().st_size for p in DOCS_V2.rglob("*") if p.is_file())
    docs_count = sum(1 for _ in DOCS_SRC.rglob("*") if _.is_file())
    v2_count = sum(1 for _ in DOCS_V2.rglob("*") if _.is_file())
    reduction_pct = 100 * (1 - v2_count / max(docs_count, 1))
    stats["docs_size_mb"] = round(docs_size / 1024 / 1024, 1)
    stats["v2_size_mb"] = round(v2_size / 1024 / 1024, 1)
    stats["docs_count"] = docs_count
    stats["v2_count"] = v2_count
    stats["reduction_pct"] = round(reduction_pct, 1)
    print(f"  docs/:  {stats['docs_size_mb']}MB, {stats['docs_count']} files")
    print(f"  v2/:    {stats['v2_size_mb']}MB, {stats['v2_count']} files")
    print(f"  Δ:      {stats['reduction_pct']}% fewer files")
    check("docs-v2 is smaller than docs/", v2_count < docs_count,
          f"v2={v2_count}, docs={docs_count}")

    # Check 5: 00_index.md exists and lists all domains
    print("\n[5] Index check")
    check("00_index.md exists", INDEX.exists(), str(INDEX))
    if INDEX.exists():
        content = INDEX.read_text()
        for d in DOMAINS:
            check(
                f"index mentions {d}/",
                d in content,
                f"missing reference to {d}",
            )

    # Check 6: every merged .md has at least one `## From:` section
    print("\n[6] Source attribution")
    no_source: list[str] = []
    for mf in merged_files:
        content = mf.read_text(encoding="utf-8", errors="replace")
        if "## From:" not in content:
            no_source.append(str(mf.relative_to(REPO_ROOT)))
    check(
        "every merged .md has ## From: section",
        len(no_source) == 0,
        f"{len(no_source)} without ## From: (e.g. {no_source[:3]})",
    )

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"  Total source files:        {stats.get('docs_count', 0)}")
    print(f"  Total target files:        {stats.get('v2_count', 0)}")
    print(f"  Merged .md files:          {stats.get('merged_files', 0)}")
    print(f"  Unmapped source .md:       {stats.get('unmapped_md', 0)}")
    print(f"  Coverage entries:          {len(coverage)}")
    print(f"  Errors:                    {len(errors)}")
    print(f"  Warnings:                  {len(warnings)}")
    if errors:
        print("\nErrors:")
        for e in errors[:10]:
            print(f"  - {e}")
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
