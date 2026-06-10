-- Dimension: Languages
-- Reference table for languages including Celtic languages
MODEL (
    name marts.dim_language,
    kind SEED (
        path '../../../seeds/languages.csv'
    ),
    description 'Language dimension table including Celtic languages (Irish, Welsh, Scottish Gaelic, Manx)'
);
