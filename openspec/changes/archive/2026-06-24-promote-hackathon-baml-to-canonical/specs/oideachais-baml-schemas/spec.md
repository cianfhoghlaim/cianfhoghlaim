## ADDED Requirements

### Requirement: Circular extraction BAML

The oideachais quadrant MUST provide an `ExtractCircularMeta` BAML function at `sruth/oideachais/baml_src/circular_extraction.baml`. The function MUST extract a `CircularExtraction` (composed of `CircularReference`, `MarkingSchemeSummary`, and `TopicDistribution` classes) from a Department of Education circular PDF. The function MUST use the canonical `LitellmClient` (routes through the LiteLLM gateway).

#### Scenario: Agent extracts circular metadata

- **WHEN** an agent has a DoE circular PDF and calls `ExtractCircularMeta(pdf_text=..., filename=...)`
- **THEN** the function returns a `CircularExtraction` with `circular` (CircularReference), `scheme` (MarkingSchemeSummary with topics), `raw_text_excerpt`, and `extraction_confidence`
- **AND** the call goes through the canonical `LitellmClient` (LiteLLM gateway), not the hand-rolled HF Inference wrapper
