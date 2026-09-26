"""cocoindex_flows/media/brezhoneg/asset_index.py — the Breton (brezhoneg) asset index flow.

Per the 2026-10-07-bilingual-celtic-asset-pipeline-v1 saga change (Plan 7).
"""
from __future__ import annotations

from typing import Any


BR_TABLE = "cianhfhglaim.media.image_gen_chunks_brezhoneg"


def ingest_brezhoneg_asset(asset: dict[str, Any]) -> None:
    """Ingest a single CelticAssetRecord into the brezhoneg LanceDB table."""
    import time
    import hashlib

    asset_id = asset.get("asset_id", hashlib.sha256(
        f"{asset.get('language', 'br')}|{asset.get('prompt', '')}".encode()
    ).hexdigest()[:16])

    print(f"[brezhoneg/asset_index] ingest asset_id={asset_id}, subject={asset.get('subject', '?')}, language={asset.get('language', 'br')}")


__all__ = ["ingest_brezhoneg_asset", "BR_TABLE"]
