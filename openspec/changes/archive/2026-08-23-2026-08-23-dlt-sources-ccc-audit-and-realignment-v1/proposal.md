# 2026-08-23-dlt-sources-ccc-audit-and-realignment-v1

## Why

Per the Phase A plan, the first deliverable is a CCC audit of ALL `dlt_sources/` (1,957 files, 2,116 `@dlt.source`/`@dlt.resource` decorators across 15 sub-trees). The audit identifies the actual coverage of the lakehouse vs the BIEP v3 + per-corpus model + the sprawled-but-converged aims.

## Why now

- The dlt_sources/ tree has **1,957 Python files** but only **1 subtree (common/)** has a README.md — 14 of the 15 subtrees have no documentation
- 2,116 `@dlt.source`/`@dlt.resource` decorators but no canonical index of which tangent / phase / audience they serve
- The Phase A plan calls for realignment + per-subtree AGENTS.md
- Phase C (TG4 + Foghlaim), Phase B (Tuatha), Phase D (Apple Photos) all need the dlt_sources tree to be in a known-clean state before they can land

## Audit findings (the inventory)

### Headline numbers

| Metric | Value |
|:--|--:|
| Total `.py` files | 1,957 |
| Total `@dlt.source` | 928 |
| Total `@dlt.resource` | 1,188 |
| Total decorators | 2,116 |
| Sub-trees (15) | american_nations / api_sources / apple_photos / british_isles / common / commonwealth / crypteolas / european_nations / european_union / filesystem / jobs / language / media / official_media / portfolio |
| Sub-trees with README.md | 1/15 (only `common/`) |
| Sub-trees with AGENTS.md | 0/15 |

### Per-subtree counts

| Subtree | .py files | @dlt.source | @dlt.resource | Tangent served |
|:--|--:|--:|--:|:--|
| `american_nations/` | 51 | 24 | 24 | Americas jurisdiction (Brazil + Mexico + US + Venezuela) |
| `api_sources/` | 11 | 6 | 14 | Cross-corpus API sources (YouTube + Spotify + SoundCloud + GitHub + LinkedIn + ResearchGate + TG4 player + Foghlaim lessons) |
| `apple_photos/` | 1 | 1 | 2 | Apple Photos 5th leabharlann corpus (partial — DLT source missing) |
| `british_isles/` | 237 | 106 | 273 | BIEP v3 flagship (8 jurisdictions × 5 stages + 5 verticals) |
| `common/` | 28 | 3 | 4 | Cross-corpus helpers (destinations, registry, base classes) |
| `commonwealth/` | 633 | 292 | 292 | Commonwealth jurisdictions (AU + CA + IN + NZ + NG + ZA + official) |
| `crypteolas/` | 15 | 18 | 49 | Tuatha's Crypteolas achievement ledger (defi + github + local + docs) |
| `european_nations/` | 859 | 407 | 407 | European nations (40 jurisdictions × 5 verticals) |
| `european_union/` | 27 | 19 | 18 | EU official body (eu_pilot + Ukraine depth upgrade) |
| `filesystem/` | 17 | 8 | 39 | File system sources (leaving_cert + zotero + takeout + UoG) |
| `jobs/` | 2 | 0 | 1 | Dagster job entry points |
| `language/` | 25 | 11 | 45 | Celtic language sources (ainm + canuint + duchas + gaois + heritage + tearma + UD) |
| `media/` | 22 | 9 | 30 | Media sources (animation + comics + games + official + celtic_history + prose) |
| `official_media/` | 20 | 2 | 2 | Official media (Instagram + fediverse + companies_house + hmgcc + ggy) |
| `portfolio/` | 7 | 2 | 8 | Croilar portfolio (artwork + cv + labels + source + teaching) |

### Per-British-Isles-jurisdiction counts (the BIEP v3 flagship)

| Jurisdiction | .py files | Note |
|:--|--:|:--|
| `british_isles/ireland/` | ~120 | The flagship — 6 LC subjects + 6 JC subjects + 6 verticals |
| `british_isles/england/` | ~30 | A-Level + GCSE (3 boards × 2 levels) |
| `british_isles/scotland/` | ~25 | SQA (3 levels) |
| `british_isles/wales/` | ~20 | WJEC (Welsh-medium + EN, 2 levels) |
| `british_isles/northern_ireland/` | ~15 | CCEA (2 levels) |
| `british_isles/crown_dependencies/` | ~15 | Jersey + Guernsey + Isle of Man |
| `british_isles/_cross/` | ~12 | Cross-jurisdiction helpers (`jurisdiction_pipeline_base.py` etc.) |

### Per-European-Nation pattern (the sprawl)

| Subtree | .py files | Pattern |
|:--|--:|:--|
| `european_nations/_shared/` | 2 | `nation_source.py` (the canonical base class) |
| 40 nations × 5 verticals | ~857 | education + government + law + medicine + statistics |

This is the canonical pattern that the sprawled-but-converged aims are reaching for. The 40 nations all follow the same `_shared/nation_source.py` + per-vertical pattern.

## Realignment decisions

### Decision 1: Add 1-line AGENTS.md to each of the 15 subtrees (gap-fill documentation)

| Subtree | New AGENTS.md line (1 line each) |
|:--|:--|
| `american_nations/AGENTS.md` | `american_nations/`: the 4 Americas jurisdictions (BR + MX + US + VE) — 51 .py files, 24 @dlt.source. |
| `api_sources/AGENTS.md` | `api_sources/`: the cross-corpus API sources (YouTube + Spotify + SoundCloud + GitHub + LinkedIn + ResearchGate + TG4 player + Foghlaim) — 11 .py files, 6 @dlt.source. |
| `apple_photos/AGENTS.md` | `apple_photos/`: the 5th leabharlann corpus (macOS Photos library) — 1 .py file (the DLT source is in flight per Phase D). |
| `british_isles/AGENTS.md` | `british_isles/`: the BIEP v3 flagship (8 jurisdictions × 5 stages + 5 verticals) — 237 .py files, 106 @dlt.source. The canonical pattern lives at `_cross/jurisdiction_pipeline_base.py`. |
| `common/AGENTS.md` | (existing) |
| `commonwealth/AGENTS.md` | `commonwealth/`: the 6 Commonwealth jurisdictions (AU + CA + IN + NZ + NG + ZA) — 633 .py files, 292 @dlt.source. |
| `crypteolas/AGENTS.md` | `crypteolas/`: the Tuatha Crypteolas achievement ledger (defi + github + local + docs) — 15 .py files, 18 @dlt.source. |
| `european_nations/AGENTS.md` | `european_nations/`: the 40 European nations (each follows `_shared/nation_source.py` pattern × 5 verticals: education + government + law + medicine + statistics) — 859 .py files, 407 @dlt.source. |
| `european_union/AGENTS.md` | `european_union/`: the EU pilot + Ukraine depth upgrade — 27 .py files, 19 @dlt.source. |
| `filesystem/AGENTS.md` | `filesystem/`: the file system sources (leaving_cert + zotero + takeout + UoG) — 17 .py files, 8 @dlt.source. |
| `jobs/AGENTS.md` | `jobs/`: the Dagster job entry points (currently 1 @dlt.resource) — 2 .py files. |
| `language/AGENTS.md` | `language/`: the Celtic language sources (ainm + canuint + duchas + gaois + heritage + tearma + UD) — 25 .py files, 11 @dlt.source. |
| `media/AGENTS.md` | `media/`: the media sources (animation + comics + games + official + celtic_history + prose) — 22 .py files, 9 @dlt.source. |
| `official_media/AGENTS.md` | `official_media/`: the official media (Instagram + fediverse + companies_house + hmgcc + ggy) — 20 .py files, 2 @dlt.source. |
| `portfolio/AGENTS.md` | `portfolio/`: the Croilar portfolio (artwork + cv + labels + source + teaching) — 7 .py files, 2 @dlt.source. |

### Decision 2: Wire `british_isles/ireland/education/university_of_galway_deep.py` into the BIEP v3 5-phase pattern (the University of Galway source is currently orphaned)

The file `dlt_sources/british_isles/ireland/education/university_of_galway_deep.py` exists but is not wired into the BIEP v3 5-phase pattern (Ingestion → Materials → Model Lifecycle → Asset Generation → Agent Operations). It needs:
- A Dagster asset in `orchestration/defs/1_ingestion/uog_deep/` (the L1 ingestion layer)
- A CocoIndex v1 App for embedding
- A MotherDuck / LanceDB table

### Decision 3: Add leabharlann maths + CS education notes as canonical sources

The `leabharlann/` repo (separate from this monorepo) has maths + CS education notes that should be added as canonical sources in the lakehouse. The recommended approach:
- Add a new `dlt_sources/cianchosaint/cianchosaint/__cross/education_notes.py` (no — Cianchosaint is a separate repo, defer)
- Add a new `dlt_sources/api_sources/leabharlann_education_notes.py` (better)
- Or document that leabharlann sources are accessed via a cross-repo bridge (deferred to a future change)

### Decision 4: Wire dagster-mlflow plugin for native MLflow tracing

Dagster 1.13.18 has the `dagster-mlflow` plugin for native MLflow tracing. The current `mlflow` stack is in `bonneagar/stacks/mlflow/` (running MLflow v3.15.1 per Phase A4 work). The plugin is not currently wired.

Add `dagster-mlflow>=0.22.0` to `pyproject.toml` and update the `orchestration/definitions.py` to use `mlflow_tracking` resource.

### Decision 5: Add `cognee_health_check` Dagster sensor

Per the `indexing-and-cognition` spec, the 7 typed cognee clusters should be health-checked. Add a Dagster sensor that:
- Runs every 6 hours
- Checks each cluster's `add + cognify` endpoint
- Emits a `cognee_health` asset materialization per cluster
- Alerts via Langfuse if any cluster is down

## Spec delta

See `specs/british-isles-education-pipeline-v3/spec.md` for the 2 ADDED Requirements.

## Out of scope (deferred)

- Per-corpus DuckLake schema isolation (deferred per Phase A1 removal)
- New per-tangent sub-directories (deferred per Phase A2 decision to realign + audit)
- Cianchosaint integration (deferred per Phase 0 decision)

## Dependencies

`Blocked by: none` (the audit is the foundation)
`Blocked by (soft): 2026-08-22-concurrent-agent-write-safety-v1` (the file safety protocol)
`Affected repos: cianfhoghlaim`

## Cross-references

- `openspec/changes/2026-08-22-openspec-audit-and-merge-v1/proposal.md` — the prior audit
- `openspec/changes/2026-08-22-stale-changes-triage-v1/proposal.md` — the triage document
- `dlt_sources/DATA_PLATFORM_ROUTER.md` — the existing router
- `dlt_sources/AGENTS.md` — the existing dlt_sources AGENTS.md (251 lines)