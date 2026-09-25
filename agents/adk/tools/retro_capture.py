"""agents/adk/tools/retro_capture.py — the libretro + ludusavi screenshot wrapper.

Per the 2026-10-03-cocoindex-retro-gameplay-v1 saga change (Plan 3 of
openspec/plans/2026-10-01-convergence-saga-v1.md).

This module wraps the ``libretro-retroarch`` headless stack
(``http://libretro-retroarch:8080``) + the ``ludusavi`` save-state
manager. It exposes:

- ``capture_screenshot(platform, game_id, scene_type)`` — capture one PNG
- ``list_roms()`` — list the canonical retro_library entries
- ``restore_save_state(platform, game_id, save_state_path)`` — load a save state via ludusavi
- ``run_macro(macro_script_path)`` — run a deterministic libretro macro

When the libretro stack isn't running (offline dev mode), the functions
fall back to stub behaviour that returns deterministic placeholder PNGs +
deterministic save-state paths.

Reference:
    openspec/changes/2026-10-03-cocoindex-retro-gameplay-v1/specs/cocoindex-retro-gameplay/spec.md
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import time
import urllib.request
import urllib.error
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# The libretro-retroarch + ludusavi stacks (deferred to Plan 5 bring-up)
LIBRETRO_API = os.environ.get("LIBRETRO_API", "http://libretro-retroarch:8080")
LUDUSAVI_API = os.environ.get("LUDUSAVI_API", "http://ludusavi:8080")

# The canonical retro_library: 6 games across 5 platforms (per the spec).
# Sourced from openspec/specs/retro-game-design-catalogue/spec.md
RETRO_LIBRARY: list[dict[str, Any]] = [
    {"platform": "nes",     "game_id": "number_munchers",      "title": "Number Munchers",                          "year": 1990, "igdb_id": "4366",  "rom_sha256": "deadbeef0001"},
    {"platform": "appleii", "game_id": "oregon_trail",          "title": "The Oregon Trail",                         "year": 1971, "igdb_id": "4367",  "rom_sha256": "deadbeef0002"},
    {"platform": "dos",     "game_id": "carmen_sandiego",       "title": "Where in the World is Carmen Sandiego?",  "year": 1985, "igdb_id": "4368",  "rom_sha256": "deadbeef0003"},
    {"platform": "gb",      "game_id": "pokemon_red",           "title": "Pokémon Red",                              "year": 1996, "igdb_id": "4369",  "rom_sha256": "deadbeef0004"},
    {"platform": "gba",     "game_id": "golden_sun",            "title": "Golden Sun",                               "year": 2001, "igdb_id": "4370",  "rom_sha256": "deadbeef0005"},
    {"platform": "switch",  "game_id": "hades",                "title": "Hades",                                    "year": 2020, "igdb_id": "4371",  "rom_sha256": "deadbeef0006"},
]


@dataclass(frozen=True)
class ScreenshotResult:
    """A single captured screenshot."""
    platform: str
    game_id: str
    scene_id: str           # title | menu | gameplay | boss | minigame | end | ...
    scene_type: str         # same enum
    path: str               # local file path
    sha256: str             # PNG SHA-256
    duration_ms: int        # capture time
    stub: bool              # True if generated offline (no libretro)


def list_roms() -> list[dict[str, Any]]:
    """List the canonical retro_library entries.

    Returns:
        List of dicts with keys: platform, game_id, title, year, igdb_id, rom_sha256.
    """
    return list(RETRO_LIBRARY)


def _offline_png(width: int = 320, height: int = 240) -> bytes:
    """A 1x1 transparent PNG, used as the stub screenshot when libretro is unreachable."""
    return (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
        b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4"
        b"\x89\x00\x00\x00\rIDATx\x9cc\xfc\xcf\xc0P\x0f\x00\x05\x00\x01"
        b"\xe2&\x05[\x00\x00\x00\x00IEND\xaeB`\x82"
    )


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


async def capture_screenshot(
    platform: str,
    game_id: str,
    scene_id: str = "title",
    *,
    save_state_path: str | None = None,
    output_dir: str | Path | None = None,
) -> ScreenshotResult:
    """Capture a single screenshot from the libretro headless stack.

    Args:
        platform: NES | SNES | GB | GBA | Genesis | PS1 | DOS | AppleII | Switch
        game_id: The canonical retro_library game_id (e.g. "number_munchers")
        scene_id: title | menu | gameplay | boss | minigame | end | custom
        save_state_path: Optional ludusavi path to restore before capture
        output_dir: Where to write the PNG (defaults to stedding/ingest_queue/retro/)

    Returns:
        ScreenshotResult with path + sha256 + duration_ms + stub flag
    """
    t0 = time.monotonic()

    if output_dir is None:
        output_dir = Path(os.environ.get(
            "BI_EP_RETRO_SCREENSHOTS_ROOT",
            Path.cwd() / "stedding" / "ingest_queue" / "retro",
        ))
    output_dir = Path(output_dir) / platform / game_id
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{scene_id}.png"

    # 1. Restore the save state if provided (via ludusavi)
    if save_state_path:
        try:
            await restore_save_state(platform, game_id, save_state_path)
        except Exception as exc:
            logger.warning("restore_save_state failed: %s", exc)

    # 2. Try the real libretro headless stack
    try:
        url = f"{LIBRETRO_API}/v1/screenshot?platform={platform}&game_id={game_id}&scene={scene_id}"
        req = urllib.request.Request(url, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            png_bytes = resp.read()
        out_path.write_bytes(png_bytes)
        duration_ms = int((time.monotonic() - t0) * 1000)
        return ScreenshotResult(
            platform=platform,
            game_id=game_id,
            scene_id=scene_id,
            scene_type=scene_id,
            path=str(out_path),
            sha256=_sha256_bytes(png_bytes),
            duration_ms=duration_ms,
            stub=False,
        )
    except (urllib.error.URLError, ConnectionError, TimeoutError) as exc:
        logger.warning("libretro unreachable (%s) — falling back to offline stub PNG", exc)

    # 3. Offline fallback: write a 1x1 PNG + sidecar manifest
    png_bytes = _offline_png()
    out_path.write_bytes(png_bytes)
    duration_ms = int((time.monotonic() - t0) * 1000)
    manifest_path = out_path.with_suffix(".json")
    manifest_path.write_text(json.dumps({
        "platform": platform,
        "game_id": game_id,
        "scene_id": scene_id,
        "stub": True,
        "stub_note": "libretro headless stack unreachable; offline fallback PNG",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }, indent=2))
    return ScreenshotResult(
        platform=platform,
        game_id=game_id,
        scene_id=scene_id,
        scene_type=scene_id,
        path=str(out_path),
        sha256=_sha256_bytes(png_bytes),
        duration_ms=duration_ms,
        stub=True,
    )


async def restore_save_state(platform: str, game_id: str, save_state_path: str) -> dict[str, Any]:
    """Restore a save state via the ludusavi stack.

    Args:
        platform: The retro platform
        game_id: The canonical retro_library game_id
        save_state_path: The ludusavi-managed save state path

    Returns:
        Dict with `restored`, `ludusavi_response` keys
    """
    try:
        url = f"{LUDUSAVI_API}/v1/restore?platform={platform}&game_id={game_id}"
        req = urllib.request.Request(url, data=json.dumps({"save_state_path": save_state_path}).encode(), headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=15) as resp:
            return {"restored": True, "ludusavi_response": json.loads(resp.read())}
    except (urllib.error.URLError, ConnectionError, TimeoutError) as exc:
        logger.warning("ludusavi unreachable (%s) — falling back to no-op", exc)
        return {"restored": False, "stub": True, "stub_note": "ludusavi unreachable", "error": str(exc)}


async def run_macro(macro_script_path: str) -> dict[str, Any]:
    """Run a deterministic libretro macro (Python file that presses buttons in sequence)."""
    try:
        url = f"{LIBRETRO_API}/v1/macro"
        req = urllib.request.Request(url, data=json.dumps({"macro_script_path": macro_script_path}).encode(), headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=60) as resp:
            return {"ran": True, "macro_response": json.loads(resp.read())}
    except (urllib.error.URLError, ConnectionError, TimeoutError) as exc:
        logger.warning("libretro unreachable (%s) — falling back to no-op", exc)
        return {"ran": False, "stub": True, "error": str(exc)}


__all__ = [
    "capture_screenshot",
    "list_roms",
    "restore_save_state",
    "run_macro",
    "ScreenshotResult",
    "RETRO_LIBRARY",
]
