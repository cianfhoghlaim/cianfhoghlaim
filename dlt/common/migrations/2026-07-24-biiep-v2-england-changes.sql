-- DuckLake migration: 2026-07-24-biiep-v2-england-changes
--
-- Per the 2026-07-24-biep-v2-gov-uk-change-detection-v1 change.
--
-- Creates the audit table that records every detected change in the
-- England awarding-body specs (AQA / OCR / Edexcel) since the BIEP v2
-- pipeline landed.

CREATE TABLE IF NOT EXISTS oideachais.education.british_isles.england.changes (
    -- Primary identifier
    change_id                VARCHAR PRIMARY KEY
        DEFAULT gen_random_uuid()::text,

    -- Detection metadata
    detected_at              TIMESTAMP NOT NULL DEFAULT NOW(),
    board                    VARCHAR NOT NULL         -- 'aqa' | 'ocr' | 'edexcel'
        CHECK (board IN ('aqa', 'ocr', 'edexcel')),
    subject                  VARCHAR NOT NULL,        -- 'mathematics', 'english_language', ...
    qualification_level      VARCHAR NOT NULL         -- 'gcse' | 'a_level'
        CHECK (qualification_level IN ('gcse', 'a_level')),

    -- Source URLs
    spec_url                 VARCHAR NOT NULL,
    spec_path                VARCHAR,                -- local cached path

    -- Version + content hashes (for the freshness guarantee)
    old_version              VARCHAR,
    new_version              VARCHAR NOT NULL,
    old_hash                 VARCHAR,
    new_hash                 VARCHAR NOT NULL,

    -- BAML re-extraction status (set by the england_england_re_extraction_job)
    extraction_rerun_id      VARCHAR,                -- back-reference to the Dagster run
    extraction_status        VARCHAR                  -- 'success' | 'failed' | 'pending'
        CHECK (extraction_status IN ('success', 'failed', 'pending')),
    extraction_started_at    TIMESTAMP,
    extraction_completed_at  TIMESTAMP,
    ragas_score              DECIMAL(5,4),           -- 0.0000–1.0000

    -- Alerting + observability
    slack_alert_sent_at      TIMESTAMP,
    email_alert_sent_at      TIMESTAMP,
    langfuse_trace_id        VARCHAR,

    -- Audit fields
    ingested_at              TIMESTAMP NOT NULL DEFAULT NOW(),
    last_updated_at          TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Soft delete (for the per-change retention policy)
    archived_at              TIMESTAMP
);

-- Indexes for the canonical access patterns.
CREATE INDEX IF NOT EXISTS idx_changes_board
    ON oideachais.education.british_isles.england.changes (board);

CREATE INDEX IF NOT EXISTS idx_changes_subject_qualification_level
    ON oideachais.education.british_isles.england.changes (subject, qualification_level);

CREATE INDEX IF NOT EXISTS idx_changes_detected_at
    ON oideachais.education.british_isles.england.changes (detected_at DESC);

CREATE INDEX IF NOT EXISTS idx_changes_extraction_status
    ON oideachais.education.british_isles.england.changes (extraction_status);
