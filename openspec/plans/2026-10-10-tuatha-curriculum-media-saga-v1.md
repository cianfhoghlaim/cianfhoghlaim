# Saga Plan: tuatha-curriculum-media-saga-v1

Status: **draft**
Opened: 2026-10-10
Supersedes the retro-game-placeholder scope of
`2026-10-01-convergence-saga-v1.md` (Plan 3) without removing it.

## Why this saga exists

The convergence saga (2026-10-01) wired a **retro-game design-pattern**
catalogue (Number Munchers → Golden Sun → Hades) as the MMO's inspiration
surface. That catalogue shipped with a deliberate artifact: a 6-entry
`RETRO_LIBRARY` in `agents/adk/tools/retro_capture.py` whose `rom_sha256`
values are placeholders (`deadbeef000{1..6}`) and whose extraction
prompts only ever describe **retro** games.

Two things are now true that were not true on 2026-10-01:

1. The reference corpus has grown well past retro games. Four modern
   media surfaces are first-class now:
   - **Hades / Hades 2** — Olympian boon / rogue-lite power economy (Class D)
   - **Avatar: The Last Airbender + Korra** — 4+1 element bending (Class C)
   - **X-Men (Hickman Marvel run)** — the X-gene / mutant power taxonomy (Class A)
   - **The Wheel of Time** — saidar / saidin / the One Power, and — new —
     a **per-chapter** schema so the pipeline can identify *when* a power
     is used, chapter by chapter, across all 14 books (Class B)
2. The Leaving Certificate corpus (`leaving_certificate/`, 14 subject
   directories + NCCA policy PDFs) and a set of **hand-made examples**
   (`stedding/geog.pdf`, the `PastLC-IrishEnglish` images) need to land
   in the lakehouse so the media descriptors can be *conditioned on real
   syllabus rows* rather than invented ones.

This saga closes both gaps and then ties the media-intel surface to
**Leaving Certificate Art** (palette / composition / visual-grammar
comparative study) and **Leaving Certificate English** (the Comparative
Study: theme/issue, cultural context, literary genre, general vision) —
the two subjects whose assessment already asks students to compare media.

## The 4 media classes (the cross-media frame)

| Class | Work | Medium | Default model | BAML file |
|-------|------|--------|---------------|-----------|
| A | X-Men (Hickman run) | comic | qwen3-vl-8b (`ocr_vision`, `media_descriptor`) | `baml_src/media/comic_descriptor.baml` |
| B | The Wheel of Time | prose (+ per-chapter) | text model (`Primary`) | `baml_src/media/prose_descriptor.baml`, `baml_src/media/wheel_of_time.baml` |
| C | Avatar: The Last Airbender | animation | qwen3-vl-8b | `baml_src/media/animation_descriptor.baml` |
| D | Hades / Hades 2 | game | qwen3-vl-8b | `baml_src/media/gameplay_descriptor.baml` |

Every class emits a 7-axis record (power_event, visual_grammar, palette,
vfx_vocabulary, narrative_beat, transferability, provenance) with
`provenance.shippable = false` enforced. The cross-media frame
(`baml_src/media/media_power_system.baml`) adds a single
`MediaPowerDescriptor` that any class can map onto, plus the
`ComparativeStudyLens` (LC English) and the Art comparative-study axes.

## Plans (this saga)

### Plan 1 — Cross-media power schema (DONE in this change)
- `baml_src/media/media_power_system.baml` — `PowerSystemKind`
  (DivineBoon / ElementalBending / MutantGene / Channeling / Cosmic /
  Other), `ElementalAxis`, `PowerScaleTier`, `MediaMedium`,
  `PowerUseEvent`, `MediaVisualGrammar`, `PaletteSignature`,
  `ComparativeStudyLens`, `MediaPowerProvenance`, `MediaPowerDescriptor`,
  `ExtractMediaPowerDescriptor`.
- `baml_src/media/wheel_of_time.baml` — `WotChapterSchema`,
  `WotPowerUseEvent`, `WotCharacterMention`, `WotPowerSystem`, `WotFlow`,
  `ExtractWotChapterSchema`. **Per-chapter**, not per-passage.
- Fix the pre-existing build break in
  `baml_src/british_isles/_cross/asset_generation.baml` (invalid inline
  client id + un-comma'd params) so `baml-cli generate` builds the whole
  project again.

### Plan 2 — Media library replacing the retro placeholder
- `agents/adk/tools/media_library.py` — the canonical `MEDIA_LIBRARY`
  covering the 4 classes above (plus the retro games as *homage*
  references, no longer the sole surface), each with an honest
  `rights_holder`, a `derivation_class` (`description_only`), and
  `shippable = False`. Replaces the `deadbeef…` placeholder semantics for
  the modern surfaces; the retro ROM entries stay as ingest rows.
- Rewrite the per-class extraction prompts so they cite the modern works
  first and the retro games only as homage.

### Plan 2b — Retro placeholder cleanup
- `agents/adk/tools/retro_capture.py` `RETRO_LIBRARY` — annotate the
  `rom_sha256` placeholder, mark `stub = True`, and add the
  `media_class` key so the retro rows join the cross-media frame.

### Plan 3 — CocoIndex flows (R1–R4 conformant)
- `cocoindex_flows/media/media_power_embedding.py` — embeds every
  `MediaPowerDescriptor` into `lance://media.media_power_descriptors`.
- `cocoindex_flows/media/wheel_of_time_embedding.py` — embeds every
  `WotChapterSchema` into `lance://media.wheel_of_time_chapters` keyed by
  `(book_index, chapter_number)`.
- `cocoindex_flows/media/curriculum_hydration.py` — walks
  `leaving_certificate/` + the operator's hand-made examples and upserts
  into DuckLake.

### Plan 2.5 — Curriculum hydration (DuckLake)
- New DuckLake tables:
  - `cianfhoghlaim.lc.geography.topics`
  - `cianfhoghlaim.lc.gaeilge.poems_higher`
  - `cianfhoghlaim.lc.english.poets_higher`
  - `cianfhoghlaim.education.ie.policies`
- `scripts/curriculum_hydrate.py` — the operator-friendly CLI.

### Plan 3.5 — Generative assets conditioned on syllabus
- Extend `agents/adk/tools/image_generation.py` prompts so media-intel
  descriptors + hydrated syllabus rows condition the generated assets
  (design-pattern + homage style only; never literal reuse).

### Plan 4 — LC Art + LC English Comparative Study lens
- The `ComparativeStudyLens` axis (theme/issue, cultural context,
  literary genre, general vision + Art composition/palette) lands in
  `media_power_system.baml`; the marimo dashboard renders it.

### Plan 5 — Skills + docs tie-off
- Broaden `.agents/skills/retro-gameplay/SKILL.md` → a `media-intel`
  companion skill that names all 4 classes + the curriculum hydration.
- Update `AGENTS.md` + `CHEATSHEET.md`.

## Non-goals
- Storing any copyrighted pixels / panels / animation frames / game art.
- A new agent (the media-intel tools attach to the existing
  `retro_pattern_agent`, renamed conceptually to the media-intel agent).
- Replacing the retro catalogue — it stays as the "where we came from"
  reference.

## Verification
- `./.venv/bin/baml-cli generate --from ./baml_src` exits 0.
- `bunx openspec validate 2026-10-10-media-intel-and-curriculum-hydration-v1 --strict` passes.
- `ruff check` + `mypy` clean on the touched Python.
