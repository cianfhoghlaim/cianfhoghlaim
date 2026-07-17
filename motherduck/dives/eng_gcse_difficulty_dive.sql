-- MotherDuck Dive: eng_gcse_difficulty_dive
--
-- GCSE Bloom's-taxonomy distribution per England awarding board × subject.
-- Surfaces which topics are assessed at higher cognitive demands across
-- the 18 GCSE cohorts (3 boards × 9 subjects × 2 levels).
--
-- Per openspec/changes/2026-07-21-biep-v2-england-aqa-ocr-baml-pipeline-v1/.

CREATE DIVE eng_gcse_difficulty_dive AS
SELECT
    subject,
    board,
    blooms_taxonomy_level,
    COUNT(*) AS question_count
FROM cianfhoghlaim.education.british_isles.england.exam_papers
WHERE qualification_level = 'gcse'
GROUP BY subject, board, blooms_taxonomy_level
ORDER BY subject, board, blooms_taxonomy_level;
