# `croilar-cv-extraction` capability spec

## Purpose

`croilar-cv-extraction` is a capability of the Cianfhoghlaim platform. This document is the canonical capability spec; the corresponding source code lives in the appropriate quadrant. See `docs/00_index.md` for the quadrant map and `docs/00-core/CLAUDE.md` for the project identity.


BAML-based extraction of the author's CV / achievements / teaching / identity documents. The extraction converts scanned PDFs in `author_cian_deacy_lyons_mac_an_déisigh_uí_liatháin/` into structured markdown + searchable indexes.

## Requirements
### Requirement: PDF Ingestion
The system SHALL ingest scanned PDFs from the `author_cian_deacy_lyons_mac_an_déisigh_uí_liatháin/` source directories.

#### Scenario: Achievement PDFs ingested
- **WHEN** the `cv_pdf_ingestion` Dagster asset materializes
- **THEN** the asset SHALL scan `author_cian_deacy_lyons_mac_an_déisigh_uí_liatháin/achievement/` for PDF files
- **AND** for each PDF, the asset SHALL extract text via PDF parsing (pymupdf or pdfplumber)
- **AND** the extracted text SHALL be stored in the `croilar.cv_raw` table in DuckDB

#### Scenario: Teaching PDFs ingested
- **WHEN** the `placement_ingestion` Dagster asset materializes
- **THEN** the asset SHALL scan `author_cian_deacy_lyons_mac_an_déisigh_uí_liatháin/teaching/` for PDF files
- **AND** for each PDF, the asset SHALL extract text and store it in the `croilar.teaching_raw` table

#### Scenario: Identity documents ingested
- **WHEN** the `id_document_verification` Dagster asset materializes
- **THEN** the asset SHALL scan `author_cian_deacy_lyons_mac_an_déisigh_uí_liatháin/identity/` and `vetting/` for documents
- **AND** PII documents SHALL be GPG-encrypted before storage (see PII handling)

### Requirement: BAML Extraction
The system SHALL use the new BAML schemas to extract structured data from the ingested PDFs.

#### Scenario: CV extraction
- **WHEN** the `cv_extraction` Dagster asset materializes
- **THEN** for each row in `croilar.cv_raw`, the BAML `cv_extraction.baml` schema SHALL be invoked via LiteLLM proxy (`extract` model)
- **AND** the output SHALL be one of: `EducationEntry`, `Award`, `Publication`, `Reference`
- **AND** the extracted rows SHALL be stored in the `croilar.cv_extracted` table

#### Scenario: Teaching extraction
- **WHEN** the `teaching_extraction` Dagster asset materializes
- **THEN** for each row in `croilar.teaching_raw`, the BAML `teaching_extraction.baml` schema SHALL be invoked
- **AND** the output SHALL be one of: `Placement`, `StudentFeedback`, `CurriculumDesigned`
- **AND** the extracted rows SHALL be stored in the `croilar.teaching_extracted` table

#### Scenario: Identity extraction
- **WHEN** the `id_document_verification` Dagster asset materializes
- **THEN** for each row in the PII-encrypted table, the BAML `identity_verification.baml` schema SHALL be invoked
- **AND** the output SHALL be `DocumentType`, `IssuingAuthority`, `ExpiryDate`
- **AND** the output (non-PII summary) SHALL be stored in the `croilar.identity_verified` table

### Requirement: Search Index
The system SHALL build a semantic search index over the extracted markdown.

#### Scenario: CV search index built
- **WHEN** the `cv_search_index` Dagster asset materializes
- **THEN** for each row in `croilar.cv_extracted`, the asset SHALL embed the text via CocoIndex
- **AND** store the embeddings in LanceDB collection `croilar_cv`
- **AND** write a JSON index file to `croilar/cv/search_index.json`

#### Scenario: Teaching search index built
- **WHEN** the `teaching_search` Dagster asset materializes
- **THEN** for each row in `croilar.teaching_extracted`, the asset SHALL embed the text via CocoIndex
- **AND** store the embeddings in LanceDB collection `croilar_teaching`
- **AND** write a JSON index file to `croilar/teaching/search_index.json`

### Requirement: Bilingual Output
The system SHALL extract both English and Irish (Gaeilge) fields from the source PDFs.

#### Scenario: Irish fields extracted
- **WHEN** the BAML schema is invoked on a CV PDF
- **THEN** the output SHALL include both `description_en` and `description_ga` fields where applicable
- **AND** the schema SHALL use the specialised Irish models (UCCIX, GaBERT) from the LiteLLM proxy

#### Scenario: Irish search index
- **WHEN** the search index is built
- **THEN** the index SHALL include a `lang` field per document (`en` or `ga`)
- **AND** the public site's search UI SHALL filter by language
