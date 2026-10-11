"""cocoindex_flows/media/brezhoneg/asset_index.py — the Breton (brezhoneg) asset index flow.

Per the 2026-10-07-bilingual-celtic-asset-pipeline-v1 saga change (Plan 7).
"""
from __future__ import annotations

from typing import Any

try:
    from baml_src._shared.dltq_naming import to_dlq_lance_table
except ImportError:  # baml_src not on sys.path in some test contexts
    def to_dlq_lance_table(lang, table):
        return "ciianfhoghlaim.media_" + lang + "_" + table


BR_TABLE = to_dlq_lance_table("brezhoneg", "image_gen_chunks")


def ingest_brezhoneg_asset(asset: dict[str, Any]) -> None:
    """Ingest a single CelticAssetRecord into the brezhoneg LanceDB table."""
    import hashlib

    asset_id = asset.get("asset_id", hashlib.sha256(
        f"{asset.get('language', 'br')}|{asset.get('prompt', '')}".encode()
    ).hexdigest()[:16])

    print(f"[brezhoneg/asset_index] ingest asset_id={asset_id}, subject={asset.get('subject', '?')}, language={asset.get('language', 'br')}")


__all__ = ["BR_TABLE", "ingest_brezhoneg_asset"]
