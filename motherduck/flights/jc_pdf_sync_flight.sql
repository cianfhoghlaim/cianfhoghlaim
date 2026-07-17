-- MotherDuck Flight: jc_pdf_sync_flight
--
-- Daily BIEP v2 sync of any new Junior Cycle PDFs landed in the
-- canonical S3 path:
--   s3://garage/cianfhoghlaim/junior_cycle/<subject>/<lang>/<year>/<file>.pdf
--
-- Per the 2026-07-20-biep-v2-junior-cycle-extraction-v1 change.
--
-- For each new PDF, runs the 4-path OCR/VLM ensemble (Change 3):
--   1. BAML ExtractJCCurriculum
--   2. Unstract workflow
--   3. qwen3-vl-8b raw response
--   4. gemma-4-26B-A4B raw response
-- Then RAGAS-votes + writes the per-path DuckLake tables.

CREATE FLIGHT jc_pdf_sync_flight
SCHEDULE '0 2 * * *'  -- 02:00 UTC daily
DATABASE md_oideachais
AS

-- 1. Discover new PDFs in the S3 garage bucket.
WITH new_pdfs AS (
    SELECT
        subject,
        language,
        year,
        filename,
        s3_uri,
        content_hash
    FROM cianfhoghlaim._aws.s3_discover(
        bucket_url := 's3://garage/cianfhoghlaim/junior_cycle/',
        pattern := '*.pdf',
        since := NOW() - INTERVAL '24 hours'
    )
),

-- 2. For each new PDF, run the 4-path ensemble (Change 3 biiep_ocr_ensemble).
ensemble_outputs AS (
    SELECT
        s3_uri,
        unnest([
            :baml_canonical, :unstract_json, :qwen3_vl, :gemma4
        ]) AS path
    FROM new_pdfs
),

-- 3. RAGAS votes + writes the per-path DuckLake tables + the voted canonical.
voted AS (
    SELECT *
    FROM ragas.biiep_extraction_consensus(
        ensemble_outputs,
        faithfulness_threshold := 0.85,
        answer_relevance_threshold := 0.85,
        context_precision_threshold := 0.85
    )
)

-- 4. Land the voted canonical in the per-subject LanceDB tables.
INSERT INTO cianfhoghlaim.education.british_isles.ireland.junior_cycle.{subject}.{language}
    SELECT * FROM voted
    WHERE ragas_score >= 0.70;
