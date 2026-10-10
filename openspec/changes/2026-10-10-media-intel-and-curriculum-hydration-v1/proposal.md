# Change: 2026-10-10-media-intel-and-curriculum-hydration-v1

## Why

The `cianfhoghlaim` / Tuatha British Isles MMO catalogues the *design
patterns* (not the literal assets) of reference media so its designers
can riff on proven power economies. The convergence saga
(`openspec/plans/2026-10-01-convergence-saga-v1.md`, Plan 3) built that
catalogue around **retro games only** and shipped with two artifacts:

1. `agents/adk/tools/retro_capture.py::RETRO_LIBRARY` carries
   placeholder `rom_sha256` values (`deadbeef000{1..6}`) and its prompts
   describe retro titles exclusively.
2. `baml_src/british_isles/_cross/asset_generation.baml` fails to build
   (invalid inline client id + un-comma'd parameters), so
   `baml-cli generate` cannot run — the whole BAML surface is frozen.

Meanwhile the reference corpus has grown past retro games to four modern
media surfaces — **Hades**, **Avatar: The Last Airbender**, **X-Men
(Hickman)**, and **The Wheel of Time** — and the Wheel of Time needs a
**per-chapter** schema so the pipeline can identify *when* a power is
used across all 14 books. Finally, the Leaving Certificate corpus
(`leaving_certificate/`, 14 subjects + NCCA policies) plus the operator's
hand-made examples (`stedding/geog.pdf`, the `PastLC-IrishEnglish`
images) are not yet in the lakehouse, so descriptors cannot be
*conditioned on real syllabus rows*.

Without this change the MMO's media-intel surface is stale, its BAML
does not compile, and its generative assets are ungrounded. The
descriptors also need to land **in line with Leaving Certificate Art**
(palette/composition/visual-grammar comparative study) and **Leaving
Certificate English** (the Comparative Study: theme/issue, cultural
context, literary genre, general vision).

This is Plan 1 + Plan 2 + Plan 2.5 of
`openspec/plans/2026-10-10-tuatha-curriculum-media-saga-v1.md`.

## What Changes

### Code — BAML (new + fixed)
- **NEW** `baml_src/media/media_power_system.baml` — the cross-media
  `MediaPowerDescriptor` + `PowerUseEvent` + `MediaVisualGrammar` +
  `PaletteSignature` + `ComparativeStudyLens` + `MediaPowerProvenance`
  and the `ExtractMediaPowerDescriptor` function (client
  `MediaIntelPrimary`). Enums: `PowerSystemKind`, `MediaMedium`,
  `ElementalAxis`, `PowerScaleTier`.
- **NEW** `baml_src/media/wheel_of_time.baml` — the **per-chapter**
  `WotChapterSchema` + `WotPowerUseEvent` + `WotCharacterMention` and the
  `ExtractWotChapterSchema` function (client `MediaIntelPrimary`). Enums:
  `WotPowerSystem`, `WotFlow`.
- **FIX** `baml_src/british_isles/_cross/asset_generation.baml` — replace
  the invalid `client "openai/gpt-4o-mini"` with `client Primary`, add the
  missing commas between function parameters, and interpolate the inputs.
  (Pre-existing build break; blocks `baml-cli generate`.)

### Code — media library (new)
- **NEW** `agents/adk/tools/media_library.py` — the canonical media-intel
  library covering the 4 classes (Hades / Avatar / X-Men / Wheel of Time)
  with `Rightsholder` provenance, `shippable = false` enforced, and the
  class → BAML-function → model-family routing table. Supersedes the
  retro-only `RETRO_LIBRARY` as the primary inspiration surface while
  keeping retro entries as the "where we came from" tier.
- **EDIT** `agents/adk/tools/retro_capture.py` — annotate the placeholder
  `rom_sha256` values and add `media_class = "retro"` + `artifact = true`.

### Code — CocoIndex flows (new)
- **NEW** `cocoindex_flows/media/media_power_embedding.py` — embeds every
  `MediaPowerDescriptor` into `lance://media.media_power_descriptors`.
- **NEW** `cocoindex_flows/media/wheel_of_time_embedding.py` — embeds every
  `WotChapterSchema` into `lance://media.wheel_of_time_chapters` keyed by
  `(book_index, chapter_number)`.
- **NEW** `cocoindex_flows/media/curriculum_hydration.py` — walks
  `leaving_certificate/` + the operator's hand-made examples and upserts
  into DuckLake.

### Code — curriculum hydration (new)
- **NEW** `scripts/curriculum_hydrate.py` — the operator CLI that reads
  the LC PDFs + `stedding/geog.pdf` + the `PastLC-IrishEnglish` images and
  writes the DuckLake rows.

### New DuckLake tables
- `cianfhoghlaim.lc.geography.topics`
- `cianfhoghlaim.lc.gaeilge.poems_higher`
- `cianfhoghlaim.lc.english.poets_higher`
- `cianfhoghlaim.education.ie.policies`

### New LanceDB tables
- `lance://media.media_power_descriptors`
- `lance://media.wheel_of_time_chapters`

### Reference surfaces
- `baml_src/media/{comic,animation,prose,gameplay,official_document}_descriptor.baml` — the 5 existing per-medium extractors (re-used, not replaced)
- `openspec/specs/retro-game-design-catalogue/spec.md` — the existing spec
- `openspec/plans/2026-10-10-tuatha-curriculum-media-saga-v1.md` — the saga

## Impact

- **Affected specs**: `media-intel-and-curriculum-hydration` (added),
  `retro-game-design-catalogue` (extended).
- **Affected code**: `baml_src/media/`, `baml_src/british_isles/_cross/`,
  `agents/adk/tools/`, `cocoindex_flows/media/`, `scripts/`.
- **Unblocks**: `baml-cli generate` (every BAML consumer, including the
  Dagster + DLT + agent API layers).
- **Non-goals**: no copyrighted pixels/panels/frames stored; no new agent;
  retro catalogue retained as the legacy tier.
