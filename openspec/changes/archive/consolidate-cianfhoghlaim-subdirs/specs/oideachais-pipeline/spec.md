## MODIFIED Requirements

### Requirement: dlt sources for the 9 British Isles nations

The system SHALL provide dlt sources for ALL 9 British Isles nations
(Ireland, England, Scotland, Wales, Northern Ireland, Isle of Man,
Jersey, Guernsey, and the Channel Islands). Each nation SHALL have
sources for the 4 canonical domains (education, law, medicine,
statistics) plus culture (for Ireland + Scotland).

#### Scenario: A nation dlt source imports correctly

- **GIVEN** any of the 9 nations: `ie`, `en`, `sct`, `wls`, `ni`,
  `iom`, `jey`, `ggy`, or `ci`
- **WHEN** a dagster asset in `dagster/assets/by_domain/{law,medicine}.py`
  imports `from dlt/domains/{nation}/{law,medicine}/{source}.py`
- **THEN** the import succeeds (no `ImportError`)
- **AND** the corresponding `dlt/british_isles/{nation}/{domain}/__init__.py`
  re-exports the canonical source function

#### Scenario: The 14 broken imports are fixed

- **GIVEN** the pre-existing state (verified before this change)
  where 7 dagster assets in `dagster/assets/law/{nation}/__init__.py`
  and 7 dagster assets in
  `dagster/assets/medicine/{nation}/__init__.py` import from the
  broken `dlt_sources.{nation}.{law,medicine}` paths
- **WHEN** this change is applied
- **THEN** all 14 imports are fixed to point at the canonical
  `dlt/domains/{nation}/{domain}/` paths
- **AND** `ccc search "dlt_sources\.\\w+\.law"` returns 0 hits

### Requirement: Dagster by_domain consolidation (law + medicine)

The system SHALL consolidate the 14 single-asset dagster nation
`__init__.py` files (`dagster/assets/law/{nation}/__init__.py` + the
7 corresponding `medicine/{nation}/__init__.py` files) into 2
`dagster/assets/by_domain/{law,medicine}.py` files. Each
by_domain file SHALL contain 7 `@asset` functions (one per nation).

#### Scenario: dg list defs shows the by_domain shape

- **WHEN** `dg list defs` is run after this change
- **THEN** the asset graph shows 2 by_domain groups (`law`, `medicine`)
  with 7 assets each
- **AND** the 14 old `law_{nation}_*` / `medicine_{nation}_*` asset
  names are replaced by `by_domain.law.{nation}_legislation` /
  `by_domain.medicine.{nation}_*`

### Requirement: Storage graph client unification

The system SHALL provide a single canonical multi-graph abstraction
layer at `storage/_shared/` (falkordb.py, memgraph.py, neo4j.py,
interface.py). The top-level duplicates (`storage/falkordb_client.py`,
`storage/memgraph_client.py`) SHALL be deleted (zero callers).
The hand-rolled pure-Python Graphiti implementation at
`storage/temporal.py` SHALL be deleted (replaced by the
`graphiti_core`-wrapped `storage/temporal_client.py`).

#### Scenario: A developer imports the canonical graph client

- **WHEN** the developer runs
  `from cianfhoghlaim.storage.falkordb import falkordb_client`
- **THEN** it imports from `storage/_shared/falkordb.py` (the canonical
  multi-graph abstraction layer)
- **AND** the old `storage/falkordb_client.py` is gone

### Requirement: croilar notebooks live in croilar-portal

The system SHALL move the 8 croilar-specific notebooks from
`cianfhoghlaim/notebooks/croilar/` to
`cianfhoghlaim/web/apps/croilar-portal/notebooks/`. The croilar-portal
app SHALL pick up the notebooks in its build.

#### Scenario: The croilar-portal app discovers the notebooks

- **WHEN** `bun --filter croilar-portal build` is run after this change
- **THEN** the 8 notebooks are included in the croilar-portal build
  output
- **AND** they are NOT in the cianfhoghlaim/ notebooks/ dashboard
  anymore