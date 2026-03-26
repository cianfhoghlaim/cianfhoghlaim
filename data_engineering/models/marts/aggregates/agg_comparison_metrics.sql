-- Aggregate: Comparison Metrics
-- Summary statistics for cross-nation curriculum comparison
MODEL (
    name marts.agg_comparison_metrics,
    kind FULL,
    cron '@daily',
    description 'Aggregate metrics for curriculum comparison dashboard'
);

WITH nation_counts AS (
    SELECT
        n.nation_code AS nation,
        COUNT(*) AS total_outcomes,
        COUNT(CASE WHEN f.is_celtic_medium THEN 1 END) AS celtic_medium_outcomes,
        COUNT(DISTINCT f.subject_id) AS unique_subjects,
        COUNT(DISTINCT f.curriculum_level) AS unique_levels
    FROM marts.fact_learning_outcome f
    LEFT JOIN marts.dim_nation n ON f.nation_id = n.nation_id
    GROUP BY n.nation_code
)

SELECT
    nc.nation,
    nc.total_outcomes,
    nc.celtic_medium_outcomes,
    nc.unique_subjects,
    nc.unique_levels,
    ROUND(nc.celtic_medium_outcomes * 100.0 / NULLIF(nc.total_outcomes, 0), 2) AS celtic_medium_percentage,
    CURRENT_TIMESTAMP AS computed_at
FROM nation_counts nc
ORDER BY nc.nation
