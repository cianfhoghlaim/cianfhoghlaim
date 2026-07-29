## MODIFIED Requirements

### Requirement: BIEP v3 stack critical-path fixes

The system SHALL have:
1. Canonical `md:cianfhoghlaim` URI (no `md:oideachais` anywhere in active code)
2. Canonical `bge-m3` embedder (no `bge-large-en-v1.5` in lifespan)
3. 4 BIEP v3 MotherDuck Flights registered in config.yaml
4. 6 missing jurisdiction loaders in `dlt/british_isles/_cross/registry_loader.py`
5. `BIEPSubjectComponent.build_defs()` returning real Definitions
6. 5 sensors returning real RunRequests (not unconditional SkipReason)
7. Dagster group names using underscore (not slash)
8. `dg.toml` pointing to the real `orchestration.definitions` module
9. End-to-end PDF → BAML → DuckLake → CocoIndex chain functional

#### Scenario: Canonical namespace is md:cianfhoghlaim

- **WHEN** `grep -rE "oideachais[^a-z]" notebooks/_shared/ dlt/api_sources/ motherduck/flights/`
  runs
- **THEN** 0 active references SHALL be found (excluding `_legacy/`, `archive/`)
- **AND** `notebooks/_shared/db.py:LAKEHOUSE_URI_DEFAULT == "md:cianfhoghlaim"`

#### Scenario: 4 BIEP v3 flights registered + functional

- **WHEN** `duckdb -c "SELECT name FROM motherduck_dwh.flights WHERE name LIKE '%full_coverage%'"`
  runs
- **THEN** 4 flights SHALL be listed (ireland, england, sct_wls_ni, crown)

#### Scenario: Dagster group names are valid

- **WHEN** `dg check yaml` runs
- **THEN** 0 validation errors SHALL appear (no `/` in group names)

#### Scenario: seed_registry produces 1,560 rows

- **WHEN** `python3 -c "from dlt.british_isles._cross.registry_loader import seed_registry; print(seed_registry())"`
  runs
- **THEN** the output SHALL show ≥ 1,560 rows seeded across 8 jurisdictions