#!/usr/bin/env python3
"""
gen-per-domain-manifests.py — Generate per-domain manifest artifacts.

For each of the 9 canonical domains, emit:
  docs-v2/.migration/manifests/<NN-domain>.json
    - topic → [source file paths]
    - file_count, total_size_bytes, source_count

These are committed to git so the per-domain commit history has substance.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_V2 = REPO_ROOT / "docs-v2"
MANIFESTS_DIR = DOCS_V2 / ".migration" / "manifests"
COVERAGE = DOCS_V2 / ".migration" / "coverage.json"

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
    "10-loose-files",
    "11-scripts",
    "12-configs",
    "13-images",
]


def main() -> int:
    if not COVERAGE.exists():
        print(f"ERROR: {COVERAGE} not found; run migrate-docs-v2.py first")
        return 1
    coverage = json.loads(COVERAGE.read_text())
    MANIFESTS_DIR.mkdir(parents=True, exist_ok=True)

    # Invert mapping: target → [sources]
    target_to_sources: dict[str, list[str]] = {}
    for src, tgt in coverage.items():
        target_to_sources.setdefault(tgt, []).append(src)

    for d in DOMAINS:
        prefix = f"docs-v2/{d}/"
        targets = {t: srcs for t, srcs in target_to_sources.items() if t.startswith(prefix)}
        # Group by topic
        topics: dict[str, dict] = {}
        for tgt, srcs in targets.items():
            # target format: docs-v2/<domain>/<topic>/<topic>.md
            parts = Path(tgt).relative_to(f"docs-v2/{d}").parts
            topic = parts[0] if parts else "root"
            if topic not in topics:
                topics[topic] = {"files": [], "source_count": 0}
            tgt_path = DOCS_V2 / d / Path(tgt).relative_to(f"docs-v2/{d}")
            if tgt_path.exists():
                topics[topic]["files"].append(tgt_path.name)
                size = tgt_path.stat().st_size
                topics[topic]["size_bytes"] = topics[topic].get("size_bytes", 0) + size
            topics[topic]["source_count"] += len(srcs)
            topics[topic]["sources"] = topics[topic].get("sources", []) + srcs

        manifest = {
            "domain": d,
            "target_files": sum(1 for t in targets if not t.endswith("/")),
            "source_files": sum(len(srcs) for srcs in targets.values()),
            "topics": topics,
        }
        out = MANIFESTS_DIR / f"{d}.json"
        out.write_text(json.dumps(manifest, indent=2, sort_keys=True))
        print(f"  {d}: {manifest['target_files']} targets, {manifest['source_files']} sources, {len(topics)} topics")

    return 0


if __name__ == "__main__":
    sys.exit(main())
