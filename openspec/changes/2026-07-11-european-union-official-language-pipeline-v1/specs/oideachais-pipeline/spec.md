## ADDED Requirements

### Requirement: EU institutional pipeline cross-referenced from cianfhoghlaim-pipeline

The cianfhoghlaim-pipeline capability MUST cross-reference the new EU
institutional pipeline
([`european-union-official-language-pipeline`](../../../specs/european-union-official-language-pipeline/spec.md))
and the EU nations + Ukraine pipeline
([`european-nations-ukraine-pipeline`](../../../specs/european-nations-ukraine-pipeline/spec.md))
in the `## Cross-references` section.

#### Scenario: A new file in the EU expansion obeys the contract

- **WHEN** a developer reads the cianfhoghlaim-pipeline spec
- **THEN** the `## Cross-references` section MUST list
  `european-union-official-language-pipeline` AND
  `european-nations-ukraine-pipeline`
