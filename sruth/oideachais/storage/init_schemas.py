"""
DuckDB Schema Initialization for Celtic Education Platform.

Creates unified database with schemas:
- education: Irish curriculum content (from oideachas)
- statistics: Multi-nation education statistics (from oideachas_oileáin)
- celtic: Celtic language corpus (from teanga)
- geospatial: Boundaries and spatial data
- training: ML training datasets

CRITICAL: DuckDB is SINGLE-THREADED ONLY - concurrent access causes segfault/corruption.

Usage:
    python -m storage.init_schemas
"""
from __future__ import annotations

import os
from pathlib import Path


def init_database(db_path: str | Path | None = None) -> None:
    """Initialize DuckDB with all schemas and spatial extension."""
    import duckdb

    if db_path is None:
        data_dir = Path(os.getenv("CELTIC_EDUCATION_DATA_DIR", "./storage/data"))
        db_path = data_dir / "celtic_education.duckdb"

    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = duckdb.connect(str(db_path))

    # Install and load spatial extension
    conn.execute("INSTALL spatial;")
    conn.execute("LOAD spatial;")

    # Create schemas
    schemas = ["education", "statistics", "celtic", "geospatial", "training"]
    for schema in schemas:
        conn.execute(f"CREATE SCHEMA IF NOT EXISTS {schema};")

    # ========================================================================
    # education schema (from oideachas)
    # ========================================================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS education.curriculum_pages (
            id VARCHAR PRIMARY KEY,
            url VARCHAR NOT NULL,
            title VARCHAR,
            content TEXT,
            source VARCHAR NOT NULL,  -- 'ncca', 'curriculumonline', 'examinations'
            language VARCHAR DEFAULT 'en',  -- 'en', 'ga'
            subject VARCHAR,
            level VARCHAR,  -- 'primary', 'junior_cycle', 'senior_cycle'
            crawled_at TIMESTAMP DEFAULT current_timestamp,
            content_hash VARCHAR
        );
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS education.pdf_documents (
            id VARCHAR PRIMARY KEY,
            url VARCHAR NOT NULL,
            filename VARCHAR,
            document_type VARCHAR,  -- 'syllabus', 'examiner_report', 'circular'
            subject VARCHAR,
            year INTEGER,
            language VARCHAR DEFAULT 'en',
            content TEXT,
            extracted_at TIMESTAMP DEFAULT current_timestamp
        );
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS education.learning_outcomes (
            id VARCHAR PRIMARY KEY,
            curriculum_page_id VARCHAR REFERENCES education.curriculum_pages(id),
            subject VARCHAR NOT NULL,
            strand VARCHAR,
            strand_unit VARCHAR,
            outcome_text TEXT NOT NULL,
            outcome_text_ga TEXT,  -- Irish translation
            level VARCHAR,
            class_group VARCHAR
        );
    """)

    # ========================================================================
    # statistics schema (from oideachas_oileáin)
    # ========================================================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS statistics.england_dfe (
            id VARCHAR PRIMARY KEY,
            indicator_name VARCHAR NOT NULL,
            value DOUBLE,
            year INTEGER,
            school_urn VARCHAR,
            lsoa_code VARCHAR,
            local_authority VARCHAR,
            region VARCHAR,
            source_url VARCHAR,
            retrieved_at TIMESTAMP DEFAULT current_timestamp
        );
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS statistics.scotland_gov (
            id VARCHAR PRIMARY KEY,
            indicator_name VARCHAR NOT NULL,
            value DOUBLE,
            year INTEGER,
            school_code VARCHAR,
            datazone VARCHAR,  -- Scottish equivalent of LSOA
            local_authority VARCHAR,
            source_url VARCHAR,
            retrieved_at TIMESTAMP DEFAULT current_timestamp
        );
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS statistics.wales_statswales (
            id VARCHAR PRIMARY KEY,
            indicator_name VARCHAR NOT NULL,
            value DOUBLE,
            year INTEGER,
            school_code VARCHAR,
            lsoa_code VARCHAR,
            local_authority VARCHAR,
            source_url VARCHAR,
            retrieved_at TIMESTAMP DEFAULT current_timestamp
        );
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS statistics.ni_nisra (
            id VARCHAR PRIMARY KEY,
            indicator_name VARCHAR NOT NULL,
            value DOUBLE,
            year INTEGER,
            school_code VARCHAR,
            soa_code VARCHAR,  -- NI Super Output Area
            local_government_district VARCHAR,
            source_url VARCHAR,
            retrieved_at TIMESTAMP DEFAULT current_timestamp
        );
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS statistics.ireland_cso (
            id VARCHAR PRIMARY KEY,
            indicator_name VARCHAR NOT NULL,
            value DOUBLE,
            year INTEGER,
            school_roll_number VARCHAR,
            small_area_code VARCHAR,  -- CSO Small Area (18,641 areas)
            county VARCHAR,
            source_url VARCHAR,
            retrieved_at TIMESTAMP DEFAULT current_timestamp
        );
    """)

    # ========================================================================
    # celtic schema (from teanga)
    # ========================================================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS celtic.duchas_volumes (
            id VARCHAR PRIMARY KEY,
            collection VARCHAR NOT NULL,  -- 'main', 'schools'
            volume_id VARCHAR,
            page_number INTEGER,
            text_content TEXT,
            language VARCHAR DEFAULT 'ga',
            parish VARCHAR,
            county VARCHAR,
            collector VARCHAR,
            year_collected INTEGER,
            transcription_status VARCHAR
        );
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS celtic.canuint_recordings (
            id VARCHAR PRIMARY KEY,
            recording_id VARCHAR NOT NULL,
            speaker_id VARCHAR,
            dialect VARCHAR,  -- 'connacht', 'munster', 'ulster', 'standard'
            text_content TEXT,
            audio_url VARCHAR,
            duration_seconds DOUBLE,
            county VARCHAR,
            transcription TEXT,
            phonetic_transcription TEXT
        );
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS celtic.ud_sentences (
            id VARCHAR PRIMARY KEY,
            treebank VARCHAR NOT NULL,  -- 'ga_idt', 'gd_arcosg', 'cy_ccg', 'br_keb', 'gv_cadhan'
            sentence_id VARCHAR,
            text TEXT NOT NULL,
            tokens JSON,  -- Array of token objects
            language VARCHAR NOT NULL,
            genre VARCHAR
        );
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS celtic.tearma_terms (
            id VARCHAR PRIMARY KEY,
            en_term VARCHAR NOT NULL,
            ga_term VARCHAR NOT NULL,
            domain VARCHAR,  -- 'education', 'law', 'science', etc.
            definition_en TEXT,
            definition_ga TEXT,
            source VARCHAR,
            notes TEXT
        );
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS celtic.logainm_places (
            id VARCHAR PRIMARY KEY,
            english_name VARCHAR,
            irish_name VARCHAR NOT NULL,
            place_type VARCHAR,
            county VARCHAR,
            latitude DOUBLE,
            longitude DOUBLE,
            historical_forms JSON
        );
    """)

    # ========================================================================
    # geospatial schema
    # ========================================================================

    # Use DuckDB Spatial for geometry columns
    conn.execute("""
        CREATE TABLE IF NOT EXISTS geospatial.irish_small_areas (
            sa_2016 VARCHAR PRIMARY KEY,
            geometry GEOMETRY,  -- DuckDB Spatial geometry type
            county VARCHAR,
            electoral_division VARCHAR,
            settlement VARCHAR,
            population_2022 INTEGER,
            hp_deprivation_score DOUBLE,  -- Pobal HP Deprivation Index
            centroid_lat DOUBLE,
            centroid_lon DOUBLE
        );
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS geospatial.uk_lsoa_boundaries (
            lsoa_code VARCHAR PRIMARY KEY,
            geometry GEOMETRY,
            lsoa_name VARCHAR,
            local_authority_code VARCHAR,
            local_authority_name VARCHAR,
            region VARCHAR,
            country VARCHAR,  -- 'England', 'Wales'
            population_2021 INTEGER,
            imd_decile INTEGER  -- Index of Multiple Deprivation
        );
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS geospatial.scotland_datazones (
            datazone_code VARCHAR PRIMARY KEY,
            geometry GEOMETRY,
            datazone_name VARCHAR,
            local_authority VARCHAR,
            population_2021 INTEGER,
            simd_decile INTEGER  -- Scottish IMD
        );
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS geospatial.ni_super_output_areas (
            soa_code VARCHAR PRIMARY KEY,
            geometry GEOMETRY,
            soa_name VARCHAR,
            local_government_district VARCHAR,
            population_2021 INTEGER,
            nimdm_decile INTEGER  -- NI Multiple Deprivation Measure
        );
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS geospatial.schools_locations (
            school_id VARCHAR PRIMARY KEY,
            geometry GEOMETRY,
            school_name VARCHAR NOT NULL,
            school_type VARCHAR,
            nation VARCHAR NOT NULL,  -- 'Ireland', 'England', 'Scotland', 'Wales', 'NI'
            language_medium VARCHAR,  -- 'English', 'Irish', 'Welsh', 'Gaelic', 'Bilingual'
            address TEXT,
            postcode VARCHAR,
            latitude DOUBLE,
            longitude DOUBLE,
            statistical_area_code VARCHAR  -- Links to appropriate boundary table
        );
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS geospatial.met_office_stations (
            station_id VARCHAR PRIMARY KEY,
            geometry GEOMETRY,
            station_name VARCHAR,
            latitude DOUBLE,
            longitude DOUBLE,
            elevation_m DOUBLE,
            region VARCHAR,
            country VARCHAR
        );
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS geospatial.met_office_observations (
            id VARCHAR PRIMARY KEY,
            station_id VARCHAR REFERENCES geospatial.met_office_stations(station_id),
            observation_date DATE,
            max_temp_c DOUBLE,
            min_temp_c DOUBLE,
            rainfall_mm DOUBLE,
            sunshine_hours DOUBLE,
            wind_speed_knots DOUBLE
        );
    """)

    # ========================================================================
    # training schema (for ML datasets)
    # ========================================================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS training.parallel_corpus (
            pair_id VARCHAR PRIMARY KEY,
            source_text TEXT NOT NULL,
            target_text TEXT NOT NULL,
            source_lang VARCHAR DEFAULT 'en',
            target_lang VARCHAR DEFAULT 'ga',
            alignment_score DOUBLE,
            source_document VARCHAR,
            domain VARCHAR,  -- 'curriculum', 'legal', 'folklore'
            created_at TIMESTAMP DEFAULT current_timestamp
        );
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS training.ocr_samples (
            id VARCHAR PRIMARY KEY,
            image_path VARCHAR NOT NULL,
            ground_truth TEXT NOT NULL,
            predicted_text TEXT,
            model_name VARCHAR,
            cer DOUBLE,  -- Character Error Rate
            wer DOUBLE,  -- Word Error Rate
            language VARCHAR DEFAULT 'ga',
            document_type VARCHAR,
            created_at TIMESTAMP DEFAULT current_timestamp
        );
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS training.curriculum_translations (
            id VARCHAR PRIMARY KEY,
            source_id VARCHAR,  -- Reference to education.curriculum_pages
            source_text TEXT NOT NULL,
            source_lang VARCHAR NOT NULL,
            translations JSON,  -- {"ga": "...", "cy": "...", "gd": "...", ...}
            translation_model VARCHAR,
            quality_scores JSON,  -- Per-language quality scores
            created_at TIMESTAMP DEFAULT current_timestamp
        );
    """)

    conn.close()
    print(f"Database initialized at: {db_path}")


def create_spatial_indexes(db_path: str | Path | None = None) -> None:
    """Create spatial indexes for efficient geo queries."""
    import duckdb

    if db_path is None:
        data_dir = Path(os.getenv("CELTIC_EDUCATION_DATA_DIR", "./storage/data"))
        db_path = data_dir / "celtic_education.duckdb"

    conn = duckdb.connect(str(db_path))

    # Spatial indexes are created via R-tree internally by DuckDB Spatial
    # Create regular indexes on commonly joined columns

    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_irish_sa_county ON geospatial.irish_small_areas(county);",
        "CREATE INDEX IF NOT EXISTS idx_uk_lsoa_la ON geospatial.uk_lsoa_boundaries(local_authority_code);",
        "CREATE INDEX IF NOT EXISTS idx_schools_nation ON geospatial.schools_locations(nation);",
        "CREATE INDEX IF NOT EXISTS idx_schools_language ON geospatial.schools_locations(language_medium);",
        "CREATE INDEX IF NOT EXISTS idx_met_obs_date ON geospatial.met_office_observations(observation_date);",
        "CREATE INDEX IF NOT EXISTS idx_parallel_domain ON training.parallel_corpus(domain);",
        "CREATE INDEX IF NOT EXISTS idx_parallel_langs ON training.parallel_corpus(source_lang, target_lang);",
    ]

    for idx in indexes:
        conn.execute(idx)

    conn.close()
    print("Spatial indexes created")


if __name__ == "__main__":
    init_database()
    create_spatial_indexes()
