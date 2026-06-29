# oideachais-pipeline (delta: Phase 3 research findings)

> Filled by Phase 3 research agent (12/12 prompts complete).
> See `openspec/research/2026-06-28-browserbase-credit-program/phase-3/`.

## ADDED Requirements

### Requirement: dlt REST + sitemap.xml is the canonical ingestion pattern

The system SHALL use dlt REST sources (seeded via `sitemap.xml`) as
the canonical ingestion pattern for every public website, with
respect for each site's anti-scraping posture (rate limits, Cloudflare
challenges, robots.txt).

#### Scenario: sitemap.xml-seeded dlt source

- **GIVEN** a public website with a discoverable `sitemap.xml`
- **WHEN** the dlt source is built with `dlt.sources.sitemap(...)`
- **THEN** dlt discovers all URLs in the sitemap
- **AND** fetches them via the REST pattern with rate limiting
- **AND** writes to the Iceberg catalog as the canonical lakehouse

### Requirement: BAML ExtractEn + ExtractEnStrong is the canonical extraction stack

The system SHALL use BAML with the `ExtractEn` (cheap, fast) and
`ExtractEnStrong` (expensive, accurate) clients as the canonical
extraction stack, both routing through LiteLLM `minimax` alias.

#### Scenario: BAML extraction of exam paper

- **GIVEN** an examinations.ie PDF for Leaving Cert Maths 2024
- **WHEN** `ExtractExaminationPDF` runs with `client ExtractEnStrong`
- **THEN** it returns structured form (subject, year, component,
  question_count, max_marks, etc.)
- **AND** the call traces to Langfuse via the BAML @observe decorator

### Requirement: All 12 source sites catalogued with anti-scraping posture

The system SHALL maintain a canonical catalogue of all 12 source sites
(8 British Isles + 2 Crown Dependencies + 2 Reference) with their
anti-scraping posture documented.

#### Scenario: New source site onboarding

- **GIVEN** a new source site (e.g., a new Crown Dependency)
- **WHEN** a developer adds it to the Leabharlann corpus
- **THEN** they create a discovery report in
  `openspec/research/2026-06-28-browserbase-credit-program/phase-3/`
- **AND** document: site structure, dropdown cascade, URL pattern,
  anti-scraping posture, BAML extraction strategy

### Requirement: gov.uk standard rate limiting is respected

The system SHALL respect the gov.uk standard rate limit of ~10 req/sec
per IP, using sitemap.xml as the canonical seed for gov.uk ingestion.

#### Scenario: gov.uk ingestion rate

- **GIVEN** a gov.uk dlt source
- **WHEN** the ingestion job runs
- **THEN** it makes at most 10 requests per second per IP
- **AND** sets the User-Agent header identifying Cianfhoghlaim
- **AND** reads from `/sitemap.xml` for the URL seed

### Requirement: Zotero Web API v3 is the canonical leabharlann corpus source

The system SHALL use the Zotero Web API v3 (OAuth 1.0a) as the canonical
source for the `leabharlann/zotero` subdirectory (1,800+ items), with
rate limiting at 10 req/sec (free tier).

#### Scenario: Zotero weekly sync

- **GIVEN** a Zotero library with an API key
- **WHEN** the weekly cron runs
- **THEN** it fetches new items via `/items?since={last_version}`
- **AND** writes to the Iceberg catalog as the canonical corpus

### Requirement: arxiv API + OAI-PMH is the canonical research paper source

The system SHALL use the arxiv API + OAI-PMH endpoint as the canonical
source for arxiv research papers in the leabharlann corpus (600+ items),
with rate limiting at 1 req/sec (per arxiv TOS).

#### Scenario: arxiv daily incremental ingest

- **GIVEN** an arxiv API key (none required, but User-Agent is)
- **WHEN** the daily cron runs
- **THEN** it fetches papers from categories [cs.LG, cs.CL, cs.AI, cs.CV]
  published since yesterday
- **AND** writes to the Iceberg catalog

### Requirement: Bilingual processing for Irish + Welsh sites

The system SHALL process bilingual content (curriculumonline.ie's
`/en/` and `/ga/`; gov.wales's English + Welsh) as separate cross-corpus
entries to enable multilingual search.

#### Scenario: Irish-language curriculum extraction

- **GIVEN** curriculumonline.ie has `/en/` and `/ga/` mirror pages
- **WHEN** the dlt source processes both
- **THEN** each language gets its own Iceberg table
- **AND** a cross-language search query (e.g., "calculus") returns
  both English and Irish matches

### Requirement: per-site BAML extraction schema with T&Cs gate (Wave 2)

The system SHALL maintain a BAML extraction schema **per source site**
in `cianfhoghlaim/core/baml/_oideachais_src/site_schemas/` (one
`ClassifyExamination`, `ClassifyCurriculumOutcome`,
`ClassifyZoteroItem`, `ClassifyArxivPaper`, etc. per site), and SHALL
gate every site-specific BAML call behind the site's T&Cs /
robots.txt / rate-limit posture recorded in the `site_posture` Iceberg
table.

#### Scenario: BAML extraction gated on site posture

- **GIVEN** the `site_posture` table records
  `(site="examinations.ie", tcs="OK-rate-limited", rate_limit=2)`
- **WHEN** a dlt pipeline runs the BAML extraction on the fetched
  examinations.ie PDFs
- **THEN** it caps the BAML call rate at 2 req/sec (matching the
  site's T&Cs)
- **AND** sets the `User-Agent` header to
  `Cianfhoghlaim/1.0 (research; contact: cian@cianfhoghlaim.ie)`
- **AND** records every BAML call in Langfuse with the site posture
  context

### Requirement: Wave 3 marimo dashboard is the canonical ingestion-health surface

The system SHALL publish a **Wave 3 marimo dashboard**
(`oideachais_ingestion_health.py`) that displays, for each of the 12
source sites, the following columns: last successful run timestamp,
row count, asset-check status, T&Cs posture, anti-scraping incidents
in the last 7 days, and any TCA-only or sitemap-absent markers.

#### Scenario: Marimo dashboard renders 12-site health grid

- **GIVEN** the marimo notebook is served from
  `oideachais-web/observability/ingestion-health`
- **WHEN** a user opens the page
- **THEN** it shows a 12-row table (one per source site) with the
  ingestion health columns
- **AND** a "last 7 days incidents" stacked bar chart
- **AND** a "TCA-only" filter that highlights the 3 sites with
  teacher-only content (curriculumonline, NCCA, education-ni)

### Requirement: examinations.ie PHP-form dropdown cascade + arxiv OAI-PMH are the canonical exam + research sources

The system SHALL scrape the `examinations.ie` exam archive at
`https://www.examinations.ie/exammaterialarchive` via a headless
browser interaction (Stagehand MCP / Playwright) that handles the
PHP-style checkbox-gated dropdown form (year → cycle → subject →
component → language), and SHALL ingest arxiv papers via the OAI-PMH
endpoint (`https://export.arxiv.org/oai2`) with the canonical
category filter `[cs.LG, cs.CL, cs.AI, cs.CV]` and rate limiting at
1 req/3 sec (per the Wave-2 update to the arxiv v2 etiquette).

#### Scenario: examinations.ie dropdown cascade

- **GIVEN** the dlt source for examinations.ie needs to discover all
  Leaving Cert 2024 papers
- **WHEN** a Playwright session opens the dropdown form
- **WHEN** it selects year=2024, cycle="Leaving Certificate",
  subject="Mathematics", component="Paper 1", language="English"
- **THEN** the form POSTs to `exammaterialarchive.php` and returns
  the list of PDF URLs
- **AND** the dlt source fetches each PDF and stores it in the
  Iceberg `examination_papers` table

#### Scenario: arxiv OAI-PMH daily incremental

- **GIVEN** the arxiv sync cron runs daily at 02:00 UTC
- **WHEN** the dlt source makes an OAI-PMH `ListRecords` request
  with `from=2026-06-28&set=cs.LG`
- **THEN** the response contains all cs.LG papers since 2026-06-28
- **AND** the dlt source respects the 1 req/3 sec rate limit
- **AND** the `User-Agent` header is set to
  `Cianfhoghlaim/1.0 (research; mailto:cian@cianfhoghlaim.ie)`
- **AND** each paper's abstract is embedded via BGE-M3 and written
  to the `leabharlann_arxiv_papers` Iceberg table

### Requirement: gov.scot / gov.wales / education-ni rate-limited ingestion

The system SHALL respect the rate limits of the 3 British regional
government sources as documented in their T&Cs: **education.gov.scot**
at ≤5 req/sec (the Scottish server is the slowest), **gov.wales** at
≤10 req/sec with bilingual content split, and
**education-ni.gov.uk** at ≤2 req/sec (the NI server also has
intermittent 503s on Friday afternoons — retry with exponential
backoff).

#### Scenario: education-ni.gov.uk Friday backoff

- **GIVEN** the dlt source for education-ni.gov.uk is running on a
  Friday at 15:00 BST
- **WHEN** a request returns 503
- **THEN** the source retries with exponential backoff (1s, 2s, 4s,
  8s, capped at 30s)
- **AND** the Langfuse trace records `metadata.retry_count=N` and
  `metadata.backoff_ms=M`
- **AND** after 3 consecutive failures, the asset is marked
  `BLOCKED` and a Dagster alert is raised
