-- youtube_videos_migrations.sql
--
-- Idempotent SQL migrations for the YouTube DLT source.
-- NEW (2026-09-12 — youtube-source-playlist-support-and-agent-training-v1).
--
-- Run via `apply_migrations(pipeline=pipeline)` after `pipeline.run(...)`
-- on the `__main__` invocation path, or directly from the CLI for tests.
--
-- Versioning: the `_MIGRATIONS_VERSION` constant at the top of
-- `dlt_sources/api_sources/youtube_videos.py` MUST be bumped whenever
-- a statement is added/changed/removed. The version is recorded in the
-- `_youtube_migrations` meta table so future runs can short-circuit.
--
-- Schema substitution: every `{YOUTUBE_SCHEMA}` placeholder is
-- substituted by `apply_migrations()` from the `YOUTUBE_SCHEMA` env var
-- (default `cianfhoghlaim.youtube` — matches the canonical destination
-- referenced by the CocoIndex `youtube_kg_embedding` App at
-- `cocoindex_flows/knowledge_graph/youtube_kg_embedding.py:80`).
--
-- Block separator: `\n--\n` (the `apply_migrations()` helper splits on
-- this token; keep it between every pair of statements below).
--

-- Create the 2 playlist-specific subtable views (the generic → specific
-- naming pattern; see the openspec change for the rationale). Each view
-- projects the parent `youtube_videos` table filtered by `playlist_id`.

CREATE VIEW IF NOT EXISTS {YOUTUBE_SCHEMA}.youtube_huggingface_post_training_agents AS
SELECT * FROM {YOUTUBE_SCHEMA}.youtube_videos
WHERE playlist_id = 'PLo2EIpI_JMQvQZm-kVlz4wY1vWF0LBcf5';

--

CREATE VIEW IF NOT EXISTS {YOUTUBE_SCHEMA}.youtube_google_cloud_ai_agent_crash_course AS
SELECT * FROM {YOUTUBE_SCHEMA}.youtube_videos
WHERE playlist_id = 'PLIivdWyY5sqLNeW9MPxldbbevMEJGMWBG';

--

-- The playlist registry: 1 row per playlist with aggregated metadata.
-- Useful for dashboards that need to answer "how many videos in each
-- playlist, when was the last upload, what's the total runtime".

CREATE VIEW IF NOT EXISTS {YOUTUBE_SCHEMA}.youtube_playlist_registry AS
SELECT
    playlist_id,
    COUNT(*) AS video_count,
    MIN(upload_date) AS first_upload,
    MAX(upload_date) AS last_upload,
    SUM(duration_s) AS total_duration_s,
    AVG(duration_s) AS avg_duration_s
FROM {YOUTUBE_SCHEMA}.youtube_videos
WHERE playlist_id IS NOT NULL
GROUP BY playlist_id;
