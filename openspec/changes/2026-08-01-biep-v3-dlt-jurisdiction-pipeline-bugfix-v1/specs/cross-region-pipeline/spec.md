## MODIFIED Requirements

### Requirement: dlt.common.destinations_cianfhoghlaim exports LAKEHOUSE_DUCKDB

The system SHALL require the `dlt.common.destinations_cianfhoghlaim`
module to export a module-level `LAKEHOUSE_DUCKDB` constant equal to
`"md:cianfhoghlaim"`, so the 4 BIEP v3 jurisdiction pipelines can
import it without `ImportError`.

#### Scenario: LAKEHOUSE_DUCKDB constant is exported

- **WHEN** `python3 -c "from dlt.common.destinations_cianfhoghlaim import LAKEHOUSE_DUCKDB; print(LAKEHOUSE_DUCKDB)"`
  runs
- **THEN** the output SHALL be exactly `md:cianfhoghlaim`
- **AND** no `ImportError` SHALL be raised

#### Scenario: 4 jurisdiction pipelines load without ImportError

- **WHEN** each of the 4 BIEP v3 jurisdiction pipeline modules
  (`ireland_jurisdiction_pipeline`,
  `england_jurisdiction_pipeline`,
  `sct_wls_ni_jurisdiction_pipeline`,
  `crown_dependencies_jurisdiction_pipeline`) is imported
- **THEN** no `ImportError` SHALL be raised
- **AND** `python3 -c "from dlt.british_isles.<jurisdiction>.education.*_jurisdiction_pipeline import <name>; print(<name>())"`
  returns a DLT pipeline object