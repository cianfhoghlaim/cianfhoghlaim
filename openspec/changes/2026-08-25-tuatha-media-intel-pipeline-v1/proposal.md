# Change: tuatha-media-intel-pipeline (v1)

## Why

We need a reproduction-grade pipeline that turns game + comic + GBA
captures into typed BAML records + embeddings so the British Isles
Formative Assessment MMO can populate the ANAM particle corpus (the
turquoise/blue primary currency + the Celtic-deity counterpart set).

The user explicitly identified **Hades**, **Absolute Superman** (DC,
Jason Aaron 2024-), and **Golden Sun** (GBA, Camelot) as the first three
sources. The Hades corpus maps to the 10 Olympians → 10 Tuatha Dé
deities. The Absolute Superman corpus maps the red dust of Krypton →
the ANAM turquoise/blue particle. The Golden Sun corpus maps the 4
elements (Venus/Mars/Jupiter/Mercury) → the Tuatha 4-element binding.

We will not commit copyrighted game frames, comic pages, or BLOB assets
to the repository (per the `tuatha` skill `shippable: false` invariant):
the full-resolution assets stay in a Pangolin-private volume; the Lance
fat tables store only a downsampled thumb + the BAML-extracted
description + the embedding.

## What changes

1. New `baml_src/tuatha_media_intel.baml` — 3 typed classes
   (HadesBoon / ComicParticleFrame / GbaMagicSystem) + 1 join class
   (AnamParticle) + 5 functions.
2. New `cocoindex_flows/tuatha_media_intel/` — 4 v1 Apps
   (hades_boons / comic_particles / gba_magic / anam_particles) +
   shared `_shared/__init__.py` lifespan.
3. New `tuatha_media_intel/capture/tuatha-capture/` — Swift Package
   Manager CLI wrapping Apple ScreenCaptureKit + hevc_videotoolbox,
   with a JSON-RPC unix socket for control.
4. New `tuatha_media_intel/capture/python/` — Python capture shims for
   the GBA (mgba-py + libmgba) + comic (CBZ / Pillow / scikit-learn)
   flows.
5. New `orchestration/defs/2_materials/tuatha_media_intel.py` — 8
   Dagster assets (capture × 3, embed × 3, join × 1, RAGAS asset_check).
6. New `bonneagar/stacks/tuatha-media-intel/` — 6-file GOLD_STANDARD
   Docker Compose stack (cocoindex-runner + baml-codegen +
   ragas-evaluator + mlflow-sidecar + locket).
7. New `notebooks/tuatha_anam_dashboard.py` + `notebooks/tuatha_anam/`
   — 4-tab marimo design surface (Sources / Boons / Particles / Join).
8. New `agents/meaisinfhoghlaim/tuatha_capture_agent.py` — the ADK
   agent that owns the Hermes Phase 2 control loop (Phase 1 stubbed).
9. New `dlt_sources/tuatha_media_intel/{hades,comic,gba}/source.yaml`
   — the 3 source manifests with `legal_notes` populated.

## Impact

- Affected specs:
  - `openspec/specs/cianfhoghlaim-educational-mmo/spec.md` (del §11
    to add the ANAM pipeline cross-reference).
  - `openspec/specs/british-isles-formative-assessment/spec.md`
    (del §5 to add the 4-element binding source).
  - `openspec/specs/centralized-model-registry/spec.md` (del §11 OCR/VLM
    Pipeline to add 3 new vision model entries if not present).
  - `openspec/specs/dual-search-architecture/spec.md` (no del — the
    Lance multimodal fat table fits the existing §3 pattern).
- Affected stacks:
  - `bonneagar/stacks/tuatha-media-intel/` (new stack).
- Affected assets:
  - 8 new Dagster assets in `tuatha_capture` + `tuatha_embed` +
    `tuatha_join` + `tuatha_quality` groups.

## Out of scope

- Babylon.js 3D game front-end (HARD-ARCHIVED per the 2026-08-25
  consolidation change).
- Pent-Elemental Cosmology theming (HARD-ARCHIVED per the same change).
- The Celtic MMO design itself (gated on this corpus being populated).
- Hermes Agent computer-use activation (Phase 2 stub only).

## Verification

1. `mise run coc:stack-doctor` passes for `tuatha-media-intel`.
2. `mise run lint:registry --strict` exits 0 (no hardcoded model strings).
3. `baml-cli test baml_src/tuatha_media_intel.baml` passes the 3 test cases.
4. `swift build -c release` in `tuatha-capture/` succeeds.
5. First end-to-end run:
   - Start the Swift daemon via the LaunchAgent.
   - Open Hades → daemon captures → manifest.jsonl grows.
   - Trigger `mise run cocoindex:update tuatha_hades_boons`.
   - Verify the Lance fat table contains rows via the marimo notebook.
   - Verify the Langfuse trace + MLflow metric are populated.
6. RAGAS asset_check `ragas_anam_color_anchor` passes (threshold ≥ 0.85).
