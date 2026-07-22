-- MotherDuck Flight: sct_wls_ni_flight
--
-- Per the 2026-08-02-biep-v3-motherduck-flights-v1 change.
--
-- Daily 04:00 UTC. Scans s3://garage/cianfhoghlaim/{scotland,wales,northern_ireland}/
-- for new PDFs (380 SCT + WJEC + CCEA cohorts) and runs the
-- sct_wls_ni_jurisdiction_pipeline + the 4-path OCR/VLM ensemble +
-- RAGAS vote.

CREATE FLIGHT sct_wls_ni_flight
SCHEDULE '0 4 * * *'  -- 04:00 UTC daily
DATABASE md:cianfhoghlaim
AS

WITH new_pdfs AS (
    SELECT
        s3_uri,
        content_hash,
        jurisdiction,
        stage,
        subject_slug,
        board,
        qualification_level,
        language
    FROM cianfhoghlaim._aws.s3_discover(
        bucket_url := 's3://garage/cianfhoghlaim/',
        pattern := '*.pdf',
        since := NOW() - INTERVAL '24 hours',
        path_filter := '^/(scotland|wales|northern_ireland)/'
    )
),

ensemble_outputs AS (
    SELECT *
    FROM cianfhoghlaim.meaisinfhoghlaim.ocr.ensemble.ensembled_extractor(
        pdf_uri := s3_uri,
        jurisdiction := jurisdiction,
        scope := 'education',
        subject := subject_slug,
        board := board,
        qualification_level := qualification_level,
        language := language,
        baml_function := 'ExtractCurriculumSyllabus'
    )
    FROM new_pdfs
),

voted AS (
    SELECT *
    FROM cianfhoghlaim.meaisinfhoghlaim.evaluation.ragas_biiep_ensemble(
        ensemble_outputs,
        ragas_threshold := 0.70
    )
)

INSERT INTO cianfhoghlaim.education
    SELECT * FROM voted
    WHERE ragas_passed = TRUE
      AND jurisdiction IN ('scotland', 'wales', 'northern_ireland');
