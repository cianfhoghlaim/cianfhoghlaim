# Stages vocabulary — the canonical Stage-0..Stage-3 contract

Every new website-based DLT source MUST follow this vocabulary.
This document is the single source of truth across
`dlt_sources/british_isles/ireland/education/`,
`dlt_sources/british_isles/university/`,
`dlt_sources/_lakehouse/`, and the related CocoIndex + Cognify
callsites.

## Stage 0 — `*_stage0_audit` (Firecrawl `/agent` discover)

| Field | Value |
|---|---|
| Owner | Firecrawl SDK / MCP |
| Trigger | `BackendRouter.pre_research(base_url, goal, budget_hint=2)` |
| Output | `ResearchSiteMap{ discovered_paths: list[URL], recommended_strategy: Literal["crawl4ai-static","firecrawl-agent"] }` |
| Persistence | `university_research_sitemap` LanceDB table |
| Default credit cap | `STAGE_0_MAX_CREDITS=20` |
| Fixture-mode | `MaterializeResult(skipped_fixture=True)` when `SecretsResolver.has_real_credentials() == False` |
| Dagster asset name convention | `<group>_stage0_audit` |
| BAML / DuckLake usage | NONE |

## Stage 1 — `*_stage1_collect` (bulk_scrape)

| Field | Value |
|---|---|
| Owner | Firecrawl `/scrape` (paid) or Crawl4AI (free) per `BackendRouter.bulk_scrape` strategy |
| Trigger | `BackendRouter.bulk_scrape(url, prefer_free=True)` |
| Output | DLT rows with `{ url, page_kind, raw_markdown, raw_html, backend_used, content_hash, scraped_at }` |
| Persistence | DuckLake `cianfhoghlaim.<domain>.<page_kind>` table |
| Per-resource primary key | `{url, content_hash}` (idempotent merge) |
| Fixture-mode | `status="skipped_fixture"` rows with `academic_year=0` |
| Dagster asset name convention | `<group>_stage1_collect` |

## Stage 2 — `*_baml_extract` (BAML typed extraction)

| Field | Value |
|---|---|
| Owner | BAML `ExtractEn` LiteLLM client (the canonical gateway alias) |
| Trigger | `b.ExtractUoGOfficialDocument(prompt, image_url=…)` |
| Output | Typed BAML rows (`UoGOfficialDocument`, `UoGNUIMemberDescriptor`, etc.) |
| Persistence | DuckLake typed table `cianfhoghlaim.education.ie.<table>` (one per source) |
| Fixture-mode | `status="baml_client_missing"` until `baml generate` has produced the client |
| Dagster asset name convention | `<group>_baml_extract` |

## Stage 3 — `*_embed_lance` + `*_duckdb_sink` (CocoIndex + LanceDB + DuckLake)

| Field | Value |
|---|---|
| Owner | CocoIndex v1 `@coco.fn` (LanceDB) + DuckLake `dlt` (Postgres+S3) |
| Trigger | `cocoindex update <AppName>` + dlt pipeline runs |
| Output | LanceDB vector table (BGE-M3 1024-d) + DuckLake typed table |
| Persistence | `lancedb_data/<table>.lance` + `lakehouse.cianfhoghlaim.education.ie.<table>` |
| Fixture-mode | No-op when `SecretsResolver.has_real_credentials() == False` |
| Dagster asset name convention | `<group>_embed_lance`, `<group>_duckdb_sink` |

## Cross-stage contract

Every new group MUST have:
1. A Stage 0 audit asset that emits a `MaterializeResult` with
   `pages_audited, paths_discovered, credit_used`.
2. A Stage 1 collector with a `@dlt.resource` that yields rows
   with a stable `primary_key` (so re-runs are idempotent).
3. A Stage 2 BAML extractor that routes through `ExtractEn`.
4. A Stage 3 LanceDB writer that follows the canonical v1 App
   pattern (4-rule conformance contract per
   `openspec/specs/cianfhoghlaim-cocoindex-v1-migration/spec.md`).
5. A Stage 3 DuckLake writer that respects the
   `destination=` keyword and writes to whichever backend
   resolved.

The BashBoard pattern + marimo notebook for the group SHALL
**always** read from the Stage-3 DuckLake tables (so the same
notebook works in CI, local dev, and the production stack).

## Example wiring (UoG official docs)

| Asset | Stage | Reads from | Writes to |
|---|---|---|---|
| `uog_official_docs_stage0_audit` | 0 | the FIRECRAWL_API_KEY | `university_research_sitemap` LanceDB |
| `uog_official_docs_stage1_collect` | 1 | the table above | `cianfhoghlaim.education.ie.uog_official_documents` |
| `uog_official_docs_baml_extract` | 2 | `uog_official_documents` | `cianfhoghlaim.education.ie.uog_official_documents` (typed columns) |
| `uog_official_docs_embed_lance` | 3 | the typed table | LanceDB `uog_official_documents` |
| `uog_official_docs_duckdb_sink` | 3 | the typed table | DuckLake (whichever backend resolved) |
