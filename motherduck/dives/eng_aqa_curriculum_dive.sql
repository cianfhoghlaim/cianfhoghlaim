-- MotherDuck Dive: eng_aqa_curriculum_dive
--
-- England AQA qualification curriculum coverage BIEP v2
-- (per openspec/changes/2026-07-21-biep-v2-england-aqa-ocr-baml-pipeline-v1/).
--
-- 9 AQA priority subjects × 2 qualification levels (GCSE + A-Level) = 18 cohorts.
-- Each cohort is the topic + assessment-objective coverage metric for that
-- (board, subject, qualification_level) triple.

CREATE DIVE eng_aqa_curriculum_dive AS
SELECT
    board,
    subject,
    qualification_level,
    COUNT(*) AS chunk_count,
    COUNT(DISTINCT topic) AS topic_count,
    COUNT(DISTINCT assessment_objective_id) AS ao_count,
    MAX(ingested_at) AS last_ingested_at
FROM oideachais.education.british_isles.england.aqa._all_qualifications
GROUP BY board, subject, qualification_level
ORDER BY qualification_level, subject;
