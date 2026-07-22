-- MotherDuck Flight: england_full_coverage_flight
--
-- Per the 2026-08-02-biep-v3-motherduck-flights-v1 change.
--
-- Daily 03:00 UTC. Scans s3://garage/cianfhoghlaim/england/ for new
-- PDFs (3 boards × 92 subjects × 2 levels) and runs the generic
-- england_jurisdiction_pipeline + the 4-path OCR/VLM ensemble +
-- RAGAS vote.

CREATE FLIGHT england_full_coverage_flight
SCHEDULE '0 3 * * *'  -- 03:00 UTC daily
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
        bucket_url := 's3://garage/cianfhoghlaim/england/',
        pattern := '*.pdf',
        since := NOW() - INTERVAL '24 hours'
    )
),

ensemble_outputs AS (
    SELECT *
    FROM cianfhoghlaim.meaisinfhoghlaim.ocr.ensemble.ensembled_extractor(
        pdf_uri := s3_uri,
        jurisdiction := 'england',
        scope := 'education',
        subject := subject_slug,
        board := board,
        qualification_level := qualification_level,
        language := language,
        baml_function := 'ExtractUKQualSpec'
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

INSERT INTO cianfhoghlaim.education.england
    SELECT * FROM voted
    WHERE ragas_passed = TRUE;
