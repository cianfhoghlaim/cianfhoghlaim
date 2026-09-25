"""agents/adk/tools/retro_pattern_extractor.py — the BAML → typed pattern tool.

Per the 2026-10-03-cocoindex-retro-gameplay-v1 saga change (Plan 3 of
openspec/plans/2026-10-01-convergence-saga-v1.md).

Wraps the BAML ``ExtractGameplayPattern`` function (in
``baml_src/media/extract_design_pattern.baml``) + the SAM3 sprite
segmentation glue (against the ``sam3-server`` stack).

This is the second tool in the retro_pattern_agent's toolchain:
1. capture_screenshot (from retro_capture.py)
2. sam3_segment (in this module) — segment the screenshot
3. extract_retro_pattern (in this module) — BAML call → typed RetroGameplayPattern
"""
from __future__ import annotations

import asyncio
import base64
import json
import logging
import os
import urllib.request
import urllib.error
from typing import Any

logger = logging.getLogger(__name__)


# The SAM3 server stack (deferred to Plan 5 bring-up)
SAM3_API = os.environ.get("SAM3_API", "http://sam3-server:8080")


async def sam3_segment(
    screenshot_path: str,
    classes: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Send a screenshot to the SAM3 server for sprite segmentation.

    Args:
        screenshot_path: Local path to the PNG
        classes: Optional list of class hints (e.g. ["boon_icon", "ui_button", "character_portrait"])

    Returns:
        List of segments ``{bbox: [x, y, w, h], class: str, score: float}``.
        Falls back to a single full-image bounding box when the SAM3
        stack is unreachable (offline dev mode).
    """
    try:
        with open(screenshot_path, "rb") as fh:
            png_bytes = fh.read()
        png_b64 = base64.b64encode(png_bytes).decode()

        body = {"screenshot_b64": png_b64, "classes": classes or []}
        req = urllib.request.Request(
            f"{SAM3_API}/v1/segment",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            segments = json.loads(resp.read())
        logger.info("sam3_segment: %d segments for %s", len(segments), screenshot_path)
        return segments
    except (urllib.error.URLError, ConnectionError, TimeoutError, FileNotFoundError) as exc:
        logger.warning("sam3_segment fallback: %s — returning single full-image bbox", exc)
        return [{"bbox": [0, 0, 320, 240], "class": "full_image", "score": 1.0, "stub": True}]


async def extract_retro_pattern(
    *,
    screenshot_path: str,
    game_id: str,
    platform: str,
    rom_sha256: str,
    scene_id: str = "title",
    scene_hint: str | None = None,
    save_state_path: str | None = None,
    macro_script_path: str | None = None,
) -> dict[str, Any]:
    """Run the BAML ExtractGameplayPattern on a screenshot.

    Reads the PNG → base64-encodes → calls the BAML client → returns the
    typed RetroGameplayPattern record (which feeds into the
    retro_design_embedding CocoIndex flow).

    When the BAML client isn't generated (per the standard
    ``baml_client not generated`` warning), this falls back to a stub
    pattern with deterministic placeholder fields.
    """
    try:
        from baml_client.baml_client.sync_client import b  # type: ignore[import-not-found]
    except ImportError:
        logger.warning("baml_client not generated — returning stub pattern")
        return _stub_pattern(screenshot_path, game_id, platform, rom_sha256, scene_id)

    try:
        with open(screenshot_path, "rb") as fh:
            png_b64 = base64.b64encode(fh.read()).decode()

        # The BAML function signature is in baml_src/media/extract_design_pattern.baml
        pattern = b.ExtractGameplayPattern(
            screenshot_b64=png_b64,
            session_log=None,
            game_id=game_id,
            scene_hint=scene_hint or scene_id,
            platform=platform,
            rom_sha256=rom_sha256,
            save_state_path=save_state_path,
            macro_script=macro_script_path,
        )
        # pattern is a RetroGameplayPattern Pydantic model → dict
        return pattern.model_dump()
    except Exception as exc:
        logger.warning("BAML ExtractGameplayPattern failed: %s — falling back to stub", exc)
        return _stub_pattern(screenshot_path, game_id, platform, rom_sha256, scene_id)


def _stub_pattern(
    screenshot_path: str, game_id: str, platform: str, rom_sha256: str, scene_id: str
) -> dict[str, Any]:
    """The stub pattern when the BAML client isn't generated yet."""
    from datetime import datetime, UTC
    import hashlib

    # Deterministic stub based on the screenshot content (so the
    # pattern_id is reproducible for the same screenshot)
    try:
        with open(screenshot_path, "rb") as fh:
            screenshot_sha256 = hashlib.sha256(fh.read()).hexdigest()
    except FileNotFoundError:
        screenshot_sha256 = "no_screenshot"

    return {
        "pattern_id": hashlib.sha256(
            f"{platform}|{game_id}|{scene_id}|{screenshot_sha256}".encode()
        ).hexdigest()[:16],
        "game_id": game_id,
        "scene_id": scene_id,
        "platform": platform,
        "title": f"Stub pattern for {game_id} {scene_id}",
        "source": {
            "platform": platform,
            "game_id": game_id,
            "rom_sha256": rom_sha256,
            "screenshot_sha256": screenshot_sha256,
            "save_state_path": "",
            "macro_script": "",
            "captured_at": datetime.now(UTC).isoformat(),
        },
        "genre": {"rogue_like": "", "mmorpg": "", "jrpg": "", "monster_tamer": "",
                  "puzzle": "", "language_learning": "", "match_three": "", "other": "stub"},
        "power_events": [],
        "visual_grammar": {},
        "palette": {
            "dominant_hex": [], "accent_hex": [], "emissive_hex": [],
            "per_element_palette": {}, "contrast_strategy": "",
        },
        "design_notes": "(stub: baml_client not generated)",
        "ingested_at": datetime.now(UTC).isoformat(),
    }


__all__ = [
    "sam3_segment",
    "extract_retro_pattern",
]
