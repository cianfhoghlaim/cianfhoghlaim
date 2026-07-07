# Celtic Asset Generation — ADDED Requirements from `ingest-culture-heritage`

This delta adds 1 new requirement to the existing `celtic-asset-generation` spec. It does NOT modify any existing requirement.

## ADDED Requirements

### Requirement: Culture heritage extraction schema

A new BAML file `sruth/oideachais/baml_src/culture_extraction.baml` SHALL define a `CultureHeritageClaim` class and an `ExtractCultureClaims` function over the BAML `LitellmClient` so the existing LLM-routing rules apply unchanged.

The schema extracts cultural-heritage claims from the 6 personal-heritage Gemini Deep Research PDFs at `leabharlann/gemini_deep_research/culture/` and routes them through the canonical 5-stage celtic-asset-generation pipeline (BAML extraction → CocoIndex v1 embedding → Cognee cognify → Graphiti temporal memory → LanceDB vector).

#### Scenario: When a culture PDF is extracted

- **WHEN** the `culture_heritage_extract` Dagster asset is materialised
- **THEN** every page of the source PDF MUST produce at least one `CultureHeritageClaim` record
- **AND** every record SHALL carry an `evidence_quality` ∈ {PRIMARY, SECONDARY, INFERENCE}
- **AND** claims with `confidence < 0.6` SHALL be routed to a `low_confidence_review` asset check rather than the production table

#### Scenario: When the BAML client is regenerated

- **WHEN** `baml-cli generate` runs against `sruth/oideachais/baml_src/culture_extraction.baml`
- **THEN** the generated `baml_client/` module exposes `ExtractCultureClaims` as a callable function
- **AND** the function signature accepts `(pdf_path: str, context: str)` and returns `list[CultureHeritageClaim]`
- **AND** the generated Pydantic model for `CultureHeritageClaim` validates against the 7-field shape (claim_text, people_mentioned, places_mentioned, dates, evidence_quality, wikipedia_links, confidence)

#### Scenario: When the culture_heritage claims feed the celtic 5-stage pipeline

- **WHEN** a `CultureHeritageClaim` passes the low_confidence_review check
- **THEN** it is embedded by the `culture_heritage_embedding` v1 CocoIndex App into the `oideachais.culture_heritage_chunks` LanceDB table
- **AND** the embedding uses the `BAAI/bge-m3` model (1024-dim, multilingual) — the same embedding model as the rest of the platform
- **AND** the embedded chunks are cognified into the `culture_heritage` Cognee dataset
- **AND** the cognified entities are emitted to the unified graph with cross-dataset edges