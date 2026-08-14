-- =============================================================================
-- firecrawl_meta_schema.sql
--
-- The 3 new lakehouse schemas created by the
-- 2026-08-14-firecrawl-corpus-and-examinations-ie-v1 change (Phase 4a).
-- Applied via `notebooks/_shared/firecrawl_corpus_loader.py:init_schemas()`
-- (idempotent — IF NOT EXISTS).
--
-- Storage backend: `md:cianfhoghlaim` (MotherDuck / DuckLake)
-- (per the canonical BIEP destination from
-- dlt_sources/common/destinations_cianfhoghlaim.py).
--
-- Companion table (LanceDB):
-- lancedb://md:cianfhoghlaim/firecrawl_corpus/docs_index
-- =============================================================================


-- ---------------------------------------------------------------------------
-- 1. The agent reference corpus
-- ---------------------------------------------------------------------------

CREATE SCHEMA IF NOT EXISTS cianfhoghlaim.firecrawl_corpus;

-- One table per package (one CREATE per package; a trigger creates
-- missing tables at loader time). The 17 packages are listed in the
-- corpus loader's PACKAGE_WHITELIST.

CREATE TABLE IF NOT EXISTS cianfhoghlaim.firecrawl_corpus.docs (
    doc_id           VARCHAR PRIMARY KEY,
    url              VARCHAR NOT NULL,
    title            VARCHAR,
    description      VARCHAR,
    markdown         TEXT NOT NULL,
    summary          TEXT,
    links            JSON,
    metadata         JSON,
    package          VARCHAR NOT NULL,
    package_version  VARCHAR,
    section          VARCHAR,
    scraped_at       TIMESTAMP NOT NULL,
    content_hash     VARCHAR NOT NULL,
    scraped_via      VARCHAR NOT NULL,
    credits_used     INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_firecrawl_docs_url ON cianfhoghlaim.firecrawl_corpus.docs(url);
CREATE INDEX IF NOT EXISTS idx_firecrawl_docs_hash ON cianfhoghlaim.firecrawl_corpus.docs(content_hash);
CREATE INDEX IF NOT EXISTS idx_firecrawl_docs_package ON cianfhoghlaim.firecrawl_corpus.docs(package);
CREATE INDEX IF NOT EXISTS idx_firecrawl_docs_scraped_at ON cianfhoghlaim.firecrawl_corpus.docs(scraped_at);

-- The unified cross-package search index (BGE-M3 1024-d embeddings).
-- The canonical query surface for the 12-agent fleet.

CREATE TABLE IF NOT EXISTS cianfhoghlaim.firecrawl_corpus.docs_index (
    chunk_id       VARCHAR PRIMARY KEY,
    doc_id         VARCHAR NOT NULL,
    package        VARCHAR NOT NULL,
    url            VARCHAR NOT NULL,
    chunk_offset   INTEGER NOT NULL,
    chunk_text     TEXT NOT NULL,
    embedding      FLOAT[1024],
    scraped_at     TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_firecrawl_docs_index_package ON cianfhoghlaim.firecrawl_corpus.docs_index(package);
CREATE INDEX IF NOT EXISTS idx_firecrawl_docs_index_doc_id ON cianfhoghlaim.firecrawl_corpus.docs_index(doc_id);


-- ---------------------------------------------------------------------------
-- 2. The ingestion observability schema
-- ---------------------------------------------------------------------------

CREATE SCHEMA IF NOT EXISTS cianfhoghlaim.firecrawl_meta;

-- Append-only scrape log (drives the budget tracker + the 12-agent
-- fleet's per-pipeline cost analysis).

CREATE TABLE IF NOT EXISTS cianfhoghlaim.firecrawl_meta.scrapes (
    scrape_id          VARCHAR PRIMARY KEY,
    started_at         TIMESTAMP NOT NULL,
    completed_at       TIMESTAMP,
    tool               VARCHAR NOT NULL,
    pipeline           VARCHAR NOT NULL,
    url                VARCHAR,
    urls_count         INTEGER,
    credits_used       INTEGER NOT NULL,
    credits_estimated  INTEGER,
    cache_hit          BOOLEAN DEFAULT FALSE,
    status             VARCHAR,
    error_message      TEXT,
    metadata           JSON
);

CREATE INDEX IF NOT EXISTS idx_firecrawl_scrapes_pipeline ON cianfhoghlaim.firecrawl_meta.scrapes(pipeline, started_at);
CREATE INDEX IF NOT EXISTS idx_firecrawl_scrapes_tool ON cianfhoghlaim.firecrawl_meta.scrapes(tool, started_at);
CREATE INDEX IF NOT EXISTS idx_firecrawl_scrapes_started_at ON cianfhoghlaim.firecrawl_meta.scrapes(started_at);

-- The rolling budget tracker (rebuilt nightly by the
-- firecrawl_budget_asset).

CREATE TABLE IF NOT EXISTS cianfhoghlaim.firecrawl_meta.budget (
    day               DATE PRIMARY KEY,
    credits_used      INTEGER NOT NULL,
    credits_estimated INTEGER NOT NULL,
    scrapes_count     INTEGER NOT NULL,
    pipelines         JSON,
    top_urls          JSON,
    over_budget       BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_firecrawl_budget_over_budget ON cianfhoghlaim.firecrawl_meta.budget(over_budget);


-- ---------------------------------------------------------------------------
-- 3. The 17-package extended schema (one CREATE per package)
-- ---------------------------------------------------------------------------
-- The corpus loader's create_package_table() helper invokes this block
-- idempotently for each package in PACKAGE_WHITELIST. The view
-- firecrawl_corpus.all_docs unifies them for cross-package queries.

CREATE OR REPLACE VIEW cianfhoghlaim.firecrawl_corpus.all_docs AS
SELECT * FROM cianfhoghlaim.firecrawl_corpus.docs;

CREATE OR REPLACE VIEW cianfhoghlaim.firecrawl_corpus.all_index AS
SELECT * FROM cianfhoghlaim.firecrawl_corpus.docs_index;
