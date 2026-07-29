## ADDED Requirements

### Requirement: Global jurisdiction display-name convention

The cianfhoghlaim-pipeline capability MUST adopt the global jurisdiction
display-name convention declared by the
[`cross-region-pipeline`](../../../specs/cross-region-pipeline/spec.md)
umbrella spec: full country / state names in every display string,
short IDs in every identifier.

#### Scenario: A new jurisdiction file obeys the convention

- **WHEN** a developer reads the cianfhoghlaim-pipeline spec
- **THEN** the `## Cross-references` section MUST point at the
  `cross-region-pipeline/spec.md` rename convention
