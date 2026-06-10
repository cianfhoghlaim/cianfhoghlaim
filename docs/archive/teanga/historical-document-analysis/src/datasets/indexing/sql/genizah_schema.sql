-- ============================================================================
-- CORE DOCUMENT TABLES
-- ============================================================================

-- Canonical documents (single source of truth per physical document)
CREATE TABLE genizah_documents (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Canonical identification
    canonical_shelf_mark VARCHAR(255) UNIQUE NOT NULL,
    institution VARCHAR(100) NOT NULL,  -- Cambridge, JTS, Bodleian, etc.
    collection VARCHAR(100),  -- Taylor-Schechter, Adler, etc.
    subcollection VARCHAR(50),  -- AS, NS, etc.

    -- Document classification
    document_type VARCHAR(100),  -- letter, legal_document, literary, liturgical, etc.
    language VARCHAR(50)[],  -- ['Hebrew', 'Arabic', 'Judeo-Arabic']
    script VARCHAR(50)[],  -- ['Hebrew', 'Arabic']

    -- Content
    transcription TEXT,
    translation TEXT,
    description TEXT,

    -- Dating and provenance
    dating_text VARCHAR(255),  -- "11th century", "1050-1100 CE"
    dating_start_year INT,  -- -500 to 2000 (normalized)
    dating_end_year INT,
    place_written VARCHAR(255),  -- "Fustat", "Old Cairo"

    -- Scholarly metadata
    material VARCHAR(50),  -- paper, parchment, papyrus
    condition_notes TEXT,
    paleographic_notes TEXT,

    -- Relationships
    joins_with VARCHAR(255)[],  -- Other shelf marks this joins with
    related_documents UUID[],  -- UUIDs of related documents

    -- Quality metrics
    completeness_score FLOAT,  -- 0-1 based on metadata completeness
    has_transcription BOOLEAN DEFAULT FALSE,
    has_translation BOOLEAN DEFAULT FALSE,
    has_images BOOLEAN DEFAULT FALSE,
    image_count INT DEFAULT 0,

    -- Flexible metadata storage
    metadata JSONB,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Indexes
    CONSTRAINT valid_completeness CHECK (completeness_score BETWEEN 0 AND 1)
);

-- Document source records (track all sources for each document)
CREATE TABLE document_source_records (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_uuid UUID NOT NULL REFERENCES genizah_documents(uuid) ON DELETE CASCADE,

    -- Source identification
    source_name VARCHAR(50) NOT NULL,  -- 'PGP', 'Cambridge', 'Friedberg', 'NLI'
    source_id VARCHAR(255) NOT NULL,  -- Their internal ID
    source_url TEXT,
    source_shelf_mark VARCHAR(255),  -- Their version of shelf mark

    -- Source metadata (stored as-is for provenance)
    source_metadata JSONB,

    -- Quality tracking
    metadata_quality VARCHAR(20),  -- 'high', 'medium', 'low'
    is_primary_source BOOLEAN DEFAULT FALSE,

    -- Timestamps
    scraped_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Constraints
    UNIQUE(source_name, source_id)
);

-- Shelf mark variants (all known forms of the same shelf mark)
CREATE TABLE shelf_mark_variants (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_uuid UUID NOT NULL REFERENCES genizah_documents(uuid) ON DELETE CASCADE,

    variant_shelf_mark VARCHAR(255) NOT NULL,
    variant_type VARCHAR(50),  -- 'normalized', 'scholarly', 'database', 'historical', 'join'
    source VARCHAR(50),  -- Which source uses this variant

    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(variant_shelf_mark)
);

-- ============================================================================
-- IMAGE TABLES
-- ============================================================================

-- Images with source tracking (one-to-many with documents)
CREATE TABLE genizah_images (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_uuid UUID NOT NULL REFERENCES genizah_documents(uuid) ON DELETE CASCADE,

    -- Source tracking
    source_name VARCHAR(50) NOT NULL,  -- Which repository provided this image
    source_record_uuid UUID REFERENCES document_source_records(uuid),

    -- Image identification
    image_url TEXT NOT NULL,
    thumbnail_url TEXT,
    image_order INT NOT NULL,  -- 1, 2, 3... for sequencing

    -- Image metadata
    side VARCHAR(20),  -- 'recto', 'verso', 'page_1', 'page_2', etc.
    folio_number VARCHAR(50),  -- '1r', '1v', '2r', '2v'
    image_type VARCHAR(20),  -- 'color', 'multispectral', 'infrared', 'bw'

    -- Technical details
    width INT,
    height INT,
    resolution VARCHAR(50),  -- '300dpi', '600dpi'
    file_format VARCHAR(10),  -- 'jpg', 'tiff', 'png'
    file_size_bytes BIGINT,
    quality_score FLOAT,  -- 0-1, for choosing best image when duplicates exist

    -- IIIF support
    iiif_manifest_url TEXT,
    iiif_image_id TEXT,

    -- Additional metadata
    metadata JSONB,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(document_uuid, source_name, image_order),
    CONSTRAINT valid_quality CHECK (quality_score IS NULL OR quality_score BETWEEN 0 AND 1)
);

-- ============================================================================
-- BIBLIOGRAPHIC SOURCES TABLES
-- ============================================================================

-- Bibliographic sources (journal articles, books, chapters)
CREATE TABLE bibliographic_sources (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Source type
    source_type VARCHAR(50) NOT NULL,  -- 'article', 'book', 'chapter', 'thesis', 'catalog'

    -- Basic bibliographic info
    title TEXT NOT NULL,
    authors TEXT[],
    editors TEXT[],
    publication_year INT,
    publisher VARCHAR(255),
    publication_place VARCHAR(255),

    -- Journal-specific
    journal VARCHAR(255),
    volume VARCHAR(50),
    issue VARCHAR(50),
    pages VARCHAR(50),

    -- Book-specific
    book_title TEXT,  -- For chapters
    series VARCHAR(255),
    edition VARCHAR(50),

    -- Identifiers
    doi VARCHAR(255),
    isbn VARCHAR(20),
    issn VARCHAR(20),
    url TEXT,

    -- Content
    abstract TEXT,
    keywords TEXT[],
    full_text TEXT,  -- Complete text (can be entire book)
    language VARCHAR(50),

    -- Full-text search vector (optional)
    full_text_tsv tsvector,

    -- Quality and tracking
    has_full_text BOOLEAN DEFAULT FALSE,
    word_count INT,
    shelf_marks_mentioned TEXT[],  -- Quick reference to mentioned shelf marks

    -- Flexible metadata
    metadata JSONB,

    -- Source tracking
    source_url TEXT,
    scraped_at TIMESTAMP,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Document-source mentions (junction table linking documents to bibliography)
CREATE TABLE document_source_mentions (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Core relationship
    document_uuid UUID NOT NULL REFERENCES genizah_documents(uuid) ON DELETE CASCADE,
    source_uuid UUID NOT NULL REFERENCES bibliographic_sources(uuid) ON DELETE CASCADE,

    -- Mention details
    shelf_mark_mentioned VARCHAR(255),  -- Actual shelf mark used in the source
    mention_context TEXT,  -- The passage/paragraph mentioning the document

    -- Location in source
    page_number VARCHAR(50),  -- '23', '23-24', 'n.45'
    paragraph_number INT,
    section_title TEXT,

    -- Extraction metadata
    extraction_method VARCHAR(50),  -- 'regex', 'nlp', 'manual', 'llm'
    confidence_score FLOAT,  -- 0-1

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(document_uuid, source_uuid, page_number),
    CONSTRAINT valid_confidence CHECK (confidence_score BETWEEN 0 AND 1)
);

-- Bibliographic chunks (for Elasticsearch embedding)
CREATE TABLE bibliographic_chunks (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_uuid UUID NOT NULL REFERENCES bibliographic_sources(uuid) ON DELETE CASCADE,

    -- Chunk content
    chunk_text TEXT NOT NULL,
    chunk_order INT NOT NULL,  -- Sequence within source

    -- Chunk metadata
    chunk_type VARCHAR(50) NOT NULL,  -- 'shelf_mark_mention', 'semantic_section', 'full_document'
    chunk_size_tokens INT,

    -- References
    shelf_marks_in_chunk TEXT[],  -- Shelf marks mentioned in this chunk
    document_uuids UUID[],  -- References to genizah_documents

    -- Section metadata
    section_title TEXT,
    section_type VARCHAR(50),  -- 'introduction', 'analysis', 'conclusion', 'footnote'
    page_range VARCHAR(50),

    -- For Elasticsearch indexing
    needs_embedding BOOLEAN DEFAULT TRUE,
    last_embedded_at TIMESTAMP,

    -- Flexible metadata
    metadata JSONB,

    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(source_uuid, chunk_order)
);

-- ============================================================================
-- EMBEDDINGS TRACKING (for multiple embedding models)
-- ============================================================================

-- Track which embedding models have been applied
CREATE TABLE embedding_models (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    model_name VARCHAR(100) UNIQUE NOT NULL,  -- 'nomic-embed-text-v1.5', 'openai-text-embedding-3-large'
    model_version VARCHAR(50),
    embedding_dimension INT NOT NULL,

    -- ElasticSearch index mapping
    elasticsearch_index VARCHAR(100) UNIQUE NOT NULL,  -- 'genizah_chunks_nomic_v1.5'

    -- Model metadata
    model_type VARCHAR(50),  -- 'text', 'multimodal'
    languages_supported TEXT[],
    is_active BOOLEAN DEFAULT TRUE,

    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Track embedding status per chunk per model
CREATE TABLE chunk_embeddings (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    chunk_uuid UUID NOT NULL REFERENCES bibliographic_chunks(uuid) ON DELETE CASCADE,
    model_uuid UUID NOT NULL REFERENCES embedding_models(uuid) ON DELETE CASCADE,

    -- Embedding metadata (actual vectors stored in Elasticsearch)
    elasticsearch_doc_id VARCHAR(255),  -- ID in the ES index
    embedded_at TIMESTAMP DEFAULT NOW(),

    -- Quality metrics
    embedding_success BOOLEAN DEFAULT TRUE,
    error_message TEXT,

    UNIQUE(chunk_uuid, model_uuid)
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- genizah_documents indexes
CREATE INDEX idx_docs_institution ON genizah_documents(institution);
CREATE INDEX idx_docs_collection ON genizah_documents(collection);
CREATE INDEX idx_docs_type ON genizah_documents(document_type);
CREATE INDEX idx_docs_language ON genizah_documents USING GIN(language);
CREATE INDEX idx_docs_dating ON genizah_documents(dating_start_year, dating_end_year);
CREATE INDEX idx_docs_metadata ON genizah_documents USING GIN(metadata);
CREATE INDEX idx_docs_joins ON genizah_documents USING GIN(joins_with);
CREATE INDEX idx_docs_updated ON genizah_documents(updated_at DESC);

-- document_source_records indexes
CREATE INDEX idx_source_records_document ON document_source_records(document_uuid);
CREATE INDEX idx_source_records_source ON document_source_records(source_name);
CREATE INDEX idx_source_records_source_id ON document_source_records(source_name, source_id);
CREATE INDEX idx_source_records_metadata ON document_source_records USING GIN(source_metadata);

-- shelf_mark_variants indexes
CREATE INDEX idx_variants_document ON shelf_mark_variants(document_uuid);
CREATE INDEX idx_variants_mark ON shelf_mark_variants(variant_shelf_mark);
CREATE INDEX idx_variants_type ON shelf_mark_variants(variant_type);

-- genizah_images indexes
CREATE INDEX idx_images_document ON genizah_images(document_uuid);
CREATE INDEX idx_images_source ON genizah_images(source_name);
CREATE INDEX idx_images_order ON genizah_images(document_uuid, image_order);
CREATE INDEX idx_images_type ON genizah_images(image_type);
CREATE INDEX idx_images_quality ON genizah_images(quality_score DESC NULLS LAST);

-- bibliographic_sources indexes
CREATE INDEX idx_biblio_type ON bibliographic_sources(source_type);
CREATE INDEX idx_biblio_year ON bibliographic_sources(publication_year);
CREATE INDEX idx_biblio_authors ON bibliographic_sources USING GIN(authors);
CREATE INDEX idx_biblio_keywords ON bibliographic_sources USING GIN(keywords);
CREATE INDEX idx_biblio_shelf_marks ON bibliographic_sources USING GIN(shelf_marks_mentioned);
CREATE INDEX idx_biblio_fulltext ON bibliographic_sources USING GIN(full_text_tsv);
CREATE INDEX idx_biblio_has_text ON bibliographic_sources(has_full_text) WHERE has_full_text = TRUE;

-- document_source_mentions indexes
CREATE INDEX idx_mentions_document ON document_source_mentions(document_uuid);
CREATE INDEX idx_mentions_source ON document_source_mentions(source_uuid);
CREATE INDEX idx_mentions_shelf_mark ON document_source_mentions(shelf_mark_mentioned);
CREATE INDEX idx_mentions_confidence ON document_source_mentions(confidence_score DESC);

-- bibliographic_chunks indexes
CREATE INDEX idx_chunks_source ON bibliographic_chunks(source_uuid);
CREATE INDEX idx_chunks_order ON bibliographic_chunks(source_uuid, chunk_order);
CREATE INDEX idx_chunks_type ON bibliographic_chunks(chunk_type);
CREATE INDEX idx_chunks_shelf_marks ON bibliographic_chunks USING GIN(shelf_marks_in_chunk);
CREATE INDEX idx_chunks_documents ON bibliographic_chunks USING GIN(document_uuids);
CREATE INDEX idx_chunks_needs_embedding ON bibliographic_chunks(needs_embedding) WHERE needs_embedding = TRUE;

-- chunk_embeddings indexes
CREATE INDEX idx_embeddings_chunk ON chunk_embeddings(chunk_uuid);
CREATE INDEX idx_embeddings_model ON chunk_embeddings(model_uuid);
CREATE INDEX idx_embeddings_success ON chunk_embeddings(embedding_success);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Update updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_genizah_documents_updated_at BEFORE UPDATE ON genizah_documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_document_source_records_updated_at BEFORE UPDATE ON document_source_records
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_genizah_images_updated_at BEFORE UPDATE ON genizah_images
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bibliographic_sources_updated_at BEFORE UPDATE ON bibliographic_sources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Update full-text search vector for bibliographic sources
CREATE TRIGGER biblio_fulltext_update
    BEFORE INSERT OR UPDATE OF full_text ON bibliographic_sources
    FOR EACH ROW EXECUTE FUNCTION
    tsvector_update_trigger(full_text_tsv, 'pg_catalog.english', full_text);

-- Update image count on genizah_documents
CREATE OR REPLACE FUNCTION update_document_image_count()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE genizah_documents
    SET image_count = (
        SELECT COUNT(DISTINCT uuid)
        FROM genizah_images
        WHERE document_uuid = COALESCE(NEW.document_uuid, OLD.document_uuid)
    ),
    has_images = (
        SELECT COUNT(*) > 0
        FROM genizah_images
        WHERE document_uuid = COALESCE(NEW.document_uuid, OLD.document_uuid)
    )
    WHERE uuid = COALESCE(NEW.document_uuid, OLD.document_uuid);
    RETURN COALESCE(NEW, OLD);
END;
$$ language 'plpgsql';

CREATE TRIGGER update_image_count_insert AFTER INSERT ON genizah_images
    FOR EACH ROW EXECUTE FUNCTION update_document_image_count();

CREATE TRIGGER update_image_count_delete AFTER DELETE ON genizah_images
    FOR EACH ROW EXECUTE FUNCTION update_document_image_count();

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Complete document view with all sources and images
CREATE VIEW v_documents_complete AS
SELECT
    d.*,
    (SELECT json_agg(json_build_object(
        'source_name', sr.source_name,
        'source_url', sr.source_url,
        'source_shelf_mark', sr.source_shelf_mark,
        'is_primary', sr.is_primary_source
    )) FROM document_source_records sr WHERE sr.document_uuid = d.uuid) as sources,

    (SELECT json_agg(json_build_object(
        'variant', v.variant_shelf_mark,
        'type', v.variant_type
    )) FROM shelf_mark_variants v WHERE v.document_uuid = d.uuid) as shelf_mark_variants,

    (SELECT COUNT(*) FROM genizah_images i WHERE i.document_uuid = d.uuid) as total_images,

    (SELECT COUNT(*) FROM document_source_mentions m WHERE m.document_uuid = d.uuid) as bibliography_count
FROM genizah_documents d;

-- Bibliography with mention counts
CREATE VIEW v_bibliography_with_mentions AS
SELECT
    b.*,
    (SELECT COUNT(*) FROM document_source_mentions m WHERE m.source_uuid = b.uuid) as document_mention_count,
    (SELECT COUNT(*) FROM bibliographic_chunks c WHERE c.source_uuid = b.uuid) as chunk_count,
    (SELECT COUNT(*) FROM bibliographic_chunks c
     WHERE c.source_uuid = b.uuid AND c.needs_embedding = FALSE) as embedded_chunk_count
FROM bibliographic_sources b;

-- ============================================================================
-- EXAMPLE DATA
-- ============================================================================

-- Insert example embedding models
INSERT INTO embedding_models (model_name, model_version, embedding_dimension, elasticsearch_index, languages_supported) VALUES
('nomic-embed-text-v1.5', 'v1.5', 768, 'genizah_chunks_nomic_v1_5', ARRAY['en', 'he', 'ar']),
('openai-text-embedding-3-large', 'v3', 3072, 'genizah_chunks_openai_large', ARRAY['en', 'he', 'ar', 'multilingual']),
('cohere-embed-multilingual-v3', 'v3', 1024, 'genizah_chunks_cohere_multi', ARRAY['multilingual']);