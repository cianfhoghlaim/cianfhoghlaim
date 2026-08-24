# dlt-sources-domain-restructure Specification

## Purpose

`dlt-sources-domain-restructure` is a capability of the Cianfhoghlaim
platform that codifies the canonical domain-first namespace for
`dlt_sources/`. After this spec is implemented:

- `dlt_sources/<domain>/<jurisdiction>/<geography>/` is the canonical
  layout for law, medicine, and education sources
- `dlt_sources/<themed_package>/` is the canonical layout for
  lexicographic, cultural_heritage, local_archive, media_text,
  media_comics, media_games, media_animation, media_personal,
  api_documentation, api_github, api_local, crypteolas_chain,
  crypteolas_docs, crypteolas_defi, cv, artwork, labels, raw_files
- `dlt_sources/common/destinations/{ducklake,motherduck,filesystem,iceberg}.py`
  is the canonical destinations layout
- All legacy paths remain importable via re-export shims for at least
  one release cycle

This spec captures Wave 1 of the 2026-08-24 master refactor plan.

## Requirements

### Requirement: Domain-first law/ split

The 59 `dlt_sources/<geography>/<jurisdiction>/law/` directories SHALL
be relocated to `dlt_sources/law/<jurisdiction>/<geography>/`.

#### Scenario: Every law/ directory lives under dlt_sources/law/

- **WHEN** `find dlt_sources -maxdepth 4 -name "law" -type d -not -path "*__pycache__*"` runs
- **THEN** every result SHALL match the pattern `dlt_sources/law/<jurisdiction>/<geography>/law`
- **AND** the count SHALL equal 59

### Requirement: Domain-first medicine/ split

Same as the law/ requirement, applied to all `medicine/` directories.
The 61 medicine/ directories SHALL be relocated to
`dlt_sources/medicine/<jurisdiction>/<geography>/`.

### Requirement: Domain-first education/ split

The 61 K-12 / secondary `education/` directories SHALL be relocated to
`dlt_sources/education/<jurisdiction>/<geography>/`. The tertiary
(3rd-level, university) content SHALL live under
`dlt_sources/education/tertiary/<institution>/`.

#### Scenario: Tertiary pipelines live under education/tertiary/

- **WHEN** `ls dlt_sources/education/tertiary/` runs
- **THEN** the result SHALL include `uog/` (University of Galway — the
  1st example) and `nui_federation/` (NUI federation)
- **AND** `uog/` SHALL contain `exam_papers/`, `personal_archive/`,
  `official_docs/`, `students_union/` subdirs

### Requirement: Themed package restructure

The themed packages SHALL be reorganised as follows:

| Old location | New location |
|:--|:--|
| `dlt_sources/language/{ainm,canuint*,logainm,tearma*,universal_dependencies,_canuint_helpers,_tearma_helpers,_gaois_helpers}.py` | `dlt_sources/lexicographic/` |
| `dlt_sources/language/{celtic_mythology,duchas*,gaois*,heritage,hidden_heritages,_duchas_images_helpers}.py` | `dlt_sources/cultural_heritage/` |
| `dlt_sources/language/{local_documents_by_subject,local_education_documents,_local_documents_helpers}.py` | `dlt_sources/local_archive/` |
| `dlt_sources/media/{official,prose,celtic_history_research,animation}/` | `dlt_sources/media_text/` |
| `dlt_sources/media/comics/` | `dlt_sources/media_comics/` |
| `dlt_sources/media/games/` | `dlt_sources/media_games/` |
| `dlt_sources/api_sources/defi/` | `dlt_sources/crypteolas_defi/` (merges with crypteolas/defi) |
| `dlt_sources/api_sources/documentation/` | `dlt_sources/api_documentation/` |
| `dlt_sources/api_sources/github/` | `dlt_sources/api_github/` |
| `dlt_sources/api_sources/local/` | `dlt_sources/api_local/` |
| `dlt_sources/crypteolas/{local,github}/` | `dlt_sources/crypteolas_chain/` |
| `dlt_sources/crypteolas/documentation/` | `dlt_sources/crypteolas_docs/` |
| `dlt_sources/apple_photos/` | `dlt_sources/media_personal/` |
| `dlt_sources/filesystem/` | `dlt_sources/raw_files/` |
| `dlt_sources/portfolio/{cv,artwork,labels}/` | `dlt_sources/{cv,artwork,labels}/` (split) |
| `dlt_sources/jobs/` | `dlt_sources/_jobs/` (rename — CLI dispatcher) |

### Requirement: Layer-grouped destinations

The destinations layout SHALL be consolidated to:

```
dlt_sources/common/destinations/
├── __init__.py            # named_destinations() factory
├── ducklake.py            # DuckLake + Postgres catalog
├── motherduck.py          # MotherDuck DuckLake (prod)
├── filesystem.py          # local + S3 + GCS + Azure
└── iceberg.py             # Iceberg REST catalog (Lakekeeper)
```

The legacy files at `dlt_sources/_lakehouse/destinations.py`,
`dlt_sources/_lakehouse/personal_archive_destinations.py`, and
`dlt_sources/common/destinations_*.py` SHALL be replaced by re-export shims.

#### Scenario: named_destinations() returns the right factory

- **WHEN** `from dlt_sources.common.destinations import named_destinations; d = named_destinations('ducklake_cianfhoghlaim')` runs
- **THEN** `d` SHALL be a valid dlt destination instance
- **AND** `d.destination_name` SHALL equal `'ducklake'`

### Requirement: Geographic de-sprawl

The geographic packages (american_nations, british_isles, european_nations,
european_union, commonwealth, celtic) SHALL KEEP their English names per
the user's preference. After Wave 1:

- `law/`, `medicine/`, `education/` subdirs SHALL be removed (migrated up)
- `_cross/` variants SHALL be merged (only exist in `cocoindex_flows/`,
  deferred to Wave 3)
- `university/` and `statistics/` subdirs SHALL be retained
- `sct_wls_ni/` (joint cross-jurisdiction stats) SHALL be retained

#### Scenario: Geographic trees have only non-domain-specific content

- **WHEN** `find dlt_sources/{american_nations,british_isles,european_nations,european_union,commonwealth,celtic} -maxdepth 3 -name "law" -o -name "medicine" -o -name "education"` runs
- **THEN** the result SHALL be empty (all migrated up to domain-first layout)

### Requirement: Backwards compatibility via re-export shims

Every legacy import path SHALL remain resolvable via re-export shims in
the old location's `__init__.py`.

#### Scenario: All legacy imports resolve

- **WHEN** `tests/dlt_sources/test_legacy_aliases.py` runs
- **THEN** every legacy import in the test SHALL succeed:
  - `from dlt_sources.commonwealth.nigeria.law import nass`
  - `from dlt_sources.british_isles.england.law import <...>`
  - `from dlt_sources.european_nations.poland.law import <...>`
  - `from dlt_sources.commonwealth.australia.medicine import tga`
  - `from dlt_sources.language import ainm, canuint, tearma, logainm`
  - `from dlt_sources.media.comics import <...>`
  - `from dlt_sources.api_sources.defi import <...>`
  - `from dlt_sources.crypteolas.local import <...>`
  - `from dlt_sources._lakehouse.destinations import <...>`
  - `from dlt_sources.common.destinations_cianfhoghlaim import <...>`

### Requirement: Documentation updates

The following files SHALL be updated to reflect the new namespace:

- `dlt_sources/LEGACY_ALIASES.md` — extend with the new mappings
- `dlt_sources/AGENTS.md` — update routing + key sources table
- `dlt_sources/README.md` — update package index
- `dlt_sources/DATA_PLATFORM_ROUTER.md` — update conventions

#### Scenario: AGENTS.md counts match reality

- **WHEN** `find dlt_sources/law dlt_sources/medicine dlt_sources/education -mindepth 1 -maxdepth 1 -type d` runs
- **THEN** the count SHALL equal ~180 (59 law + 61 medicine + 61 education jurisdictions)
- **AND** `dlt_sources/AGENTS.md` SHALL claim this count

### Requirement: Migration tooling

The Wave 1 migration SHALL be performed by
`scripts/wave_1_dlt_sources_restructure.py` which:

- Discovers every `law/`, `medicine/`, `education/`, `university/` subdir
- Discovers every file in `language/`, `media/`, `api_sources/`, `crypteolas/`,
  `apple_photos/`, `filesystem/`, `portfolio/`
- Builds a migration map: `old_path → new_path`
- Executes `git mv` for each move (preserves file history)
- Generates `__init__.py` re-export shims for legacy paths
- Has `--dry-run` flag for verification
