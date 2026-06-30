"""
6-stage PDF processing pipeline for NCCA syllabus + SEC past paper +
SEC marking-scheme PDFs.

Implements the `oideachais-pdf-processing` capability spec at
`openspec/specs/oideachais-pdf-processing/spec.md`.

The 6 stages are:
1. OCR (VLM dispatch) — `select_ocr_backend()` from cocoindex.ocr_aware_flow
2. Diagram detection — Granite-Docling + Molmo2-8B
3. BAML extraction — ExtractLeavingCertSyllabus / ExtractPastPaper / ExtractMarkingScheme
4. Topic validation — fuzzy-match against NCCA taxonomy
5. Semantic chunking — CocoIndex v1 + BGE-M3
6. Lakehouse + Cognee + Graphiti — DuckLake + KG + temporal

The pipeline is invoked from Dagster assets at
`assets/asset_generation/official_documents/{syllabus,past_paper,marking_scheme}.py`
"""

from .pipeline import (
    PDFProcessingPipeline,
    PDFProcessingResult,
    Stage1Result,
    Stage2Result,
    Stage3Result,
    Stage4Result,
    Stage5Result,
    Stage6Result,
)
from .diagram_detector import DiagramDetector, DiagramResult
from .topic_validator import TopicValidator, ValidationResult
from .semantic_chunker import SemanticChunker, ChunkResult

__all__ = [
    "PDFProcessingPipeline",
    "PDFProcessingResult",
    "Stage1Result",
    "Stage2Result",
    "Stage3Result",
    "Stage4Result",
    "Stage5Result",
    "Stage6Result",
    "DiagramDetector",
    "DiagramResult",
    "TopicValidator",
    "ValidationResult",
    "SemanticChunker",
    "ChunkResult",
]
