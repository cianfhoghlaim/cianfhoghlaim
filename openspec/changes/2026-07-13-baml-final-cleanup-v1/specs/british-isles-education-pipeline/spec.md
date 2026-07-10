# Spec Delta — british-isles-education-pipeline

This delta adds one new requirement to the existing `british-isles-education-pipeline` capability. Existing requirements are preserved unchanged.

## ADDED Requirements

### Requirement: MarkingPoint classes are uniquely named per BAML file

The British-Isles Education Pipeline SHALL avoid duplicate BAML class names for marking-scheme point records. The cross-stage shared marking point class in `cianfhoghlaim/baml/education/_shared/strand_outcome.baml` SHALL be named `MarkingPointStrand`, and the SEC marking-scheme PDF extraction class in `cianfhoghlaim/baml/education/pdfs/leaving_cert_marking_scheme.baml` SHALL be named `MarkingPointSec`.

#### Scenario: no bare MarkingPoint class remains

- **GIVEN** the duplicate-class cleanup has landed
- **WHEN** the BAML tree is searched for exact class declarations matching `^class MarkingPoint\b`
- **THEN** the count is `0`
- **AND** `MarkingCriteria.marking_points` in `_shared/strand_outcome.baml` uses `MarkingPointStrand[]`
- **AND** `MarkingSchemeSec.markingPoints` in `pdfs/leaving_cert_marking_scheme.baml` uses `MarkingPointSec[]`

#### Scenario: remaining BAML diagnostics are scoped separately

- **GIVEN** `mise run baml:generate` is run after this duplicate rename
- **WHEN** BAML still reports parser diagnostics in `lc_extraction/*.baml` or other pre-existing files
- **THEN** those diagnostics remain owned by the BIEP v1 / dedicated BAML syntax cleanup scope decision, not by this MarkingPoint duplicate fix
