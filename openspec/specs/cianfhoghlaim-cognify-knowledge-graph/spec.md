# Oideachais Cognify Knowledge Graph Capability

## Purpose

`cianfhoghlaim-cognify-knowledge-graph` is a capability of the Cianfhoghlaim
platform. The corresponding source code lives at
`cianfhoghlaim/cognee_integration/` (the 5-stage cross-stage cognify +
site-analysis cognify + leabharlann cognify adapters) and
`cianfhoghlaim/graph/` (the application-layer FalkorDB + Memgraph clients).
See `docs/00_index.md` for the quadrant map and
`docs/00-core/CLAUDE.md` for the project identity.

This spec was consolidated from the 2 separate `knowledge-graph` and
`leabharlann-cognify-and-cross-archive-edges` specs.

## Background

Knowledge graph construction via Cognee (5-stage curriculum knowledge
graph with 8 cross-stage edges, site-analysis cognify, leabharlann
cognify with 3 datasets), with deterministic cross-archive edge
population in FalkorDB. The full 133-line `knowledge-graph` spec is
subsumed by this spec; the 36-line `leabharlann-cognify-and-cross-archive-edges`
spec is also subsumed.
## Requirements
### Requirement: 5-stage cross-stage knowledge graph

The system SHALL build a 5-stage curriculum knowledge graph with 8
cross-stage edges spanning Aistear → Primary → Junior Cycle → Senior
Cycle → Tertiary.

#### Scenario: 8 cross-stage edges

- **GIVEN** the 5 stage dlt sources have materialised
- **WHEN** the `cross_stage_cognify` Dagster asset runs
- **THEN** the Cognee cognify pass creates the 8 cross-stage edges:
  - `(:AistearPrinciple) -[:BRIDGES_TO]-> (:PrimaryLearningOutcome)`
  - `(:PrimaryLearningOutcome) -[:PREPARES_FOR]-> (:JCLearningOutcome)`
  - `(:JCLearningOutcome) -[:PROGRESSES_TO]-> (:SCLearningOutcome)`
  - `(:SCLearningOutcome) -[:ASSESSED_BY]-> (:ExamQuestion)`
  - `(:LCSubject) -[:REQUIRED_FOR]-> (:CAOCourse)`
  - `(:CAOCourse) -[:DELIVERS]-> (:Programme)`
  - `(:QQIFetAward) -[:LADDERS_INTO]-> (:CAOCourse)`
  - `(:Apprenticeship) -[:ALTERNATIVE_TO]-> (:CAOCourse)`

### Requirement: Site-analysis cognify

The system SHALL cognify `SiteAnalysis` records (the firecrawl /
browserbase MCP-driven site audits) into a separate Cognee dataset
`cianfhoghlaim_site_analysis`.

#### Scenario: Site analysis cognify

- **GIVEN** a `SiteAnalysis` row (CMS detection, layout, robots.txt,
  captcha)
- **WHEN** the `cognify_site_analysis_rows` function is called
- **THEN** the Cognee cognify pass creates the 4 edge types: `uses_cms`,
  `hosts_pdf`, `requires_captcha`, `has_robots_txt`

### Requirement: Leabharlann cognify

The system SHALL cognify the 3 leabharlann corpora (books, zotero,
takeout) into 3 Cognee datasets.

#### Scenario: Books cognify

- **GIVEN** the `leabharlann_books` dlt source has materialised
- **WHEN** the `cognify_leabharlann_books` Dagster asset runs
- **THEN** the rows are added to the Cognee dataset `leabharlann_books`
  and `cognify()` is called

#### Scenario: Zotero cognify

- **GIVEN** the `leabharlann_zotero` dlt source has materialised
- **WHEN** the `cognify_leabharlann_zotero` Dagster asset runs
- **THEN** the rows are added to the Cognee dataset `leabharlann_zotero`
  and `cognify()` is called

#### Scenario: Takeout cognify

- **GIVEN** the `leabharlann_takeout_v1` dlt source has materialised
- **WHEN** the `cognify_leabharlann_takeout` Dagster asset runs
- **THEN** the rows are added to the Cognee dataset `leabharlann_takeout`
  and `cognify()` is called

### Requirement: Cross-archive edges (FalkorDB)

The system SHALL populate FalkorDB with deterministic cross-archive
edges between the 3 leabharlann corpora.

#### Scenario: arxiv_id match creates CITES edge

- **GIVEN** a Zotero paper with `arxiv_id=2504.02890` and a Gemini deep
  research report that cites `https://arxiv.org/abs/2504.02890`
- **WHEN** the `cross_archive_edges` Dagster asset runs
- **THEN** a `(:GeminiReport)-[:CITES {arxiv_id: "2504.02890"}]->(:ZoteroPaper)`
  edge is created in FalkorDB

#### Scenario: Module title match creates TEACHES edge

- **GIVEN** a UoG artefact with `module_title="Handwritten Text
  Recognition for Irish"` and a Zotero paper with `title="Handwritten
  Text Recognition (HTR) for Irish-Langu"`
- **WHEN** the `cross_archive_edges` Dagster asset runs
- **THEN** a `(:UoGArtifact)-[:TEACHES {match_kind: "title"}]->(:ZoteroPaper)`
  edge is created in FalkorDB (60% token-overlap heuristic)

#### Scenario: URL match creates CITES edge

- **GIVEN** a Takeout document whose body contains
  `https://gemini-report.example/abc` and a Gemini report whose
  `cited_urls` includes the same URL
- **WHEN** the `cross_archive_edges` Dagster asset runs
- **THEN** a `(:TakeoutDoc)-[:CITES {url: "..."}]->(:GeminiReport)`
  edge is created in FalkorDB

### Requirement: Cross-archive graph query API

The system SHALL expose a FastAPI route at `GET /cross-archive-graph/{query}`
that runs a FalkorDB query and returns a JSON node+edge payload.

#### Scenario: Live query returns 200

- **GIVEN** a user issues `GET /cross-archive-graph/irish%20NLP`
- **WHEN** the request is processed
- **THEN** the route returns HTTP 200 with `{"nodes": [...], "edges": [...], "total": N}`
- **AND** the response is cached in Redis for 5 minutes (FalkorDB's
  `cache_query_result`)

### Requirement: Daily cognify cron

The system SHALL fire the 4 cognify + cross-archive assets on a daily
cron at 02:00 UTC.

#### Scenario: Daily cron fires

- **GIVEN** the `cognee_cron_sensor` is enabled
- **WHEN** the cron tick at 02:00 UTC arrives
- **THEN** the sensor fires 4 `RunRequest`s (3 cognify + 1 cross-archive)
  with `run_key` derived from the date

### Requirement: BAML TypeBuilder dynamic schema (cognify-friendly)

The system SHALL use BAML `@@dynamic` classes + `TypeBuilder.add_baml(...)`
for cognify-time extraction when the source schema is not known at
`.baml` authoring time (e.g. for ad-hoc corpus ingestion).

#### Scenario: Dynamic cognify

- **GIVEN** a BAML function `GenerateCognifySchema(content) -> Schema`
  that describes the schema in BAML source, plus an
  `ExecuteCognify(content, { tb: TypeBuilder }) -> Response` function
  with `class Response { @@dynamic }`
- **WHEN** the cognify pipeline runs against an ad-hoc source
- **THEN** the LLM describes the schema, the TypeBuilder builds it,
  and the second call extracts structured data
- **AND** the data lands in the Cognee dataset as the
  pre-`@@dynamic` source schema would

### Requirement: DLT → Cognee → Memgraph multi-destination fan-out

The system SHALL use a single DLT pipeline to fan out extracted
records to: (a) DuckLake for tabular, (b) LanceDB for vector,
(c) Cognee for cognify, (d) Memgraph / FalkorDB for graph.

#### Scenario: Four-destination fan-out

- **GIVEN** a DLT resource `@dlt.resource(name="curriculum")` yields
  extracted curriculum records
- **WHEN** the pipeline runs with
  `pipeline.run([curriculum, lancedb_adapter(curriculum, embed=[...]),
  cognee_destination(), memgraph_destination()])`
- **THEN** the records SHALL be written to all 4 destinations
  in a single pipeline run
- **AND** the DLT state is unified (one `pipeline.last_trace`, not four)

### Requirement: Runtime evals + auto-retry loop on cognify inputs

The system SHALL apply the 6 deterministic runtime evals (sum
validation, positive values, subtotal consistency, unit price
accuracy, grand total calculation, data completeness) + auto-retry
loop to every cognify input BEFORE the cognify call, so cognify
only sees valid records.

#### Scenario: Eval-failing input is re-extracted, not cognified

- **GIVEN** a BAML extraction of a receipt where the grand total
  fails the eval (sum + tax ≠ grand_total)
- **WHEN** the eval loop runs
- **THEN** the extraction is retried (max 1 retry) per the
  BAML auto-retry pattern
- **AND** if both attempts fail the eval, the record is logged
  and skipped — it is NEVER fed to `cognee.add(...)`
- **AND** the cognify dataset is guaranteed to contain only
  eval-passing records

## Cross-references

- [`cianfhoghlaim/cognee_integration/`](../../cianfhoghlaim/cognee_integration/) (the 3 cognify adapters)
- [`cianfhoghlaim/cognify_rules/`](../../cianfhoghlaim/cognify_rules/) (the cross-archive rules)
- [`cianfhoghlaim/graph/`](../../cianfhoghlaim/graph/) (FalkorDB + Memgraph clients)
- [`cianfhoghlaim/web/hono-api/src/routes/cross_archive_graph.py`](../../cianfhoghlaim/web/hono-api/src/routes/cross_archive_graph.py) (the API route)
- [`.agents/skills/cognee/SKILL.md`](../../.agents/skills/cognee/SKILL.md)
- [`.agents/skills/falkordb/SKILL.md`](../../.agents/skills/falkordb/SKILL.md)
- [`openspec/specs/cianfhoghlaim-leabharlann/spec.md`](cianfhoghlaim-leabharlann/spec.md) (the upstream leabharlann pipeline)

## Migrated from (2026-07-06)

- `author-archive-cross-corpus-kg` — the `cianfhoghlaim_author_archive` single Cognee dataset pattern was merged into the 5 leabharlann cognify datasets + 3 cross-archive edge types
