## Shipped in code

All work proposed here has been delivered to the codebase since this change was opened. The remaining tasks are validation gates + the final `openspec archive` call.

# Extend the `cianfhoghlaim-marimo-dashboards` capability (Phase 2)

## Why

The `cianfhoghlaim-marimo-dashboards` capability shipped its first 10 dashboards
at `notebooks/10_marimo_dashboards/` via commit `44cabc151`. Those 10
dashboards covered the BIEP v1 corpus, Cognee knowledge graph, cross-archive
navigation, lakehouse table browser, BAML extraction log viewer, per-subject
analytics, Gaeilge language coverage, CocoIndex v1 conformance, agent memory,
and Dagster asset lineage.

The leabharlann corpus (216 docs × 6 subdirs), the university extraction
(8 universities + 5 TUs + QQI coverage), the cross-archive edges (BIEP ↔
leabharlann, BIEP ↔ official-media, leabharlann ↔ culture-heritage), and the
K-12 → university year-level pipeline coverage all need their own operator-
facing dashboards. The Phase-1 dashboards left these surfaces visible only
through SQL queries or the cognify KG.

This change ships **10 additional marimo dashboards** (Phase 2) at
`notebooks/11_marimo_dashboards_v2/`. Each follows the same
300-400 LOC pattern from the prior commit `44cabc151` (PEP 723 inline deps,
`duckdb.connect("md:oideachais")` with graceful local-DuckDB fallback,
synthetic-data fallback for offline development, altair charts, mo.ui.altair_chart
panels, and a health banner).

## What changes

- New subdir `notebooks/11_marimo_dashboards_v2/` with **10
  dashboards** (01..10):
  - 01-03 — **leabharlann corpus dashboards** (corpus overview, 6-subdir
    matrix, BGE-M3 embedding coverage)
  - 04-05 — **university extraction dashboards** (institution matrix for
    8 universities + 5 TUs + QQI coverage)
  - 06-08 — **cross-archive edges** (BIEP ↔ leabharlann, BIEP ↔
    official-media, leabharlann ↔ culture-heritage)
  - 09-10 — **K-12 → university pipeline coverage** (per-stage matrix +
    year-level coverage)
- `notebooks/cli.py` — added `11_marimo_dashboards_v2` to
  the `GROUPS` tuple (so `cianfhoghlaim-marimo list 11_marimo_dashboards_v2`
  discovers the new entries)
- 1 MODIFIED spec delta on `cianfhoghlaim-marimo-dashboards/spec.md` —
  adds requirement R-v2 (Phase 2 complete: 5-10 additional marimo
  dashboards at `notebooks/11_marimo_dashboards_v2/0[1-9]_*.py` +
  `10_*.py` ship the leabharlann corpus + university extraction +
  cross-archive edges + K-12 → university pipeline coverage)

## Non-goals

- Do NOT touch the 10 existing dashboards at
  `notebooks/10_marimo_dashboards/`
- Do NOT touch the 50+ archived openspec changes under
  `openspec/changes/archive/*`
- Do NOT touch the 7 `baml/education/lc_extraction/*.baml` files (owned
  by the BIEP v1 change)

## Dependencies

Blocked by: `2026-07-14-cianfhoghlaim-marimo-dashboards-v1` (the
Phase-1 commit `44cabc151` that shipped the first 10 dashboards).
This change can archive only after the Phase-1 commit lands on
`main` (already done — Phase 1 archived 2026-07-14).

## Cross-repo sync

Single-repo change (all paths under `cianfhoghlaim/` and
`openspec/`). No `bonneagar/` or `leabharlann/` touchpoints.

## Dependencies

- `Blocked by: 2026-07-14-cianfhoghlaim-marimo-dashboards-v1` (the
  Phase-1 commit `44cabc151` that shipped the first 10 dashboards)
  — already archived on 2026-07-14.
- `Blocked by (soft): 2026-07-14-cianfhoghlaim-cognify-knowledge-graph-v1`
  (the cross-archive cognify pass that produces the edge tables
  consumed by the 06-08 cross-archive edge dashboards) — already
  archived on 2026-07-14.
- `Affected repos: cianfhoghlaim` (only).