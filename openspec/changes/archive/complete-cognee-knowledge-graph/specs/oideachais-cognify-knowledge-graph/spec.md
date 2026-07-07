## MODIFIED Requirements

### Requirement: The cross-stage cognify SHALL call cognee.cognify
The system MUST call `cognee.cognify(dataset_name="...")` on the
loaded cross-stage data, not just log edge definitions. The
cross-stage cognify MUST be the canonical entry point for
cross-stage edge materialisation; no other code path SHALL
create cross-stage edges.

The `cognee_integration/cross_stage_cognify.py` asset MUST:
1. Iterate over the 8 `EDGE_DEFINITIONS`
2. Add each edge to Cognee via `cognee.add(...)`
3. Call `await cognee.cognify(dataset="oideachais.cross_stage")`
4. Return the number of edges actually created

#### Scenario: The cross-stage cognify runs
- **WHEN** the `cognee_integration/cross_stage_cognify.py`
  asset is materialised
- **THEN** it MUST actually call `cognee.cognify()`, not just
  log edge definitions

#### Scenario: Cognee is not available
- **WHEN** the `cognee` Python package is not installed
- **THEN** the asset MUST return 0 edges with a warning
- **AND** the asset MUST NOT raise an exception

#### Scenario: Cognee's LLM key is missing
- **WHEN** `cognee.cognify()` fails with an LLM-key error
- **THEN** the asset MUST catch the exception and return 0 edges
  with a warning
- **AND** the asset MUST NOT crash the Dagster materialisation

### Requirement: All 8 author-archive cross-corpus edge rules SHALL be wired
The oideachais cognify pass MUST execute all 8 documented
author-archive cross-corpus edge rules.

#### Scenario: The cross-corpus cognify pass runs
- **WHEN** the `cognee_integration/author_archive_cognify.py`
  cognify pass is triggered
- **THEN** all 8 edge rules MUST be evaluated
- **AND** the resulting FalkorDB graph MUST contain edges of
  each of the 8 types
- **AND** the `EDGE_TYPES` constant in
  `cognee_integration/author_archive_cognify.py` MUST list
  all 8 edge types
