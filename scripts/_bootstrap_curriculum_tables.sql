-- scripts/_bootstrap_curriculum_tables.sql
--
-- Per the 2026-10-10-media-intel-and-curriculum-hydration-v1 change.
--
-- Bootstrap DDL for the 4 new curriculum-hydration tables.
--
-- PHYSICAL TABLE NAMES (local DuckLake dev default):
--   - cianfhoghlaim.geography_topics
--   - cianfhoghlaim.gaeilge_poems_higher
--   - cianfhoghlaim.english_poets_higher
--   - cianfhoghlaim.education_ie_policies
--
-- These match the 4 ``@dlt.resource(table_name=...)`` declarations in
-- ``scripts/curriculum_hydrate.py`` and the DLT
-- ``dataset_name="cianfhoghlaim"`` default. DLT writes rows at
-- ``<dataset>.<table_name>``, so the four tables materialise here.
--
-- CANONICAL (MotherDuck BIEP) names — kept for documentation only:
--   - cianfhoghlaim.lc.geography.topics
--   - cianfhoghlaim.lc.gaeilge.poems_higher
--   - cianfhoghlaim.lc.english.poets_higher
--   - cianfhoghlaim.education.ie.policies
--
-- When the operator opts in to MotherDuck (the ``MOTHERDUCK_TOKEN``
-- branch in ``scripts/curriculum_hydrate.py::_build_destination``),
-- a follow-up migration will rename the four tables to the canonical
-- 4-part MotherDuck form. The renaming is tracked as a separate
-- saga change (not part of this bootstrap).
--
-- Substitutions (local DuckLake physical name → canonical name):
--   cianfhoghlaim.geography_topics           → cianfhoghlaim.lc.geography.topics
--   cianfhoghlaim.gaeilge_poems_higher       → cianfhoghlaim.lc.gaeilge.poems_higher
--   cianfhoghlaim.english_poets_higher       → cianfhoghlaim.lc.english.poets_higher
--   cianfhoghlaim.education_ie_policies      → cianfhoghlaim.education.ie.policies
--
-- DuckDB 1.4/1.5.x has a known parser limitation: 4-part
-- ``CREATE TABLE catalog.schema.subject.table`` and 3-part
-- ``CREATE TABLE schema.subject.table`` with a dot in the leftmost
-- segment (e.g. ``education.ie``) both fail on a fresh connection
-- with either ``NameListToString NOT IMPLEMENTED`` or the leftmost
-- segment being treated as a CATALOG rather than a SCHEMA. The
-- canonical 4-part form is therefore deferred to MotherDuck where the
-- parser handles dotted schema segments natively.

CREATE SCHEMA IF NOT EXISTS cianfhoghlaim;
USE cianfhoghlaim;

CREATE TABLE IF NOT EXISTS geography_topics (
    topic_id            VARCHAR PRIMARY KEY,
    subject_slug        VARCHAR NOT NULL,
    level               VARCHAR NOT NULL,
    language            VARCHAR NOT NULL,
    title               VARCHAR NOT NULL,
    topic_phrase        VARCHAR NOT NULL,
    learning_outcomes   VARCHAR[] NOT NULL,
    source_pdf          VARCHAR NOT NULL,
    source_page         INTEGER NOT NULL,
    source_url          VARCHAR NOT NULL,
    extracted_at        VARCHAR NOT NULL,
    stub                BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS gaeilge_poems_higher (
    poem_id             VARCHAR PRIMARY KEY,
    poet                VARCHAR NOT NULL,
    title_ga            VARCHAR NOT NULL,
    title_en            VARCHAR NOT NULL,
    collection          VARCHAR NOT NULL,
    year                INTEGER,
    prescribed_period   VARCHAR NOT NULL,
    theme_or_issue      VARCHAR NOT NULL,
    source_pdf          VARCHAR NOT NULL,
    source_page         INTEGER NOT NULL,
    source_url          VARCHAR NOT NULL,
    provenance_pdf      VARCHAR,
    extracted_at        VARCHAR NOT NULL,
    stub                BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS english_poets_higher (
    poet_id             VARCHAR PRIMARY KEY,
    poet_name           VARCHAR NOT NULL,
    work_title          VARCHAR NOT NULL,
    prescribed_period   VARCHAR NOT NULL,
    theme_or_issue      VARCHAR NOT NULL,
    cultural_context    VARCHAR NOT NULL,
    literary_genre      VARCHAR NOT NULL,
    general_vision      VARCHAR NOT NULL,
    source_pdf          VARCHAR NOT NULL,
    source_page         INTEGER NOT NULL,
    extracted_at        VARCHAR NOT NULL,
    stub                BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS education_ie_policies (
    policy_id           VARCHAR PRIMARY KEY,
    policy_name         VARCHAR NOT NULL,
    policy_slug         VARCHAR NOT NULL,
    publish_year        INTEGER,
    summary             VARCHAR NOT NULL,
    key_clauses         VARCHAR[] NOT NULL,
    source_pdf          VARCHAR NOT NULL,
    source_url          VARCHAR NOT NULL,
    extracted_at        VARCHAR NOT NULL,
    stub                BOOLEAN NOT NULL
);
