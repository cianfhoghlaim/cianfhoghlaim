-- Fact: Learning Outcomes
-- Main fact table linking outcomes to dimensions
MODEL (
    name marts.fact_learning_outcome,
    kind FULL,
    cron '@daily',
    owner oideachais,
    description 'Fact table for learning outcomes across all nations'
);

SELECT
    u.outcome_id,
    n.nation_id,
    s.subject_id,
    l.mapping_id AS level_id,
    lang.language_id,
    u.source_url,
    u.title,
    u.content,
    u.source,
    u.resource_type,
    u.curriculum_level,
    u.is_celtic_medium,
    u.indexed_at,
    u.content_hash,
    u.embedding_text,
    u._loaded_at
FROM int.int_unified_outcomes u
LEFT JOIN marts.dim_nation n ON u.nation = n.nation_code
LEFT JOIN marts.dim_subject s ON u.subject = s.subject_code
LEFT JOIN marts.dim_level l ON u.curriculum_level = l.level_code AND u.nation = l.nation
LEFT JOIN marts.dim_language lang ON u.language = lang.language_code
