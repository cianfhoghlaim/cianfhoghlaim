# Author-Archive Cross-Corpus Knowledge Graph

This spec covers the unified knowledge graph that combines the 6
author-archive corpora into a single Cognee dataset with 8 edge types
and 5 deterministic edge-population rules.

## Purpose

The 6 corpora (official_media, uog_coursework, personal_records,
gemini_deep_research, zotero, takeout) are stored in 4 separate
DuckLake / LanceDB tables. The user said: "we want to know what data
we have and how it was sourced". A single knowledge graph with
cross-corpus edges is the answer.

## ADDED Requirements

### Requirement: Single unified Cognee dataset

The system MUST provide a single Cognee dataset named
``oideachais_author_archive`` that holds nodes from all 6 corpora.

#### Scenario: Cognify the official_media corpus

- **WHEN** ``cognify_author_archive_rows(rows, corpus='official_media')``
  is called with N rows
- **THEN** the rows are added to the ``oideachais_author_archive`` dataset
- **AND** each row gets the ``OfficialMediaSource`` node label
- **AND** the returned summary has ``rows = N``

#### Scenario: Cognify the uog_coursework corpus

- **WHEN** ``cognify_author_archive_rows(rows, corpus='uog_coursework')``
  is called
- **THEN** the rows are added with the ``UoGArtifact`` label
- **AND** the module-specific `subject` (MATA / SOFTWARE / IRISH / EDUCATION / PERSONAL)
  is preserved as a node property

#### Scenario: Cognify the personal_records corpus with identity excluded

- **WHEN** the caller passes only 29 rows (achievement + teaching)
- **THEN** the dataset does NOT contain any ``PersonalRecord`` node
  from the ``identity/`` subdir
- **AND** the returned summary has ``rows = 29``

### Requirement: 8 edge types across the 6 corpora

The system MUST support the following 8 edge types in the
``oideachais_author_archive`` graph:

  1. ``(:OfficialMediaSource) -[:PUBLISHES]-> (:ZoteroPaper)``
  2. ``(:OfficialMediaSource) -[:DISCUSSES]-> (:UoGArtifact)``
  3. ``(:UoGArtifact) -[:TEACHES]-> (:ZoteroPaper)``
  4. ``(:PersonalRecord) -[:AWARDED]-> (:UoGArtifact)``
  5. ``(:GeminiReport) -[:CITES]-> (:ZoteroPaper)``
  6. ``(:TakeoutDoc) -[:CITES]-> (:GeminiReport)``
  7. ``(:UoGArtifact) -[:LOCATED_IN]-> (:OfficialMediaSource)``
  8. ``(:PersonalRecord) -[:AFFILIATED_WITH]-> (:OfficialMediaSource)``

#### Scenario: All 8 edge types registered

- **WHEN** ``EDGE_TYPES`` is read
- **THEN** the list has exactly 8 entries
- **AND** each entry matches the format ``<SourceLabel>-[:<VERB>]-><TargetLabel>``

### Requirement: 5 deterministic cross-corpus edge rules

The system MUST provide a function
``build_all_cross_corpus_queries(...)`` that builds the 5 Cypher
MERGE queries for the cross-corpus edge population:

  1. ``om_publishes_zotero``: match by arxiv_id or paper title in
     the OM's `site_structure_summary` or `sample_markdown`
  2. ``om_discusses_uog``: match by content-type overlap or
     topic overlap between OM's `primary_content_types` and UoG's
     `key_topics`
  3. ``personal_awarded_uog``: match by title or course_code
     between the personal record and the UoG module
  4. ``uog_located_in_om``: match by institution name (extracted
     from the OM's URL host) in the UoG artefact's text
  5. ``personal_affiliated_om``: match by institution name in a
     teaching personal record's text

#### Scenario: CPS.gov.uk publishes a Zotero paper

- **WHEN** the OM is cps.gov.uk and the Zotero paper has
  ``arxiv_id = '2402.02890'`` and ``title = 'CPS legal guidance on
  sexual offences'``
- **AND** the OM's `site_structure_summary` contains the title
  "CPS legal guidance on sexual offences"
- **THEN** the ``om_publishes_zotero`` rule builds an edge
  ``(:OfficialMediaSource {source_id: 'cps_gov_uk'}) -[:PUBLISHES
  {match_kind: 'title'}]-> (:ZoteroPaper {file_hash: '...'})``

#### Scenario: University of Galway mata artefact is located in the OM

- **WHEN** the UoG artefact's `module_title` is "Cryptography" and
  the OM is ``universityofgalway_ie``
- **THEN** the ``uog_located_in_om`` rule builds an edge
  ``(:UoGArtifact) -[:LOCATED_IN {match_kind: 'institution'}]->
  (:OfficialMediaSource {source_id: 'universityofgalway_ie'})``

### Requirement: Dagster assets for the cross-corpus cognify

The system MUST provide 3 Dagster assets in the
``author_archive_kg`` group:

  - ``author_archive_cognify`` - runs the Cognee cognify pass
  - ``author_archive_cross_edges`` - runs the 5-rule edge
    population
  - ``author_archive_kg_summary`` - emits a JSON summary of the
    graph state to ``oideachais/official_media/kg_summary.json``

#### Scenario: Cognify asset materialises

- **WHEN** the ``author_archive_cognify`` asset runs
- **THEN** the returned ``MaterializeResult`` has the keys
  ``dataset``, ``total_rows``, ``by_corpus``
- **AND** ``by_corpus`` has 6 entries (one per corpus)

#### Scenario: KG summary asset materialises

- **WHEN** the ``author_archive_kg_summary`` asset runs
- **THEN** the file ``oideachais/official_media/kg_summary.json`` is
  written
- **AND** it contains the keys ``dataset``, ``corpora``, ``edge_types``,
  ``by_corpus_edges``

### Requirement: Unified marimo dashboard

The system MUST provide a marimo notebook at
``oideachais/notebooks/dashboards/author_archive/unified_dashboard.py``
with 4 tabs:

  1. Source provenance (Stage 1) - per-source pre-research + bulk
     scrape + condense records
  2. UoG coursework (Stage 2) - per-module BAML extraction summary
  3. Cross-corpus knowledge graph (Stage 3) - node counts by label,
     edge counts by type, top 10 most-connected sources
  4. Credit usage (Stage 0.5) - Firecrawl budget burndown, recent
     charges, monthly projection

The notebook MUST include a strong-stance footer card (non-dismissible
per the project convention).

#### Scenario: Dashboard renders the 4 tabs

- **WHEN** the marimo app is started
- **THEN** the user sees 4 section headings
- **AND** a strong-stance footer card linking to the OpenSpec change

## Cross-references

- `oideachais/cognee_integration/author_archive_cognify.py` — the Cognee helper
- `oideachais/cognify_rules/author_archive_cross_corpus.py` — the 5 rules
- `oideachais/dagster_defs/assets/official_media/author_archive_kg_assets.py` — 3 Dagster assets
- `oideachais/notebooks/dashboards/author_archive/unified_dashboard.py` — the unified marimo
