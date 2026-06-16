# Spec Delta — `author-archive-baml-extraction` (MODIFIED — add `ZoteroPaper`)

## Purpose

`author-archive-baml-extraction` is an existing capability of the Cianfhoghlaim platform. The canonical spec lives at `openspec/changes/author-archive-gemini-and-uos-ingestion/specs/author-archive-baml-extraction/spec.md`. This delta adds the `ZoteroPaper` schema and `ExtractZoteroMetadata` function.

## MODIFIED Requirements

### Requirement: Zotero Paper Extraction
The system SHALL extract structured fields from every Zotero PDF using the BAML `ExtractZoteroMetadata` function.

#### Scenario: Function defined
- **GIVEN** `baml_src/author_archive.baml` is generated
- **WHEN** the function is invoked with `(pdf_text, file_name, arxiv_id)` for a Zotero PDF
- **THEN** the BAML client SHALL return a `ZoteroPaper` instance with `paper_kind: PaperKind` (one of `arxiv_preprint | journal_article | conference_paper | thesis | book_chapter | book | other`), `arxiv_id: string?`, `doi: string?`, `title: string`, `authors: list[Author]` (each `Author` with `name: string`, `affiliation: string?`), `year: int?`, `abstract: string?`, `venue: string?`, `irish_relevant: bool`, `htr_relevant: bool`, `confidence: float` (clamped 0.0-1.0)

#### Scenario: arXiv ID propagation
- **GIVEN** a Zotero PDF with `arxiv_id = "2504.02890"` (extracted from the filename by the dlt source)
- **WHEN** the BAML extractor runs
- **THEN** the `arxiv_id` field in the returned `ZoteroPaper` SHALL match the input
- **AND** if the BAML extractor disagrees (e.g. the paper is actually a journal article, not an arXiv preprint), the BAML value SHALL win

#### Scenario: Irish / HTR relevance flags
- **GIVEN** a Zotero PDF about Irish language HTR (e.g. `Castilho et al. - An End-to-End Approach for Handwriting Recognition.pdf`)
- **WHEN** the BAML extractor runs
- **THEN** `htr_relevant = true` and `irish_relevant = true` (or false, depending on the actual content)
- **AND** the downstream CocoIndex App MAY use these flags to filter or weight search results

#### Scenario: TSV metadata skipped
- **GIVEN** a `*.tsv` file in `leabharlann/zotero/`
- **WHEN** the asset materialises
- **THEN** the TSV SHALL NOT be parsed as a metadata source
- **AND** the metadata SHALL come from the BAML extractor (or the filename regex if BAML is not available)

## REMOVED Requirements

*(None.)*
