-- MotherDuck Dive: eng_a_level_complexity_dive
--
-- A-Level mark-allocation patterns per England awarding board × subject.
-- Surfaces the mark-allocation distribution (and the implied cognitive
-- demand) of A-Level questions across the 9 A-Level subjects × 3 boards.
--
-- Per openspec/changes/2026-07-21-biep-v2-england-aqa-ocr-baml-pipeline-v1/.

CREATE DIVE eng_a_level_complexity_dive AS
SELECT
    subject,
    board,
    AVG(marks) AS avg_marks_per_question,
    MAX(marks) AS max_marks_per_question,
    COUNT(*) AS question_count,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY marks) AS median_marks
FROM cianfhoghlaim.education.british_isles.england.exam_papers
WHERE qualification_level = 'a_level'
GROUP BY subject, board
ORDER BY subject, board;
