-- Dimension: Nations
-- Reference table for Celtic nations and England
MODEL (
    name marts.dim_nation,
    kind SEED (
        path '../../../seeds/nations.csv'
    ),
    description 'Nation dimension table for Celtic education platform'
);
