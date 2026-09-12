# CocoIndex Pipeline Trigger via ADK Capability

## Purpose

`cocoindex-pipeline-trigger-via-adk` wraps CocoIndex v1 App updates as
ADK `FunctionTool`s. The `cocoindex_index_agent` invokes
`coco.update()` on a named App and emits asset-materialization events.

## Requirements

### Requirement: ADK FunctionTool for CocoIndex App update
The system SHALL provide an ADK `FunctionTool` named
`update_cocoindex_app` that takes an `app_module_path` (string) and
returns an `CocoIndexUpdateResult` dict with `app_name`, `rows_indexed`,
and `embedder_name`.

#### Scenario: Update a CocoIndex app
- **WHEN** `cocoindex_index_agent` invokes `update_cocoindex_app(app_module_path="cocoindex_flows._shared.gemini_deep_research")`
- **THEN** the named App's `coco.update()` MUST be called
- **AND** MUST emit a `STATE_DELTA` AG-UI event with `app_name` and `rows_indexed`
- **AND** MUST use the `BAAI/bge-m3` 1024-d embedder from the shared `_lifespan.py`

#### Scenario: App not registered
- **WHEN** `app_module_path` does not resolve to a CocoIndex App
- **THEN** the FunctionTool MUST raise `ValueError` with a clear message

### Requirement: Embedder resolution from centralized registry
The system SHALL resolve the embedder via `MODEL_REGISTRY.resolve("embedder", "default")`
instead of hard-coding an embedder name. This ensures embedder
consistency across the 96 L3 defs (closes gap #4 from
`INDEXING_LAYER_SURVEY.md`).

#### Scenario: Embedder resolution
- **WHEN** `cocoindex_index_agent` initialises
- **THEN** it MUST call `MODEL_REGISTRY.resolve("embedder", "default")` to get the embedder
- **AND** the default embedder MUST be `BAAI/bge-m3` (1024-d multilingual)
