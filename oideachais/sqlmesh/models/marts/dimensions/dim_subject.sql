-- Dimension: Subjects
-- Derived dimension from curriculum data
MODEL (
    name marts.dim_subject,
    kind FULL,
    cron '@daily',
    owner oideachais,
    description 'Subject dimension derived from curriculum content'
);

SELECT
    ROW_NUMBER() OVER (ORDER BY subject) AS subject_id,
    subject AS subject_code,
    subject AS subject_name,
    -- Group subjects into areas
    CASE
        WHEN subject IN ('mathematics', 'numeracy') THEN 'stem'
        WHEN subject IN ('science', 'physics', 'chemistry', 'biology', 'science_technology') THEN 'stem'
        WHEN subject IN ('computing', 'technologies', 'technology') THEN 'stem'
        WHEN subject IN ('english', 'languages', 'literacy') THEN 'languages_literacy'
        WHEN subject IN ('irish', 'gaelic', 'welsh') THEN 'celtic_languages'
        WHEN subject IN ('history', 'geography', 'social_studies', 'humanities') THEN 'humanities'
        WHEN subject IN ('art', 'music', 'expressive_arts') THEN 'arts'
        WHEN subject IN ('physical_education', 'health_wellbeing', 'learning_for_life') THEN 'wellbeing'
        ELSE 'other'
    END AS subject_area,
    -- Is this a Celtic language subject
    CASE WHEN subject IN ('irish', 'gaelic', 'welsh') THEN true ELSE false END AS is_celtic_subject,
    COUNT(*) AS outcome_count
FROM int.int_unified_outcomes
WHERE subject IS NOT NULL
GROUP BY subject
