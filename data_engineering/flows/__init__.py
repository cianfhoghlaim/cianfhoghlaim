"""
CocoIndex Flows for Celtic Education Pipeline.

Provides:
- Curriculum embedding with mandatory batching (100+ per call)
- Translation to all Celtic languages
- Geospatial indexing with spatial joins
- HNSW index management for bulk inserts

CRITICAL CONSTRAINTS:
- Embedding batching: MANDATORY minimum 100 per call
- HNSW indexes: DROP before bulk inserts >50 rows
- DuckDB: Single-threaded only

Flows:
- curriculum_embedding: Chunk → Embed → LanceDB
- curriculum_translation: Detect → Translate → Store
- geospatial_indexing: Boundaries → Spatial Join → Index
"""

from .curriculum_embedding import (
    HNSW_DROP_THRESHOLD,
    MIN_EMBEDDING_BATCH_SIZE,
    CurriculumEmbeddingFlow,
    EmbeddingConfig,
    EmbeddingEngine,
    LanceDBEmbeddingSink,
    TextChunker,
    create_embedding_flow,
)
from .curriculum_translation import (
    CELTIC_LANGUAGES,
    TRANSLATION_MODELS,
    CurriculumTranslationConfig,
    CurriculumTranslationTransform,
    create_translation_flow,
    run_translation_batch,
)
from .geospatial_indexing import (
    GeoParquetWriter,
    GeospatialIndexConfig,
    H3SpatialIndexer,
    LocationIndexTransform,
    create_geospatial_indexing_flow,
    run_geospatial_indexing,
)
from .learning_outcome_graph import (
    LearningOutcomeExtractor,
    LearningOutcomeGraphBuilder,
    LearningOutcomeRelation,
    LearningPathFinder,
    RelationshipType,
    build_subject_graph,
    find_learning_path,
)
from .ocr_embedding import (
    BatchEmbedder,
    LanceDBOCRSink,
    OCREmbeddingConfig,
    OCREmbeddingFlow,
    OCREmbeddingResult,
    OCRTextChunker,
    run_ocr_embedding_flow,
    run_ocr_embedding_flow_sync,
)

# Research embedding (migrated from taighde)
from .research_embedding import (
    code_embedding_flow,
    document_embedding_flow,
    embed_code_chunk,
    embed_document_chunk,
    find_similar_code,
    search_by_subject,
    search_code,
    search_cs_documents,
    search_documents,
    search_irish_documents,
    search_java_code,
)

__all__ = [
    # Embedding
    "EmbeddingConfig",
    "CurriculumEmbeddingFlow",
    "TextChunker",
    "EmbeddingEngine",
    "LanceDBEmbeddingSink",
    "create_embedding_flow",
    "MIN_EMBEDDING_BATCH_SIZE",
    "HNSW_DROP_THRESHOLD",
    # Translation
    "CurriculumTranslationConfig",
    "CurriculumTranslationTransform",
    "create_translation_flow",
    "run_translation_batch",
    "CELTIC_LANGUAGES",
    "TRANSLATION_MODELS",
    # Geospatial
    "GeospatialIndexConfig",
    "H3SpatialIndexer",
    "LocationIndexTransform",
    "GeoParquetWriter",
    "create_geospatial_indexing_flow",
    "run_geospatial_indexing",
    # OCR Embedding
    "OCREmbeddingConfig",
    "OCRTextChunker",
    "BatchEmbedder",
    "LanceDBOCRSink",
    "OCREmbeddingResult",
    "OCREmbeddingFlow",
    "run_ocr_embedding_flow",
    "run_ocr_embedding_flow_sync",
    # Learning Outcome Graph
    "RelationshipType",
    "LearningOutcomeRelation",
    "LearningOutcomeExtractor",
    "LearningOutcomeGraphBuilder",
    "LearningPathFinder",
    "build_subject_graph",
    "find_learning_path",
    # Research Embedding (migrated from taighde)
    "document_embedding_flow",
    "embed_document_chunk",
    "search_documents",
    "search_by_subject",
    "search_irish_documents",
    "search_cs_documents",
    "code_embedding_flow",
    "embed_code_chunk",
    "search_code",
    "find_similar_code",
    "search_java_code",
]
