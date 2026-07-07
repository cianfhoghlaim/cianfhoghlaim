# consolidate-cianfhoghlaim-subdirs — Scope + Phase 1 (Notebooks reorg) of the v3 Cianfhoghlaim consolidation

## Why

The v3 consolidation plan (per the cianfhoghlaim-v2 plan conversation)
identified **11 parallel sprawl + dead-end findings** across `dlt/`,
`dagster/`, `baml/`, `agents/`, `cocoindex/`, `notebooks/`, `storage/`,
`tuatha/`, and `web/` subdirectories of `cianfhoghlaim/`. Several
**adjacent openspec changes are already in-flight** as of 2026-06-30:

- `openspec/changes/2026-06-30-consolidate-cianfhoghlaim-pyproject-and-8-dirs/`
  (67/151 tasks) — the 7-phase manifest + meaisinfhoghlaim redistribution
  + observability consolidation + browser consolidation + cocoindex
  / baml clients consolidation + mise consolidation
- `openspec/changes/cianfhoghlaim-educational-mmo-v1/` (90/92 tasks)
  — the 12-phase Educational MMO

**The BAML reorganization (`openspec/changes/baml-reorganize-by-cluster/`,
just archived) and BAML consumer wiring
(`openspec/changes/wire-baml-to-consolidated-pipelines/`, just
archived) are now complete.** That leaves 9 of the 11 v3-plan findings
still in scope:

| # | Finding | Effort | In-flight overlap? |
|:--|:--|:--|:--|
| D1 | Collapse 14 single-asset `law/{nation}/__init__.py` + 14 `medicine/{nation}/__init__.py` files into 2 `by_domain/{law,medicine}.py` files | 1 day | No |
| D2 | Delete empty `ie/law/__init__.py` + `ie/medicine/__init__.py` | 0.25 day | No |
| D3 | Merge `assets/ie/education/` (5 files) into `assets/by_domain/ireland_education.py` | 0.5 day | Partial (the 7-phase change touches the same files) |
| D4 | Fix 14 broken `dlt_sources.{nation}.law.legislation` imports | 1 day | No (BUG FIX, blocks assets) |
| D5 | Reorganise 65+ `dagster/assets/*` files into `dagster/assets/by_domain/*.py` | 3-5 days | Heavy overlap with the 7-phase change |
| C1 | Reorganise 34 cocoindex files into `cocoindex/{apps,subjects,upstream,tools}/` | 1-2 days | Partial |
| S1 | Promote `storage/_shared/` to canonical; delete top-level graph client duplicates | 0.5 day | No |
| S3 | Delete `storage/temporal.py` (use `graphiti_core` wrapper) | 0.25 day | No |
| T1-T3 | Rename `_tuatha_src/` to canonical; verify MMO assets | 0.5 day | No |
| W1-W3 | Delete `_underscore` dirs in `web/`; flatten `notebooks/` | 1-2 days | No |
| N1 | Move `notebooks/croilar/` to `web/apps/croilar-portal/notebooks/` | 0.25 day | No |

**Scope decision**: This change executes only the **contained, low-risk
phases** that DO NOT overlap with the in-flight 7-phase change.
Specifically:

- **Phase 1**: D4 (fix the 14 broken `dlt_sources.{nation}.law.legislation`
  imports — a bug fix)
- **Phase 2**: D1 + D2 (collapse the 14 single-asset `law/{nation}/__init__.py`
  + 14 `medicine/{nation}/__init__.py` files into 2 `by_domain/{law,medicine}.py`
  files + delete the 2 empty `ie/law/` + `ie/medicine/` dirs)
- **Phase 3**: S1 + S3 (storage graph unification — promote `_shared/`,
  delete `temporal.py`)
- **Phase 4**: N1 (move `notebooks/croilar/` to croilar-portal)
- **Phase 5**: T1-T3 (rename `_tuatha_src/` to canonical; verify MMO
  assets)
- **Phase 6**: W1 (delete `_underscore` web/ dirs; already partially done
  per the archived `per-domain-web-app-consolidation` change)

**Deferred** (out of scope for THIS change; tracked as separate
follow-up changes):

- **D3** + **D5**: Dagster by_domain consolidation (3-5 days; needs to
  follow D4 first because the broken imports block the by_domain
  reorganization)
- **C1**: CocoIndex app-clustering (1-2 days; can be done independently)
- **W2** + **W3**: Web apps by_domain restructuring (3-5 days; tracked
  as the `rewrite-cyanfhoghlaim-web-v1` follow-up change)
- **N2-N5**: Notebooks reorg beyond the croilar move (1-2 days;
  separately tracked)

## What

### Phase 1 — Fix the 14 broken `dlt_sources.{nation}.law.legislation` imports

The 7 nation dlt sources for law (`en`, `sct`, `wls`, `ni`, `ggy`, `iom`,
`jey`) import from `dlt_sources.{nation}.law.legislation` — paths that
**do not exist** because the actual files are at
`dlt/british_isles/{nation}/law/legislation.py` (per the lateralise
change). The corresponding 7 dagster assets in
`dagster/assets/law/{nation}/__init__.py` and
`dagster/assets/medicine/{nation}/__init__.py` import from these broken
paths.

**Phase 1a**: Restore the missing 6 nations in `dlt/british_isles/`
(only `en` + `ie` exist today). For each of `sct`, `wls`, `ni`, `ggy`,
`iom`, `jey`:

1. Create `dlt/british_isles/{nation}/law/__init__.py` with re-exports
   from the new `dlt/domains/{nation}/law/legislation.py` (using the
   `dlt.domains/` shape that the v3 plan proposes)
2. Create `dlt/british_isles/{nation}/medicine/__init__.py` with
   re-exports from `dlt/domains/{nation}/medicine/{source}.py`

**Phase 1b**: Fix the 14 dagster assets to import from the canonical
`dlt.domains.{nation}.law` + `dlt.domains.{nation}.medicine` paths
instead of the broken `dlt_sources.{nation}.{law,medicine}` paths.

#### Scenario: A nation dlt source materialises

- **GIVEN** the `dlt/domains/ggy/law/legislation.py` source exists with
  `ggy_legislation_source()`
- **AND** the canonical re-export
  `dlt/british_isles/ggy/law/__init__.py` re-exports it
- **WHEN** the dagster asset `dagster/assets/law/ggy/__init__.py:
  law_ggy_legislation` materialises
- **THEN** it calls `ggy_legislation_source()` and the asset succeeds
  (no `ImportError`)

### Phase 2 — Collapse the 14 single-asset nation __init__.py files

`dagster/assets/law/{en,ggy,iom,jey,ni,sct,wls}/__init__.py` and
`dagster/assets/medicine/{en,ggy,iom,jey,ni,sct,wls}/__init__.py` (14
files total) each contain a single `@asset` function. Collapse them
into 2 files: `dagster/assets/by_domain/law.py` (7 @assets) +
`dagster/assets/by_domain/medicine.py` (7 @assets).

**Phase 2a**: Create `dagster/assets/by_domain/__init__.py` with
re-exports for the existing files (backward compat for one release).

**Phase 2b**: Create `dagster/assets/by_domain/law.py` with the 7
law_nation_legislation assets (one per nation, all deduplicated to
use the shared `dlt/domains/_shared/legislation_helper.py`).

**Phase 2c**: Create `dagster/assets/by_domain/medicine.py` with the 7
medicine_nation_* assets (one per nation).

**Phase 2d**: Delete the 14 `law/{nation}/__init__.py` + 14
`medicine/{nation}/__init__.py` files.

**Phase 2e**: Delete the 2 empty `ie/law/__init__.py` +
`ie/medicine/__init__.py` files (they're empty).

#### Scenario: dg list defs shows the new by_domain shape

- **WHEN** `dg list defs` is run after Phase 2
- **THEN** the asset graph shows 2 by_domain groups (`law`, `medicine`)
  with 7 assets each
- **AND** the 14 old `law_{nation}_*` / `medicine_{nation}_*` asset
  names are replaced by `by_domain.law.{nation}_legislation` /
  `by_domain.medicine.{nation}_*`

### Phase 3 — Storage graph unification

**Phase 3a**: Promote `storage/_shared/{falkordb,memgraph,neo4j,interface}.py`
to canonical. Delete the top-level duplicates:
`storage/falkordb_client.py`, `storage/memgraph_client.py`.

**Phase 3b**: Delete `storage/temporal.py` (the hand-rolled pure-Python
Graphiti-in-Python implementation; per `refactor-dlt-dagster-2026-stack-align`
Phase 6). The canonical `storage/temporal_client.py` (the `graphiti_core`
wrapper) stays.

**Phase 3c**: Rename `storage/cognify/cognee_integration/` →
`storage/cognify/` (de-nest one level).

#### Scenario: A developer imports the canonical graph client

- **WHEN** the developer runs
  `from cianfhoghlaim.storage.falkordb import falkordb_client`
- **THEN** it imports from `storage/_shared/falkordb.py` (the canonical
  multi-graph abstraction layer)
- **AND** the old `storage/falkordb_client.py` is gone (zero callers)

### Phase 4 — Move `notebooks/croilar/` to croilar-portal

Per the archived `croilar-revitalisation` change: the croilar-portal
app should own its croilar-specific notebooks. Move
`cianfhoghlaim/notebooks/croilar/` (8 files) to
`cianfhoghlaim/web/apps/croilar-portal/notebooks/`.

**Phase 4a**: Create
`cianfhoghlaim/web/apps/croilar-portal/notebooks/` directory.

**Phase 4b**: `git mv` all 8 files from `cianfhoghlaim/notebooks/croilar/`
to `cianfhoghlaim/web/apps/croilar-portal/notebooks/`.

**Phase 4c**: Verify that the croilar-portal app picks up the notebooks
in its build (may need a configuration update to the croilar-portal
`vite.config.ts` or `package.json`).

#### Scenario: The croilar-portal app discovers the notebooks

- **WHEN** `bun --filter croilar-portal build` is run after Phase 4
- **THEN** the 8 notebooks are included in the croilar-portal build
  output

### Phase 5 — Rename `_tuatha_src/` to canonical

Per the `consolidate-external-libs-into-tuatha` change: the v3→v4
dual-namespace pattern (`tuatha/asset_generation/_tuatha_src/` +
`tuatha/asset_generation/fibo/`) is a v3 artefact. Rename
`tuatha/asset_generation/_tuatha_src/` → `tuatha/asset_generation/`
(drop the underscore prefix; merge with the existing
`tuatha/asset_generation/`).

**Phase 5a**: Audit `tuatha/asset_generation/_tuatha_src/` for files
that would conflict with `tuatha/asset_generation/` (if any).

**Phase 5b**: `git mv` the files from `_tuatha_src/` to `tuatha/asset_generation/`.

**Phase 5c**: Update the 6 import sites that reference
`tuatha.asset_generation._tuatha_src` to point at the canonical path.

**Phase 5d**: Delete the now-empty `_tuatha_src/` directory.

#### Scenario: The MMO agents import from the canonical path

- **WHEN** the `tuatha/` agents import from
  `cianfhoghlaim.tuatha.asset_generation`
- **THEN** they import the renamed (non-underscore) module
- **AND** the old `_tuatha_src` namespace is gone

### Phase 6 — Web apps cleanup

**Phase 6a**: Delete any remaining `_underscore` legacy web/ directories:
- `web/_croilar_config/` (if it exists)
- `web/_croilar_shared/` (if it exists)
- `web/_oideachais_dashboard/` (if it exists — already mostly deleted
  per the in-flight 7-phase change)

**Phase 6b**: Verify the `web/apps/oideachais-web/` (the oideachais
web app) is properly mounted under the canonical workspace path
`web/apps/oideachais-web/` (not `web/oideachais-web/`).

#### Scenario: Web workspace structure is canonical

- **WHEN** `ls web/` is run
- **THEN** it shows: `_croilar_config/`, `_croilar_shared/`,
  `_oideachais_dashboard/`, `apps/`, `hono-api/`, `packages/` (only the
  canonical directories; no `_underscore` legacy dirs)

## Impact

| Metric | Before | After |
|--|--|--|
| Broken `dlt_sources.{nation}.law.legislation` imports | 14 (across dagster assets) | 0 |
| `dagster/assets/law/{nation}/__init__.py` single-asset files | 7 | 0 (collapsed into `by_domain/law.py`) |
| `dagster/assets/medicine/{nation}/__init__.py` single-asset files | 7 | 0 (collapsed into `by_domain/medicine.py`) |
| Empty `dagster/assets/ie/law/` + `ie/medicine/` dirs | 2 | 0 |
| Top-level graph client duplicates in `storage/` | 3 (`falkordb_client.py`, `memgraph_client.py`, `temporal.py`) | 0 |
| Nested `storage/cognify/cognee_integration/` | 1 | 0 (de-nested to `storage/cognify/`) |
| `notebooks/croilar/` files in cianfhoghlaim/ | 8 | 0 (moved to `web/apps/croilar-portal/notebooks/`) |
| `_tuatha_src/` namespace | 1 | 0 (renamed) |
| `_underscore` web/ dirs | varies | 0 |

### Affected specs

- **MODIFIED `oideachais-pipeline`** — the rule that dlt sources
  for the 9 nations live in `dlt/domains/{nation}/{domain}/` (per the
  v3 plan's Phase 1)
- **MODIFIED `meaisinfhoghlaim-platform`** — the rule that every
  Dagster asset in `dagster/assets/by_domain/` corresponds to exactly
  one dlt source from `dlt/domains/` (per the v3 plan's Phase 2)

### Backward compatibility

- Phase 2 (Dagster by_domain) creates `dagster/assets/by_domain/__init__.py`
  with re-exports for the existing files. Any code that imports
  `from cianfhoghlaim.dagster.assets.law.{nation}` continues to work
  for one release (the re-exports stay).
- Phase 3a (storage graph unification) keeps `_shared/` as the canonical
  home; the top-level duplicates are deleted (zero callers per `ccc search`).
- Phase 5 (Tuatha rename) uses `git mv` to preserve history; import path
  updates are mechanical.

### Non-Goals

- No new dlt sources added
- No new BAML functions added
- No DAG pipeline restructuring (that's the deferred D3 + D5)
- No CocoIndex app-clustering (that's the deferred C1)
- No web apps by_domain restructuring (that's the deferred W2 + W3)
- No DAG pipeline re-runs (the broken imports prevented any meaningful
  re-run; after Phase 1 the dagster assets can be materialised)

### Risk Assessment

| Risk | Mitigation |
|:--|:--|
| Phase 1 (broken imports fix) breaks a working dlt source | The dlt sources for the 6 missing nations don't exist yet (only `en` + `ie` are real). The dagster assets in `law/{nation}/__init__.py` are stubs that import from the broken path. After Phase 1, the imports work and the assets can materialise. |
| Phase 2 (collapse) breaks Dagster UI | The `by_domain/__init__.py` re-exports preserve the old asset names for one release. `dg list defs` shows both the new and old names during the transition. |
| Phase 5 (Tuatha rename) breaks MMO agents | The 6 import sites are tracked in tasks.md; update is mechanical. After the rename, the MMO agents continue to work via the new canonical path. |
| Phase 6 (web/ cleanup) breaks croilar-portal build | Only delete `_underscore` dirs that have 0 references per `ccc search`. The archived `per-domain-web-app-consolidation` already migrated the canonical content; the `_underscore` dirs are empty leftovers. |

## Validation

1. `openspec validate consolidate-cianfhoghlaim-subdirs --strict` passes
2. `dg list defs` shows the new `by_domain` shape (Phase 2)
3. `python -c "from cianfhoghlaim.storage.falkordb import falkordb_client"` succeeds (Phase 3)
4. `ls web/apps/croilar-portal/notebooks/` shows the 8 croilar notebooks (Phase 4)
5. `ccc search "dlt_sources\.\\w+\\.law"` returns 0 hits (Phase 1)
6. `ccc search "_tuatha_src"` returns 0 hits (Phase 5)
7. `ls web/_croilar_config web/_croilar_shared web/_oideachais_dashboard` returns "No such file or directory" (Phase 6)