## ADDED Requirements

### Requirement: cross-nation audit produced for SQA / WJEC / CCEA / AQA / Pearson

The system SHALL produce and maintain a canonical cross-nation content
audit document at `docs/agents/cross-nation-content-audit.md` that
covers the 5 British-Isles nations' exam boards — **SQA** (Scotland),
**WJEC + CBAC** (Wales), **AQA** (England, board 1 of 3),
**Pearson Edexcel** (England, board 2 of 3), and **CCEA** (Northern
Ireland) — plus a sub-section for the **Crown Dependencies** (Isle of
Man, Jersey, Guernsey).

For each nation, the audit SHALL document the canonical exam-board URL,
the syllabus / paper / marking-scheme file layout, the language
convention, the partition pattern, and the syllabus-topic overlap
with the 6 Irish LC priority subjects.

The audit SHALL also include a per-nation mapping to the 7
`baml/education/lc_extraction/*.baml` functions
(`ExtractCurriculumSyllabus`, `ExtractExamPaperLayout`,
`ExtractMarkingSchemeGuideline`, `ExtractCrossLinguisticConcept`,
`ExtractSyllabusDiagram`, `ExtractCircular`, `LinkCircularToSyllabus`)
and the 5 `baml/education/cross_nation/*.baml` functions
(`ExtractCrossNationSpec`, `AlignOutcomes`, `CompareCurricula`,
`TranslateEducationalContent`, `IdentifyResourceSharing`).

#### Scenario: audit doc is queryable

- **WHEN** the v2 design lead opens `docs/agents/cross-nation-content-audit.md`
- **THEN** the doc SHALL be 2,000-3,000 words
- **AND** SHALL document at least 1 working exam-board URL per nation
- **AND** SHALL include a per-nation language + partition pattern
- **AND** SHALL include a shared-vs-nation-specific topics table

#### Scenario: ccc finds the audit doc + the 5 scaffolded sources

- **WHEN** the user runs `ccc search "cross-nation scaffold"`
- **THEN** the audit doc + the 5 scaffolded DLT sources
  SHALL all be returned in the result set

### Requirement: 5 scaffolded DLT sources (one per nation) pass the smoke test

The system SHALL provide 5 scaffolded DLT source modules at:

- `cianfhoghlaim/dlt/british_isles/scotland/education/sqa/syllabus_source.py`
- `cianfhoghlaim/dlt/british_isles/wales/education/wjec/syllabus_source.py`
- `cianfhoghlaim/dlt/british_isles/england/education/aqa/syllabus_source.py`
- `cianfhoghlaim/dlt/british_isles/england/education/pearson/syllabus_source.py`
- `cianfhoghlaim/dlt/british_isles/northern_ireland/education/ccea/syllabus_source.py`

Each source SHALL:

- Decorate a `@dlt.resource(name="<subject>_syllabus", write_disposition="merge", primary_key=["url"])` for the canonical `mathematics` proof-of-concept subject.
- Read from `stedding/site_scrape_samples/<board>/<lang>/<subject>/sample.json` when the cache file exists.
- Yield 1 row when the cache file is present, 0 rows otherwise.
- Use the `get_dlt_destination(namespace="<board>")` factory from `cianfhoghlaim/dlt/common/destinations_oideachais.py` (the v1 BIEP's per-namespace `warehouse`-equivalent named destination).
- Honour `USE_LOCAL_SCRAPES=true` to skip any future live network calls.

The 5 sources are read-only scaffolds — they MUST NOT make live
network calls and MUST NOT depend on Firecrawl, Crawl4AI, or any
external HTTP client.

#### Scenario: scaffolded source reads 1 row from cache

- **GIVEN** `stedding/site_scrape_samples/sqa/en/mathematics/sample.json` exists
- **WHEN** `dlt.pipeline(pipeline_name="biep_sqa_smoke", destination=duckdb).run(sqa_syllabus_source())` runs
- **THEN** the pipeline SHALL complete with 1 row in the `sqa_mathematics_syllabus` DuckDB table
- **AND** the row's `url` SHALL equal the `sourceURL` field of the cache file

#### Scenario: scaffolded source reads 0 rows when cache is absent

- **GIVEN** `stedding/site_scrape_samples/wjec/en/mathematics/sample.json` does NOT exist
- **WHEN** the wjec smoke test runs
- **THEN** the pipeline SHALL complete with 0 rows
- **AND** SHALL NOT raise an exception
- **AND** SHALL log a `using_local_scrape_samples` warning that the cache file was not found

## MODIFIED Requirements

### Requirement: Cross-nation extension deferred to v2

The system SHALL NOT (in v1) ingest Scotland (SQA), Wales (WJEC),
England (AQA/OCR/Edexcel), Northern Ireland (CCEA), Isle of Man,
Jersey, or Guernsey curricula. These are scoped for the separate v2
change; the canonical fact base for v2 is the cross-nation content
audit at `docs/agents/cross-nation-content-audit.md` produced by
`openspec/changes/2026-07-09-cross-nation-content-audit-v1/`, and
the 5 scaffolded DLT sources at
`cianfhoghlaim/dlt/british_isles/{scotland,wales,england,england,northern_ireland}/education/{sqa,wjec,aqa,pearson,ccea}/syllabus_source.py`
are the proof-of-concept preconditions for v2 production-isation.

#### Scenario: v2 boundary

- **WHEN** a developer queries the v1 BIEP for Scottish curriculum data
- **THEN** the system returns an empty result with the message
  "deferred to v2; cross-nation extension is the next phase"
- **AND** the v1 BIEP SHALL NOT import or instantiate any of the 5
  scaffolded cross-nation DLT sources
