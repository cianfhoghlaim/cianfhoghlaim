---
name: media-intel
description: Cross-media design-pattern catalogue for the Cianfhoghlaim / Tuatha British Isles MMO — the 4 media classes (X-Men Hickman / Wheel of Time / Avatar: The Last Airbender / Hades) + the per-chapter Wheel of Time schema + the Leaving Certificate corpus hydration CLI (DuckLake) + the 3 CocoIndex flows. Surfaces the cross-media `MediaPowerDescriptor`, the per-chapter `WotChapterSchema`, the canonical `MEDIA_LIBRARY` (Hades / Avatar / X-Men / Wheel of Time + retro homage tier), and the `core:hydrate:curriculum` mise task. Strictly description-only (`shippable = false`); no copyrighted pixels, panels, frames, or game art are ever stored. Use when adding a new media class, extending the per-chapter wheel-of-time schema, debugging the curriculum hydration CLI, wiring a new CocoIndex media flow, mapping a descriptor onto the LC English Comparative Study or LC Art palette/composition axes, or asking "how does the MMO source its inspiration surface?". Triggers: 'media-intel', 'media library', 'MEDIA_LIBRARY', 'Hades boon', 'Avatar bending', 'X-Men mutant', 'Wheel of Time channeling', 'WotChapterSchema', 'MediaPowerDescriptor', 'ComparativeStudyLens', 'shippable=false', 'description-only', 'curriculum_hydrate', 'core:hydrate:curriculum', 'comparison study', 'LC Art palette', 'LC English theme'.
location: .agents/skills/media-intel/SKILL.md
---

# Media-Intel — Cross-Media Design-Pattern Catalogue

The Tuatha MMO's inspiration surface for the four "modern" reference
media classes (Hades / Avatar: The Last Airbender / X-Men / The Wheel
of Time) plus the legacy retro-game tier, the per-chapter Wheel of
Time schema, and the Leaving Certificate corpus hydration CLI. Every
descriptor in this surface is **description-only**
(`provenance.shippable = false`); no copyrighted pixels, panels,
animation frames, or game art are ever stored.

Upstream sources:

- [`openspec/plans/2026-10-10-tuatha-curriculum-media-saga-v1.md`](../../openspec/plans/2026-10-10-tuatha-curriculum-media-saga-v1.md)
  — the saga plan (Plans 1, 2, 2b, 2.5, 3, 3.5, 4, 5)
- [`openspec/changes/2026-10-10-media-intel-and-curriculum-hydration-v1/proposal.md`](../../openspec/changes/2026-10-10-media-intel-and-curriculum-hydration-v1/proposal.md)
  — the change proposal
- [`openspec/changes/2026-10-10-media-intel-and-curriculum-hydration-v1/specs/media-intel-and-curriculum-hydration/spec.md`](../../openspec/changes/2026-10-10-media-intel-and-curriculum-hydration-v1/specs/media-intel-and-curriculum-hydration/spec.md)
  — the canonical spec (8 Requirements)

The companion skill at
[`.agents/skills/retro-gameplay/SKILL.md`](../retro-gameplay/SKILL.md)
remains the "where we came from" reference for the Number Munchers →
Golden Sun → Hades retro lineage; canonical surface lives here.

## Invariant (description-only)

Every `MediaPowerDescriptor`, every `WotChapterSchema`, and every
`MediaEntry` in `MEDIA_LIBRARY` carries a `Provenance` whose
`shippable` field is `False`. Violators are dropped at the CocoIndex
embedding layer with a `media_intel_shippable_violation` log line and
are never written to LanceDB or DuckLake.

- `MEDIA_LIBRARY`: `Provenance.__post_init__` raises on non-`False`
  (`agents/adk/tools/media_library.py:79`)
- `MediaEntry.__post_init__`: re-checks the `Provenance.shippable`
  flag (`agents/adk/tools/media_library.py:110`)
- `assert_description_only()`: library-wide guard
  (`agents/adk/tools/media_library.py:346`)
- `cocoindex_flows/media/media_power_embedding.py:53` and
  `wheel_of_time_embedding.py:51`: drop any descriptor whose
  `provenance.shippable` is not exactly `False`

## The 4 media classes

| Class | Work | Medium | Default model family | BAML function | Source file |
|:--|:--|:--|:--|:--|:--|
| **A** | X-Men (Hickman run) | Comic | `ocr_vision` (`xmen_scene`) | `ExtractComicDescriptor` | `baml_src/media/comic_descriptor.baml` |
| **B** | The Wheel of Time | Prose (+ per-chapter) | `text_llm` (`Primary`) | `ExtractWotChapterSchema` | `baml_src/media/wheel_of_time.baml` |
| **C** | Avatar: The Last Airbender (+ Korra) | Animation | `ocr_vision` (`media_descriptor`) | `ExtractAnimationDescriptor` | `baml_src/media/animation_descriptor.baml` |
| **D** | Hades / Hades 2 | Game | `ocr_vision` (`hades_boon`) | `ExtractHadesBoon` | `baml_src/media/gameplay_descriptor.baml` |

Every class emits a 7-axis record (`power_event`, `visual_grammar`,
`palette`, `vfx_vocabulary`, `narrative_beat`, `transferability`,
`provenance`) under the cross-media frame
`baml_src/media/media_power_system.baml`. The Wheel of Time is the
prose sibling — per-chapter, not per-passage — and uses the
`WotChapterSchema` for chapter-level indexing.

The legacy retro tier (Number Munchers, Golden Sun) remains in
`MEDIA_LIBRARY` with `media_class = "retro"` and `artifact = True` —
the "where we came from" homage tier.

## Canonical file paths

| Artifact | Path |
|:--|:--|
| Canonical media library | `agents/adk/tools/media_library.py` |
| Cross-media power schema | `baml_src/media/media_power_system.baml` |
| Per-chapter WoT schema | `baml_src/media/wheel_of_time.baml` |
| Per-medium extractors (existing) | `baml_src/media/{comic,animation,prose,gameplay,official_document}_descriptor.baml` |
| Curriculum hydration CLI | `scripts/curriculum_hydrate.py` |
| Curriculum table schemas | `scripts/_curriculum_table_schemas.py` |
| CocoIndex flow (cross-media) | `cocoindex_flows/media/media_power_embedding.py` |
| CocoIndex flow (WoT per-chapter) | `cocoindex_flows/media/wheel_of_time_embedding.py` |
| CocoIndex flow (curriculum hydration) | `cocoindex_flows/media/curriculum_hydration.py` |
| Retro capture (legacy) | `agents/adk/tools/retro_capture.py` |

## BAML functions

All 3 routable via the `MediaIntelPrimary` client:

```python
from baml_client import b
from pathlib import Path

# 1. Cross-media (Hades / Avatar / X-Men / Film)
descriptor = b.ExtractMediaPowerDescriptor(
    image=Path("frame.png").read_bytes(),   # never stored
    work="Avatar: The Last Airbender",
    scene_id="s01e01-the-boy-in-the-iceberg",
    medium="animation",
    power_system="elemental_bending",
    rights_holder="Nickelodeon / Paramount",
    evidence="Katara raises a column of water from the sea, a curved ribbon of water lit pale blue.",
)
# descriptor.provenance.shippable == False (enforced by the prompt template)

# 2. Wheel of Time per-chapter
chapter = b.ExtractWotChapterSchema(
    chapter_text="Moiraine channels to shield the group as Trollocs attack the inn at Emond's Field...",
    book="The Eye of the World",
    book_index=1,
    chapter_number=12,
    chapter_title="Dust on the Wind",
    rights_holder="Tor Books",
)
# chapter.provenance.shippable == False

# 3. Media library routing table (Python-side, no BAML call)
from agents.adk.tools.media_library import (
    MEDIA_LIBRARY, first_class_media, power_descriptor_targets,
)
targets = power_descriptor_targets()
# List[dict] — one row per first-class entry, with model_family / role / resolved model
```

The 3 BAML test cases (`avatar_katara_waterbending`,
`xmen_jean_grey_telekinesis`, `hades_athena_boon`,
`tEotW_ch12`) live at the bottom of their respective `baml_src/media/*.baml`
files. Run with `./.venv/bin/baml-cli test`.

## Curriculum hydration

Hydrates 4 DuckLake tables from the Leaving Certificate corpus + the
operator's hand-made examples. Primary-keyed on the provenance triple
`(source_pdf, source_page, source_url)`.

| DuckLake table (canonical MotherDuck form) | Local DuckLake table | Source |
|:--|:--|:--|
| `cianfhoghlaim.lc.geography.topics` | `cianfhoghlaim.geography_topics` | `leaving_certificate/geography/**` + `stedding/geog.pdf` |
| `cianfhoghlaim.lc.gaeilge.poems_higher` | `cianfhoghlaim.gaeilge_poems_higher` | `PastLC-IrishEnglish/page_00{1..3}.png` (Irish side) |
| `cianfhoghlaim.lc.english.poets_higher` | `cianfhoghlaim.english_poets_higher` | `PastLC-IrishEnglish/page_00{1..3}.png` (English side) |
| `cianfhoghlaim.education.ie.policies` | `cianfhoghlaim.education_ie_policies` (dotted `education.ie` deferred to MotherDuck; local DuckDB 1.4/1.5.x rejects it) | 5 NCCA policy PDFs at `leaving_certificate/` root |

Operator quick path (the canonical entry point):

```bash
# Hydrate all 4 tables (geography + gaeilge + english + policies)
mise run core:hydrate:curriculum
# expands to: uv run python scripts/curriculum_hydrate.py --all

# Surgical subcommands
uv run python scripts/curriculum_hydrate.py --subject geography
uv run python scripts/curriculum_hydrate.py --subject english --subject gaeilge
uv run python scripts/curriculum_hydrate.py --policies
uv run python scripts/curriculum_hydrate.py --source stedding/geog.pdf

# Dry-run (alias --no-dlt) — emits JSONL under stedding/ingest_queue/curriculum/
uv run python scripts/curriculum_hydrate.py --all --dry-run
```

Local-vs-canonical naming convention: the canonical MotherDuck form
uses dotted LC-stage namespaces (`cianfhoghlaim.lc.<subject>.table`,
`cianfhoghlaim.education.ie.policies`); the local DuckLake form uses
underscores (`cianfhoghlaim.<subject>_<table>`) because DuckDB
≤ 1.5.x rejects dotted identifiers. The CLI normalises both.

## The 3 CocoIndex flows

All conform to R1–R4 (R1 imports `shared_lifespan` + canonical
`EMBEDDER` / `LANCE_DB` from `.._shared._lifespan`; R2 declares no new
`ContextKey[`; R3 declares `app = coco.App(coco.AppConfig(name=...))`
at module scope; R4 uses ≥ 1 `@coco.fn(` decorator):

| CocoIndex v1 App | Mounts | Keyed by | Source |
|:--|:--|:--|:--|
| `media_power_embedding` | `lance://media.media_power_descriptors` | `(media_class, key)` | `cocoindex_flows/media/media_power_embedding.py` |
| `wheel_of_time_embedding` | `lance://media.wheel_of_time_chapters` | `(book_index, chapter_number)` | `cocoindex_flows/media/wheel_of_time_embedding.py` |
| `curriculum_hydration` | DuckLake schema mount for the 4 tables | n/a (schema-only stub) | `cocoindex_flows/media/curriculum_hydration.py` |

Embedder: shared `BAAI/bge-m3` (1024-d, multilingual) per
`cocoindex_flows/_shared/_lifespan.py:108`.

## Routing table — "where do I do X for media-intel?"

| I want to... | Look at... |
|:--|:--|
| Add a new reference work to `MEDIA_LIBRARY` | `agents/adk/tools/media_library.py` — append a `MediaEntry(...)`; `__post_init__` enforces `shippable = False` |
| Add a new field to the cross-media descriptor | `baml_src/media/media_power_system.baml` — extend `MediaPowerDescriptor` + `ExtractMediaPowerDescriptor`'s prompt |
| Add a new field to the per-chapter WoT schema | `baml_src/media/wheel_of_time.baml` — extend `WotChapterSchema` + `ExtractWotChapterSchema` |
| Hydrate a new syllabus table | `scripts/curriculum_hydrate.py` + `scripts/_curriculum_table_schemas.py` (add a `TypedDict` + register in `TABLE_SCHEMAS`) |
| Run a curriculum hydration | `mise run core:hydrate:curriculum` (alias for `python scripts/curriculum_hydrate.py --all`) |
| Embed a new media-power row | the `media_power_embedding` CocoIndex v1 App — run from the marimo comparative-study dashboard |
| Map descriptors onto LC English Comparative Study axes | `ComparativeStudyLens` (`baml_src/media/media_power_system.baml:108`) |
| Map descriptors onto LC Art palette/composition axes | `PaletteSignature` + `MediaVisualGrammar.composition` |

## DO NOT

- Set `provenance.shippable = True` on any `MediaEntry`,
  `MediaPowerDescriptor`, or `WotChapterSchema`. The CocoIndex
  embedding layer drops violators; the media library refuses to
  construct them.
- Store the source frame, panel, chapter text, ROM dump, or
  animation cel inside the lakehouse. The contract is **description
  only** — `source_url`, `source_timestamp`, and short `evidence`
  quotes only.
- Replace the retro catalogue. The legacy retro tier stays as the
  "where we came from" reference; the modern 4 classes are the
  primary inspiration surface.
- Add a new agent for media-intel. The cross-media and per-chapter
  tools attach to the existing `retro_pattern_agent` (renamed
  conceptually to the media-intel agent per the saga).

## Cross-references

- [`openspec/plans/2026-10-10-tuatha-curriculum-media-saga-v1.md`](../../openspec/plans/2026-10-10-tuatha-curriculum-media-saga-v1.md)
  — the saga plan
- [`openspec/changes/2026-10-10-media-intel-and-curriculum-hydration-v1/`](../../openspec/changes/2026-10-10-media-intel-and-curriculum-hydration-v1/)
  — the umbrella change (proposal + spec + tasks)
- [`.agents/skills/retro-gameplay/SKILL.md`](../retro-gameplay/SKILL.md)
  — the legacy retro tier (still the "where we came from" reference)
- [`.agents/skills/baml-schema-sync/SKILL.md`](../baml-schema-sync/SKILL.md)
  — the BAML codegen skill
- [`.agents/skills/dlt/SKILL.md`](../dlt/SKILL.md) — DLT conventions
  for the curriculum hydration CLI
- [`.agents/skills/cocoindex/SKILL.md`](../cocoindex/SKILL.md) —
  CocoIndex v1 App conventions (R1–R4)
- [`.agents/skills/centralized-registry/SKILL.md`](../centralized-registry/SKILL.md)
  — `MODEL_REGISTRY` resolution (no hardcoded model strings)
