# Change: Vision-model syllabus diagram generation

## Why

`tuatha/asset_generation/fibo/` is the one part of "asset generation"
genuinely implemented before this change — a real VLM-validate-and-
refine diagram generator (`generated_images`'s validation/refinement
loop, backed by `FiboResource`/`ValidationResource`) — but it was never
connected to the real `SyllabusDiagram` BAML extraction output.
`fibo_json_configs` reads from `data/concepts/<subject>_concepts.json`
if present, and falls back to a small hardcoded `SAMPLE_CONCEPTS` dict
("Covalent Bonding", "Ionic Bonding", ...) baked directly into the
function when that file doesn't exist — the normal case. Separately,
the canonical `celtic-asset-generation` spec describes 4 successive
pipelines (`official_documents/`, `subject_assets/`, `language_assets/`,
`exporters/{babylon,godot,unity,unreal}`) at a path
(`cianfhoghlaim/assets/asset_generation/`) that doesn't exist in the
live tree, targeting 6 Celtic languages and 4 game-engine exporters —
none of which this platform's actual, current architecture builds
toward (2D TanStack Start client, no Babylon.js/Godot/Unity/Unreal, no
Celtic-language asset pipeline). This change closes the first gap for
real and names the second explicitly rather than silently leaving it
uncorrected.

## What Changes

- Extend `tuatha/asset_generation/fibo/assets.py` with a new asset,
  `fibo_configs_from_syllabus_diagrams`, that calls the real (and, per
  `2026-08-08-docs-informed-quest-and-credential-generation-v1`,
  now-fixed) `ExtractSyllabusDiagram` BAML function against a
  subject's actual English-medium syllabus PDF text, and turns each
  genuinely-detected diagram into a FIBO generation config — never a
  fabricated concept. Self-contained PDF discovery (mirroring the
  relevant slice of `quest_pack_assets.py`'s heuristic, not importing
  across the `tuatha/`/`orchestration/defs/` layer boundary).
- Document, rather than silently work around, a real pre-existing
  limitation found while wiring this: `ExtractSyllabusDiagram` is
  declared `client BIEPV3Vision` but takes no `image` parameter — it
  only ever sees extracted PDF text, so detection is textual (figure
  captions, "Figure N:" references), not true vision-based bounding-
  box pointing despite the vision-client and molmo2-8b framing already
  present in the module's own docstring. Wiring a real page-image input
  through BAML is flagged as separate future work.
- Add a `Requirement: FIBO 2D educational diagram generation (as-built)`
  to the `celtic-asset-generation` spec describing the real pipeline
  that exists today (`fibo_json_configs` / `generated_images` /
  `fibo_configs_from_syllabus_diagrams`), and a correction note in the
  spec's Purpose section flagging that the "4 successive independent
  pipelines" / 6-Celtic-language / 4-game-engine-exporter description
  does not match the live tree — a full rewrite or removal of that
  aspirational content is left to a dedicated cleanup change (already
  cross-referenced by the spec's own "Asset Generation Source Schema
  Provisional" requirement), not attempted wholesale here.

## Dependencies

`Blocked by (soft): 2026-08-08-docs-informed-quest-and-credential-
generation-v1` (full per-subject coverage depends on that change's
real `SyllabusDocument`/`SyllabusDiagram` extraction fixes; this change
can run in parallel using the existing extraction functions once
they're fixed). `Affected repos: cianfhoghlaim (single repo)`

## Impact

- Capabilities: MODIFIED `celtic-asset-generation` (Purpose-section
  correction note + new as-built Requirement).
- Code: `tuatha/asset_generation/fibo/assets.py` (new
  `fibo_configs_from_syllabus_diagrams` asset + `_find_english_
  syllabus_pdf` helper), `tuatha/asset_generation/fibo/__init__.py`
  (export update).
