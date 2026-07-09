# Tasks — CocoIndex v1 remaining-apps migration + CI gate

Mirror of the 5 concrete work items in `proposal.md`.

## 1. Drop the audit tool from `1d94711c1` into `dlt/common/`

- [x] Copy `cianfhoghlaim/dlt/common/cocoindex_v1_migrate.py` from commit
  `1d94711c1` (the 5-tangent modernization).
- [x] Run `--check-only` to confirm the baseline: 7/47 flows pass.
- [x] Add `# R4-exempt: <reason>` marker support so
  `apple_photos_geospatial.py` (GeoParquet output, no embedding column)
  can be exempted from R4.
- [x] Document the marker in the docstring + update the R4 violation message.

## 2. Migrate the 14 existing priority flows to v1 conformance

### R4-only fixes (12 flows — add `declare_vector_index(column="embedding")`)

- [x] `agent_registry.py` — the `agent_registry` LanceDB table needs `declare_vector_index(column="embedding")`.
- [x] `apple_photos_metadata.py` — same.
- [x] `apple_photos_chunks.py` — same.
- [x] `codebase_indexing.py` — the `codebase_chunks` table (only — `codebase_graph` + `codebase_graph_edges` are not vector tables).
- [x] `cocoindex_v1_conformance.py` — the `conformance_check_history` table needs `declare_vector_index(column="embedding")`.
- [x] `history_embedding.py` — R3+R4: the embedder source is missing in the existing flow; rebuild from the mathematics_embedding.py template.
- [x] `ireland_legal_embedding.py` — same R4-only fix.
- [x] `leabharlann_embedding.py` — same R4-only fix (3 inner apps).
- [x] `university_embedding.py` — same R4-only fix (2 inner apps).
- [x] `upstream_api_surface.py` — same R4-only fix.
- [x] `upstream_blog_monitor.py` — same R4-only fix.

### R4-exempt (1 flow)

- [x] `apple_photos_geospatial.py` — GeoParquet output; no embedding column. Add `# R4-exempt: GeoParquet output, no embedding column` marker.

### Substantial rewrites (3 flows)

- [x] `cross_subject_competency_embedding.py` — rewrite from the old `lancedb.TableTarget(db=..., embedding=embedder.embedding())` pattern to the canonical `lancedb.mount_table_target` + `declare_vector_index(column="embedding")` pattern.
- [x] `leabharlann_flow.py` — convert the skeleton (no `coco.App(...)` at module scope) to a real v1 App using the `leabharlann_embedding.py` template. The 6 corpora share a single `leabharlann_chunks` LanceDB table.
- [x] `ocr_aware_flow.py` — convert the skeleton (no `coco.App(...)` at module scope) to a real v1 App using the `leabharlann_embedding.py` template. The Ireland syllabus corpus walks the 5 educational stages + emits `ireland_syllabus_chunks`.
- [x] `unified_embedding.py` — remove the legacy `@cocoindex.flow` reference + add `declare_vector_index(column="embedding")` to the 2 inner apps.

## 3. Add 11 new L3 Dagster Component YAMLs

For each non-LC App that doesn't already have a `defs.yaml` in
`orchestration/defs/3_model_lifecycle/cocoindex_v1/<app>/`:

- [x] `agent_registry/defs.yaml`
- [x] `apple_photos_metadata/defs.yaml`
- [x] `apple_photos_chunks/defs.yaml`
- [x] `apple_photos_geospatial/defs.yaml`
- [x] `cross_subject_competency_embedding/defs.yaml`
- [x] `cv_embedding/defs.yaml`
- [x] `history_embedding/defs.yaml`
- [x] `leabharlann_flow/defs.yaml`
- [x] `mythology_embedding/defs.yaml`
- [x] `ocr_aware_flow/defs.yaml`
- [x] `root_pdfs_embedding/defs.yaml`

Each uses `type: cianfhoghlaim.orchestration.components.CelticModelLifecycleComponent`
with `app_name`, `module`, `embedding_model: BAAI/bge-large-en-v1.5`,
`hnsw_index: true`, `conformance_required: true`.

## 4. Add the `daily_cocoindex_v1_assets_materialize` schedule

- [x] `orchestration/defs/3_model_lifecycle/cocoindex_v1/_schedules/defs.yaml` —
  cron `0 3 * * *` (03:00 UTC), targets `group:cocoindex_v1/*`.

## 5. Wire the CI gate

- [x] `mise.toml` — add `[tasks.cocoindex.conformance]` running the audit tool.
- [x] `.github/workflows/cocoindex-conformance.yaml` — new workflow triggered on
  PRs + pushes to `main`/`pick-4-biep-v1`. Runs `mise run cocoindex:conformance`,
  posts a PR comment via `peter-evans/create-or-update-comment` on failure,
  uploads the audit report as a build artifact, fails the build on any violation.

## 6. Spec delta

- [x] `openspec/changes/2026-07-09-cocoindex-v1-remaining-apps-v1/specs/oideachais-cocoindex-v1-migration/spec.md` —
  ADDED Requirements "22-priority flow migration batch completed" +
  "v1 conformance check as CI gate". Bumps spec from 2 → 7 Requirements.

## 7. Validate + push

- [x] `openspec validate 2026-07-09-cocoindex-v1-remaining-apps-v1 --strict`
- [x] `uv run python cianfhoghlaim/dlt/common/cocoindex_v1_migrate.py --check-only` →
  22/22 of the existing priority flows pass
- [x] `git add ... && git commit -m "..." && git push origin pick-4-biep-v1`

## Open questions

None at submit time. The 4 non-existent priority flows
(`leabharlann_zotero_embedding.py`,
`leabharlann_takeout_embedding.py`,
`official_media_feed_embedding.py`,
`official_media_post_embedding.py`) are documented in the
priority-list output as "may not exist as standalone" and
are not migrated here — they live as inner apps in
`leabharlann_embedding.py` and `unified_embedding.py`
which are in this batch.