"""agents/adk/tools/retro_pattern_helpers.py — the standalone helpers for the retro gameplay pattern catalog.

Per the 2026-10-03-cocoindex-retro-gameplay-v1 saga change (Plan 3 of
openspec/plans/2026-10-01-convergence-saga-v1.md).

Lives in agents/ (not cocoindex_flows/) because the relative import
``from .._shared._lifespan import`` breaks when the helpers are imported
standalone (for scripts + marimo notebooks). The cocoindex flow itself
imports these helpers and feeds them into the CocoIndex runtime.

Reference:
    openspec/changes/2026-10-03-cocoindex-retro-gameplay-v1/specs/cocoindex-retro-gameplay/spec.md
"""
from __future__ import annotations

import hashlib
from datetime import datetime, UTC
from typing import Any


def pattern_id(platform: str, game_id: str, scene_id: str, screenshot_sha256: str) -> str:
    """Deterministic ID for a pattern record."""
    h = hashlib.sha256()
    h.update(f"{platform}|{game_id}|{scene_id}|{screenshot_sha256}".encode())
    return h.hexdigest()[:16]


def build_embedding_text(row: dict[str, Any]) -> str:
    """Build the embedding text from a pattern row dict.

    Concatenates the structured pattern fields into a single text that
    BAAI/bge-m3 can embed for semantic search ("find me games with
    similar boon systems").
    """
    parts = [
        f"{row.get('platform', '')} game {row.get('game_id', '')} scene {row.get('scene_id', '')}",
        row.get("title", ""),
        row.get("genre", ""),
        row.get("design_notes", ""),
        " ".join(row.get("palette_dominant_hex", []) or []),
        " ".join(row.get("palette_accent_hex", []) or []),
    ]
    return " | ".join(p for p in parts if p)


def ingest_pattern_simple(
    *,
    platform: str,
    game_id: str,
    scene_id: str,
    title: str,
    genre: str,
    design_notes: str = "",
    palette_dominant_hex: list[str] | None = None,
    palette_accent_hex: list[str] | None = None,
    palette_emissive_hex: list[str] | None = None,
    power_events_json: str = "[]",
    visual_grammar_json: str = "{}",
    source_rom_sha256: str = "",
    source_screenshot_sha256: str = "",
    source_save_state_path: str = "",
    source_macro_script: str = "",
    source_captured_at: str = "",
) -> dict[str, Any]:
    """The no-CocoIndex helper for offline dev mode.

    Returns the dict that would have been upserted into LanceDB. Use
    this when the CocoIndex runtime isn't installed OR when the LanceDB
    table doesn't exist yet (during initial setup).
    """
    pid = pattern_id(platform, game_id, scene_id, source_screenshot_sha256)
    return {
        "pattern_id": pid,
        "game_id": game_id,
        "scene_id": scene_id,
        "platform": platform,
        "genre": genre,
        "title": title,
        "design_notes": design_notes,
        "palette_dominant_hex": palette_dominant_hex or [],
        "palette_accent_hex": palette_accent_hex or [],
        "palette_emissive_hex": palette_emissive_hex or [],
        "power_events_json": power_events_json,
        "visual_grammar_json": visual_grammar_json,
        "source_rom_sha256": source_rom_sha256,
        "source_screenshot_sha256": source_screenshot_sha256,
        "source_save_state_path": source_save_state_path,
        "source_macro_script": source_macro_script,
        "source_captured_at": source_captured_at,
        "ingested_at": datetime.now(UTC).isoformat(),
    }


__all__ = ["pattern_id", "build_embedding_text", "ingest_pattern_simple"]
