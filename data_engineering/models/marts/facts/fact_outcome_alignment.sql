-- Fact: Outcome Alignments
-- Cross-nation curriculum alignment relationships
MODEL (
    name marts.fact_outcome_alignment,
    kind FULL,
    cron '@daily',
    owner oideachais,
    description 'Fact table for semantic alignments between learning outcomes across nations'
);

-- This table will be populated by the embedding alignment process
-- Placeholder structure for now
SELECT
    CAST(NULL AS VARCHAR) AS alignment_id,
    CAST(NULL AS VARCHAR) AS source_outcome_id,
    CAST(NULL AS VARCHAR) AS target_outcome_id,
    CAST(NULL AS VARCHAR) AS source_nation,
    CAST(NULL AS VARCHAR) AS target_nation,
    CAST(NULL AS VARCHAR) AS alignment_type,  -- EQUIVALENT, PARTIAL_OVERLAP, PREREQUISITE, etc.
    CAST(NULL AS DOUBLE) AS confidence_score,
    CAST(NULL AS VARCHAR) AS method,  -- semantic, manual, llm
    CAST(NULL AS VARCHAR[]) AS shared_concepts,
    CAST(NULL AS VARCHAR) AS reasoning,
    CAST(NULL AS TIMESTAMP) AS computed_at,
    CAST(NULL AS VARCHAR) AS validated_by
WHERE false
