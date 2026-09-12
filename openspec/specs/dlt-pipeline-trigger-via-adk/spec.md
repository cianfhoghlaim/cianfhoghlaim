# DLT Pipeline Trigger via ADK Capability

## Purpose

`dlt-pipeline-trigger-via-adk` wraps DLT pipeline invocations as ADK
`FunctionTool`s. The `dlt_trigger_agent` invokes
`pipeline.run(source())` and emits asset-materialization events into
the AG-UI stream.

## Requirements

### Requirement: ADK FunctionTool for DLT source invocation
The system SHALL provide an ADK `FunctionTool` named `run_dlt_source`
that takes a `source_module_path` (string), a `pipeline_name` (string),
and a `dataset_name` (string) and returns a `PipelineRunResult` dict
with `load_info`, `row_counts`, and `schema_version`.

#### Scenario: Trigger a DLT pipeline
- **WHEN** `dlt_trigger_agent` invokes `run_dlt_source(source_module_path="dlt_sources._shared.gemini_deep_research", pipeline_name="gemini_deep_research_pipeline", dataset_name="oideachais_gemini_deep_research")`
- **THEN** the DLT pipeline MUST run with the source's `@dlt.source` decorator applied
- **AND** MUST emit a `STATE_DELTA` AG-UI event with `pipeline_run_id` and `load_info`
- **AND** MUST log to Langfuse via `@observe`

#### Scenario: Source not found
- **WHEN** `source_module_path` does not resolve to a Python module
- **THEN** the FunctionTool MUST raise `ValueError` with a clear message
- **AND** MUST NOT execute any pipeline run

### Requirement: DLT source wrapping for Gemini Deep Research API
The system SHALL provide `dlt_sources/_shared/gemini_deep_research.py`
exposing a `gemini_deep_research_source()` function decorated with
`@dlt.source` that yields `gemini_deep_research_report` resources
produced from the Gemini Deep Research API.

#### Scenario: Source materializes reports
- **WHEN** `gemini_deep_research_source(max_reports=10)` is called with a valid `GOOGLE_API_KEY`
- **THEN** the source MUST yield up to 10 `gemini_deep_research_report` rows
- **AND** each row MUST include `report_id`, `query`, `interactions`, `synthesized_report`, `citations`, `created_at`
