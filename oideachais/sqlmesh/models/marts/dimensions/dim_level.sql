-- Dimension: Education Levels
-- Cross-nation education level mappings
MODEL (
    name marts.dim_level,
    kind SEED (
        path '../../../seeds/level_mappings.csv'
    ),
    description 'Education level dimension with cross-nation equivalences'
);
