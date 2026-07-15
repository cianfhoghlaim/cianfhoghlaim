-- MotherDuck Dive: jc_curriculum_dive
--
-- Junior Cycle curriculum coverage BIEP v2 (per
-- openspec/changes/2026-07-20-biep-v2-junior-cycle-extraction-v1/).
--
-- 18 NCCA JC subjects × 3 years × 2 languages = 108 cohorts.
-- Each cohort is the topic-coverage metric for that (subject, year, language) triple.
--
-- Backed by the per-subject per-year per-language LanceDB tables at
-- `oideachais.jc.<subject>.<year>_<lang>` (populated by the
-- `junior_cycle_embedding` CocoIndex App from
-- `cocoindex/subjects/junior_cycle_embedding.py`).

CREATE DIVE jc_curriculum_dive AS
SELECT
    subject,
    -- "year_1" / "year_2" / "year_3" extracted from the table name
    REGEXP_EXTRACT(table_name, r'oideachais\.jc\.([^.]+)\.year_(\d)_(en|ga)', 2) AS year,
    REGEXP_EXTRACT(table_name, r'oideachais\.jc\.([^.]+)\.year_(\d)_(en|ga)', 3) AS language,
    COUNT(*) AS chunk_count,
    COUNT(DISTINCT strand) AS strand_count,
    COUNT(DISTINCT topic) AS topic_count,
    MAX(ingested_at) AS last_ingested_at
FROM oideachais.education.british_isles.ireland.junior_cycle._all_subjects
GROUP BY subject, year, language
ORDER BY subject, year, language;
