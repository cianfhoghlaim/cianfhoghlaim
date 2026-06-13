#!/usr/bin/env python3
"""
pair-walk.py — Recursively walk a docs/ directory, pairing 1-4 .md files
at a time and presenting them to the user for merge/keep decisions.

Uses ccc (semantic search) and Cognee (knowledge graph) to score similarity
and surface overlap. The user makes every merge decision.

Usage:
    uv run scripts/pair-walk.py docs/02-data-platform/
    uv run scripts/pair-walk.py docs/02-data-platform/ --max-files 4
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

COGNEE_URL = "http://localhost:8100"
COGNEE_DATASET = "pair-walk-context"


def ccc_search(query: str, paths: list[str] | None = None, limit: int = 5) -> list[dict[str, Any]]:
    """Run ccc search and return parsed text-format results.
    ccc doesn't have --json; we parse its human output."""
    cmd = ["ccc", "search", query, "--limit", str(limit)]
    if paths:
        cmd.extend(["--path", *paths])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            return []
        # Parse human format:
        # --- Result 1 (score: 0.686) ---
        # File: <path>:<lines> [<lang>]
        # <content...>
        results: list[dict[str, Any]] = []
        for m in re.finditer(
            r"--- Result (\d+) \(score: ([\d.]+)\) ---\nFile: ([^\n]+)\n",
            result.stdout,
        ):
            idx, score, fileinfo = m.groups()
            # File info: "path:start-end [lang]"
            file_match = re.match(r"([^:]+):(\d+)-(\d+)\s*\[([^\]]+)\]", fileinfo)
            if file_match:
                path, start, end, lang = file_match.groups()
                results.append(
                    {
                        "rank": int(idx),
                        "score": float(score),
                        "file": path,
                        "start": int(start),
                        "end": int(end),
                        "lang": lang,
                    }
                )
        return results
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []


def ccc_describe(path: str) -> str:
    """Run ccc describe on a file."""
    cmd = ["ccc", "describe", path]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return ""


def ccc_pair_similarity(file_a: Path, file_b: Path) -> float:
    """Score how similar two files are by running ccc search with each
    file's first heading as the query and looking for the other file."""
    title_a = extract_title(file_a) or file_a.stem
    title_b = extract_title(file_b) or file_b.stem
    # Query A → does B come up?
    results_ab = ccc_search(title_a, paths=None, limit=10)
    score_ab = max(
        (float(r["score"]) for r in results_ab if file_b.name in r["file"]),
        default=0.0,
    )
    # Query B → does A come up?
    results_ba = ccc_search(title_b, paths=None, limit=10)
    score_ba = max(
        (float(r["score"]) for r in results_ba if file_a.name in r["file"]),
        default=0.0,
    )
    return max(score_ab, score_ba)


def extract_title(path: Path) -> str | None:
    """Extract H1 title from a .md file."""
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    # First H1
    m = re.search(r"^#\s+(.+?)$", content, re.MULTILINE)
    if m:
        return m.group(1).strip()
    return None


def extract_frontmatter(path: Path) -> dict[str, str]:
    """Extract simple YAML frontmatter."""
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}
    if not content.startswith("---"):
        return {}
    end = content.find("\n---", 3)
    if end == -1:
        return {}
    fm: dict[str, str] = {}
    for line in content[3:end].splitlines():
        if ":" in line and not line.startswith(" "):
            key, _, val = line.partition(":")
            fm[key.strip()] = val.strip().strip("'\"")
    return fm


def extract_h2_sections(path: Path) -> list[str]:
    """Extract H2 section titles."""
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    return [m.group(1).strip() for m in re.finditer(r"^##\s+(.+?)$", content, re.MULTILINE)]


def file_summary(path: Path) -> dict[str, Any]:
    """Build a one-screen summary of a .md file."""
    title = extract_title(path) or path.stem
    fm = extract_frontmatter(path)
    sections = extract_h2_sections(path)
    size = path.stat().st_size
    return {
        "path": str(path),
        "title": title,
        "frontmatter": fm,
        "h2_sections": sections[:20],
        "size_kb": round(size / 1024, 1),
    }


def present_pair(files: list[Path]) -> None:
    """Pretty-print a 1-4 file pairing for the user."""
    print("\n" + "=" * 70)
    print(f"PAIRING: {len(files)} files")
    print("=" * 70)
    for i, f in enumerate(files, 1):
        s = file_summary(f)
        print(f"\n[{i}] {s['path']}")
        print(f"    Title:    {s['title']}")
        print(f"    Size:     {s['size_kb']} KB")
        if s["frontmatter"]:
            for k, v in list(s["frontmatter"].items())[:4]:
                print(f"    {k:11s} {v[:60]}")
        if s["h2_sections"]:
            print(f"    Sections ({len(s['h2_sections'])}):")
            for sec in s["h2_sections"][:10]:
                print(f"      - {sec}")
            if len(s["h2_sections"]) > 10:
                print(f"      ... +{len(s['h2_sections']) - 10} more")
    # Pairwise similarity
    if len(files) >= 2:
        print("\nSimilarity (ccc):")
        for i in range(len(files)):
            for j in range(i + 1, len(files)):
                sim = ccc_pair_similarity(files[i], files[j])
                print(f"  [{i+1}] <-> [{j+1}]: {sim:.3f}")


def get_user_decision(files: list[Path]) -> str:
    """Prompt the user for a decision on this pairing."""
    print("\nDecision?")
    print("  [m] merge  — write a merged file in this dir, keep originals as .superseded")
    print("  [k] keep   — leave as separate files")
    print("  [e] expand — show me full contents of one file (you'll be asked which)")
    print("  [d] deeper — run deeper ccc+cognee analysis (slow)")
    print("  [s] skip   — skip this pairing, move to next")
    print("  [q] quit   — stop the walk")
    while True:
        choice = input("\n> ").strip().lower()
        if choice in ("m", "k", "e", "d", "s", "q"):
            return choice


def list_md_files(directory: Path, recursive: bool = True) -> list[Path]:
    """List all .md files in a directory."""
    if recursive:
        return sorted(p for p in directory.rglob("*.md") if p.is_file())
    return sorted(p for p in directory.glob("*.md") if p.is_file())


def cluster_by_similarity(files: list[Path]) -> list[list[Path]]:
    """Cluster files using ccc similarity. Files with sim > 0.6 to any other
    file in the cluster stay together; isolates go in their own cluster."""
    if not files:
        return []
    clusters: list[list[Path]] = []
    for f in files:
        placed = False
        for cluster in clusters:
            # Check similarity to cluster representative
            for member in cluster[:1]:
                sim = ccc_pair_similarity(f, member)
                if sim > 0.6:
                    cluster.append(f)
                    placed = True
                    break
            if placed:
                break
        if not placed:
            clusters.append([f])
    return clusters


def walk_directory(directory: Path, max_files: int) -> int:
    """Walk the directory, presenting pairings to the user."""
    files = list_md_files(directory)
    print(f"\nFound {len(files)} .md files in {directory}")
    if not files:
        return 0

    # Cluster
    clusters = cluster_by_similarity(files)
    print(f"After clustering: {len(clusters)} clusters")
    for i, c in enumerate(clusters):
        print(f"  [{i+1}] {len(c)} files: {c[0].name}{' ...' if len(c) > 1 else ''}")

    decisions = 0
    for cluster in clusters:
        if len(cluster) > max_files:
            # Recurse: split cluster
            print(f"\n[Cluster of {len(cluster)} files] — recursing into sub-pairs")
            # Pair within cluster
            for i in range(0, len(cluster), 2):
                pair = cluster[i : i + 2]
                if len(pair) == 1:
                    print(f"\n  Single: {pair[0].name} — leaving alone")
                    continue
                present_pair(pair)
                decision = get_user_decision(pair)
                decisions += 1
                if decision == "q":
                    return decisions
        else:
            present_pair(cluster)
            decision = get_user_decision(cluster)
            decisions += 1
            if decision == "q":
                return decisions
    return decisions


def main() -> int:
    parser = argparse.ArgumentParser(description="Pair-walk a docs/ directory")
    parser.add_argument("directory", help="Directory to walk (e.g., docs/02-data-platform/)")
    parser.add_argument("--max-files", type=int, default=4, help="Max files per pairing (default 4)")
    parser.add_argument("--recursive", action="store_true", help="Recurse into subdirs")
    args = parser.parse_args()
    directory = Path(args.directory)
    if not directory.exists():
        print(f"ERROR: {directory} does not exist")
        return 1
    decisions = walk_directory(directory, args.max_files)
    print(f"\nWalk complete. {decisions} decisions made.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
