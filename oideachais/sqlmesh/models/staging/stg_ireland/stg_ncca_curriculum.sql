-- Staging model for Ireland NCCA curriculum data
-- Source: curriculumonline.ie (stored in education.curriculum_pages)
MODEL (
    name stg.stg_ncca_curriculum,
    kind FULL,
    cron '@daily',
    owner oideachais,
    description 'Staged Ireland NCCA curriculum specifications and learning outcomes'
);

SELECT
    cp.id AS outcome_id,
    cp.url AS source_url,
    cp.title,
    COALESCE(cp.content, '') AS content,
    'ireland' AS nation,
    COALESCE(cp.source, 'ncca') AS source,
    'curriculum' AS resource_type,
    -- Map curriculum levels
    CASE
        WHEN LOWER(cp.level) = 'junior_cycle' THEN 'ie_junior_cycle'
        WHEN LOWER(cp.level) = 'senior_cycle' OR cp.url LIKE '%leaving-cert%' THEN 'ie_senior_cycle'
        WHEN cp.url LIKE '%primary%' AND cp.url NOT LIKE '%post-primary%' THEN 'ie_primary'
        WHEN cp.url LIKE '%transition-year%' THEN 'ie_transition_year'
        ELSE 'ie_junior_cycle'  -- Default to junior cycle for our data
    END AS curriculum_level,
    -- Use subject column or detect from URL/title
    COALESCE(
        LOWER(cp.subject),
        CASE
            WHEN LOWER(cp.url) LIKE '%gaeilge%' OR LOWER(cp.url) LIKE '%irish%' THEN 'irish'
            WHEN LOWER(cp.url) LIKE '%mathematics%' OR LOWER(cp.url) LIKE '%maths%' THEN 'mathematics'
            WHEN LOWER(cp.url) LIKE '%english%' THEN 'english'
            WHEN LOWER(cp.url) LIKE '%science%' THEN 'science'
            WHEN LOWER(cp.url) LIKE '%history%' THEN 'history'
            WHEN LOWER(cp.url) LIKE '%geography%' THEN 'geography'
            ELSE 'other'
        END
    ) AS subject,
    -- Detect language
    COALESCE(
        LOWER(cp.language),
        CASE
            WHEN LOWER(cp.url) LIKE '%gaeilge%' OR LOWER(cp.url) LIKE '%/ga/%' THEN 'ga'
            ELSE 'en'
        END
    ) AS language,
    cp.crawled_at AS indexed_at,
    cp.content_hash,
    CURRENT_TIMESTAMP AS _loaded_at
FROM education.curriculum_pages cp
WHERE cp.url IS NOT NULL
