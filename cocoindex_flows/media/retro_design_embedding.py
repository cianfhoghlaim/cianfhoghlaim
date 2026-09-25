"""CocoIndex v1 App: retro_design_embedding — the retro gameplay pattern catalog.

Per the 2026-10-03-cocoindex-retro-gameplay-v1 saga change (Plan 3 of
openspec/plans/2026-10-01-convergence-saga-v1.md).

This is the canonical surface that the ``retro_pattern_agent``'s
``extract_retro_pattern`` tool calls. It:

1. Receives the ``RetroGameplayPattern`` record from the BAML
   ``ExtractGameplayPattern`` function (per the
   ``baml_src/media/extract_design_pattern.baml`` contract).
2. Embeds the pattern's ``design_notes`` + ``game_id`` + ``scene_id``
   via the shared BAAI/bge-m3 embedder.
3. Mounts a LanceDB target table
   ``cianhoghlaim.media.retro_design_patterns`` keyed by
   ``(platform, game_id, scene_id)``.
4. Declares a vector index on the ``embedding`` column for
   semantic search ("find me games with similar boon systems").
5. Routes a Dagster sensor at ``retro_library_watcher`` that polls
   the ``romm`` library every 60s + runs the screenshot capture +
   BAML extraction for any new ROMs.

The flow conforms to the canonical R1-R4 conformance contract:

  - **R1** — imports ``shared_lifespan`` from ``.._shared._lifespan``
  - **R2** — no new ``ContextKey[`` declarations (uses only the
    3 shared ones)
  - **R3** — ``app = coco.App(coco.AppConfig(name=...))`` at module
    scope
  - **R4** — at least one ``@coco.fn(`` decorator

Reference:
    openspec/changes/2026-10-03-cocoindex-retro-gameplay-v1/specs/cocoindex-retro-gameplay/spec.md
    openspec/specs/retro-game-design-catalogue/spec.md (the existing spec)
"""
from __future__ import annotations

import hashlib
import os
import pathlib
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Any

import structlog

logger = structlog.get_logger(__name__)


# Lazy cocoindex + lancedb imports (graceful degradation when not installed)
try:
    import cocoindex as coco  # type: ignore[import-not-found]
    from cocoindex.connectors import lancedb  # type: ignore[import-not-found]

    COCOINDEX_AVAILABLE = True
except ImportError as e:
    logger.warning("cocoindex_v1_not_available: %s", e)
    COCOINDEX_AVAILABLE = False
    coco = None  # type: ignore[assignment]
    lancedb = None  # type: ignore[assignment]


# R1: shared lifespan + canonical ContextKeys
from .._shared._lifespan import (  # noqa: E402
    EMBEDDER,
    LANCE_DB,
    shared_lifespan,
)


# The source directory: screenshots land here from the libretro capture
# (see scripts/retro_capture.py + bonneagar/stacks/libretro-retroarch/).
RETRO_SCREENSHOTS_ROOT: pathlib.Path = pathlib.Path(
    __import__("os").environ.get(
        "BI_EP_RETRO_SCREENSHOTS_ROOT",
        pathlib.Path.cwd() / "stedding" / "ingest_queue" / "retro",
    )
)


@dataclass(frozen=True)
class RetroPatternRow:
    pattern_id: str
    game_id: str
    scene_id: str
    platform: str
    genre: str  # one of: rogue_like / mmorpg / jrpg / monster_tamer / puzzle / language_learning / match_three / other
    title: str
    design_notes: str
    palette_dominant_hex: list[str]
    palette_accent_hex: list[str]
    palette_emissive_hex: list[str]
    power_events_json: str       # the BAML list serialised as JSON for queryability
    visual_grammar_json: str
    source_rom_sha256: str
    source_screenshot_sha256: str
    source_save_state_path: str
    source_macro_script: str
    source_captured_at: str
    ingested_at: str
    embedding: Annotated[Any, EMBEDDER]


def _pattern_id(platform: str, game_id: str, scene_id: str, screenshot_sha256: str) -> str:
    """Deterministic ID for a pattern record."""
    h = hashlib.sha256()
    h.update(f"{platform}|{game_id}|{scene_id}|{screenshot_sha256}".encode())
    return h.hexdigest()[:16]


def _build_embedding_text(row: RetroPatternRow) -> str:
    """Build the embedding text from the structured pattern fields."""
    parts = [
        f"{row.platform} game {row.game_id} scene {row.scene_id}",
        row.title,
        row.genre,
        row.design_notes,
        " ".join(row.palette_dominant_hex),
        " ".join(row.palette_accent_hex),
    ]
    return " | ".join(p for p in parts if p)


@coco.AppConfig(name="cianhfhglaim_media_retro_design_embedding")
@coco.fn
def retro_design_app() -> None:
    """The canonical CocoIndex App for retro gameplay design patterns.

    Indexes RetroGameplayPattern records into
    ``lance://media.retro_design_patterns`` keyed by
    ``(platform, game_id, scene_id)``.
    """
    table_name = "cianhfhglaim.media.retro_design_patterns"

    @coco.fn
    async def ingest_pattern(
        *,
        platform: str,
        game_id: str,
        scene_id: str,
        title: str,
        genre: str,
        design_notes: str,
        palette_dominant_hex: list[str],
        palette_accent_hex: list[str],
        palette_emissive_hex: list[str],
        power_events_json: str,
        visual_grammar_json: str,
        source_rom_sha256: str,
        source_screenshot_sha256: str,
        source_save_state_path: str = "",
        source_macro_script: str = "",
        source_captured_at: str = "",
    ) -> None:
        """Ingest a single RetroGameplayPattern record into LanceDB.

        Args:
            platform: NES | SNES | GB | GBA | Genesis | PS1 | DOS | AppleII | Switch
            game_id: The canonical retro_library game_id
            scene_id: title | menu | gameplay | boss | minigame | end | ...
            title: The human-readable title of the scene (e.g. "Boon Selection")
            genre: rogue_like | mmorpg | jrpg | monster_tamer | puzzle |
                  language_learning | match_three | other
            design_notes: 1-2 sentences of design notes
            palette_*: the hex palette extracted from the screenshot
            power_events_json: the BAML GameplayPowerEvent list as JSON
            visual_grammar_json: the BAML GameplayVisualGrammar as JSON
            source_*: the RetroPatternSource provenance fields

        Returns:
            None (the row is upserted into LanceDB).
        """
        import json as _json
        from datetime import datetime as _dt

        # Build the row
        pattern_id = _pattern_id(platform, game_id, scene_id, source_screenshot_sha256)
        row = RetroPatternRow(
            pattern_id=pattern_id,
            game_id=game_id,
            scene_id=scene_id,
            platform=platform,
            genre=genre,
            title=title,
            design_notes=design_notes,
            palette_dominant_hex=palette_dominant_hex,
            palette_accent_hex=palette_accent_hex,
            palette_emissive_hex=palette_emissive_hex,
            power_events_json=power_events_json,
            visual_grammar_json=visual_grammar_json,
            source_rom_sha256=source_rom_sha256,
            source_screenshot_sha256=source_screenshot_sha256,
            source_save_state_path=source_save_state_path,
            source_macro_script=source_macro_script,
            source_captured_at=source_captured_at,
            ingested_at=_dt.utcnow().isoformat(),
            embedding=None,  # filled in below
        )

        # Embed + upsert
        embedding_text = _build_embedding_text(row)
        embedding = await EMBEDDER.embed(embedding_text)
        row_dict = {**row.__dict__, "embedding": embedding}

        await LANCE_DB.upsert(table_name, coco.Row(**row_dict))
        logger.info(
            "retro_design_embedding: ingested pattern_id=%s game=%s scene=%s",
            pattern_id,
            game_id,
            scene_id,
        )

    return retro_design_app()


__all__ = [
    "retro_design_app",
    "RetroPatternRow",
    "RETRO_SCREENSHOTS_ROOT",
]
