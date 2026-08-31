# cocoindex-v1-module-path-migration Specification

## Purpose

`cocoindex-v1-module-path-migration` is a capability of the
Cianfhoghlaim platform that codifies the canonical module-path
mapping from the pre-refactor flat layout (`cianfhoghlaim.cocoindex.<app>`)
to the actual CocoIndex v1 package layout
(`cianfhoghlaim.cocoindex_flows.<subpkg>.<app>`).

This spec captures the **Wave 0 unblocker** identified by the 2026-08-24
master refactor plan: 85 `defs.yaml` files in
`orchestration/defs/3_model_lifecycle/cocoindex_v1/` use the broken
pre-refactor module path, causing every CocoIndex App to raise
`dg.Failure(cocoindex_v1_module_import_failed)` at execute time.

After this spec is implemented:

- `dg list defs` lists all ~190 CocoIndex v1 assets
- `mise run sync:dagster` passes
- `mise run lint:drift-docs` passes (the AGENTS.md drift cleanup is included)

## ADDED Requirements

### Requirement: Module-path migration map
The system SHALL be remapped per the following table:.

#### Bucket A — Per-nation education embeddings (55 files)

For each `orchestration/defs/3_model_lifecycle/cocoindex_v1/european_nations_<iso3>_education/defs.yaml`:

- **WHEN** the file contains `module: cianfhoghlaim.cocoindex.european_nations_<iso3>_education_embedding`
- **THEN** the file SHALL contain `module: cianfhoghlaim.cocoindex_flows.european_nations._factory`
- **AND** the `app_name:` SHALL remain unchanged (the factory exposes one
  `coco.App` per ISO-3 nation; the App name is the same as the legacy
  per-nation file)

ISO-3 codes (40 total): `alb, aut, bel, bgr, bih, che, cyp, cze, dnk, esp,
est, fin, fra, geo, deu, grc, hrv, hun, isl, ita, lva, lie, ltu, lux, mlt,
mda, mne, nld, mkd, nor, pol, prt, rou, srb, svk, svn, swe, tur, ukr, xkx`.

#### Bucket B — LC subjects (6 files)

For `orchestration/defs/3_model_lifecycle/cocoindex_v1/lc_subjects/defs.yaml`:

- **WHEN** the file contains `module: cianfhoghlaim.cocoindex.mathematics_embedding`
- **THEN** the file SHALL contain `module: cianfhoghlaim.cocoindex_flows.subjects.lc_subject_embedding`
- **AND** the same mapping applies to `chemistry_embedding`, `geography_embedding`,
  `english_embedding`, `computer_science_embedding`
- **AND** `gaeilge_embedding` is a SPECIAL CASE — it maps to
  `cianfhoghlaim.cocoindex_flows.celtic.gaeilge_embedding` (Irish-only per
  BIEP v1 spec, no English sibling)

#### Bucket C — Specialised Apps (20 files)

For each `orchestration/defs/3_model_lifecycle/cocoindex_v1/<app>/defs.yaml`:

| Legacy `module:` | New `module:` |
|:--|:--|
| `cianfhoghlaim.cocoindex.americas_california_education_embedding` | `cianfhoghlaim.cocoindex_flows.american_nations.united_states.california_education_embedding` |
| `cianfhoghlaim.cocoindex.commonwealth_education_embedding` | `cianfhoghlaim.cocoindex_flows.biep_parity.lc_subject_embedding` |
| `cianfhoghlaim.cocoindex.en_education` | `cianfhoghlaim.cocoindex_flows.british_isles.england.education` |
| `cianfhoghlaim.cocoindex.eu_multilingual_alignment_embedding` | `cianfhoghlaim.cocoindex_flows.european_nations._factory` |
| `cianfhoghlaim.cocoindex.code_embedding` | `cianfhoghlaim.cocoindex_flows.infrastructure.code_embedding` |
| `cianfhoghlaim.cocoindex.api_index` | `cianfhoghlaim.cocoindex_flows.infrastructure.api_index` |
| `cianfhoghlaim.cocoindex.config_index` | `cianfhoghlaim.cocoindex_flows.infrastructure.config_index` |
| `cianfhoghlaim.cocoindex.codebase_graph` | `cianfhoghlaim.cocoindex_flows.infrastructure.codebase_graph` |
| `cianfhoghlaim.cocoindex.codebase_index` | `cianfhoghlaim.cocoindex_flows.infrastructure.codebase_index` |
| `cianfhoghlaim.cocoindex.apple_photos_chunks` | `cianfhoghlaim.cocoindex_flows.media_personal.apple_photos_chunks` |
| `cianfhoghlaim.cocoindex.apple_photos_geospatial` | `cianfhoghlaim.cocoindex_flows.media_personal.apple_photos_geospatial` |
| `cianfhoghlaim.cocoindex.apple_photos_metadata` | `cianfhoghlaim.cocoindex_flows.media_personal.apple_photos_metadata` |
| `cianfhoghlaim.cocoindex.cross_subject_competency_embedding` | `cianfhoghlaim.cocoindex_flows.biep_parity.cross_subject_competency_embedding` |
| `cianfhoghlaim.cocoindex.culture_heritage_embedding` | `cianfhoghlaim.cocoindex_flows.cultural_heritage.embedding` |
| `cianfhoghlaim.cocoindex.cv_embedding` | `cianfhoghlaim.cocoindex_flows.cv.embedding` |
| `cianfhoghlaim.cocoindex.agent_registry` | `cianfhoghlaim.cocoindex_flows.infrastructure.agent_registry` |
| `cianfhoghlaim.cocoindex.university_courses` | `cianfhoghlaim.cocoindex_flows.education.tertiary.uog.courses` |
| `cianfhoghlaim.cocoindex.docs_skills_consolidation` | `cianfhoghlaim.cocoindex_flows.infrastructure.docs_skills_consolidation` |
| `cianfhoghlaim.cocoindex.academic_history_flow` | `cianfhoghlaim.cocoindex_flows.infrastructure.academic_history_flow` |
| `cianfhoghlaim.cocoindex.root_pdfs_embedding` | `cianfhoghlaim.cocoindex_flows.infrastructure.root_pdfs_embedding` |

#### Scenario: All module paths resolve to importable Python modules

- **WHEN** `for f in orchestration/defs/3_model_lifecycle/cocoindex_v1/*/defs.yaml; do python -c "import $(grep '^[[:space:]]*module:' $f | head -1 | awk '{print \$2}' | tr -d '\n')" 2>&1 | grep -q "Error" && echo FAIL $f; done` runs
- **THEN** no file outputs `FAIL` (every module imports successfully)

#### Scenario: The legacy comment in layer3_model_lifecycle.py is updated

- **WHEN** Wave 0 lands
- **THEN** the comment at `orchestration/components/layer3_model_lifecycle.py:296-301`
  SHALL be removed or rewritten to reflect that the module-path issue is resolved

### Requirement: Partition-name typo fix
The system SHALL be corrected..

- **WHEN** `grep -rn "cianhoghlaim_scope" orchestration` runs
- **THEN** the result SHALL be empty (no occurrences)

- **AND** `biiep_v3_scope_year_partition` SHALL continue to be importable
- **AND** no `defs.yaml` file references the typo'd partition name (verified
  by `grep -rln "cianhoghlaim_scope\|biiep_v3_scope_year_partition" orchestration/defs --include="*.yaml"`)

#### Scenario: partitions_v2.py imports cleanly

- **WHEN** `uv run python -c "from orchestration.partitions_v2 import biiep_v3_scope_year_partition; print(biep_v3_scope_year_partition)"` runs
- **THEN** the import succeeds without error

### Requirement: AGENTS.md drift cleanup

The `orchestration/AGENTS.md` file SHALL reflect the actual current counts
of assets, jobs, schedules, sensors, and asset checks.

- **WHEN** `mise run lint:drift-docs` runs
- **THEN** the drift check SHALL pass (every number in AGENTS.md matches
  the actual code state)

#### Scenario: Asset count in orchestration/AGENTS.md matches defs/ inventory

- **WHEN** `find orchestration/defs -name "defs.yaml" | wc -l` runs
- **THEN** the count SHALL be ≥ 190 (post-Wave-0)
- **AND** `orchestration/AGENTS.md` line 29 SHALL claim "~190 assets" (not "199")

#### Scenario: Sensor count in orchestration/AGENTS.md matches code

- **WHEN** `grep -rln "@dg.sensor" orchestration --include="*.py" | wc -l` runs
- **THEN** the count SHALL be ≤ 15 (post-Wave-0, after the 2026-08-23 batch consolidated some sensors)
- **AND** `orchestration/AGENTS.md` SHALL claim "~13 sensors"

### Requirement: CocoIndex pipeline executes end-to-end
The system SHALL be `1.0.20`.

#### Scenario: Default scenario

- **WHEN** `uv run python -c "import cocoindex; print(cocoindex.__version__)"` runs

- **AND** `uv run python -c "from cocoindex_flows.celtic import gaeilge_embedding; print(gaeilge_embedding.GaeilgeEmbedding)"` succeeds

- **AND** `mise run sync:dagster` passes without `cocoindex_v1_module_import_failed` errors

### Requirement: v0 CocoIndex stragglers (deferred to Wave 3)
The system SHALL be inventoried here so Wave 3 can execute.
the rewrite. The full list is in
`openspec/changes/2026-08-24-wave-3-cocoindex-v0-stragglers-v1/spec.md`.

| File | v0 API detected | v1 target API |
|:--|:--|:--|
| `cocoindex_flows/european_nations_cross/law_embedding.py` | `from cocoindex.connectors import lancedb` | `lancedb.mount_table_target(LANCE_DB, ...)` |
| `cocoindex_flows/european_nations_cross/medicine_embedding.py` | Same | Same |
| `cocoindex_flows/european_nations_cross/education_embedding.py` | Same | Same |
| `cocoindex_flows/commonwealth/nigeria/education_embedding.py` | Same | Same |
| `cocoindex_flows/commonwealth/canada/provinces/quebec/montreal_education_embedding.py` | Same | Same |
| `cocoindex_flows/commonwealth_cross/education_embedding.py` | Same | Same |
| `cocoindex_flows/american_nations/united_states/california_education_embedding.py` | Same | Same |
| `cocoindex_flows/british_isles/england/ocr_education_embedding.py` | Same | Same |
| `cocoindex_flows/british_isles/england/aqa_education_embedding.py` | Same | Same |
| `cocoindex_flows/british_isles/england/edexcel_education_embedding.py` | Same | Same |
| `cocoindex_flows/subjects/education_subject_embedding.py` | Same | Same |
| `cocoindex_flows/media_intel/cross_medium_compare.py` | Helper, no v0/v1 import | N/A |
| `cocoindex_flows/media_intel/media_descriptors.py` | Helper, no v0/v1 import | N/A |
| `cocoindex_flows/biep_parity/baml_runtime_integration.py` | Helper, no v0/v1 import | N/A |
| `cocoindex_flows/infrastructure/test_phase0_primitives.py` | Test, imports v1 | N/A (already v1) |
| `cocoindex_flows/infrastructure/test_youtube_kg_smoke.py` | Test, imports v1 | N/A (already v1) |
| `cocoindex_flows/_shared/cocoindex_query_api.py` | API surface, helper | N/A |
| `cocoindex_flows/infrastructure/__init__.py` | Marker | N/A |

Wave 3 (`2026-08-24-wave-3-cocoindex-v0-stragglers-v1`) is the change that
actually performs the migration. This spec only documents the inventory.

#### Scenario: v0 inventory is accurate

- **WHEN** `find cocoindex_flows -name "*.py" -not -path "*__pycache__*" | xargs grep -L "import cocoindex as coco\|@coco\.fn\|coco\.App\|coco\.ContextKey" 2>/dev/null` runs
- **THEN** the resulting file count SHALL equal the table above (or its
  post-Wave-0 update)

