# 2026-08-24-wave-1-dlt-sources-domain-restructure-v1

## Why

The 2026-08-24 master refactor plan identified Wave 1 as the **largest
single refactor** in the 8-wave cascade. Three structural problems with
the current `dlt_sources/` layout motivate this change:

1. **Law and Medicine are buried inside jurisdiction trees.** The current
   structure puts domain-specific sources inside their geographic parent:
   ```
   dlt_sources/commonwealth/nigeria/law/nass.py
   dlt_sources/commonwealth/nigeria/states/lagos/law/legislation.py
   dlt_sources/european_nations/poland/law/<...>
   dlt_sources/british_isles/england/law/<...>
   ```
   There are **59 `law/` directories** and **61 `medicine/` directories**
   scattered across 4 geographic trees (american_nations, british_isles,
   commonwealth, european_nations) + european_union. This makes it
   impossible to write a cross-jurisdiction law pipeline (e.g.
   "ingest every nation's statute book into a single LanceDB table")
   without scanning every tree.

2. **Education is split across multiple trees.** Education subdirs exist
   under `british_isles/<jurisdiction>/education/`,
   `commonwealth/<country>/education/`, `european_nations/<country>/education/`,
   `american_nations/<country>/education/`, `european_union/education/`,
   AND the `language/` package has 4 education-adjacent sources
   (`local_education_documents.py`, `celtic_mythology.py`, etc.). The
   tertiary (3rd-level, university) sources are scattered between
   `british_isles/ireland/university/` (the legacy sruth-era spot) and
   the new UoG + NUI federation flat files at the orchestration layer.

3. **Themed packages have inconsistent structure.** `language/` mixes
   lexicographic (ainm, canuint, tearma, logainm) with cultural heritage
   (celtic_mythology, heritage, hidden_heritages, duchas, gaois) with
   local archive (local_documents_by_subject). `media/` mixes text-based
   (official, prose) with comics (VLM-required) with games. `api_sources/`
   mixes crypto (defi) with documentation with github with local.
   `crypteolas/` is essentially a subset of `api_sources/defi/`.

This Wave 1 refactor reorganises `dlt_sources/` into a **domain-first
namespace**: `dlt_sources/<domain>/<jurisdiction>/...` instead of
`dlt_sources/<geography>/<jurisdiction>/<domain>/...`.

## User preferences (locked-in from prior turns)

| Decision | Choice |
|:--|:--|
| Geographic package naming | **KEEP ENGLISH** (american_nations, british_isles, european_nations, european_union, commonwealth, celtic) |
| Themed package restructure | **Analyse-then-restructure** (lexicographic / cultural_heritage / local_archive / media_text / media_comics / media_games / media_animation / api_finance / api_documentation / api_github / api_local / crypteolas_chain / crypteolas_docs / crypteolas_defi) |
| Domain-first restructure | **law / medicine / education cross-cut by jurisdiction** — but KEEP the geographic tree for non-domain-specific sources (statistics, official_media, etc.) |
| Tertiary pipelines (UoG, NUI) | **Under `dlt_sources/education/tertiary/<institution>/`** (UoG = 1st example: `exam_papers/`, `personal_archive/`, `official_docs/`, `students_union/`) |
| Destinations restructure | **Layer-grouped** (`dlt_sources/common/destinations/{ducklake.py, motherduck.py, filesystem.py, iceberg.py}` with `named_destinations()` factory) |
| Backwards compatibility | **Re-export shims** in legacy `__init__.py` files preserve old import paths for at least 1 release cycle (per the existing `LEGACY_ALIASES.md` precedent) |
| Migration tooling | **`git mv`** (preserves file history) driven by a Python script in `scripts/wave_1_dlt_sources_restructure.py` |

## Dependencies

`Blocked by: 2026-08-24-wave-0-cocoindex-module-path-repair-v1` (✅ landed commit `f0344b787`)
`Unblocks: 2026-08-24-wave-2-orchestration-vertical-pipelines-v1, 2026-08-24-wave-3-cocoindex-v0-stragglers-v1, 2026-08-24-wave-4-ducklake-v1-hardening-v1`
`Affected repos: cianfhoghlaim` (single-repo change)

## What changes

### 1. Domain-first law/ split — 59 directories

For every `dlt_sources/<geography>/<jurisdiction>/law/` directory:

- **WHEN** a `law/` directory exists at `dlt_sources/<geography>/<jurisdiction>/law/`
- **THEN** it SHALL be moved to `dlt_sources/law/<jurisdiction>/<geography>/`
- **AND** the old path SHALL remain importable via a re-export shim in
  `dlt_sources/<geography>/<jurisdiction>/law/__init__.py`

Geographies in scope: `american_nations`, `british_isles`, `commonwealth`,
`european_nations`, `european_union`.

### 2. Domain-first medicine/ split — 61 directories

Same mapping as law/, applied to all `medicine/` directories:

- `dlt_sources/<geography>/<jurisdiction>/medicine/` →
  `dlt_sources/medicine/<jurisdiction>/<geography>/`

### 3. Domain-first education/ split — 61 directories

- `dlt_sources/<geography>/<jurisdiction>/education/` →
  `dlt_sources/education/<jurisdiction>/<geography>/`
- The K-12 / secondary / Leaving Cert / GCSE etc. content

### 4. Tertiary sub-dir under education/

- The post-2026-08-23 UoG flat files (`uog_exam`, `uog_official_docs`,
  `uog_personal_archive`, `uog_personal_archive_figures`, `uog_students_union`)
  SHALL be relocated into `dlt_sources/education/tertiary/uog/`:
  - `exam_papers/` (was `orchestration/defs/uog_exam.py` flat)
  - `personal_archive/` (was `orchestration/defs/uog_personal_archive.py` + figures)
  - `official_docs/` (was `orchestration/defs/uog_official_docs.py`)
  - `students_union/` (was `orchestration/defs/uog_students_union.py`)
- `nui_federation/` SHALL also live under `education/tertiary/`

### 5. Themed package restructure

| Old | New | Notes |
|:--|:--|:--|
| `dlt_sources/language/ainm.py`, `canuint*.py`, `logainm.py`, `tearma*.py`, `universal_dependencies.py` | `dlt_sources/lexicographic/` | Lexicographic sources (dictionaries, terminology) |
| `dlt_sources/language/celtic_mythology.py`, `duchas*.py`, `gaois*.py`, `heritage.py`, `hidden_heritages.py` | `dlt_sources/cultural_heritage/` | Cultural heritage (folklore, mythology, schools collection) |
| `dlt_sources/language/local_documents_by_subject.py`, `local_education_documents.py` | `dlt_sources/local_archive/` | Personal local archive |
| `dlt_sources/media/official/`, `media/prose/`, `media/celtic_history_research/`, `media/animation/` | `dlt_sources/media_text/` | Text-based media |
| `dlt_sources/media/comics/` | `dlt_sources/media_comics/` | VLM-required comics |
| `dlt_sources/media/games/` | `dlt_sources/media_games/` | VLM + structured games |
| `dlt_sources/api_sources/defi/` | `dlt_sources/crypteolas_defi/` | Crypto DeFi (folds into crypteolas/) |
| `dlt_sources/api_sources/documentation/` | `dlt_sources/api_documentation/` | API documentation scraping |
| `dlt_sources/api_sources/github/` | `dlt_sources/api_github/` | GitHub-specific API |
| `dlt_sources/api_sources/local/` | `dlt_sources/api_local/` | Local API sources |
| `dlt_sources/crypteolas/local/` + `github/` | `dlt_sources/crypteolas_chain/` | Chain indexer sources |
| `dlt_sources/crypteolas/documentation/` | `dlt_sources/crypteolas_docs/` | Crypto docs |
| `dlt_sources/crypteolas/defi/` | MERGES INTO `dlt_sources/crypteolas_defi/` | (the two defi/ dirs are duplicates) |
| `dlt_sources/apple_photos/` | `dlt_sources/media_personal/` | Personal photos |
| `dlt_sources/filesystem/` | `dlt_sources/raw_files/` | Raw filesystem staging |
| `dlt_sources/portfolio/` | split into `dlt_sources/cv/`, `dlt_sources/artwork/`, `dlt_sources/labels/` | Portfolio subdomains |

### 6. Geographic de-sprawl

- `dlt_sources/british_isles/_cross/` — DOES NOT EXIST in `dlt_sources/`
  (only in `cocoindex_flows/`, deferred to Wave 3)
- `dlt_sources/british_isles/sct_wls_ni/` — KEEP (joint cross-jurisdiction stats)
- `dlt_sources/british_isles/<jurisdiction>/university/` — KEEP
  (generic university content)
- All other geographic directories: KEEP English names, just remove
  the migrated `law/`/`medicine/`/`education/` subdirs

### 7. Layer-grouped destinations

Replace:
- `dlt_sources/_lakehouse/destinations.py` (the generic factory)
- `dlt_sources/_lakehouse/personal_archive_destinations.py`
- `dlt_sources/common/destinations_cianfhoghlaim.py`
- `dlt_sources/common/destinations_tuatha.py`
- `dlt_sources/common/destinations_personal_archive_destinations.py`
- `dlt_sources/common/named_destinations.py`

With:
- `dlt_sources/common/destinations/__init__.py` — `named_destinations()` factory
- `dlt_sources/common/destinations/ducklake.py` — DuckLake + Postgres catalog
- `dlt_sources/common/destinations/motherduck.py` — MotherDuck DuckLake (prod)
- `dlt_sources/common/destinations/filesystem.py` — local + S3 + GCS + Azure
- `dlt_sources/common/destinations/iceberg.py` — Iceberg REST catalog (Lakekeeper)

Re-export shims in `_lakehouse/destinations.py` and the legacy
`common/destinations_*.py` files preserve old import paths.

### 8. LEGACY_ALIASES.md, AGENTS.md, README.md, DATA_PLATFORM_ROUTER.md updates

- `dlt_sources/LEGACY_ALIASES.md` — extend with the new mappings
- `dlt_sources/AGENTS.md` — update the routing + key sources table
- `dlt_sources/README.md` — update the package index
- `dlt_sources/DATA_PLATFORM_ROUTER.md` — update the 6 critical conventions
  to reference the new domain-first namespace

## Out of scope

- CocoIndex v0→v1 API migration (Wave 3)
- Orchestration vertical pipeline Components (Wave 2)
- DuckLake v1.0 namespace consolidation (Wave 4)
- Web apps consolidation (Wave 5)
- Frontend modernisation (Wave 6)
- OTel semantic conventions (Wave 7)

## Verification

After Wave 1 lands:

1. `uv run python -c "import dlt_sources"` succeeds
2. `uv run python -c "from dlt_sources.law.ireland import injuries_ie"` succeeds
3. `uv run python -c "from dlt_sources.education.tertiary.uog import exam_papers"` succeeds
4. `uv run python -c "from dlt_sources.crypteolas_chain import ethereum_blockchain"` succeeds
5. `uv run python -c "from dlt_sources.common.destinations import named_destinations; d = named_destinations('ducklake_cianfhoghlaim'); print(d)"` succeeds
6. All old import paths still resolve via re-export shims:
   - `from dlt_sources.commonwealth.nigeria.law import nass` (legacy)
   - `from dlt_sources.british_isles.england.law import <...>` (legacy)
7. `mise run sync:all` passes (7 layers: paths + ccc + cognee + skills + mcp + drift-docs + dagster)
8. `tests/dlt_sources/test_subject_sources.py` passes
9. `tests/dlt_sources/test_destinations.py` passes
10. `tests/dlt_sources/test_legacy_aliases.py` (NEW) passes — every old import path resolves

## Migration tooling

The script `scripts/wave_1_dlt_sources_restructure.py` performs all
`git mv` operations atomically and verifies each move. Use:

```bash
uv run python scripts/wave_1_dlt_sources_restructure.py --dry-run
uv run python scripts/wave_1_dlt_sources_restructure.py
```

## References

- Master plan: `openspec/plans/2026-08-24-master-refactor-plan.md`
- Wave 0 (unblocker): `openspec/changes/2026-08-24-wave-0-cocoindex-module-path-repair-v1/`
- Deep analyses: `openspec/plans/2026-08-24-orchestration-cocoindex-lakehouse-deep-analysis.md`
- Existing dlt_sources legacy aliases: `dlt_sources/LEGACY_ALIASES.md`
