# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "lancedb>=0.34.0",
#     "sentence-transformers>=5.0.0",
# ]
# ///
"""
Canonical v1 CLI for the CocoIndex Code (CCC) codebase index.

Replaces the broken `bun run ccc:v1:search` shell-escape incantation in
the root `package.json` (which used a bash-style `${1:-}` inside a
double-quoted Python `-c` argument that bun's argument parser choked on).

This script:
- Uses the canonical v4 module path `cianfhoghlaim.cocoindex.codebase_indexing`
- Falls back to a direct LanceDB query at `.cocoindex_code/lancedb/codebase_chunks.lance`
  if the module import fails (which is the common case at 2026-07-06
  because `chunking.languages` is a missing sub-module in the v4 tree)
- Emits JSON on stdout: `[{"file_path": ..., "line_no": ..., "snippet": ..., "relevance": ...}]`
- Substring search by default (instant); set CCC_SEMANTIC=1 for BGE-M3 vector search

Usage:
    uv run python scripts/ccc_v1_search.py "<query>" [--limit N] [--semantic]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LANCEDB_PATH = REPO_ROOT / ".cocoindex_code" / "lancedb"


def _search_substring(query: str, limit: int) -> list[dict]:
    """Substring search via direct LanceDB query (fast, no model load)."""
    import lancedb

    db = lancedb.connect(str(LANCEDB_PATH))
    tables = db.list_tables()
    table_names = tables.tables if hasattr(tables, "tables") else tables
    if "codebase_chunks" not in table_names:
        return [{"error": "ccc_index_missing", "hint": "Run bun run ccc:v1:index first"}]
    tbl = db.open_table("codebase_chunks")

    df = tbl.to_pandas()
    mask = df["chunk_text"].str.contains(query, case=False, na=False, regex=False)
    hits = df[mask].head(limit)
    return [
        {
            "file_path": str(r["path"]),
            "line_no": int(r["chunk_start"]),
            "snippet": str(r["chunk_text"]).splitlines()[0][:500] if r["chunk_text"] else "",
            "relevance": round(1.0 - (i * 0.05), 3),
        }
        for i, (_, r) in enumerate(hits.iterrows())
    ]


def _search_semantic(query: str, limit: int) -> list[dict]:
    """Semantic search via BGE-M3 (slow first call due to model load)."""
    import lancedb
    import numpy as np
    from sentence_transformers import SentenceTransformer

    db = lancedb.connect(str(LANCEDB_PATH))
    tbl = db.open_table("codebase_chunks")

    model = SentenceTransformer("BAAI/bge-m3", trust_remote_code=True)
    query_vec = model.encode([query])[0].astype(np.float32)
    results = tbl.search(query_vec).limit(limit * 3).to_list()
    return [
        {
            "file_path": r.get("path", ""),
            "line_no": int(r.get("chunk_start", 0)),
            "snippet": (r.get("chunk_text") or "").splitlines()[0][:500] if r.get("chunk_text") else "",
            "relevance": float(r.get("_distance", 1.0)),
        }
        for r in results
    ]


def _search_module(query: str, limit: int) -> list[dict] | None:
    """Try the canonical v4 module first; return None on import failure."""
    try:
        import asyncio

        from cianfhoghlaim.cocoindex.codebase_indexing import search_codebase

        rows = asyncio.run(search_codebase(query))
        return [
            {
                "file_path": r.get("path", ""),
                "line_no": int(r.get("chunk_start", 0)),
                "snippet": (r.get("chunk_text") or "").splitlines()[0][:500] if r.get("chunk_text") else "",
                "relevance": float(r.get("score", 0)),
            }
            for r in rows[:limit]
        ]
    except Exception as exc:
        print(f"# module_import_failed: {exc}", file=sys.stderr)
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description="v1 CCC search")
    parser.add_argument("query", help="search query")
    parser.add_argument("--limit", type=int, default=10, help="max results")
    parser.add_argument("--semantic", action="store_true", help="use BGE-M3 vector search")
    args = parser.parse_args()

    # 1. Try the canonical module first
    results = _search_module(args.query, args.limit)

    # 2. Fall back to direct LanceDB substring search
    if results is None:
        if args.semantic or os.environ.get("CCC_SEMANTIC", "").lower() in {"1", "true"}:
            results = _search_semantic(args.query, args.limit)
        else:
            results = _search_substring(args.query, args.limit)

    json.dump(results, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
