"""marimo notebook: retro_patterns — the retro gameplay pattern catalog browser.

Per the 2026-10-03-cocoindex-retro-gameplay-v1 saga change (Plan 3 of
openspec/plans/2026-10-01-convergence-saga-v1.md).

A marimo dashboard that displays the retro gameplay design pattern
catalog (currently a stub since the CocoIndex runtime + libretro +
SAM3 aren't running yet). When Plan 5 brings up the Lakehouse stack
(the LanceDB-backed ``media.retro_design_patterns`` table), this
notebook auto-discovers the real patterns.

Run with:
    uv run marimo edit notebooks/dashboards/retro_patterns.py
    uv run python notebooks/dashboards/retro_patterns.py --cli
"""
from __future__ import annotations

import marimo

__generated_with = "0.14.0"
app = marimo.App(width="full")


@app.cell
def _intro() -> None:
    import marimo as mo

    mo.md(
        """
        # Retro Gameplay Pattern Catalog (Plan 3 of the 2026-10 convergence saga)

        Operator console for the **RetroGameplayPattern** catalog.
        Displays the design patterns (genre + power events + visual grammar
        + palette) extracted from retro educational games (Hades / Hades 2 /
        WoW / Golden Sun / Pokémon) via libretro + SAM3 + BAML.

        ## The 6 canonical retro_library entries

        | Platform | Game | Year | Genre (BAML) |
        |:--|:--|--:|:--|
        | NES | Number Munchers | 1990 | puzzle |
        | AppleII | The Oregon Trail | 1971 | language_learning |
        | DOS | Where in the World is Carmen Sandiego? | 1985 | other |
        | GB | Pokémon Red | 1996 | monster_tamer |
        | GBA | Golden Sun | 2001 | jrpg |
        | Switch | Hades | 2020 | rogue_like |

        ## What this dashboard shows (when the pipeline is up)

        - Per-game + per-scene pattern breakdown
        - The hex palette extracted from each screenshot
        - The power events visible in each scene
        - The visual grammar (HUD layout + camera + composition)
        - The provenance (ROM sha256 + screenshot sha256 + save state path)

        ## How patterns are catalogued

        1. `scripts/retro_capture.py <game_id>` captures a screenshot via libretro
        2. `agents/adk/tools/retro_pattern_extractor.py:sam3_segment` segments the screenshot
        3. `agents/adk/tools/retro_pattern_extractor.py:extract_retro_pattern` runs BAML ExtractGameplayPattern
        4. `agents/adk/tools/retro_pattern_helpers.py:ingest_pattern_simple` upserts to LanceDB
        """
    )
    return


@app.cell
def _demo_data() -> None:
    """Stub demo data — replaced by the real LanceDB query when Plan 5 brings up the lakehouse bridge."""
    import marimo as mo
    import json

    # The 6 canonical retro_library entries with stub patterns
    patterns = [
        {
            "pattern_id": "8db79c8a8688de71",
            "game_id": "hades",
            "scene_id": "title",
            "platform": "switch",
            "title": "Hades — Title Screen",
            "genre": "rogue_like",
            "palette": ["#1a0e1a", "#d4af37", "#f0e6d2"],
            "power_events_count": 0,
            "design_notes": "(stub: baml_client not generated)",
        },
        {
            "pattern_id": "stub_nmunchers_title",
            "game_id": "number_munchers",
            "scene_id": "title",
            "platform": "nes",
            "title": "Number Munchers — Title Screen",
            "genre": "puzzle",
            "palette": ["#000000", "#ffffff"],
            "power_events_count": 0,
            "design_notes": "(stub: baml_client not generated)",
        },
        {
            "pattern_id": "stub_oregon_trail_title",
            "game_id": "oregon_trail",
            "scene_id": "title",
            "platform": "appleii",
            "title": "The Oregon Trail — Title Screen",
            "genre": "language_learning",
            "palette": ["#000000", "#ffcc00"],
            "power_events_count": 0,
            "design_notes": "(stub: baml_client not generated)",
        },
        {
            "pattern_id": "stub_pokemon_red_title",
            "game_id": "pokemon_red",
            "scene_id": "title",
            "platform": "gb",
            "title": "Pokémon Red — Title Screen",
            "genre": "monster_tamer",
            "palette": ["#f8d030", "#3868e8"],
            "power_events_count": 0,
            "design_notes": "(stub: baml_client not generated)",
        },
        {
            "pattern_id": "stub_golden_sun_title",
            "game_id": "golden_sun",
            "scene_id": "title",
            "platform": "gba",
            "title": "Golden Sun — Title Screen",
            "genre": "jrpg",
            "palette": ["#3a4f8c", "#d4af37"],
            "power_events_count": 0,
            "design_notes": "(stub: baml_client not generated)",
        },
        {
            "pattern_id": "stub_carmen_sandiego_title",
            "game_id": "carmen_sandiego",
            "scene_id": "title",
            "platform": "dos",
            "title": "Where in the World is Carmen Sandiego? — Title Screen",
            "genre": "other",
            "palette": ["#000000", "#ffcc00", "#cc0000"],
            "power_events_count": 0,
            "design_notes": "(stub: baml_client not generated)",
        },
    ]
    mo.md(
        f"""
        ## Pattern Catalog (6 stub entries — replaced when Plan 5 brings up the lakehouse bridge)

        {mo.ui.table(patterns, label="patterns")}
        """
    )
    return


@app.cell
def _summary() -> None:
    import marimo as mo

    mo.md(
        """
        ## Summary

        - **Total patterns**: 6 (stub)
        - **Platforms**: 5 (NES, AppleII, DOS, GB, GBA, Switch)
        - **BAML function**: `ExtractGameplayPattern` (per `baml_src/media/extract_design_pattern.baml`)
        - **CocoIndex flow**: `cocoindex_flows/media/retro_design_embedding.py`
        - **LanceDB table**: `media.retro_design_patterns`
        - **Reference**: `openspec/changes/2026-10-03-cocoindex-retro-gameplay-v1/`
        """
    )
    return


if __name__ == "__main__":
    app.run()
