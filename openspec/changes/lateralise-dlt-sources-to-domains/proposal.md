# lateralise-dlt-sources-to-domains — Migrate 50+ dlt sources to the canonical {nation}/{domain} layout

## Why

The oideachais quadrant has **two parallel layout schemes** for
dlt sources that drift apart:

| Pattern | Used by | Conforms to `cross-domain-registry`? |
|---|---|---|
| **Legacy:** `dlt_sources/uk/{england,scotland,wales,northern_ireland}/` + `dlt_sources/ireland/` + `dlt_sources/crown_dependencies/` | `oideachais/AGENTS.md` "Quick routing" table (line 44-45) | NO — the contract is `{nation}.{domain}.{entity}`, not `{region}/{nation}` |
| **Canonical:** `dlt_sources/domains/{education,law,medicine,site_analysis}/{ie,en,ni,sct,wls,iom,jey,ggy}/` | New law/medicine sources (Phase 5-7 of `lateralise-british-isles-domains`); 9 statutory law + 10 medicine + 8 education sources | YES — flat `{nation}/{domain}` matches the contract |

**Consequence:** `AGENTS.md:44-46` instructs new contributors to add a UK source to `dlt_sources/uk/scotland/`, but `cross-domain-registry/SKILL.md:151-176` says to add it to `dlt_sources/sct/education.py`. The two instructions disagree. New contributors will follow AGENTS.md and add to the legacy location, perpetuating the drift.

**This change migrates the 50+ legacy dlt sources to the canonical location** in a single atomic openspec change. After the change, there is ONE place to add a new source (the canonical `dlt_sources/domains/education/{nation}/`).

## What

### Phase 1: Update `oideachais/AGENTS.md` "Quick routing" table
The table at line 42-58 currently points new contributors to:
- `oideachais/dlt_sources/ireland/` (22 files)
- `oideachais/dlt_sources/uk/{england,scotland,wales,northern_ireland}/` (4 directories)
- `oideachais/dlt_sources/crown_dependencies/{channel_islands,isle_of_man}.py`
- `oideachais/dlt_sources/author_archive/` (4 dlt sources)

After the change, the table points to:
- `oideachais/dlt_sources/domains/education/{nation}/{source}.py` (where `{nation}` is one of `ie`, `en`, `sct`, `wls`, `ni`, `iom`, `jey`, `ggy`)
- `oideachais/dlt_sources/domains/education/{nation}/` is the canonical home for ALL education domain sources, regardless of which `region` (UK / IE / CD) they originate from

### Phase 2: Move the dlt source files
- Move `dlt_sources/uk/england/*.py` (4 files) → `dlt_sources/domains/education/en/*.py`
- Move `dlt_sources/uk/scotland/*.py` (4 files) → `dlt_sources/domains/education/sct/*.py`
- Move `dlt_sources/uk/wales/*.py` (3 files) → `dlt_sources/domains/education/wls/*.py`
- Move `dlt_sources/uk/northern_ireland/*.py` (4 files) → `dlt_sources/domains/education/ni/*.py`
- Move `dlt_sources/ireland/*.py` (24 files + `subjects/`) → `dlt_sources/domains/education/ie/*.py`
- Move `dlt_sources/crown_dependencies/channel_islands.py` → `dlt_sources/domains/education/{jey,ggy}/*.py`
- Move `dlt_sources/crown_dependencies/isle_of_man.py` → `dlt_sources/domains/education/iom/`

### Phase 3: Add backward-compat re-exports
The 6 legacy `__init__.py` files are updated to re-export from the
new locations. This is a one-release backward-compat window
(removable in a follow-up openspec change):

```python
# oideachais/dlt_sources/uk/england/__init__.py
from oideachais.dlt_sources.domains.education.en import (
    dfe_explore_statistics_source,
    national_curriculum_source,
    ofsted_source,
    gias_source,
    school_info_source,
)
```

### Phase 4: Update all import statements
- Update `oideachais/dagster_defs/assets/uk_education_assets.py`
  (12 imports)
- Update `oideachais/dagster_defs/assets/ie/education/*.py`
  (5 imports)
- Update `oideachais/dagster_defs/assets/wire_unwired_dlt_sources.py`
  (11 imports)
- Update `oideachais/dagster_defs/assets/author_archive_assets.py`
  (any dlt_sources imports)
- Update `oideachais/dagster_defs/definitions.py` (any dlt_sources imports)
- Update `oideachais/dagster_defs/asset_checks.py`
- Update `oideachais/dagster_defs/factories.py` (if it imports dlt_sources)
- Update `oideachais/dagster_defs/resources.py` (if it imports dlt_sources)
- Update `oideachais/cognee_integration/cross_stage_cognify.py`
  (if it imports dlt_sources)
- Update `oideachais/cognee_integration/author_archive_cognify.py`
  (if it imports dlt_sources)

### Phase 5: Update `oideachais/STATUS.md`
Add a section "Layout migration" that records:
- The legacy locations and their canonical replacements
- The deprecation timeline (1 release, then remove the re-exports)

## Impact

### Affected files
- **MOVED:** 38 .py files from `dlt_sources/uk/`, `dlt_sources/ireland/`, `dlt_sources/crown_dependencies/` to `dlt_sources/domains/education/{nation}/`
- **MODIFIED:** 6 legacy `__init__.py` files (re-export shims)
- **NEW:** 8 `dlt_sources/domains/education/{nation}/__init__.py` files (canonical re-exports)
- **MODIFIED:** 9 import sites in `dagster_defs/`
- **MODIFIED:** `oideachais/AGENTS.md` "Quick routing" table
- **MODIFIED:** `oideachais/STATUS.md` (new "Layout migration" section)
- **NEW:** `oideachais/REFACTORING.md` entry (deprecation timeline)

### Affected specs
- MODIFIED `oideachais-pipeline` — the rule that all dlt sources
  for the education domain MUST live in
  `oideachais/dlt_sources/domains/education/{nation}/`. The legacy
  `dlt_sources/uk/`, `dlt_sources/ireland/`, and
  `dlt_sources/crown_dependencies/` directories are forbidden.

### Backward compatibility
- The 6 legacy `__init__.py` files re-export from the new
  locations for one release. Any code that imports from
  `oideachais.dlt_sources.uk.england` will continue to work.
- The canonical `dlt_sources/domains/education/{nation}/` is
  the new home for all 38 sources.
- A follow-up openspec change (`remove-legacy-dlt-sources-shim`)
  will delete the re-export shims in the next release.

## Non-Goals

- No dlt source code changes (only file moves + import updates)
- No new dlt sources added
- No BAML or Cognee changes
- No DLT destination or DuckLake changes
- No frontend / FastAPI changes

## Risk Assessment

- **Risk: missing an import site in the migration.** Mitigation:
  the openspec change lists all known import sites; the
  `git grep` audit is run before each commit.
- **Risk: the legacy re-export shims break the import path
  resolution in the Dagster definitions.** Mitigation: the shims
  are pure re-exports (no class redefinition), so the import
  resolution is identical to the canonical path.
- **Risk: the migration touches 50+ files in one commit.** This
  is intentional — atomic moves are easier to revert than
  incremental ones. The openspec change is the single source of
  truth for the migration.

## Validation

1. `git mv` the 38 files in a single commit
2. Update 9 import sites in `dagster_defs/`
3. Update `oideachais/AGENTS.md` "Quick routing" table
4. `uv run --package oideachais python -c "import dagster_defs.definitions"` still loads
5. `from oideachais.dlt_sources.uk.england import national_curriculum_source` still works (backward compat)
6. `from oideachais.dlt_sources.domains.education.en import national_curriculum_source` works (canonical)
7. `openspec validate lateralise-dlt-sources-to-domains --strict` passes
