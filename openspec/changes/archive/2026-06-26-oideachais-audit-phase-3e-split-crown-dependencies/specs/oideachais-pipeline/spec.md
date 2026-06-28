## ADDED Requirements

### Requirement: Crown Dependencies Sources Live at Per-Nation Canonical Paths

The system SHALL split the `dlt_sources/crown_dependencies/` umbrella so that
each Crown Dependency's education source lives at `dlt_sources/{nation}/education/{entity}.py`,
matching the country-first layout convention.

#### Scenario: Jersey + Guernsey sources split into per-nation files

- **WHEN** `dlt_sources/crown_dependencies/channel_islands.py` contains both `jersey_source` and `guernsey_source`
- **THEN** the system SHALL move `jersey_source` to `dlt_sources/jey/education/channel_islands.py`
- **AND** the system SHALL move `guernsey_source` to `dlt_sources/ggy/education/channel_islands.py`
- **AND** the system SHALL extract shared private helpers (e.g. `_crawl_jersey_education`, `_crawl_guernsey_education`) to a sibling `_channel_islands_helpers.py`

#### Scenario: Isle of Man source moves to canonical home

- **WHEN** `dlt_sources/crown_dependencies/isle_of_man.py` contains `isle_of_man_source`
- **THEN** the system SHALL move `isle_of_man_source` to `dlt_sources/iom/education/isle_of_man.py`
- **AND** the system SHALL preserve the private `_crawl_iom_education` helper inline within the single-source file

#### Scenario: Per-nation `__init__.py` shims import from canonical paths

- **WHEN** the per-nation education shims (`iom/education/__init__.py`, `jey/education/__init__.py`, `ggy/education/__init__.py`) currently re-export from `crown_dependencies/`
- **THEN** the system SHALL replace each re-export with a direct import from the local canonical file (e.g. `from dlt_sources.iom.education.isle_of_man import isle_of_man_source`)
- **AND** the system SHALL break the circular import between the per-nation shims and the `crown_dependencies/` umbrella

#### Scenario: Crown Dependencies umbrella deleted

- **WHEN** all per-nation canonical files exist + all consumers import from the canonical paths
- **THEN** the system SHALL delete `dlt_sources/crown_dependencies/__init__.py`
- **AND** the system SHALL delete `dlt_sources/crown_dependencies/channel_islands.py`
- **AND** the system SHALL delete `dlt_sources/crown_dependencies/isle_of_man.py`
- **AND** the system SHALL leave no production-code references to `crown_dependencies` after deletion