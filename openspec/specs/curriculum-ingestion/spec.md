# Curriculum Ingestion Capability

## Purpose

`curriculum-ingestion` is a capability of the Cianfhoghlaim platform. This document is the canonical capability spec; the corresponding source code lives in the appropriate quadrant. See `docs/00_index.md` for the quadrant map and `docs/00-core/CLAUDE.md` for the project identity.


## Background
Processing and indexing Irish curriculum documents from NCCA, SEC, and Department of Education sources.

## Requirements

### Requirement: Document Source Integration
The system SHALL ingest curriculum documents from configured sources.

#### Scenario: NCCA Specification Import
- **GIVEN** NCCA curriculum specifications are available
- **WHEN** the ingestion pipeline runs
- **THEN** all specifications are extracted and indexed

#### Scenario: SEC Exam Paper Import
- **GIVEN** SEC exam papers and marking schemes are available
- **WHEN** the ingestion pipeline runs
- **THEN** questions and marking criteria are extracted

### Requirement: Bilingual Content Extraction
The system SHALL extract both English and Irish content from documents.

#### Scenario: Parallel Text Extraction
- **GIVEN** a bilingual curriculum document
- **WHEN** content is extracted
- **THEN** both language versions are stored with alignment

#### Scenario: Irish-Only Content
- **GIVEN** an Irish-only document
- **WHEN** content is extracted
- **THEN** the content is properly indexed with Irish language markers

### Requirement: Structural Hierarchy Preservation
The system SHALL preserve the curriculum hierarchy during ingestion.

#### Scenario: Subject-Strand-Topic Hierarchy
- **GIVEN** a curriculum specification with hierarchical structure
- **WHEN** the document is processed
- **THEN** the hierarchy (Subject → Strand → Topic → Learning Outcome) is preserved

### Requirement: Document Change Tracking
The system SHALL track changes to curriculum documents over time.

#### Scenario: Version Detection
- **GIVEN** a previously ingested document
- **WHEN** a new version is available
- **THEN** the system detects and indexes the changes

## Constraints

- All database operations through SerialDatabaseExecutor
- Batch embeddings minimum 100 texts
- Use BAML schemas for structured extraction
