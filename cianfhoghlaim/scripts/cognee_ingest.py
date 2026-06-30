#!/usr/bin/env python3
"""Ingest markdown files into Cognee from a directory tree.

Usage:
    uv run python oideachais/scripts/cognee_ingest.py <directory> <dataset_name>
Example:
    uv run python oideachais/scripts/cognee_ingest.py docs/agents docs-agents
"""

import asyncio
import hashlib
import sys
from pathlib import Path

import cognee


def file_id(filepath: Path, root: Path) -> str:
    rel = str(filepath.relative_to(root))
    return hashlib.md5(rel.encode()).hexdigest()[:12]


async def ingest_directory(directory: str, dataset_name: str):
    root = Path(directory).resolve()
    if not root.is_dir():
        print(f"ERROR: {root} is not a directory")
        sys.exit(1)

    files = sorted(root.rglob("*.md"))
    total = len(files)
    print(f"Ingesting {total} files from {root} -> dataset '{dataset_name}'")
    print("LLM: deepseek-v4-pro | Graph: Neo4j | Vector: LanceDB")
    print("-" * 60)

    for i, filepath in enumerate(files, 1):
        try:
            content = filepath.read_text()
            if len(content) < 10:  # Skip tiny files
                continue
        except Exception as e:
            print(f"  SKIP {filepath.name}: {e}")
            continue

        file_id(filepath, root)
        # Use the full file path as a unique identifier
        str(filepath.relative_to(root))

        await cognee.add(content, dataset_name=dataset_name)

        if i % 50 == 0 or i == total:
            pct = i * 100 // total
            bar = "#" * (pct // 5) + "-" * (20 - pct // 5)
            print(f"  [{bar}] {i}/{total} ({pct}%)")

    print(f"DONE: {total} files added to dataset '{dataset_name}'")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python cognee_ingest.py <directory> <dataset_name>")
        sys.exit(1)
    asyncio.run(ingest_directory(sys.argv[1], sys.argv[2]))
