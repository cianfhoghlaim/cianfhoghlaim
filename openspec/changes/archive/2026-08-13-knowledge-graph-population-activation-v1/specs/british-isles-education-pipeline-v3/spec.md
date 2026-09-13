## ADDED Requirements

### Requirement: 5-stage cognify graph populated

The system SHALL ensure that the Cognee knowledge graph at
`md:cianfhoghlaim.cognee_graph` contains nodes for all 5 stages of
the Irish education system (Aistear, Primary, Junior Cycle, Senior
Cycle, University). Each stage SHALL have a dedicated
`orchestration/defs/3_model_lifecycle/cognify/<stage>/defs.yaml` file
that registers the corresponding `lc5_<stage>_cognified` Dagster
asset. The cross-stage graph SHALL be wired with 8 BRIDGE edges
connecting adjacent stages + 38 cross-jurisdiction equivalences
connecting the Irish 5-stage graph to the England / Scotland / Wales /
NI graphs.

A `mise run sync:cognee-graph` CI gate SHALL fail the build if any
of the 5 stage cognify `defs.yaml` files is missing or if
`SELECT COUNT(*) FROM coggee_graph.nodes WHERE stage IN ('aistear',
'primary', 'jc', 'sc', 'university')` returns < 1,000.

#### Scenario: All 5 stages have populated cognify assets

- **GIVEN** the 5 cognify stages (Aistear + Primary + JC + SC + University)
- **WHEN** `dagster asset list | grep cognified` runs
- **THEN** the command returns 5+ `lc5_<stage>_cognified` assets
- **AND** `SELECT COUNT(*) FROM cognee_graph.nodes` returns ≥ 1,000
  real nodes (not stubs)

#### Scenario: 8 BRIDGE cross-stage edges connect adjacent stages

- **GIVEN** the cross-stage cognify graph
- **WHEN** the 8 BRIDGE edges are added
- **THEN** the edges connect Aistear ↔ Primary, Primary ↔ JC,
  JC ↔ SC, SC ↔ University (4 adjacent-stage edges), plus the 4
  lateral cross-qualification edges (JC ↔ England KS4, SC ↔
  Scotland Higher, etc.)
- **AND** `SELECT COUNT(*) FROM cognee_graph.edges WHERE
  relationship = 'BRIDGE'` returns 8

### Requirement: Bilingual EN+GA extraction uses the Gaeilge client

The system SHALL ensure that all BAML extraction functions whose
`subject_language == 'GA'` are wired to the `gaeilge_lc_client`
(defined in `baml_src/clients.baml`) which routes through LiteLLM to
the `uccix-mistral-24b` model — the platform's only dedicated
Irish-language model. The `gaeilge_lc_client` block SHALL be the
canonical BAML client for the 2 Gaeilge functions
(`ExtractBilingualLearningOutcome`, `ExtractCrossLinguisticGA`).

#### Scenario: A gaeilge syllabus PDF routes through the Gaeilge client

- **GIVEN** a Gaeilge-medium Leaving Certificate syllabus PDF
- **WHEN** the cognify pipeline ingests it
- **THEN** the `lc5_gaeilge_cognified` Dagster asset calls
  `b.ExtractBilingualLearningOutcome` with
  `subject_language == 'GA'`
- **AND** the BAML function invocation routes through
  `gaeilge_lc_client` → litellm → `uccix-mistral-24b`
- **AND** the response preserves Irish fadas (á, é, í, ó, ú) in the
  extracted `LearningOutcome.excerpt_ga` field
