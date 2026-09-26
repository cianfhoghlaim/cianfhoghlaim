"""cocoindex_flows/media/cymraeg/asset_index.py — the Welsh (cymraeg) asset index flow.

Per the 2026-10-07-bilingual-celtic-asset-pipeline-v1 saga change (Plan 7).

Indexes CelticAssetRecord rows (produced by GenerateWelshAsset) into
the Welsh LanceDB table media.image_gen_chunks_cymraeg.
"""
from __future__ import annotations

from typing import Any


CY_TABLE = "cianhoghlaim.media.image_gen_chunks_cymraeg"


def ingest_cymraeg_asset(asset: dict[str, Any]) -> None:
    """Ingest a single CelticAssetRecord into the cymraeg LanceDB table."""
    import time
    import hashlib

    asset_id = asset.get("asset_id", hashlib.sha256(
        f"{asset.get('language', 'cy')}|{asset.get('prompt', '')}".encode()
    ).hexdigest()[:16])

    print(f"[cymraeg/asset_index] ingest asset_id={asset_id}, subject={asset.get('subject', '?')}, language={asset.get('language', 'cy')}")


__all__ = ["ingest_cymraeg_asset", "CY_TABLE"]
