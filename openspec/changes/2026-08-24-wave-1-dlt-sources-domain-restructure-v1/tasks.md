# Tasks: 2026-08-24-wave-1-dlt-sources-domain-restructure-v1

## Phase 1: Openspec change skeleton (3 tasks)

- [x] **T1.1**: Create `openspec/changes/2026-08-24-wave-1-dlt-sources-domain-restructure-v1/proposal.md`
- [x] **T1.2**: Create `openspec/changes/2026-08-24-wave-1-dlt-sources-domain-restructure-v1/tasks.md` (this file)
- [x] **T1.3**: Create `openspec/changes/2026-08-24-wave-1-dlt-sources-domain-restructure-v1/specs/dlt-sources-domain-restructure/spec.md`

## Phase 2: Build the migration script (1 task)

- [ ] **T2.1**: Write `scripts/wave_1_dlt_sources_restructure.py`
  - Discovers every `law/`, `medicine/`, `education/`, `university/` subdir
  - Discovers every file in `language/`, `media/`, `api_sources/`, `crypteolas/`, `apple_photos/`, `filesystem/`, `portfolio/`
  - Builds a migration map: `old_path → new_path`
  - Executes `git mv` for each move (preserves history)
  - Generates `__init__.py` re-export shims for legacy paths
  - Has `--dry-run` flag

## Phase 3: Law/Medicine/Education domain-first split (3 tasks)

- [ ] **T3.1**: Domain-first law/ split — 59 directories
  - Move `dlt_sources/<geography>/<jurisdiction>/law/` → `dlt_sources/law/<jurisdiction>/<geography>/`
  - For each move, create a re-export shim at the old location

- [ ] **T3.2**: Domain-first medicine/ split — 61 directories
  - Same mapping as T3.1 for `medicine/` dirs

- [ ] **T3.3**: Domain-first education/ split — 61 directories (K-12 only)
  - Same mapping as T3.1 for `education/` dirs

## Phase 4: Tertiary pipeline relocation (1 task)

- [ ] **T4.1**: Relocate UoG + NUI federation flat files into `dlt_sources/education/tertiary/`
  - `dlt_sources/education/tertiary/uog/exam_papers/` (from orchestration)
  - `dlt_sources/education/tertiary/uog/personal_archive/`
  - `dlt_sources/education/tertiary/uog/official_docs/`
  - `dlt_sources/education/tertiary/uog/students_union/`
  - `dlt_sources/education/tertiary/nui_federation/`

## Phase 5: Themed package restructure (8 tasks)

- [ ] **T5.1**: `language/` → `lexicographic/` + `cultural_heritage/` + `local_archive/`
  - 13 lexicographic .py files → `dlt_sources/lexicographic/`
  - 8 cultural_heritage .py files → `dlt_sources/cultural_heritage/`
  - 3 local_archive .py files → `dlt_sources/local_archive/`

- [ ] **T5.2**: `media/` → `media_text/` + `media_comics/` + `media_games/` + `media_animation/`
  - 5 official/prose/celtic_history_research/animation dirs → `media_text/`
  - 1 comics dir → `media_comics/`
  - 1 games dir → `media_games/`

- [ ] **T5.3**: `api_sources/` → `api_finance/` + `api_documentation/` + `api_github/` + `api_local/`
  - `defi/` → `api_finance/` (or merge into `crypteolas_defi/` per T5.5)
  - `documentation/` → `api_documentation/`
  - `github/` → `api_github/`
  - `local/` → `api_local/`

- [ ] **T5.4**: `crypteolas/` → `crypteolas_chain/` + `crypteolas_docs/` + `crypteolas_defi/`
  - `local/` + `github/` → `crypteolas_chain/`
  - `documentation/` → `crypteolas_docs/`
  - `defi/` → `crypteolas_defi/` (merged with `api_sources/defi/` if T5.3 selected that path)

- [ ] **T5.5**: `apple_photos/` → `media_personal/`

- [ ] **T5.6**: `filesystem/` → `raw_files/`

- [ ] **T5.7**: `portfolio/` → `cv/` + `artwork/` + `labels/`

- [ ] **T5.8**: `jobs/` → `_jobs/` (rename only; CLI dispatcher)

## Phase 6: Layer-grouped destinations (1 task)

- [ ] **T6.1**: Consolidate destinations
  - Create `dlt_sources/common/destinations/__init__.py` with `named_destinations()` factory
  - Create `dlt_sources/common/destinations/{ducklake.py, motherduck.py, filesystem.py, iceberg.py}`
  - Delete `dlt_sources/_lakehouse/destinations.py` + `_lakehouse/personal_archive_destinations.py` (move content)
  - Delete `dlt_sources/common/destinations_cianfhoghlaim.py`, `_tuatha.py`, `_personal_archive_destinations.py`, `named_destinations.py`
  - Add re-export shims at the legacy locations

## Phase 7: Documentation updates (4 tasks)

- [ ] **T7.1**: Update `dlt_sources/LEGACY_ALIASES.md` with the new mappings

- [ ] **T7.2**: Update `dlt_sources/AGENTS.md` routing + key sources table

- [ ] **T7.3**: Update `dlt_sources/README.md` package index

- [ ] **T7.4**: Update `dlt_sources/DATA_PLATFORM_ROUTER.md` to reference the new namespace

## Phase 8: Verification (5 tasks)

- [ ] **T8.1**: `uv run python -c "import dlt_sources"` succeeds
- [ ] **T8.2**: Sample imports for each new domain work:
  - `from dlt_sources.law.ireland.british_isles import <...>`
  - `from dlt_sources.medicine.australia.commonwealth import tga`
  - `from dlt_sources.education.france.european_nations import <...>`
  - `from dlt_sources.education.tertiary.uog.exam_papers import <...>`
- [ ] **T8.3**: Sample imports for themed packages work:
  - `from dlt_sources.lexicographic import ainm, canuint, tearma, logainm`
  - `from dlt_sources.cultural_heritage import celtic_mythology, duchas, gaois`
  - `from dlt_sources.media_text import animation, prose, official`
  - `from dlt_sources.crypteolas_chain import <...>`
  - `from dlt_sources.media_personal import apple_photos`
- [ ] **T8.4**: Sample imports for layer-grouped destinations work:
  - `from dlt_sources.common.destinations import named_destinations`
  - `d = named_destinations('ducklake_cianfhoghlaim')`
- [ ] **T8.5**: Legacy imports still resolve via shims:
  - `from dlt_sources.commonwealth.nigeria.law import nass` (legacy)
  - `from dlt_sources.british_isles.england.law import <...>` (legacy)
  - `from dlt_sources.language import ainm` (legacy)

## Phase 9: Tests + sync (3 tasks)

- [ ] **T9.1**: `tests/dlt_sources/test_legacy_aliases.py` (NEW) — assert every old import path still resolves
- [ ] **T9.2**: `tests/dlt_sources/test_destinations.py` — assert `named_destinations()` returns the right factory
- [ ] **T9.3**: `tests/dlt_sources/test_subject_sources.py` — existing, expand to cover renamed packages
- [ ] **T9.4**: `mise run sync:all` passes (7 layers)

## Phase 10: Commit + push (2 tasks)

- [ ] **T10.1**: Stage only the Wave 1 files (NOT unrelated work):
  - All moved/created/edited files under `dlt_sources/`
  - 3 new openspec files
  - `scripts/wave_1_dlt_sources_restructure.py`

- [ ] **T10.2**: Commit with descriptive message + push

## Total: 32 tasks across 10 phases

Estimated effort: ~15 days (per the master plan's Wave 1 estimate).
