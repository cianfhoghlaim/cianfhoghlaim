# meaisinfhoghlaim-ocr-htr

## ADDED Requirements

### Requirement: BAML Collector API integration for OCR/VLM ensemble observability

The EnsembledExtractor.extract method SHALL wire the BAML Collector
API for every per-path BAML invocation, so the MLflow observability
hook fires for every successful extraction.

The reason: per the 2026-08-13-ocr-vision-activation-completion-v1
change, the _ragas_vote method uses inline scoring rather than the
canonical evaluate_ensemble from ragas_biiep_ensemble.py. The MLflow
observability hook fires only when evaluate_ensemble is called. So
without the BAML Collector wiring, MLflow never sees the per-path
token usage plus raw LLM response.

The BAML Collector API exposes three observability surfaces: usage
metrics, raw LLM response text, and HTTP response per call. Each
surface is required for downstream telemetry.

#### Scenario: Path 1 BAML extraction succeeds

- **WHEN** EnsembledExtractor.extract runs the BAML extraction for
  an Ireland LC chemistry PDF and returns a BAMLPathOutput
- **THEN** the b.ExtractChemSyllabus call MUST pass
  baml_options with a collector argument where my_collector is a
  module-level Collector instance
- **AND** the per-path record MUST populate path_output.usage
  from my_collector.last.usage
- **AND** path_output.raw_response MUST equal
  my_collector.last.raw_llm_response
- **AND** MLflow experiment biiep_v3 MUST record a run with token
  usage metrics

#### Scenario: All 4 paths wire the Collector

- **WHEN** the 4-path ensemble runs end-to-end on a real PDF
- **THEN** all 4 path outputs (baml + unstract + qwen3-vl + gemma4)
  MUST have populated usage and raw_response fields
- **AND** the canonical evaluate_ensemble MUST run with the 4
  Collector instances as inputs