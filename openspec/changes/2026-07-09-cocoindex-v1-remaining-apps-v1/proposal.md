# Proposal: CocoIndex v1 — Migrate the 14 remaining priority flows + wire v1 conformance as a CI gate

## Why

The five-tangent modernization change
(`2026-07-08-five-tangent-modernization`) shipped the
`cocoindex_v1_migrate.py` audit tool (the 4-rule R1+R2+R3+R4
checker) and migrated the 6 BIEP LC subject flows
(`mathematics_embedding.py`, `chemistry_embedding.py`,
`geography_embedding.py`, `gaeilge_embedding.py`,
`english_embedding.py`, `computer_science_embedding.py`) +
`government_circulars_embedding.py` to v1 conformance — 7/47
flows now pass. The other 14 priority flows from the 22-list
declared in the openspec MODIFIED note on
`oideachais-cocoindex-v1-migration` remain on the older
`@coco.App(shared_lifespan)` decorator pattern (which passes
the R2 regex but still misses `declare_vector_index`) or are
skeleton files with no `coco.App(...)` at module scope.

Without migration, the BIEP-v1 architecture is incomplete
and the 4-rule conformance contract is documented but never
enforced. This change closes the gap:

1. Migrates the 14 remaining priority flows to R1+R2+R3+R4
   conformance (4 of the 22 listed flows don't exist as
   standalone files — `leabharlann_zotero_embedding.py`,
   `leabharlann_takeout_embedding.py`,
   `official_media_feed_embedding.py`,
   `official_media_post_embedding.py` — they live as inner
   apps in `leabharlann_embedding.py` and
   `unified_embedding.py`, both of which are in this batch).
2. Adds `orchestration/defs/3_model_lifecycle/cocoindex_v1/<app>/defs.yaml`
   for the 11 non-LC CocoIndex v1 Apps (the L3 model-lifecycle
   Component mount via the
   `dagster-5-layer-component-architecture` 5-layer KCG pattern).
3. Wires the conformance check as a CI gate via the new
   `mise run cocoindex:conformance` task (hard fail on any
   R1/R2/R3/R4 violation) and a new
   `.github/workflows/cocoindex-conformance.yaml` workflow
   (PR-comment + artifact upload).
4. Adds `R4-exempt: <reason>` marker support to the audit tool
   for non-LanceDB Apps (the `apple_photos_geospatial.py`
   GeoParquet App is the canonical example — it has no
   `embedding` column, so `declare_vector_index` is N/A).

## What changes

### 1. Audit tool (1 file)

- `cianfhoghlaim/dlt/common/cocoindex_v1_migrate.py` — add
  R4-exempt marker support (`# R4-exempt: <reason>` on a
  standalone line exempts the file from R4). Document the
  marker in the docstring. Make the existing `--apply` mode
  a no-op (deferred to future work; today's migrations are
  hand-curated for the per-flow shape).

### 2. Flow migrations (14 files)

The 14 priority flows that fail the audit:

- `agent_registry.py` — R4 (needs `declare_vector_index`)
- `apple_photos_metadata.py` — R4
- `apple_photos_chunks.py` — R4
- `apple_photos_geospatial.py` — R4-exempt (GeoParquet, no embedding column)
- `codebase_indexing.py` — R4 (the `codebase_chunks` table needs the index)
- `cocoindex_v1_conformance.py` — R4 (the `conformance_check_history` table needs the index)
- `cross_subject_competency_embedding.py` — R3+R4 (full rewrite from old `lancedb.TableTarget(db=..., embedding=...)` to canonical `lancedb.mount_table_target` + `declare_vector_index`)
- `history_embedding.py` — R3+R4
- `ireland_legal_embedding.py` — R4
- `leabharlann_embedding.py` — R4
- `leabharlann_flow.py` — R1+R3+R4 (skeleton — convert to a real v1 App)
- `ocr_aware_flow.py` — R1+R3+R4 (skeleton — convert to a real v1 App)
- `unified_embedding.py` — R2-old + R4 (still has `@cocoindex.flow` reference + missing `declare_vector_index`)
- `university_embedding.py` — R4
- `upstream_api_surface.py` — R4
- `upstream_blog_monitor.py` — R4

That's 16 files; the first 14 are the bulk R4-only fixes;
`cross_subject_competency_embedding.py`,
`leabharlann_flow.py`, `ocr_aware_flow.py`, and
`unified_embedding.py` need more substantial rewrites.

The 4 priority-list flows that **don't exist as standalone
files** (per the original 22-list comment: "may not exist as
standalone"):

- `leabharlann_zotero_embedding.py` — lives as
  `leabharlann_embedding.leabharlann_zotero_app`
- `leabharlann_takeout_embedding.py` — lives as
  `leabharlann_embedding.leabharlann_takeout_app`
- `official_media_feed_embedding.py` — does not exist; the
  official-media pipeline uses `leabharlann_inbox` and
  `unified_embedding` instead
- `official_media_post_embedding.py` — does not exist

These are documented in the priority list as aspirational
references to flows that were folded into the consolidated
apps in `leabharlann_embedding.py` and `unified_embedding.py`.

### 3. L3 Dagster Component mounts (11 new defs.yaml files)

Add Component YAMLs to
`orchestration/defs/3_model_lifecycle/cocoindex_v1/<app>/defs.yaml`
for each non-LC App that doesn't already have one:

- `agent_registry`
- `apple_photos_metadata`
- `apple_photos_chunks`
- `apple_photos_geospatial`
- `cross_subject_competency_embedding`
- `cv_embedding`
- `history_embedding`
- `leabharlann_flow`
- `mythology_embedding`
- `ocr_aware_flow`
- `root_pdfs_embedding`

That's 11 new Component YAMLs. The 5-layer
`CelticModelLifecycleComponent` wraps each as an
`is_virtual=True` AssetSpec so the LanceDB table mirrors its
L1 upstream automatically.

Add the canonical `daily_cocoindex_v1_assets_materialize`
schedule (cron `0 3 * * *` = 03:00 UTC) at
`orchestration/defs/3_model_lifecycle/cocoindex_v1/_schedules/defs.yaml`.

### 4. CI gate (2 files)

- `mise.toml` — add `[tasks.cocoindex.conformance]` running
  `uv run python cianfhoghlaim/dlt/common/cocoindex_v1_migrate.py --check-only`
  (exits 1 on any R1/R2/R3/R4 violation; the existing
  `cic:cocoindex:conformance` task calls the
  `cocoindex_v1_conformance` App which is more expensive and
  not suitable as a CI gate).
- `.github/workflows/cocoindex-conformance.yaml` — new workflow
  triggered on PRs + pushes to `main`/`pick-4-biep-v1` that:
  - Runs `mise run cocoindex:conformance`
  - Posts a PR-comment via `peter-evans/create-or-update-comment`
    on failure (the violation table + the failing flow list)
  - Uploads the per-flow audit report as a build artifact
  - Fails the build if any R1/R2/R3/R4 violation is detected

### 5. Spec delta (1 file)

Extend the existing `oideachais-cocoindex-v1-migration` spec
with 2 ADDED Requirements:

- **22-priority flow migration batch completed** — every
  flow in the priority list satisfies the 4-rule R1+R2+R3+R4
  conformance contract (or has a documented `# R4-exempt:
  <reason>` marker if it doesn't write to LanceDB).
- **v1 conformance check as CI gate** — `mise run
  cocoindex:conformance` runs on every PR + push, fails the
  build on any R1/R2/R3/R4 violation, and posts a PR comment
  with the violation table.

This bumps the spec from 2 → 7 Requirements (5 ADDED + 3 MODIFIED
from the 5-tangent change plus this change's 2 ADDED = 7 total).

## Acceptance gates

- `openspec validate 2026-07-09-cocoindex-v1-remaining-apps-v1 --strict` passes
- `uv run python cianfhoghlaim/dlt/common/cocoindex_v1_migrate.py --check-only` reports
  all 14 existing priority flows PASS (the 4 non-existent flows are documented
  as "may not exist" in the priority-list output, no audit expectation)
- The conformance count goes from 7/47 → 22/47 flows pass
  (the 14 newly-migrated + the 1 exempt + the 7 already passing)
- `mise run cocoindex:conformance` exits 1 in CI on any R1-R4 violation
- The new `.github/workflows/cocoindex-conformance.yaml` is wired
  and runs in CI

## Push target

`origin/pick-4-biep-v1` (per the 5-tangent engagement pre-flight).

## Out of scope

- The 10 v0 archived modules (per the existing spec's V0 Archive requirement)
- The 4 "may not exist" priority flows — documented, not migrated
- The BAML streaming + fallback convention marker (T3 of the 5-tangent engagement)
- The named destinations + filesystem SQL client (T1 of the 5-tangent engagement)

Refs:
- `openspec/changes/2026-07-08-five-tangent-modernization/specs/oideachais-cocoindex-v1-migration/spec.md` (the MODIFIED delta that bumped to 8 Requirements)
- `openspec/specs/dagster-5-layer-component-architecture/spec.md` (the 5-layer KCG Components pattern)
- `openspec/specs/oideachais-cocoindex-v1-migration/spec.md` (the canonical v1 CocoIndex migration spec)