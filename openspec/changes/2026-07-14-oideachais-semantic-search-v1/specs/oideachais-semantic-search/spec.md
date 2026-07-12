# `oideachais-semantic-search` — Phase 1 MODIFIED delta

This delta MODIFIES the `oideachais-semantic-search` spec to add
**1 new requirement** that tracks Phase 1 implementation status
("13 requirements all functional + marimo UI"). The original 13
requirements are unchanged.

> **Note:** This is a MODIFIED delta (not ADDED Requirements)
> because it modifies the existing capability spec to add a new
> requirement for Phase 1 implementation status. The 13 original
> requirements remain in `openspec/specs/oideachais-semantic-search/spec.md`.

## MODIFIED Requirements

### Requirement: Phase 1 implementation status

The system SHALL track the implementation status of the 13
requirements in this spec, and SHALL mark Phase 1 as complete
when all 13 requirements have a working code-level implementation
backed by the cognify rules + the marimo notebook + the BAML
function.

#### Scenario: Phase 1 complete

- **GIVEN** the 13 requirements of `oideachais-semantic-search`
- **WHEN** the implementation change
  `2026-07-14-oideachais-semantic-search-v1` lands
- **THEN** the following code-level artifacts exist:
  - `storage/cognify/rules/semantic_search.py` — the cognify
    rules module exposing `embed_query`,
    `semantic_search`, `bm25_search`, `hybrid_search`,
    `multimodal_search`, `time_travel_search`,
    `geospatial_fts_search`, `register_embedding_provider`,
    `ingest_search_telemetry`
  - `baml/education/_shared/semantic_search.baml` — the BAML
    `SemanticSearch` function
  - `notebooks/12_semantic_search/01_search.py` — the marimo
    notebook exposing the canonical search UI
  - `cianfhoghlaim/web/hono-api/src/routes/search.py` — the FastAPI route at
    `/search/semantic`
- **AND** `openspec validate --strict` passes for the change
- **AND** `mise run baml:generate` exits 0
- **AND** the marimo notebook AST-parses cleanly
- **AND** `uv run cianfhoghlaim-marimo list 12_semantic_search`
  discovers exactly 1 entry