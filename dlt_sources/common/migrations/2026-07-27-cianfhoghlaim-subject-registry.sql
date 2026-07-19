-- DuckDB migration: cianfhoghlaim British Isles Subject Registry
--
-- Per the 2026-07-27-biep-v3-canonical-registry-v1 change.
--
-- Creates 3 tables that drive the BIEP v3 generic pipelines:
--   cianfhoghlaim.education._registry.subjects
--   cianfhoghlaim.education._registry.jurisdiction_overrides
--   cianfhoghlaim.education._registry.cross_jurisdiction_bridges

CREATE SCHEMA IF NOT EXISTS cianfhoghlaim.education._registry;

-- ----------------------------------------------------------------------------
-- 1. subjects (the canonical registry)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cianfhoghlaim.education._registry.subjects (
    -- Composite primary key
    jurisdiction           VARCHAR NOT NULL,
    stage                  VARCHAR NOT NULL,
    subject_slug           VARCHAR NOT NULL,
    board                  VARCHAR NOT NULL DEFAULT 'NONE',
    qualification_level    VARCHAR,
    language               VARCHAR NOT NULL DEFAULT 'en',

    -- Display
    display_name_en        VARCHAR NOT NULL,
    display_name_local     VARCHAR,
    concept                VARCHAR NOT NULL,
    source_url             VARCHAR,
    ncca_spec_code         VARCHAR,

    -- Operational
    baml_function          VARCHAR NOT NULL,
    source                 VARCHAR NOT NULL,
    status                 VARCHAR NOT NULL DEFAULT 'ACTIVE',
    first_introduced       VARCHAR,
    last_verified          VARCHAR,
    notes                  TEXT,

    -- Audit
    created_at             TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at             TIMESTAMP NOT NULL DEFAULT NOW(),

    PRIMARY KEY (jurisdiction, stage, subject_slug, board, qualification_level, language)
);

-- Indexes for the canonical access patterns
CREATE INDEX IF NOT EXISTS idx_subjects_jurisdiction
    ON cianfhoghlaim.education._registry.subjects (jurisdiction);

CREATE INDEX IF NOT EXISTS idx_subjects_concept
    ON cianfhoghlaim.education._registry.subjects (concept);

CREATE INDEX IF NOT EXISTS idx_subjects_status
    ON cianfhoghlaim.education._registry.subjects (status);

CREATE INDEX IF NOT EXISTS idx_subjects_stage
    ON cianfhoghlaim.education._registry.subjects (stage);

-- ----------------------------------------------------------------------------
-- 2. jurisdiction_overrides
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cianfhoghlaim.education._registry.jurisdiction_overrides (
    jurisdiction           VARCHAR NOT NULL,
    subject_slug           VARCHAR NOT NULL,
    override_field         VARCHAR NOT NULL,
    override_value         VARCHAR NOT NULL,
    reason                 VARCHAR,
    effective_from         VARCHAR,

    created_at             TIMESTAMP NOT NULL DEFAULT NOW(),

    PRIMARY KEY (jurisdiction, subject_slug, override_field)
);

-- ----------------------------------------------------------------------------
-- 3. cross_jurisdiction_bridges
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cianfhoghlaim.education._registry.cross_jurisdiction_bridges (
    concept                VARCHAR PRIMARY KEY,
    jurisdiction_slug_map  VARCHAR NOT NULL,  -- JSON: {ireland: 'gaeilge', ...}
    display_name           VARCHAR NOT NULL,
    notes                  TEXT,

    created_at             TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at             TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Seed the cross-jurisdiction bridges (the 10 core concepts that span
-- most jurisdictions)
INSERT INTO cianfhoghlaim.education._registry.cross_jurisdiction_bridges
    (concept, jurisdiction_slug_map, display_name, notes)
VALUES
    ('MATHEMATICS',
     '{"ireland":"mathematics","england":"mathematics","scotland":"mathematics","wales":"mathematics","northern_ireland":"mathematics"}',
     'Mathematics',
     'Core STEM; present in every British Isles jurisdiction'),
    ('ENGLISH',
     '{"ireland":"english","england":"english_language","england_lit":"english_literature","scotland":"english","wales":"english","northern_ireland":"english"}',
     'English (Language + Literature)',
     'England splits English into Language + Literature; other jurisdictions use a single subject'),
    ('BIOLOGY',
     '{"ireland":"biology","england":"biology","scotland":"biology","wales":"biology","northern_ireland":"biology"}',
     'Biology',
     'Core STEM'),
    ('CHEMISTRY',
     '{"ireland":"chemistry","england":"chemistry","scotland":"chemistry","wales":"chemistry","northern_ireland":"chemistry"}',
     'Chemistry',
     'Core STEM'),
    ('PHYSICS',
     '{"ireland":"physics","england":"physics","scotland":"physics","wales":"physics","northern_ireland":"physics"}',
     'Physics',
     'Core STEM'),
    ('HISTORY',
     '{"ireland":"history","england":"history","scotland":"history","wales":"history","northern_ireland":"history"}',
     'History',
     'Core humanities; Ireland also has irish_history as a separate subject'),
    ('GEOGRAPHY',
     '{"ireland":"geography","england":"geography","scotland":"geography","wales":"geography","northern_ireland":"geography"}',
     'Geography',
     'Core humanities'),
    ('COMPUTER_SCIENCE',
     '{"ireland":"computer_science","england":"computer_science","scotland":"computing_science","wales":"computer_science","northern_ireland":"computing_science"}',
     'Computer Science / Computing',
     'Scotland uses "computing_science" (no space); other jurisdictions use "computer_science"'),
    ('FRENCH',
     '{"ireland":"french","england":"french","scotland":"french","wales":"french","northern_ireland":"french"}',
     'French',
     'Modern language'),
    ('GERMAN',
     '{"ireland":"german","england":"german","scotland":"german","wales":"german","northern_ireland":"german"}',
     'German',
     'Modern language'),
    ('SPANISH',
     '{"ireland":"spanish","england":"spanish","scotland":"spanish","wales":"spanish","northern_ireland":"spanish"}',
     'Spanish',
     'Modern language'),
    ('IRISH_LANGUAGE',
     '{"ireland":"gaeilge","northern_ireland":"irish"}',
     'Gaeilge / Irish',
     'Slugs differ: Ireland uses "gaeilge", Northern Ireland uses "irish" (the Gaeltacht overlay)'),
    ('BUSINESS_STUDIES',
     '{"ireland_jc":"business_studies","england_gcse":"business","england_al":"business","scotland":"business_management"}',
     'Business Studies',
     'Slug drift across jurisdictions — Ireland JC uses "business_studies", England uses "business", Scotland uses "business_management"')
ON CONFLICT (concept) DO NOTHING;

-- ----------------------------------------------------------------------------
-- Seed Ireland subjects (Phase 2 input)
-- ----------------------------------------------------------------------------
-- 64 LC + 18 JC + 16 short courses + 36 CBAs = 134+ rows.
-- (Detailed seeding is in Phase 2; this migration just creates the
-- empty tables for now.)

-- ----------------------------------------------------------------------------
-- Trigger to auto-update updated_at
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION cianfhoghlaim.education._registry.touch_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_subjects_updated_at
    ON cianfhoghlaim.education._registry.subjects;
CREATE TRIGGER trg_subjects_updated_at
    BEFORE UPDATE ON cianfhoghlaim.education._registry.subjects
    FOR EACH ROW EXECUTE FUNCTION cianfhoghlaim.education._registry.touch_updated_at();

DROP TRIGGER IF EXISTS trg_bridges_updated_at
    ON cianfhoghlaim.education._registry.cross_jurisdiction_bridges;
CREATE TRIGGER trg_bridges_updated_at
    BEFORE UPDATE ON cianfhoghlaim.education._registry.cross_jurisdiction_bridges
    FOR EACH ROW EXECUTE FUNCTION cianfhoghlaim.education._registry.touch_updated_at();