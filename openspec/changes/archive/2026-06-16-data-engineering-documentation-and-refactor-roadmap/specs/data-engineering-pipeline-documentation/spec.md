# Spec Delta — `data-engineering-pipeline-documentation` (new capability)

The canonical spec for `data-engineering-pipeline-documentation` lives at `openspec/specs/data-engineering-pipeline-documentation/spec.md` and was created as part of this change. The canonical spec contains the full requirements. No ADDED requirements delta is required.

(All 4 Requirements + 9 Scenarios from the original change draft have been folded into the canonical spec at `openspec/specs/data-engineering-pipeline-documentation/spec.md`.)

## MODIFIED Requirements

### Requirement: Canonical spec SHALL list 9 files
The system SHALL maintain the 9 documentation files listed in the canonical `data-engineering-pipeline-documentation` spec: `sruth/oideachais/STATUS.md`, `sruth/oideachais/REFACTORING.md`, `sruth/oideachais/dlt_sources/uk/README.md`, `sruth/oideachais/dlt_sources/ireland/README.md`, `sruth/oideachais/cocoindex_flows/README.md`, `sruth/oideachais/dagster_defs/assets/README.md`, `baml_src/README.md`, `sruth/oideachais/agents/{adk,agno}/README.md`, and `docs/06-infrastructure/leabharlann-stack-overview.md`.

#### Scenario: All 9 files exist
- **GIVEN** a user checks the documentation surface
- **WHEN** they list the 9 files
- **THEN** each file SHALL exist and be non-empty

## REMOVED Requirements

*(None.)*
