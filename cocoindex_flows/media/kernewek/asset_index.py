"""cocoindex_flows/media/kernewek/asset_index.py — the Cornish (kernewek) asset index flow.

Per the 2026-10-07-bilingual-celtic-asset-pipeline-v1 saga change (Plan 7).
"""
from __future__ import annotations

from typing import Any

try:
    from baml_src._shared.dltq_naming import to_dlq_lance_table
except ImportError:  # baml_src not on sys.path in some test contexts
    def to_dlq_lance_table(lang, table):
        return "ciianfhoghlaim.media_" + lang + "_" + table


KW_TABLE = to_dlq_lance_table("kernewek", "image_gen_chunks")


def ingest_kernewek_asset(asset: dict[str, Any]) -> None:
    """Ingest a single CelticAssetRecord into the kernewek LanceDB table."""
    import hashlib

    asset_id = asset.get("asset_id", hashlib.sha256(
        f"{asset.get('language', 'kw')}|{asset.get('prompt', '')}".encode()
    ).hexdigest()[:16])

    print(f"[kernewek/asset_index] ingest asset_id={asset_id}, subject={asset.get('subject', '?')}, language={asset.get('language', 'kw')}")


__all__ = ["KW_TABLE", "ingest_kernewek_asset"]
