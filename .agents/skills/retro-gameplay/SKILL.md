---
name: retro-gameplay
description: The retro-gameplay design pattern catalog. Captures screenshots via libretro + segments via SAM3 + extracts typed design patterns via BAML + indexes them in CocoIndex-mounted LanceDB. Used by the Tuatha British Isles MMO designers to riff on the proven design patterns of retro educational games (Number Munchers / Oregon Trail / Carmen Sandiego / Pokémon / Golden Sun / Hades). Use when adding or modifying anything in the retro-gameplay chain — libretro screenshots, SAM3 sprite segmentation, the ExtractGameplayPattern BAML function, the CocoIndex flow, the retro_pattern_agent, or the marimo pattern browser.
---

# Retro Gameplay (the pattern catalog)

> **Per the 2026-10-03-cocoindex-retro-gameplay-v1 saga change** (Plan 3 of
> `openspec/plans/2026-10-01-convergence-saga-v1.md`).

## The 4-step chain

```
libretro headless (stedding/ingest_queue/retro/)
        │
        ├── STEP 1: capture_screenshot (agents/adk/tools/retro_capture.py)
        │              ↓ PNG + sha256
        ├── STEP 2: sam3_segment (agents/adk/tools/retro_pattern_extractor.py)
        │              ↓ sprite bounding boxes (full-image fallback when offline)
        ├── STEP 3: extract_retro_pattern (agents/adk/tools/retro_pattern_extractor.py)
        │              ↓ typed RetroGameplayPattern (BAML stub fallback when offline)
        └── STEP 4: ingest_pattern_simple (agents/adk/tools/retro_pattern_helpers.py)
                       ↓ record for LanceDB upsert
```

Each step gracefully falls back to stub behaviour when the
downstream service isn't running — the chain still produces a
deterministic `pattern_id` for reproducibility.

## The 6 canonical retro_library entries

| Platform | Game | Year | Genre (BAML) |
|:--|:--|--:|:--|
| NES | Number Munchers | 1990 | puzzle |
| AppleII | The Oregon Trail | 1971 | language_learning |
| DOS | Where in the World is Carmen Sandiego? | 1985 | other |
| GB | Pokémon Red | 1996 | monster_tamer |
| GBA | Golden Sun | 2001 | jrpg |
| Switch | Hades | 2020 | rogue_like |

Defined in `agents/adk/tools/retro_capture.py:RETRO_LIBRARY`.

## The BAML contract

`baml_src/media/extract_design_pattern.baml` defines:

- `RetroGameplayPattern` — the unified pattern record (game_id + scene_id + genre + power_events + visual_grammar + palette + source provenance)
- `RetroPatternSource` — the provenance (platform + game_id + rom_sha256 + screenshot_sha256 + save_state_path + macro_script)
- `ExtractGameplayPattern(screenshot_b64, session_log?, game_id, scene_hint?, platform, rom_sha256, save_state_path?, macro_script?)` — the extraction function

The 4 existing classes (`GameGenre` + `GameplayPowerEvent` +
`GameplayVisualGrammar` + `GameplayPalette`) are re-exported from
`gameplay_descriptor.baml` so the pattern record can compose them
without circular imports.

## The CocoIndex flow

`cocoindex_flows/media/retro_design_embedding.py` indexes
`RetroGameplayPattern` records into the LanceDB table
`media.retro_design_patterns` (keyed by `(platform, game_id,
scene_id)`). The flow conforms to the canonical R1-R4 conformance
contract (per the cocoindex flow doc).

The standalone helper `ingest_pattern_simple` (in
`agents/adk/tools/retro_pattern_helpers.py`) returns the dict that
would have been upserted — use this when the CocoIndex runtime isn't
installed or when the LanceDB table doesn't exist yet.

## The agent + tools

`agents/adk/retro_pattern_agent.py` is the 25th agent in the
24-agent fleet. It exposes 7 tools:

- `list_roms()` — list the 6 canonical retro_library entries
- `capture_screenshot(platform, game_id, scene_id)` — libretro screenshot
- `restore_save_state(platform, game_id, save_state_path)` — ludusavi
- `run_macro(macro_script_path)` — deterministic libretro macro
- `sam3_segment(screenshot_path, classes?)` — SAM3 sprite segmentation
- `extract_retro_pattern(screenshot_path, ...)` — BAML extraction
- `ingest_pattern_simple(...)` — LanceDB upsert

## The visible demo (C6 quality-of-life)

```bash
# List the 6 canonical retro_library entries
uv run python scripts/retro_capture.py --list-roms

# Capture + segment + extract + ingest for Hades title
uv run python scripts/retro_capture.py hades

# Capture Number Munchers menu screen
uv run python scripts/retro_capture.py number_munchers --platform nes --scene menu
```

The marimo dashboard at `notebooks/dashboards/retro_patterns.py` displays
the pattern catalog (per-game + per-scene + palette hex + design notes).

## Reference

- Plan 3 of the convergence saga: `openspec/plans/2026-10-01-convergence-saga-v1.md`
- The change: `openspec/changes/2026-10-03-cocoindex-retro-gameplay-v1/`
- The spec: `openspec/specs/cocoindex-retro-gameplay/spec.md`
- The BAML: `baml_src/media/extract_design_pattern.baml`
- The flow: `cocoindex_flows/media/retro_design_embedding.py`
- The tools: `agents/adk/tools/{retro_capture,retro_pattern_extractor,retro_pattern_helpers}.py`
- The agent: `agents/adk/retro_pattern_agent.py`
- The CLI: `scripts/retro_capture.py`
- The dashboard: `notebooks/dashboards/retro_patterns.py`

## When to use this skill

Activate when the user asks about:

- "Capture a retro screenshot" / "extract a design pattern" / "run libretro"
- "Add a new retro game" / "expand the retro_library" / "support PS1"
- "Wire SAM3 sprite segmentation" / "segment a Hades boon screen"
- "Extract the genre" / "what's the visual grammar of Pokémon Red?"
- "Browse the pattern catalog" / "open the retro dashboard"
- "Tuatha sprite bank inspiration" / "MMO asset references"
- "Why is the BAML stub fallback firing?" — answer: `baml-cli generate`
  needs to run from `baml_src/` to produce the typed Python client.
