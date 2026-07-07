# Spec Delta — `author-archive-baml-extraction` (MODIFIED — wire ExtractZoteroMetadata)

## Purpose

`author-archive-baml-extraction` is an existing capability of the Cianfhoghlaim platform. The canonical spec lives at `openspec/specs/author-archive-baml-extraction/spec.md`. This delta adds a Zotero paper extraction requirement and modifies the existing Zotero scenario to require the BAML call.

## MODIFIED Requirements

### Requirement: Zotero Paper Extraction (extended)
The system SHALL extract structured fields from every Zotero PDF using the BAML `ExtractZoteroMetadata` function. The `zotero_source()` dlt source SHALL invoke `b.ExtractZoteroMetadata` for each Zotero PDF and emit the structured `ZoteroPaper` rows via the `arxiv_papers_baml` resource.

#### Scenario: Zotero dlt source invokes BAML
- **GIVEN** a Zotero PDF in `leabharlann/zotero/` (e.g. `2504.02890v2.pdf`)
- **WHEN** the `zotero_source()` factory is invoked with `include_extraction=True`
- **THEN** the `arxiv_papers_baml` resource SHALL call `b.ExtractZoteroMetadata(pdf_text, file_name, arxiv_id)` for each arXiv paper
- **AND** the returned `ZoteroPaper` SHALL be persisted as a row in DuckDB

#### Scenario: Memoisation
- **GIVEN** the same `file_hash` has been extracted before
- **WHEN** the asset re-materialises
- **THEN** the BAML call SHALL be skipped and the cached `ZoteroPaper` rows SHALL be reused
- **AND** the cache key SHALL be `(file_hash, baml_function_name)`

## REMOVED Requirements

*(None.)*
