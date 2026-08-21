## ADDED Requirements

### Requirement: every Firecrawl call is logged to firecrawl_meta.scrapes
The system SHALL write one row to `cianfhoghlaim.firecrawl_meta.scrapes` for every firecrawl_* call (SDK or MCP).

#### Scenario: a DLT pipeline scrapes a page
- **WHEN** `dlt_sources/common/site_crawler.py` calls `firecrawl_scrape`
- **THEN** the call SHALL be logged to `firecrawl_meta.scrapes` with `pipeline`, `tool`, `credits_used`
- **AND** the log row SHALL include the `started_at`, `completed_at`, `cache_hit`, `status`, and `metadata` fields

#### Scenario: a FirecrawlMCPClient call is logged
- **WHEN** an agent calls `FirecrawlMCPClient.search(...)` or `scrape(...)` or any other method
- **THEN** the call SHALL be logged to `firecrawl_meta.scrapes` with `pipeline=agent:<name>`, `tool=<method_name>`, `credits_used=<n>`
- **AND** the originating agent's name SHALL be in the `metadata` field

### Requirement: software stack docs are ingested into firecrawl_corpus
The system SHALL ingest ~3,960 pages of upstream package docs (17 packages) into `cianfhoghlaim.firecrawl_corpus.docs.<package>` + `firecrawl_corpus.docs_index` within 2 weeks.

#### Scenario: agent queries upstream package state
- **WHEN** the agent needs to know how Dagster 1.13.x handles asset partitions
- **THEN** the `docs_index` table SHALL have ≥5 chunks for `docs.dagster.io/api/.../partitions`
- **AND** the chunks SHALL be embedded via BAAI/bge-m3 (the shared embedder from `cocoindex_flows/infrastructure/_lifespan.py`)

#### Scenario: marimo notebook orchestrates the bootstrap
- **WHEN** `notebooks/01_corpus/01_software_stack_crawl.py` runs
- **THEN** the notebook SHALL iterate the 17 packages + call `FirecrawlMCPClient.crawl` + `FirecrawlCorpus.load` for each
- **AND** the resulting `firecrawl_corpus.docs.<package>` tables SHALL have ≥ 100 rows per package
- **AND** the `docs_index` table SHALL have ≥ 1,000 rows per package

### Requirement: education sources are ingested into firecrawl_corpus
The system SHALL ingest 17 education domains into per-jurisdiction schemas within 1 month of Phase 1 completion.

#### Scenario: agent queries NCCA syllabus
- **WHEN** the agent needs the 2026 Leaving Cert Mathematics syllabus
- **THEN** the `cianfhoghlaim.lc.mathematics.higher_en` table SHALL have the latest row
- **AND** the `docs_index` table SHALL have ≥ 3 chunks for that row

#### Scenario: marimo notebook orchestrates the recurring crawl
- **WHEN** `notebooks/01_corpus/02_education_corpus_crawl.py` runs (daily at 03:00 UTC)
- **THEN** the notebook SHALL iterate the 17 domains + call `FirecrawlMCPClient.scrape` for each (using `max_age` cache to avoid re-fetching unmodified pages)
- **AND** the resulting `firecrawl_corpus.docs.<jurisdiction>` tables SHALL be updated

### Requirement: PII sources use redactPII + zeroDataRetention
The system SHALL set `redact_pii: true` and `zero_data_retention: true` on any DLT source flagged `sensitivity: "pii"`.

#### Scenario: HSE source runs
- **WHEN** `dlt_sources/british_isles/ireland/medicine/hse.py` materializes
- **THEN** the firecrawl_scrape call SHALL include `redactPII: true`
- **AND** the firecrawl_scrape call SHALL include `zeroDataRetention: true`
- **AND** the response SHALL be logged with both flags in `firecrawl_meta.scrapes.metadata`

### Requirement: examinations.ie exam papers are ingested via Interact
The system SHALL provide a DLT source at `dlt_sources/british_isles/ireland/education/examinations_papers.py` that uses the `state-exams-ie` persistent profile to authenticate and download exam papers.

#### Scenario: new paper released
- **WHEN** the `examinations_paper_sensor` detects a new paper for LC Mathematics 2026
- **THEN** the DLT source SHALL: scrape the search results page → interact to find the PDF URL → download → parse → write to `cianfhoghlaim.lc_exam_papers.mathematics.2026`
- **AND** the session SHALL be stopped cleanly (no leaked Interact sessions)
- **AND** the persistent profile SHALL be opened with `save_changes: false` (read-only mode)

#### Scenario: budget enforcement
- **WHEN** the `firecrawl_budget_asset` nightly job detects any pipeline > 150% of its allocation
- **THEN** the budget tracker SHALL flag it
- **AND** `mise run lint:firecrawl-budget` SHALL exit 1 with a clear message identifying the over-budget pipeline

### Requirement: polyglot memory over docs_index
The system SHALL provide 3 memory backends over `docs_index` (Graphiti, LanceDB, Cognee) + a router that picks the right backend based on intent.

#### Scenario: agent asks temporal question
- **WHEN** the agent query is "What was the Dagster API in version 1.10?"
- **THEN** the router SHALL route to `Graphiti` (temporal)
- **AND** the response SHALL include the version-timestamped relationships

#### Scenario: agent asks hybrid question
- **WHEN** the agent query is "How does BAML ExtractCurriculumSyllabus relate to the CocoIndex _lifespan.py pattern?"
- **THEN** the router SHALL route to `Cognee` (cross-doc graph)
- **AND** the response SHALL include the cross-doc relationships

#### Scenario: agent asks vector question
- **WHEN** the agent query is "What's the relevant chunk for this code query?"
- **THEN** the router SHALL route to `LanceDB` (vector)
- **AND** the response SHALL include the top-5 chunks sorted by cosine similarity