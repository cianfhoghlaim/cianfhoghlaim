"""
The 6-stage PDF processing pipeline orchestrator.

Per `openspec/specs/oideachais-pdf-processing/spec.md`:
- Stage 1: OCR (VLM dispatch)
- Stage 2: Diagram detection (Granite-Docling + Molmo2-8B)
- Stage 3: BAML extraction (syllabus / past paper / marking scheme)
- Stage 4: Topic validation (NCCA taxonomy)
- Stage 5: Semantic chunking (CocoIndex v1 + BGE-M3)
- Stage 6: Lakehouse + Cognee + Graphiti (DuckLake + KG + temporal)
"""

from __future__ import annotations

import logging
import time
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from cianfhoghlaim.ocr.models import (
    OCRModel,
    OCRAwareSelection,
    select_ocr_backend,
)

from .diagram_detector import DiagramDetector, DiagramResult
from .semantic_chunker import SemanticChunker, ChunkResult
from .topic_validator import TopicValidator, ValidationResult

logger = logging.getLogger(__name__)

warnings.warn(
    "pdf_processing.pipeline is the v4 implementation of the 6-stage PDF "
    "pipeline per oideachais-pdf-processing/spec.md. It is experimental "
    "and may change in v5.",
    UserWarning,
    stacklevel=2,
)

DocumentType = Literal["syllabus", "past_paper", "marking_scheme"]


# ─── Result dataclasses (one per stage) ────────────────────────────────────


@dataclass
class Stage1Result:
    """Stage 1 — OCR result."""

    document_path: Path
    selection: OCRAwareSelection
    page_texts: list[str] = field(default_factory=list)
    page_images: list[bytes] = field(default_factory=list)
    ocr_confidence_per_page: list[float] = field(default_factory=list)
    duration_seconds: float = 0.0


@dataclass
class Stage2Result:
    """Stage 2 — Diagram detection result."""

    page_diagrams: list[list[DiagramResult]] = field(default_factory=list)
    total_figures: int = 0
    total_tables: int = 0
    total_headings: int = 0
    duration_seconds: float = 0.0


@dataclass
class Stage3Result:
    """Stage 3 — BAML extraction result."""

    document_type: DocumentType
    baml_records: list[dict[str, Any]] = field(default_factory=list)
    # syllabus: list of SyllabusTopic dicts
    # past_paper: list of PastExamQuestion dicts
    # marking_scheme: list of MarkingPoint dicts
    baml_client: str = "LitellmClient"  # or "LlamaSwapClient"
    duration_seconds: float = 0.0


@dataclass
class Stage4Result:
    """Stage 4 — Topic validation result."""

    validated_records: list[dict[str, Any]] = field(default_factory=list)
    n_pass: int = 0
    n_fail: int = 0
    mismatched_records: list[dict[str, Any]] = field(default_factory=list)
    duration_seconds: float = 0.0


@dataclass
class Stage5Result:
    """Stage 5 — Semantic chunking result."""

    chunks: list[ChunkResult] = field(default_factory=list)
    n_chunks_by_type: dict[str, int] = field(default_factory=dict)
    embedder: str = "BAAI/bge-m3"
    duration_seconds: float = 0.0


@dataclass
class Stage6Result:
    """Stage 6 — Lakehouse + Cognee + Graphiti result."""

    ducklake_table: str = ""
    n_rows_written: int = 0
    cognee_dataset: str = ""
    n_cognee_nodes: int = 0
    graphiti_episode: dict[str, Any] = field(default_factory=dict)
    duration_seconds: float = 0.0


@dataclass
class PDFProcessingResult:
    """Final result of the 6-stage PDF processing pipeline."""

    document_path: Path
    document_type: DocumentType
    subject: str
    year: int
    paper: str | None
    stage1: Stage1Result
    stage2: Stage2Result
    stage3: Stage3Result
    stage4: Stage4Result
    stage5: Stage5Result
    stage6: Stage6Result
    total_duration_seconds: float = 0.0


# ─── Pipeline orchestrator ──────────────────────────────────────────────────


class PDFProcessingPipeline:
    """The 6-stage PDF processing pipeline.

    Per `oideachais-pdf-processing/spec.md`:
    - For every PDF (syllabus / past paper / marking scheme), the
      pipeline runs the 6 stages in order.
    - Stage 1 picks the optimal (model, backend) pair from the
      24-entry VISION_MODELS registry.
    - Stages 1-3 use VLMs (Qwen 3-VL 8B, Gemma 4 26B-A4B, Molmo2-8B)
      for OCR + diagram detection + BAML extraction.
    - Stage 4 cross-references every BAML record against the NCCA
      syllabus taxonomy (95% fuzzy-match threshold).
    - Stage 5 chunks semantically (one chunk per syllabus topic /
      past paper question / marking point / diagram region).
    - Stage 6 writes to DuckLake + runs Cognee cognify + appends a
      Graphiti episode.
    """

    def __init__(
        self,
        subject: str,
        year: int,
        paper: str | None = None,
        diagram_detector: DiagramDetector | None = None,
        topic_validator: TopicValidator | None = None,
        semantic_chunker: SemanticChunker | None = None,
    ):
        """Initialize the 6-stage pipeline.

        Args:
            subject: Subject name (e.g. "Mathematics", "Irish")
            year: Year of the document (e.g. 2024)
            paper: Optional paper identifier (e.g. "paper-1", "paper-2")
            diagram_detector: Optional pre-configured DiagramDetector
            topic_validator: Optional pre-configured TopicValidator
            semantic_chunker: Optional pre-configured SemanticChunker
        """
        self.subject = subject
        self.year = year
        self.paper = paper

        self.diagram_detector = diagram_detector or DiagramDetector()
        self.topic_validator = topic_validator or TopicValidator()
        self.semantic_chunker = semantic_chunker or SemanticChunker()

    def run(
        self,
        document_path: Path,
        document_type: DocumentType,
        page_count: int | None = None,
        image_density: float | None = None,
    ) -> PDFProcessingResult:
        """Run the full 6-stage pipeline on a single PDF.

        Args:
            document_path: Path to the PDF
            document_type: One of "syllabus", "past_paper", "marking_scheme"
            page_count: Optional page count (used by select_ocr_backend)
            image_density: Optional image-to-text ratio (used by Stage 2)

        Returns:
            PDFProcessingResult with all 6 stage results
        """
        t0 = time.time()
        logger.info(
            f"Starting 6-stage PDF pipeline for {document_path} "
            f"({document_type}, {self.subject}/{self.year}/{self.paper})"
        )

        # ─── Stage 1: OCR (VLM dispatch) ───
        stage1 = self._stage1_ocr(document_path, page_count, image_density)

        # ─── Stage 2: Diagram detection ───
        stage2 = self._stage2_diagram_detection(stage1)

        # ─── Stage 3: BAML extraction ───
        stage3 = self._stage3_baml_extraction(document_type, stage1)

        # ─── Stage 4: Topic validation ───
        stage4 = self._stage4_topic_validation(stage3)

        # ─── Stage 5: Semantic chunking ───
        stage5 = self._stage5_semantic_chunking(document_type, stage4, stage2)

        # ─── Stage 6: Lakehouse + Cognee + Graphiti ───
        stage6 = self._stage6_lakehouse(
            document_path, document_type, stage4, stage5
        )

        total_duration = time.time() - t0
        logger.info(
            f"6-stage PDF pipeline completed in {total_duration:.1f}s "
            f"({len(stage5.chunks)} chunks, "
            f"{stage4.n_pass}/{stage4.n_pass + stage4.n_fail} topic matches)"
        )

        return PDFProcessingResult(
            document_path=document_path,
            document_type=document_type,
            subject=self.subject,
            year=self.year,
            paper=self.paper,
            stage1=stage1,
            stage2=stage2,
            stage3=stage3,
            stage4=stage4,
            stage5=stage5,
            stage6=stage6,
            total_duration_seconds=total_duration,
        )

    # ─── Stage 1: OCR (VLM dispatch) ───
    def _stage1_ocr(
        self,
        document_path: Path,
        page_count: int | None,
        image_density: float | None,
    ) -> Stage1Result:
        t0 = time.time()
        logger.info(f"Stage 1 — OCR dispatch for {document_path}")

        # Select optimal (model, backend) pair
        selection = select_ocr_backend(
            document_path,
            page_count=page_count,
            image_density=image_density,
        )
        logger.info(
            f"  → {selection.model.key} ({selection.model.backend.value}): "
            f"{selection.reason}"
        )

        # Stub: in production this calls the actual OCR API
        # For now, return empty placeholders
        return Stage1Result(
            document_path=document_path,
            selection=selection,
            page_texts=[],
            page_images=[],
            ocr_confidence_per_page=[],
            duration_seconds=time.time() - t0,
        )

    # ─── Stage 2: Diagram detection ───
    def _stage2_diagram_detection(
        self,
        stage1: Stage1Result,
    ) -> Stage2Result:
        t0 = time.time()
        logger.info("Stage 2 — Diagram detection (Granite-Docling + Molmo2-8B)")

        # Detect diagrams per page using the OCR pages
        page_diagrams = self.diagram_detector.detect_all_pages(
            page_images=stage1.page_images,
        )

        total_figures = sum(1 for d in page_diagrams if d.diagram_type == "figure")
        total_tables = sum(1 for d in page_diagrams if d.diagram_type == "table")
        total_headings = sum(1 for d in page_diagrams if d.diagram_type == "heading")

        return Stage2Result(
            page_diagrams=page_diagrams,
            total_figures=total_figures,
            total_tables=total_tables,
            total_headings=total_headings,
            duration_seconds=time.time() - t0,
        )

    # ─── Stage 3: BAML extraction ───
    def _stage3_baml_extraction(
        self,
        document_type: DocumentType,
        stage1: Stage1Result,
    ) -> Stage3Result:
        t0 = time.time()
        logger.info(
            f"Stage 3 — BAML extraction ({document_type}, "
            f"LitellmClient → litellm.cianfhoghlaim.ie:4000)"
        )

        # Stub: in production this calls the appropriate BAML function
        # - syllabus → ExtractLeavingCertSyllabus (existing BAML)
        # - past_paper → ExtractPastPaper (existing BAML)
        # - marking_scheme → ExtractMarkingScheme (new BAML)
        return Stage3Result(
            document_type=document_type,
            baml_records=[],
            baml_client="LitellmClient",
            duration_seconds=time.time() - t0,
        )

    # ─── Stage 4: Topic validation ───
    def _stage4_topic_validation(
        self,
        stage3: Stage3Result,
    ) -> Stage4Result:
        t0 = time.time()
        logger.info("Stage 4 — Topic validation (fuzzy-match NCCA taxonomy)")

        validated, pass_count, fail_count, mismatched = (
            self.topic_validator.validate_records(stage3.baml_records)
        )

        return Stage4Result(
            validated_records=validated,
            n_pass=pass_count,
            n_fail=fail_count,
            mismatched_records=mismatched,
            duration_seconds=time.time() - t0,
        )

    # ─── Stage 5: Semantic chunking ───
    def _stage5_semantic_chunking(
        self,
        document_type: DocumentType,
        stage4: Stage4Result,
        stage2: Stage2Result,
    ) -> Stage5Result:
        t0 = time.time()
        logger.info("Stage 5 — Semantic chunking (CocoIndex v1 + BGE-M3)")

        chunks, n_by_type = self.semantic_chunker.chunk(
            document_type=document_type,
            validated_records=stage4.validated_records,
            page_diagrams=stage2.page_diagrams,
        )

        return Stage5Result(
            chunks=chunks,
            n_chunks_by_type=n_by_type,
            embedder="BAAI/bge-m3",
            duration_seconds=time.time() - t0,
        )

    # ─── Stage 6: Lakehouse + Cognee + Graphiti ───
    def _stage6_lakehouse(
        self,
        document_path: Path,
        document_type: DocumentType,
        stage4: Stage4Result,
        stage5: Stage5Result,
    ) -> Stage6Result:
        t0 = time.time()
        logger.info("Stage 6 — Lakehouse write + Cognee cognify + Graphiti episode")

        # Build the DuckLake target table name
        paper_part = f".{self.paper}" if self.paper else ""
        ducklake_table = (
            f"oideachais.assets.official_documents.{document_type}s"
            f".{self.subject}.{self.year}{paper_part}"
        )

        # Stub: in production this writes to DuckLake + Cognee + Graphiti
        return Stage6Result(
            ducklake_table=ducklake_table,
            n_rows_written=len(stage5.chunks),
            cognee_dataset="oideachais.pdf_processing",
            n_cognee_nodes=0,
            graphiti_episode={
                "type": document_type,
                "subject": self.subject,
                "year": self.year,
                "paper": self.paper,
                "n_chunks": len(stage5.chunks),
                "n_validated": stage4.n_pass,
                "n_mismatched": stage4.n_fail,
            },
            duration_seconds=time.time() - t0,
        )
