## MODIFIED Requirements

### Requirement: baml/ cluster taxonomy is preserved with no duplicate enum defs

The 3-cluster BAML taxonomy (`education/`, `celtic/`, `processing/`) SHALL
be preserved per `baml-reorganize-by-cluster`. The system MUST enforce
that **no duplicate enum definitions** exist across the 60+ BAML files.
Common enums are defined once in `baml/education/_shared/` and re-imported.

#### Scenario: A BAML function references LeavingCertSubject

- **GIVEN** a function in `baml/education/subjects/qpack_history.baml`
  uses the `LeavingCertSubject` enum
- **WHEN** the BAML compiler processes the file
- **THEN** that enum MUST be imported from
  `baml/education/_shared/education_level.baml` (the canonical home)
- **AND** `qpack_history.baml` SHALL NOT redefine the enum locally