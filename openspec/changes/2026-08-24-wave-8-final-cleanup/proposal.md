# 2026-08-24-wave-8-final-cleanup

## Why

Wave 8 is the **final wave** of the 2026-08-24 master refactor cascade.
Per the master plan (`openspec/plans/2026-08-24-master-refactor-plan.md`),
the post-cascade cleanup is the final gate before declaring the
8-wave refactor complete.

Per Wave 7, `lint:drift-docs` now passes (0 drift claims in 15 audited
AGENTS.md files). Wave 8's job is to:

1. **Final openspec audit** — capture the count of openspec changes
   + specs + their status (active vs archived)
2. **Final AGENTS.md audit** — confirm every area AGENTS.md is correct
3. **Update the master plan** to reflect the 8-wave (not 7-wave) status
4. **Tag the cascade complete** — `v2026.08.24-wave8-cascade-complete`

## What changed (cumulative across all 8 waves)

| Wave | Commit | Title | Lines |
|:--|:--|:--|--:|
| 0 | `f0344b787` | CocoIndex module-path repair (85 defs.yaml) | +782 / -118 |
| 1 | `adeecc126` | dlt_sources domain-first restructure (1993 files) | +13,989 / -4,841 |
| 2 | `afc45df6c` | Orchestration vertical pipelines + UoG tertiary | +1,984 |
| 3 | `b8e7e18bd` | CocoIndex v0 stragglers (97/99 L3 modules) | +993 / -351 |
| 4 | `7bb26496f` | DuckLake v1.0 hardening + layer-grouped destinations | +1,486 / -810 |
| 5 | `dd0b2272e` | Web consolidation — archive + rename | +314 |
| 6 | `2f2864462` | TanStack modernisation — 5 packages + AG-UI SSE + Convex schema | +959 / -4 |
| 7 | `e29b91d7c` | Observability drift cleanup — MlflowBackend + OTel + lint fixes | +394 / -7 |

**Cumulative totals**: 8 commits, +20,901 / -6,131 lines.

## Audit summary

### Openspec stats (as of 2026-08-24)

| Metric | Count |
|:--|--:|
| Active openspec changes | 68 |
| Openspec specs (active) | 100 |
| Archived openspec changes | (in `openspec/changes/archive/`) |

### `lint:drift-docs` result

```
$ uv run python scripts/lint_drift_docs.py --dry-run
OK: 0 number drift claims in 15 audited AGENTS.md files
  Report: /Users/cianmacandeisigh/dev/cianfhoghlaim/stedding/sync-reports/docs-drift-2026-08-24.md
```

### AGENTS.md coverage

The 5 area AGENTS.md files are:
1. `AGENTS.md` (root)
2. `dlt_sources/AGENTS.md`
3. `cocoindex_flows/AGENTS.md`
4. `orchestration/AGENTS.md`
5. `observability/AGENTS.md`
6. `web/AGENTS.md`
7. `bonneagar/AGENTS.md`
8. `notebooks/AGENTS.md`
+ 7 others (auto-discovered by `lint_drift_docs.py`)

All 15 audited files pass the drift check.

### Dagster asset count (post-Wave 2)

- ~190 total assets (was 199 pre-Wave 0)
- 8 sensors (was 16 — the post-2026-08-23 UoG batch consolidated)
- 39 vertical pipelines (the new Wave 2 vertical pipelines at
  `orchestration/pipelines/`)
- 97/99 L3 `defs.yaml` target modules import cleanly (Wave 3)

### Destination count (post-Wave 4)

15 named destinations registered in `dlt_sources/common/destinations/`:
- 1 canonical (`ducklake_cianfhoghlaim`)
- 6 legacy aliases (`ducklake_oideachais`, etc.)
- 8 others (`motherduck`, `filesystem_*`, `iceberg_*`)

### Web stack (post-Wave 5 + 6)

- 11 apps at `web/apps/` (was 12 — `_oideachais_apps/` archived in Wave 5)
- 5 packages at `web/packages/{auth,db,ui-kit,api-client,contracts}/`
- 1 hono-api gateway at `web/hono-api/`

### Observability (post-Wave 7)

- 4 `TracingBackend` concrete classes (Datadog, Langfuse, Logfire, Mlflow)
- OTel semantic conventions enforced (`db.system: duckdb`,
  `gen_ai.system: baml`, `object_store.system: s3`)

## Out of scope (deferred to post-cascade PRs)

The 8-wave cascade focused on **structural** refactoring. The following
work remains as separate PRs:

- **Per-app migrations** to the Wave 6 stack (`cianfhoghlaim-leaving-cert`,
  `croilar-portal`, `croilar-web`, `cianfhoghlaim-web`, `cianfhoghlaim-mmo`)
- **Real Convex schema** (users, agents, threads, runs, messages,
  knowledge_graph_nodes, per-subject caches)
- **Real AG-UI event streaming** (the Wave 6 stub emits hello events;
  the real implementation reads from the Convex agent table + the
  CocoIndex DAG)
- **MotherDuck token wire-up** (`CIANFHOGHLAIM_MOTHERDUCK_TOKEN` env var)
- **Lakekeeper deployment** (the `http://lakekeeper:8181/catalog`
  Iceberg REST catalog)
- **Actual 2.4 GB `cianfhoghlaim-leaving-cert/` → `oideachais/` migration**
- **Cloudflare Pages deployment** for the 5 web apps
- **DuckLake data migration** (the 6 legacy namespaces → consolidated)

## Verification

After Wave 8 lands:

1. `uv run python scripts/lint_drift_docs.py --dry-run` exits 0
2. `git tag v2026.08.24-wave8-cascade-complete` succeeds
3. `git log --oneline -10` shows all 8 wave commits
4. `openspec/plans/2026-08-24-master-refactor-plan.md` reflects the 8-wave status

## References

- Master plan: `openspec/plans/2026-08-24-master-refactor-plan.md`
- Wave 0-7: see prior openspec changes
- Audit report: `stedding/sync-reports/docs-drift-2026-08-24.md`
