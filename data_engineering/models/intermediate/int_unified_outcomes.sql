-- Intermediate model: Unified cross-nation curriculum outcomes
-- Combines staging models into a single unified view
-- Currently: Ireland only; will add other nations as data is ingested
MODEL (
    name int.int_unified_outcomes,
    kind FULL,
    cron '@daily',
    owner oideachais,
    description 'Unified learning outcomes from all Celtic nations'
);

-- Ireland curriculum data (currently available)
SELECT
    outcome_id,
    source_url,
    title,
    content,
    nation,
    source,
    resource_type,
    curriculum_level,
    subject,
    language,
    -- Flag Celtic language content
    CASE WHEN language IN ('ga', 'cy', 'gd', 'gv') THEN true ELSE false END AS is_celtic_medium,
    indexed_at,
    content_hash,
    _loaded_at,
    -- Create text for embedding (title + content excerpt)
    title || ' ' || LEFT(content, 1000) AS embedding_text
FROM stg.stg_ncca_curriculum
WHERE content IS NOT NULL AND LENGTH(content) > 50

-- TODO: Add UNION ALL for other nations when data is available
-- UNION ALL SELECT ... FROM stg.stg_dfe_national_curriculum (England)
-- UNION ALL SELECT ... FROM stg.stg_cfe_curriculum (Scotland)
-- UNION ALL SELECT ... FROM stg.stg_curriculum_for_wales (Wales)
-- UNION ALL SELECT ... FROM stg.stg_ccea_curriculum (Northern Ireland)
