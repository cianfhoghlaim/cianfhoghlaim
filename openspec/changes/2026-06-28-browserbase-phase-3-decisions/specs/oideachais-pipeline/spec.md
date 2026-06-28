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
