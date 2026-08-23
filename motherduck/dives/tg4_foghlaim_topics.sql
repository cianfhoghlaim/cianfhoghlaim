-- MotherDuck Dive: tg4_foghlaim_topics
--
-- The TG4 + Foghlaim multimodal corpus coverage view (per
-- openspec/changes/2026-08-25-tg4-foghlaim-corpus-v1/).
--
-- Joins the 6 BIEP v1 LC subjects + 18 JC subjects via the Foghlaim
-- `biep_subject` taxonomy against the TG4 player catalog + the Foghlaim
-- lessons corpus. The 4 LanceDB tables (`tg4_segments`,
-- `tg4_frame_captions`, `tg4_triples`, `tg4_quality_audits`) are the
-- downstream v1 App materialisation surfaces (see
-- `orchestration/defs/3_model_lifecycle/cocoindex_v1/tg4_foghlaim/defs.yaml`).
--
-- Drill-down: click a (biep_subject, biep_stage) cell → list the
-- TG4 player shows + Foghlaim lessons + their per-row metadata
-- (pid / lesson_id / title / duration / dialect).
--
-- Note: this Dive reads the DuckLake tables read by the v1 App:
--   - cianfhoghlaim.tg4.player_shows
--   - cianfhoghlaim.tg4.foghlaim_lessons
-- The 4 LanceDB tables are NOT joined here — they live in LanceDB
-- (per the BIEP datalake separation of concerns: DuckLake for tabular
-- metadata, LanceDB for embedding segments).

CREATE DIVE tg4_foghlaim_topics AS
WITH player_counts AS (
    SELECT
        'player' AS corpus,
        genre_gaelic AS facet,
        biep_subject,
        NULL::VARCHAR AS biep_stage,
        COUNT(*) AS row_count,
        AVG(duration_s) AS avg_duration_s
    FROM cianfhoghlaim.tg4.player_shows
    GROUP BY genre_gaelic, biep_subject
    UNION ALL
    SELECT
        'lessons' AS corpus,
        level_gaelic AS facet,
        biep_subject,
        biep_stage,
        COUNT(*) AS row_count,
        AVG(duration_s) AS avg_duration_s
    FROM cianfhoghlaim.tg4.foghlaim_lessons
    WHERE biep_subject != 'non_curriculum'
    GROUP BY level_gaelic, biep_subject, biep_stage
)
SELECT
    corpus,
    facet,
    biep_subject,
    biep_stage,
    row_count,
    avg_duration_s,
    'tg4-foghlaim-corpus-v1' AS openspec_change
FROM player_counts
ORDER BY corpus, biep_subject, biep_stage;
