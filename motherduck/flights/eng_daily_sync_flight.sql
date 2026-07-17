-- MotherDuck Flight: eng_daily_sync_flight
--
-- Daily BIEP v2 sync of any new England awarding-body PDFs landed in the
-- canonical S3 path:
--   s3://garage/cianfhoghlaim/england/<board>/<subject>/<level>/<year>/<file>.pdf
--
-- Per the 2026-07-21-biep-v2-england-aqa-ocr-baml-pipeline-v1 change.

CREATE FLIGHT eng_daily_sync_flight
SCHEDULE '0 3 * * *'  -- 03:00 UTC daily
DATABASE md:cianfhoghlaim
AS

WITH new_pdfs AS (
    SELECT
        exam_board,
        subject,
        qualification_level,
        s3_uri,
        content_hash
    FROM cianfhoghlaim._aws.s3_discover(
        bucket_url := 's3://garage/cianfhoghlaim/england/',
        pattern := '*.pdf',
        since := NOW() - INTERVAL '24 hours'
    )
),

ensemble_outputs AS (
    SELECT
        s3_uri,
        unnest([
            :baml_canonical, :unstract_json, :qwen3_vl, :gemma4
        ]) AS path
    FROM new_pdfs
),

voted AS (
    SELECT *
    FROM ragas.biiep_extraction_consensus(
        ensemble_outputs,
        faithfulness_threshold := 0.85,
        answer_relevance_threshold := 0.85,
        context_precision_threshold := 0.85
    )
)

INSERT INTO cianfhoghlaim.education.british_isles.england.{exam_board}.{subject}.{qualification_level}
    SELECT * FROM voted
    WHERE ragas_score >= 0.70;
