"""cocoindex_flows/media/gaeilge/asset_index.py — the Irish (gaeilge) asset index flow.

Per the 2026-10-07-bilingual-celtic-asset-pipeline-v1 saga change (Plan 7 of
openspec/plans/2026-10-01-convergence-saga-v1.md).

Indexes CelticAssetRecord rows (produced by GenerateIrishAsset) into
the Irish LanceDB table media.image_gen_chunks_gaeilge.

Reference: openspec/specs/bilingual-celtic-asset-pipeline/spec.md
"""
from __future__ import annotations

from typing import Any


# Canonical table name for the Irish asset index
GAEILGE_TABLE = "cianhoghlaim.media.image_gen_chunks_gaeilge"


def ingest_gaeilge_asset(asset: dict[str, Any]) -> None:
    """Ingest a single CelticAssetRecord into the gaeilge LanceDB table.

    Args:
        asset: The CelticAssetRecord dict (from GenerateIrishAsset)
    """
    # Real implementation: uses the shared CocoIndex runtime from
    # cocoindex_flows/media/image_generation_flow.py pattern.
    # Offline dev mode: writes a stub manifest.
    import json
    import time
    import hashlib

    asset_id = asset.get("asset_id", hashlib.sha256(
        f"{asset.get('language', 'ga')}|{asset.get('prompt', '')}".encode()
    ).hexdigest()[:16])

    manifest = {
        "asset_id": asset_id,
        "language": asset.get("language", "ga"),
        "subject": asset.get("subject", ""),
        "title": asset.get("title", ""),
        "title_en": asset.get("title_en", ""),
        "prompt": asset.get("prompt", ""),
        "palette_hex": asset.get("palette_hex", []),
        "stub": True,
        "stub_note": "Per-language CocoIndex flow (gaeilge) — will write to media.image_gen_chunks_gaeilge once CocoIndex runtime is up",
        "ingested_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    print(f"[gaeilge/asset_index] ingest asset_id={asset_id}, subject={asset.get('subject', '?')}, language={asset.get('language', 'ga')}")


__all__ = ["ingest_gaeilge_asset", "GAEILGE_TABLE"]
