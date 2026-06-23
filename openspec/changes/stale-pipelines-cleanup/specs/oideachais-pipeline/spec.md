## MODIFIED Requirements

### Requirement: Pipeline-level Python classes live in `dagster_defs/assets/` or `meaisinfhoghlaim/`
The oideachais quadrant SHALL NOT contain a top-level `oideachais/pipelines/`
package. All pipeline-level Python classes (dialect classifiers, document
scanners, transcript aligners, audio slicers, LLM routers) MUST live in
either:

- `dagster_defs/assets/<asset_module>.py` (when wired to a Dagster
  `@asset` or `@dlt_assets` decorator), OR
- `meaisinfhoghlaim/<subpackage>/` (the model-layer quadrant, for
  reusable library code not yet wired to Dagster)

#### Scenario: New pipeline class is needed
- **WHEN** a contributor needs to add a new pipeline class (e.g. a
  new dialect classifier or audio aligner)
- **THEN** if it has a Dagster wiring, it MUST be added to
  `dagster_defs/assets/<existing_module>.py` or a new module in
  `dagster_defs/assets/`
- **AND** if it is library code (no Dagster wiring), it MUST be
  added to the appropriate `meaisinfhoghlaim/<subpackage>/` module
  per the model-layer quadrant layout in `meaisinfhoghlaim/AGENTS.md`
- **AND** it MUST NOT be added to a top-level `oideachais/pipelines/`
  package, which is forbidden

#### Scenario: A pipeline class is moved from prototype to production
- **WHEN** a prototype pipeline class is being promoted to a
  working Dagster asset
- **THEN** the class SHOULD be moved to
  `dagster_defs/assets/<asset_module>.py` with the proper `@asset`
  decorator, `@dlt_assets` wrapper, and partition definitions
- **AND** the old prototype location (if any) MUST be deleted in
  the same commit
