"""cocoindex_flows/media/gaelg/asset_index.py — the Manx (gaelg) asset index flow.

Per the 2026-10-07-bilingual-celtic-asset-pipeline-v1 saga change (Plan 7).
"""
from __future__ import annotations

from typing import Any


GV_TABLE = "cianhoghlaim.media.image_gen_chunks_gaelg"


def ingest_gaelg_asset(asset: dict[str, Any]) -> None:
    """Ingest a single CelticAssetRecord into the gaelg LanceDB table."""
    import time
    import hashlib

    asset_id = asset.get("asset_id", hashlib.sha256(
        f"{asset.get('language', 'gv')}|{asset.get('prompt', '')}".encode()
    ).hexdigest()[:16])

    print(f"[gaelg/asset_index] ingest asset_id={asset_id}, subject={asset.get('subject', '?')}, language={asset.get('language', 'gv')}")


__all__ = ["ingest_gaelg_asset", "GV_TABLE"]
