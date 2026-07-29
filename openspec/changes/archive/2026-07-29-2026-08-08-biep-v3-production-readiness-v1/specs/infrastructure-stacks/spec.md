## MODIFIED Requirements

### Requirement: BIEP v3 stack production-ready (P2)

The system SHALL have:
1. Real OCR ensemble wiring (4 real HTTP/BAML calls)
2. Real RAGAS evaluation (replaces heuristic stub)
3. Real DuckLake writes (replaces logger.info stub)
4. Subject-scoped backfill job
5. Daily 8-jurisdiction declarative automation
6. CocoIndex consumes voted DuckLake output

#### Scenario: Real OCR ensemble

- **WHEN** `EnsembledExtractor.extract(test_pdf_path=...)` runs
- **THEN** `_call_docling` SHALL return a real HTTP response (not a sentinel string)
- **AND** `_call_unstract` SHALL return a real workflow output
- **AND** `_call_qwen3_vl` SHALL return a real LiteLLM response
- **AND** `_call_gemma4` SHALL return a real llama-swap response

#### Scenario: Real RAGAS evaluation

- **WHEN** `evaluate_ensemble(real_extraction_result)` runs
- **THEN** the RAGAS score SHALL reflect actual extraction quality
- **AND** MLflow experiment name SHALL be `"biiep_v3"`

#### Scenario: PDF → BAML → DuckLake → CocoIndex chain

- **WHEN** a test PDF lands at `s3://garage/cianfhoghlaim/ireland/lc/mathematics/2026/test.pdf`
- **THEN** the chain runs end-to-end: BAML extracts → DuckLake writes 5 per-path rows + 1 voted-canonical row → CocoIndex reads the voted-canonical → LanceDB receives the embed

#### Scenario: 8-jurisdiction daily automation

- **WHEN** the daily `AutomationCondition.cron("@daily")` triggers at midnight UTC
- **THEN** all 8 jurisdiction generic asset pipelines SHALL re-materialize

#### Scenario: Subject-scoped backfill

- **WHEN** `define_asset_job(name="ireland_lc_mathematics_backfill", selection=[...])` runs
- **THEN** only the LC mathematics partitions re-materialize (not all 544 Ireland cohorts)