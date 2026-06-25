## MODIFIED Requirements

### Requirement: Every dlt source SHALL have a Dagster asset wrapper
The oideachais quadrant SHALL provide a Dagster asset wrapper for
every `@dlt.source` function in `sruth/oideachais/dlt_sources/`. The
wrapper MUST be a plain `@asset` (or `@dlt_assets` / `@multi_asset`)
that:
1. Imports the dlt source function
2. Calls `safe_dlt_run(pipeline, source())` to materialise the
   data into DuckLake
3. Returns a `MaterializeResult` with row-count metadata
4. Has a corresponding `@asset_check` that asserts at least
   1 row was loaded (when the cache/source is non-empty)

#### Scenario: A new dlt source is added
- **WHEN** a contributor adds a new `@dlt.source` to
  `sruth/oideachais/dlt_sources/`
- **THEN** they MUST add a corresponding Dagster asset wrapper
  in the same PR, following the `leaving_cert/dlt_assets.py`
  pattern (plain `@asset` + `dlt.pipeline(...)` + `safe_dlt_run`)

#### Scenario: A dlt source is removed
- **WHEN** a contributor removes a dlt source
- **THEN** they MUST also remove the corresponding Dagster asset
  wrapper in the same PR

#### Scenario: A dlt source exists with no Dagster asset wrapper
- **WHEN** the codebase audit (`grep "dlt_sources.*<source>"`) finds
  a dlt source with no Dagster asset wrapper
- **THEN** that source is in violation of this rule and MUST be
  fixed in a follow-up change (similar to the
  `wire-unwired-dlt-sources` openspec change)

### Requirement: DLT source asset keys follow the {nation}.{domain}.{entity} contract
Every Dagster asset wrapper for a dlt source MUST use an asset
key that follows the `{nation}.{domain}.{entity}` contract from
`.agents/skills/cross-domain-registry/SKILL.md`. The 8 nation
codes are `ie` / `ni` / `en` / `sct` / `wls` / `iom` / `jey` / `ggy`.
The 5 domain codes are `education` / `medicine` / `law` /
`statistics` / `site_analysis`. The entity is the lowercase
source name (e.g. `gias`, `insight`, `simd`, `estyn`,
`jersey_education`, `guernsey_education`, `primary`,
`junior_cycle`, `tertiary`, `local_documents`, `parallel_corpus`).

#### Scenario: A new asset wrapper is added
- **WHEN** a contributor adds a Dagster asset wrapper
- **THEN** the `key` parameter MUST be a 3-tuple or 4-tuple
  `[nation, domain, entity]` or `[nation, domain, entity, sub_entity]`
- **AND** the `group_name` MUST be one of:
  - `uk_education` for EN/NI/SCT/WLS
  - `crown_dependencies_education` for IOM/JEY/GGY
  - `ie_education` for IE
