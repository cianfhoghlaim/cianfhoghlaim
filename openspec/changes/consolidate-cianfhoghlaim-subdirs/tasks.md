# consolidate-cianfhoghlaim-subdirs — Tasks (slimmed-down scope: Phases 1-6 only)

## Phase 1 — Fix the 14 broken `dlt_sources.{nation}.law.legislation` imports

### Phase 1a — Restore the 6 missing nations in `dlt/british_isles/`

- [ ] 1a.1 Audit `dlt/british_isles/{sct,wls,ni,ggy,iom,jey}/law/` —
  check what (if anything) exists at these paths
- [ ] 1a.2 For each missing nation, create
  `dlt/british_isles/{nation}/law/__init__.py` that re-exports from
  `dlt/domains/{nation}/law/legislation.py` (using the `dlt.domains/`
  shape from the v3 plan)
- [ ] 1a.3 For each missing nation, create
  `dlt/british_isles/{nation}/medicine/__init__.py` that re-exports
  from `dlt/domains/{nation}/medicine/{source}.py`
- [ ] 1a.4 If `dlt/domains/{nation}/{law,medicine}/` doesn't exist
  for any of the 6 nations, create them as STUBS (single
  `@dlt.source` function that yields 0 rows) so the dagster assets
  can materialise without `ImportError`

### Phase 1b — Fix the 14 dagster assets

- [ ] 1b.1 `dagster/assets/law/en/__init__.py` — fix the
  `from dlt_sources.en.law.legislation import en_legislation_source`
  import to point at `dlt/domains/en/law/legislation`
- [ ] 1b.2 `dagster/assets/law/ggy/__init__.py` — same
- [ ] 1b.3 `dagster/assets/law/iom/__init__.py` — same
- [ ] 1b.4 `dagster/assets/law/jey/__init__.py` — same
- [ ] 1b.5 `dagster/assets/law/ni/__init__.py` — same
- [ ] 1b.6 `dagster/assets/law/sct/__init__.py` — same
- [ ] 1b.7 `dagster/assets/law/wls/__init__.py` — same
- [ ] 1b.8 `dagster/assets/medicine/en/__init__.py` — fix to
  `dlt/domains/en/medicine/{source}`
- [ ] 1b.9 `dagster/assets/medicine/ggy/__init__.py` — same
- [ ] 1b.10 `dagster/assets/medicine/iom/__init__.py` — same
- [ ] 1b.11 `dagster/assets/medicine/jey/__init__.py` — same
- [ ] 1b.12 `dagster/assets/medicine/ni/__init__.py` — same
- [ ] 1b.13 `dagster/assets/medicine/sct/__init__.py` — same
- [ ] 1b.14 `dagster/assets/medicine/wls/__init__.py` — same

### Phase 1 validation

- [ ] 1c.1 `ccc search "dlt_sources\.\\w+\.law"` returns 0 hits
- [ ] 1c.2 `python -c "from cianfhoghlaim.dlt.british_isles.en.law import en_legislation_source"` succeeds

## Phase 2 — Collapse the 14 single-asset nation __init__.py files

- [ ] 2.1 Create `dagster/assets/by_domain/__init__.py` with re-exports
  for backward compat
- [ ] 2.2 Create `dagster/assets/by_domain/law.py` with the 7
  law_nation_legislation @assets
- [ ] 2.3 Create `dagster/assets/by_domain/medicine.py` with the 7
  medicine_nation_* @assets
- [ ] 2.4 `git rm dagster/assets/law/{en,ggy,iom,jey,ni,sct,wls}/__init__.py`
  (7 files)
- [ ] 2.5 `git rm dagster/assets/medicine/{en,ggy,iom,jey,ni,sct,wls}/__init__.py`
  (7 files)
- [ ] 2.6 `git rm dagster/assets/ie/law/__init__.py dagster/assets/ie/medicine/__init__.py`
  (2 empty files)

### Phase 2 validation

- [ ] 2.7 `dg list defs` shows the new `by_domain` shape
- [ ] 2.8 The 14 old `law_{nation}_*` / `medicine_{nation}_*` asset
  names are replaced by `by_domain.law.{nation}_legislation` /
  `by_domain.medicine.{nation}_*`

## Phase 3 — Storage graph unification

- [ ] 3.1 Verify `storage/_shared/{falkordb,memgraph,neo4j,interface}.py`
  are the canonical home (already exists per the v4 consolidation)
- [ ] 3.2 `git rm storage/falkordb_client.py` (duplicate of
  `storage/_shared/falkordb.py`)
- [ ] 3.3 `git rm storage/memgraph_client.py` (duplicate)
- [ ] 3.4 `git rm storage/temporal.py` (the hand-rolled pure-Python
  Graphiti-in-Python implementation; replaced by `storage/temporal_client.py`
  which wraps `graphiti_core`)
- [ ] 3.5 Update `storage/__init__.py` to re-export from `_shared/` and
  `temporal_client.py` instead of the deleted top-level files
- [ ] 3.6 Verify there are no remaining imports of the deleted files:
  `ccc search "from cianfhoghlaim.storage.falkordb_client"`,
  `ccc search "from cianfhoghlaim.storage.memgraph_client"`,
  `ccc search "from cianfhoghlaim.storage.temporal import"`

### Phase 3 validation

- [ ] 3.7 `python -c "from cianfhoghlaim.storage.falkordb import falkordb_client"` succeeds
- [ ] 3.8 `ls storage/_shared/` shows falkordb.py + memgraph.py + neo4j.py + interface.py

## Phase 4 — Move `notebooks/croilar/` to croilar-portal

- [ ] 4.1 Create `cianfhoghlaim/web/apps/croilar-portal/notebooks/` directory
- [ ] 4.2 `git mv` the 8 files from `cianfhoghlaim/notebooks/croilar/` to
  `cianfhoghlaim/web/apps/croilar-portal/notebooks/`:
  - `baml_extraction_quality.py`
  - `convex_function_latency.py`
  - `cv_dashboard.py`
  - `github_insights.py`
  - `music_analytics.py`
  - `music_analytics_2.py`
  - `teaching_analytics.py`
  - `web_route_health.py`
- [ ] 4.3 Verify the croilar-portal app picks up the notebooks (may
  need a `vite.config.ts` or `package.json` config update)

## Phase 5 — Rename `_tuatha_src/` to canonical

- [ ] 5.1 Audit `cianfhoghlaim/tuatha/asset_generation/_tuatha_src/` for
  files that would conflict with the existing
  `cianfhoghlaim/tuatha/asset_generation/` directory
- [ ] 5.2 `git mv` the non-conflicting files from
  `tuatha/asset_generation/_tuatha_src/` → `tuatha/asset_generation/`
- [ ] 5.3 Merge any conflicting files (resolve via the v4 spec —
  typically `_tuatha_src/` has the canonical Python source and
  `tuatha/asset_generation/` has the Dagster defs)
- [ ] 5.4 Update the 6 import sites that reference
  `tuatha.asset_generation._tuatha_src` to point at the canonical path
- [ ] 5.5 `git rm` the now-empty `_tuatha_src/` directory

### Phase 5 validation

- [ ] 5.6 `ccc search "_tuatha_src"` returns 0 hits
- [ ] 5.7 `python -c "from cianfhoghlaim.tuatha.asset_generation import asset_service"` succeeds

## Phase 6 — Web apps cleanup

- [ ] 6.1 Audit `web/_croilar_config/`, `web/_croilar_shared/`,
  `web/_oideachais_dashboard/` for remaining files
- [ ] 6.2 `git rm -r web/_croilar_config/` (if empty per the archived
  `per-domain-web-app-consolidation` change)
- [ ] 6.3 `git rm -r web/_croilar_shared/` (if empty)
- [ ] 6.4 `git rm -r web/_oideachais_dashboard/` (if empty — mostly
  already deleted per the in-flight 7-phase change)
- [ ] 6.5 Verify the oideachais web app is mounted at
  `web/apps/oideachais-web/` (canonical workspace path)

### Phase 6 validation

- [ ] 6.6 `ls web/_croilar_config web/_croilar_shared web/_oideachais_dashboard`
  returns "No such file or directory"
- [ ] 6.7 `ccc search "_croilar_config\|_croilar_shared\|_oideachais_dashboard"` returns 0 hits in the active `web/` subtree

## Final validation

- [ ] 7.1 `openspec validate consolidate-cianfhoghlaim-subdirs --strict` passes
- [ ] 7.2 All 6 phase validations pass
- [ ] 7.3 No new broken imports introduced (run `python -c "from cianfhoghlaim.dagster.definitions import defs; print(len(defs.assets))"` to verify the asset graph still loads)