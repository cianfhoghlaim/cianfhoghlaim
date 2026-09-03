"""Junior Cycle Dagster assets (BIEP v2).

Per the 2026-07-20-biep-v2-junior-cycle-extraction-v1 change.

The 72+ JC Dagster assets live under
`orchestration/defs/2_materials/junior_cycle/`:

- `subjects/` — 18 subjects × 4 layers = 72 assets (per-subject)
  - `jc_<subject>_ingested` (Layer 1 — DLT source)
  - `jc_<subject>_curriculum_extracted` (Layer 2 — BAML ExtractJCCurriculum)
  - `jc_<subject>_embedding_flow` (Layer 3 — CocoIndex v1)
  - `jc_<subject>_cognified` (Layer 4 — Cognee)
- `short_courses/` — 16 short-course composite assets
- `cbas/` — 36 CBA assets (1 per CBA)
- 1 cross-subject Graphiti stream
- 1 orchestrator composite asset

All assets use the 5-layer group_name convention `<N>_<layer>/<domain>/<slug>`.

The asset `defs.yaml` files are colocated next to their assets in the
3 subdirectories above. The 5-layer component architecture that
all 72+ assets obey is documented in
`openspec/specs/dagster-5-layer-component-architecture/spec.md`.
"""
