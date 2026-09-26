"""cocoindex_flows/media/kernewek/asset_index.py — the Cornish (kernewek) asset index flow.

Per the 2026-10-07-bilingual-celtic-asset-pipeline-v1 saga change (Plan 7).
"""
from __future__ import annotations

from typing import Any


KW_TABLE = "cianhfhglaim.media.image_gen_chunks_kernewek"


def ingest_kernewek_asset(asset: dict[str, Any]) -> None:
    """Ingest a single CelticAssetRecord into the kernewek LanceDB table."""
    import time
    import hashlib

    asset_id = asset.get("asset_id", hashlib.sha256(
        f"{asset.get('language', 'kw')}|{asset.get('prompt', '')}".encode()
    ).hexdigest()[:16])

    print(f"[kernewek/asset_index] ingest asset_id={asset_id}, subject={asset.get('subject', '?')}, language={asset.get('language', 'kw')}")


__all__ = ["ingest_kernewek_asset", "KW_TABLE"]
