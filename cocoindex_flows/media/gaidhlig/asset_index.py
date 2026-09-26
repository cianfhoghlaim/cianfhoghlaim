"""cocoindex_flows/media/gaidhlig/asset_index.py — the Scottish Gaelic (gaidhlig) asset index flow.

Per the 2026-10-07-bilingual-celtic-asset-pipeline-v1 saga change (Plan 7).
"""
from __future__ import annotations

from typing import Any


GD_TABLE = "cianhoghlaim.media.image_gen_chunks_gaidhlig"


def ingest_gaidhlig_asset(asset: dict[str, Any]) -> None:
    """Ingest a single CelticAssetRecord into the gaidhlig LanceDB table."""
    import time
    import hashlib

    asset_id = asset.get("asset_id", hashlib.sha256(
        f"{asset.get('language', 'gd')}|{asset.get('prompt', '')}".encode()
    ).hexdigest()[:16])

    print(f"[gaidhlig/asset_index] ingest asset_id={asset_id}, subject={asset.get('subject', '?')}, language={asset.get('language', 'gd')}")


__all__ = ["ingest_gaidhlig_asset", "GD_TABLE"]
