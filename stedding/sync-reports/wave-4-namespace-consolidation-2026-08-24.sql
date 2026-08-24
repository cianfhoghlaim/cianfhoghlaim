-- Wave 4 namespace consolidation migration
-- Generated: 2026-08-24T06:37:37.880526Z
-- Consolidated namespace: ducklake_cianfhoghlaim
-- Consolidated S3 prefix: s3://ducklake-cianfhoghlaim/

-- Step 1: Attach the consolidated DuckLake
ATTACH 'ducklake:postgres://loader:pass@lakehouse-postgres:5433/dlt_data' AS ducklake_cianfhoghlaim (DATA_PATH 's3://ducklake-cianfhoghlaim/');

-- Step 2: For each legacy namespace, ATTACH + COPY all tables into the consolidated namespace

-- ─── Migrate ducklake_oideachais ───
ATTACH 'ducklake:postgres://loader:pass@lakehouse-postgres:5433/ducklake_oideachais' AS ducklake_oideachais (DATA_PATH 's3://ducklake-oideachais/');
CREATE TABLE ducklake_cianfhoghlaim.british_isles.education_chunks AS SELECT * FROM ducklake_oideachais.british_isles.education_chunks;
CREATE TABLE ducklake_cianfhoghlaim.british_isles.legal_chunks AS SELECT * FROM ducklake_oideachais.british_isles.legal_chunks;
CREATE TABLE ducklake_cianfhoghlaim.british_isles.medical_chunks AS SELECT * FROM ducklake_oideachais.british_isles.medical_chunks;
DETACH ducklake_oideachais;

-- ─── Migrate ducklake_educational ───
ATTACH 'ducklake:postgres://loader:pass@lakehouse-postgres:5433/ducklake_educational' AS ducklake_educational (DATA_PATH 's3://ducklake-educational/');
CREATE TABLE ducklake_cianfhoghlaim.lc_subjects.mathematics AS SELECT * FROM ducklake_educational.lc_subjects.mathematics;
CREATE TABLE ducklake_cianfhoghlaim.lc_subjects.chemistry AS SELECT * FROM ducklake_educational.lc_subjects.chemistry;
CREATE TABLE ducklake_cianfhoghlaim.lc_subjects.gaeilge AS SELECT * FROM ducklake_educational.lc_subjects.gaeilge;
DETACH ducklake_educational;

-- ─── Migrate ducklake_crypteolas ───
ATTACH 'ducklake:postgres://loader:pass@lakehouse-postgres:5433/ducklake_crypteolas' AS ducklake_crypteolas (DATA_PATH 's3://ducklake-crypteolas/');
CREATE TABLE ducklake_cianfhoghlaim.chain.ethereum_blocks AS SELECT * FROM ducklake_crypteolas.chain.ethereum_blocks;
CREATE TABLE ducklake_cianfhoghlaim.chain.ethereum_transactions AS SELECT * FROM ducklake_crypteolas.chain.ethereum_transactions;
DETACH ducklake_crypteolas;

-- ─── Migrate ducklake_tertiary ───
ATTACH 'ducklake:postgres://loader:pass@lakehouse-postgres:5433/ducklake_tertiary' AS ducklake_tertiary (DATA_PATH 's3://ducklake-tertiary/');
CREATE TABLE ducklake_cianfhoghlaim.uoq.exam_papers AS SELECT * FROM ducklake_tertiary.uoq.exam_papers;
CREATE TABLE ducklake_cianfhoghlaim.uog.official_docs AS SELECT * FROM ducklake_tertiary.uog.official_docs;
DETACH ducklake_tertiary;

-- ─── Migrate ducklake_uog ───
ATTACH 'ducklake:postgres://loader:pass@lakehouse-postgres:5433/ducklake_uog' AS ducklake_uog (DATA_PATH 's3://ducklake-uog/');
CREATE TABLE ducklake_cianfhoghlaim.personal_archive.assignments AS SELECT * FROM ducklake_uog.personal_archive.assignments;
CREATE TABLE ducklake_cianfhoghlaim.personal_archive.notes AS SELECT * FROM ducklake_uog.personal_archive.notes;
DETACH ducklake_uog;

-- ─── Migrate ducklake_cie ───
ATTACH 'ducklake:postgres://loader:pass@lakehouse-postgres:5433/ducklake_cie' AS ducklake_cie (DATA_PATH 's3://ducklake-cie/');
CREATE TABLE ducklake_cianfhoghlaim.official_docs.modules AS SELECT * FROM ducklake_cie.official_docs.modules;
CREATE TABLE ducklake_cianfhoghlaim.students_union.events AS SELECT * FROM ducklake_cie.students_union.events;
DETACH ducklake_cie;

-- Step 3: Apply DuckLake 1.0 optimisations to the high-volume tables
-- (per the SORTED_BY_TABLES + BUCKET_PARTITIONED_TABLES constants)

ALTER TABLE leabharlann_books.leabharlann_books SET SORTED BY (subject, board, year, language);
ALTER TABLE leabharlann_zotero.leabharlann_zotero SET SORTED BY (subject, board, year, language);
ALTER TABLE leabharlann_takeout.leabharlann_takeout SET SORTED BY (subject, board, year, language);
ALTER TABLE main.weekly_downloads SET PARTITIONED BY (bucket(1000, jurisdiction));
ALTER TABLE main.language_distribution SET PARTITIONED BY (bucket(1000, jurisdiction));
ALTER TABLE media_personal.apple_photos_chunks SET (data_inlining_row_limit = 100);

-- Step 4: Drop the legacy Postgres schemas
DROP SCHEMA IF EXISTS ducklake_oideachais CASCADE;
DROP SCHEMA IF EXISTS ducklake_educational CASCADE;
DROP SCHEMA IF EXISTS ducklake_crypteolas CASCADE;
DROP SCHEMA IF EXISTS ducklake_tertiary CASCADE;
DROP SCHEMA IF EXISTS ducklake_uog CASCADE;
DROP SCHEMA IF EXISTS ducklake_cie CASCADE;
