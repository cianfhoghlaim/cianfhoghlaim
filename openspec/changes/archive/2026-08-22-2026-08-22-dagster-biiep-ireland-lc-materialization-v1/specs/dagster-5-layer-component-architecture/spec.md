## ADDED Requirements

### Requirement: Dagster BIEP Ireland LC asset materialization contract

The system SHALL materialize the 62 Ireland-LC Dagster assets (the 5-layer KCG component chain: ingestion → materials → model lifecycle → asset generation → agent operations) for the 80 pre-downloaded PDFs at `/leaving_certificate/`. The materialization MUST run as a single Dagster job + produce 80 row outputs across the 6 LC subjects (chemistry, computer_science, english, gaeilge, geography, mathematics).

#### Scenario: A new LC PDF is added to /leaving_certificate/

- **GIVEN** the operator drops a new PDF at `/leaving_certificate/<subject>/<en|ga>/<file>.pdf`
- **WHEN** they trigger the canonical LC job via `dagster job launch` (or the marimo notebook CLI)
- **THEN** the new PDF is picked up by the layer 1 filesystem scanner
- **AND** the layer 2 ingestion asset materializes the PDF → 1 new row
- **AND** the layer 3 BAML extraction asset runs the 5 canonical lc extraction functions (ExtractCurriculumSyllabus, ExtractExamPaperLayout, ExtractMarkingSchemeGuideline, ExtractCrossLinguisticConcept, ExtractSyllabusDiagram)
- **AND** the layer 4 cognify asset adds the extraction results to the Cognee knowledge graph
- **AND** the layer 5 umbrella asset asserts the 6 per-subject assets all succeeded

#### Scenario: The BIEP Ireland LC pipeline runs end-to-end in <30s

- **GIVEN** the platform is on dlt 1.30 + DuckDB 1.5.x + litellm 1.97 + langfuse v4 + mlflow 3.15
- **WHEN** the canonical LC job materializes all 62 assets
- **THEN** the total wall-clock MUST be <5 minutes
- **AND** the 80-row output MUST land in the destination (either /tmp DuckDB for the test, or the actual lakehouse-postgres for prod)
- **AND** each layer's per-asset output rows MUST match the expected count (6 per subject × 13.3 PDFs average = 80)

### Requirement: BIEP Ireland LC asset counts

The system MUST have the following asset counts in the Dagster asset graph (per the v3.30 dlt + v3.15 mlflow + v1.97 litellm + v4.16 langfuse stack):

- **Layer 1 (Ingestion)**: ≥6 `sf_filesystem_leaving_cert_<subject>` assets (one per LC subject)
- **Layer 2 (Materials)**: ≥6 `lc5_<subject>_ingested` assets
- **Layer 3 (Model Lifecycle)**: ≥24 `lc5_<subject>_<stage>_extracted` assets (6 subjects × 4 stages: syllabus, exam, marking, diagrams)
- **Layer 4 (Asset Generation)**: ≥6 `lc5_<subject>_cognified` assets
- **Layer 5 (Agent Operations)**: ≥1 `lc5_all_baml_extraction` umbrella asset

#### Scenario: The 62 Ireland-LC assets are present in Dagster

- **WHEN** the operator runs `bun run ccc:search "leaving_cert" --type graphql-assets`
- **THEN** the response MUST include ≥62 asset keys matching `lc5_*` or `sf_filesystem_leaving_cert_*`
- **AND** the 5 KCG components (Ingestion, Materials, Model Lifecycle, Asset Generation, Agent Operations) MUST each be represented
