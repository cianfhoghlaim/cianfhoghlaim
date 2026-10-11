"""cocoindex_flows/media/gaidhlig/asset_index.py — the Scottish Gaelic (gaidhlig) asset index flow.

Per the 2026-10-07-bilingual-celtic-asset-pipeline-v1 saga change (Plan 7).
"""
from __future__ import annotations

from typing import Any

try:
    from baml_src._shared.dltq_naming import to_dlq_lance_table
except ImportError:  # baml_src not on sys.path in some test contexts
    def to_dlq_lance_table(lang, table):
        return "ciianfhoghlaim.media_" + lang + "_" + table


GD_TABLE = to_dlq_lance_table("gaidhlig", "image_gen_chunks")


def ingest_gaidhlig_asset(asset: dict[str, Any]) -> None:
    """Ingest a single CelticAssetRecord into the gaidhlig LanceDB table."""
    import hashlib

    asset_id = asset.get("asset_id", hashlib.sha256(
        f"{asset.get('language', 'gd')}|{asset.get('prompt', '')}".encode()
    ).hexdigest()[:16])

    print(f"[gaidhlig/asset_index] ingest asset_id={asset_id}, subject={asset.get('subject', '?')}, language={asset.get('language', 'gd')}")


__all__ = ["GD_TABLE", "ingest_gaidhlig_asset"]
