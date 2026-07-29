## MODIFIED Requirements
### Requirement: Dagster code-location name
The Dagster code-location SHALL be named `cianfhoghlaim` (per `dg.toml`'s `code_location_name`), never the typo'd `cianfhoghlaim`.

#### Scenario: dg.toml declares the correct code-location
- **WHEN** `dg.toml` is read
- **THEN** `code_location_name = "cianfhoghlaim"` SHALL be set
