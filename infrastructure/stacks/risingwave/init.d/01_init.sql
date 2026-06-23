-- =============================================================================
-- RisingWave initial schema — Cianfhoghlaim / Oideachais
-- =============================================================================
-- Runs on first boot of the risingwave container. Creates:
--   1. Agent event streams (replaces Kafka topics)
--   2. CDC sources for all 6+ Postgres instances
--   3. Cascading MVs for curriculum + asset aggregation
--   4. Iceberg sink to Garage S3 (s3://ducklake-assets/streaming/)
--
-- Per docs/data_engineering/risingwave-sql-patterns.md:
--   - Use CREATE TABLE for CDC sources (not CREATE SOURCE)
--   - Use WATERMARK FOR on append-only streams
--   - Use indexes (which are specialized MVs) for high-frequency queries
--   - Use EMIT ON WINDOW CLOSE when results should emit only once
-- =============================================================================

-- ---------------------------------------------------------------------------
-- 1. Agent event streams (replaces Kafka agent_queries/agent_responses)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS agent_queries (
    event_id    VARCHAR PRIMARY KEY,
    payload     JSONB,
    event_time  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS agent_responses (
    event_id    VARCHAR PRIMARY KEY,
    payload     JSONB,
    event_time  TIMESTAMP DEFAULT NOW()
);

-- Hourly aggregation of agent query volume per domain
CREATE MATERIALIZED VIEW IF NOT EXISTS agent_queries_hourly AS
SELECT
    date_trunc('hour', event_time) AS hour,
    payload->>'agent_name'        AS agent_name,
    payload->>'language'         AS language,
    COUNT(*)                     AS query_count
FROM agent_queries
GROUP BY date_trunc('hour', event_time), agent_name, language;

-- Daily aggregation for the marimo dashboard
CREATE MATERIALIZED VIEW IF NOT EXISTS agent_queries_daily AS
SELECT
    date_trunc('day', hour) AS day,
    agent_name,
    language,
    SUM(query_count)       AS total
FROM agent_queries_hourly
GROUP BY date_trunc('day', hour), agent_name, language;

-- ---------------------------------------------------------------------------
-- 2. BAML extraction event stream
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS baml_extractions (
    event_id    VARCHAR PRIMARY KEY,
    payload     JSONB,
    event_time  TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_baml_extractions_time
    ON baml_extractions(event_time)
    INCLUDE (payload);

-- ---------------------------------------------------------------------------
-- 3. OCR event stream (from docling-serve, olmocr, paddleocr, etc.)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS ocr_events (
    event_id    VARCHAR PRIMARY KEY,
    payload     JSONB,
    event_time  TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ocr_events_backend
    ON ocr_extractions(payload->>'backend')
    INCLUDE (event_time);

-- ---------------------------------------------------------------------------
-- 4. Asset generation events (BAML → image gen → Garage S3)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS asset_generation_events (
    event_id    VARCHAR PRIMARY KEY,
    payload     JSONB,
    event_time  TIMESTAMP DEFAULT NOW()
);

CREATE MATERIALIZED VIEW IF NOT EXISTS asset_ragas_scores AS
SELECT
    payload->>'subject'           AS subject,
    payload->>'cycle'             AS cycle,
    payload->>'outcome_id'        AS outcome_id,
    AVG((payload->>'ragas_score')::FLOAT) AS avg_score,
    COUNT(*)                       AS asset_count
FROM asset_generation_events
WHERE payload->>'ragas_score' IS NOT NULL
GROUP BY subject, cycle, outcome_id;

-- ---------------------------------------------------------------------------
-- 5. ASR / TTS events (audio pipeline)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS audio_events (
    event_id    VARCHAR PRIMARY KEY,
    payload     JSONB,
    event_time  TIMESTAMP DEFAULT NOW(),
    WATERMARK FOR event_time AS event_time - INTERVAL '5 seconds'
) APPEND ONLY;

CREATE INDEX IF NOT EXISTS idx_audio_events_lang
    ON audio_events(payload->>'language')
    INCLUDE (event_time, payload->>'model');

-- ---------------------------------------------------------------------------
-- 6. CDC sources (replaces the per-DB polling)
-- ---------------------------------------------------------------------------
-- Production should run these against the real Postgres hosts. For dev,
-- they're commented out and we let meaisínfhoghlaim's _rw_ensure_tables()
-- bootstrap the agent_* tables only.
--
-- CREATE TABLE litellm_model_registry_cdc WITH (
--     connector = 'postgres-cdc',
--     hostname = 'litellm-db', port = '5432',
--     username = 'llmproxy', password = 'secret',
--     database.name = 'litellm', schema.name = 'public',
--     table.name = 'model_registry', slot.name = 'litellm_slot'
-- );
--
-- CREATE TABLE langfuse_traces_cdc WITH (
--     connector = 'postgres-cdc',
--     hostname = 'langfuse-postgres', port = '5432',
--     username = 'postgres', password = 'secret',
--     database.name = 'langfuse', schema.name = 'public',
--     table.name = 'traces', slot.name = 'langfuse_slot'
-- );

-- ---------------------------------------------------------------------------
-- 7. Iceberg sink to Garage S3 (durable event store)
-- ---------------------------------------------------------------------------
-- Uncomment when the garage bucket is ready:
--
-- CREATE SINK IF NOT EXISTS agent_events_iceberg FROM agent_queries_hourly
-- WITH (
--     connector = 'iceberg',
--     s3.endpoint = 'http://lakehouse-garage:3900',
--     s3.region = 'garage',
--     s3.access.key = 'lakehouse',
--     s3.secret.key = 'devpassword',
--     s3.path.style.access = 'true',
--     database.name = 'oideachais',
--     table.name = 'agent_queries_hourly'
-- ) FORMAT UPSERT ENCODE PARQUET (force_append_only = false);
