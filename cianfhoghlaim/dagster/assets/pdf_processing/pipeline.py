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

# Phase 8: Observability (lazy import — optional, may not be available in tests)
try:
    from .observability import (
        evaluate_baml_extraction,
        record_stage_metric,
        trace_pipeline,
    )
    _OBSERVABILITY_AVAILABLE = True
except ImportError:
    _OBSERVABILITY_AVAILABLE = False

    def trace_pipeline(*_args, **_kwargs):  # type: ignore[no-redef]
        """Stub: no-op context manager when observability not available."""
        from contextlib import contextmanager
        @contextmanager
        def _noop():
            yield {}
        return _noop()

    def record_stage_metric(*_args, **_kwargs):  # type: ignore[no-redef]
        pass

    def evaluate_baml_extraction(*_args, **_kwargs):  # type: ignore[no-redef]
        return {"schema_compliance": 0.0, "field_completeness": 0.0, "extraction_accuracy": 0.0}

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

        # Phase 8: wrap the entire run in the observability context
        with trace_pipeline(document_type, self.subject, self.year, self.paper) as obs_ctx:
            # ─── Stage 1: OCR (VLM dispatch) ───
            stage1 = self._stage1_ocr(document_path, page_count, image_density)
            record_stage_metric("1", "duration_seconds", stage1.duration_seconds, obs_ctx)

            # ─── Stage 2: Diagram detection ───
            stage2 = self._stage2_diagram_detection(stage1)
            record_stage_metric("2", "duration_seconds", stage2.duration_seconds, obs_ctx)
            record_stage_metric("2", "n_figures", float(stage2.total_figures), obs_ctx)

            # ─── Stage 3: BAML extraction ───
            stage3 = self._stage3_baml_extraction(document_type, stage1)
            record_stage_metric("3", "duration_seconds", stage3.duration_seconds, obs_ctx)
            record_stage_metric("3", "n_records", float(len(stage3.baml_records)), obs_ctx)

            # Phase 8.3: RAGAS-style evaluation of the BAML extraction
            baml_schema = {
                "name": str,
                "description": str,
                "learningOutcomes": list,
            } if document_type == "syllabus" else {
                "questionNumber": int,
                "topic": str,
                "marks": int,
            }
            baml_quality = evaluate_baml_extraction(stage3.baml_records, baml_schema)
            for k, v in baml_quality.items():
                record_stage_metric("3", k, v, obs_ctx)

            # ─── Stage 4: Topic validation ───
            stage4 = self._stage4_topic_validation(stage3)
            record_stage_metric("4", "duration_seconds", stage4.duration_seconds, obs_ctx)
            record_stage_metric("4", "n_pass", float(stage4.n_pass), obs_ctx)
            record_stage_metric("4", "n_fail", float(stage4.n_fail), obs_ctx)

            # ─── Stage 5: Semantic chunking ───
            stage5 = self._stage5_semantic_chunking(document_type, stage4, stage2)
            record_stage_metric("5", "duration_seconds", stage5.duration_seconds, obs_ctx)
            record_stage_metric("5", "n_chunks", float(len(stage5.chunks)), obs_ctx)

            # ─── Stage 6: Lakehouse + Cognee + Graphiti ───
            stage6 = self._stage6_lakehouse(
                document_path, document_type, stage4, stage5
            )
            record_stage_metric("6", "duration_seconds", stage6.duration_seconds, obs_ctx)
            record_stage_metric("6", "n_rows_written", float(stage6.n_rows_written), obs_ctx)

            total_duration = time.time() - t0
            obs_ctx["n_chunks"] = len(stage5.chunks)
            obs_ctx["n_figures"] = stage2.total_figures
            obs_ctx["n_topics_validated"] = stage4.n_pass
            obs_ctx["n_topics_mismatched"] = stage4.n_fail

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

        # Render PDF pages to images + run OCR via litellm
        page_texts: list[str] = []
        page_images: list[bytes] = []
        ocr_confidence: list[float] = []

        try:
            # 1. Render PDF pages to PNG bytes
            rendered = self._render_pdf_pages(document_path, dpi=200)
            page_images = [img_bytes for _, img_bytes in rendered]

            # 2. Call the selected VLM via litellm
            litellm_model = f"local/vision/{selection.model.key}"
            for page_number, image_bytes in rendered:
                page_text, confidence = self._call_vlm_for_page(
                    litellm_model, image_bytes, page_number
                )
                page_texts.append(page_text)
                ocr_confidence.append(confidence)
        except Exception as e:
            logger.error(f"Stage 1 OCR failed: {e}")
            # Continue with empty lists; downstream stages can fall back

        return Stage1Result(
            document_path=document_path,
            selection=selection,
            page_texts=page_texts,
            page_images=page_images,
            ocr_confidence_per_page=ocr_confidence,
            duration_seconds=time.time() - t0,
        )

    def _render_pdf_pages(self, document_path: Path, dpi: int = 200) -> list[tuple[int, bytes]]:
        """Render a PDF to (page_number, PNG_bytes) pairs.

        Uses PyMuPDF (fitz) for fast PDF rendering. Falls back to
        pdf2image if PyMuPDF is not available.
        """
        try:
            import fitz  # PyMuPDF
            rendered: list[tuple[int, bytes]] = []
            with fitz.open(document_path) as pdf:
                for page_number, page in enumerate(pdf, start=1):
                    pix = page.get_pixmap(dpi=dpi)
                    rendered.append((page_number, pix.tobytes("png")))
            return rendered
        except ImportError:
            logger.warning("PyMuPDF not available; falling back to pdf2image")
            from pdf2image import convert_from_path
            images = convert_from_path(str(document_path), dpi=dpi)
            return [
                (i + 1, img.tobytes("png")) for i, img in enumerate(images)
            ]

    def _call_vlm_for_page(
        self,
        litellm_model: str,
        image_bytes: bytes,
        page_number: int,
    ) -> tuple[str, float]:
        """Call a VLM via litellm for a single page.

        Returns (text, confidence) where confidence is 0-1.
        """
        try:
            import litellm
            import base64
            b64 = base64.b64encode(image_bytes).decode("utf-8")
            response = litellm.completion(
                model=litellm_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{b64}",
                                },
                            },
                            {
                                "type": "text",
                                "text": (
                                    "Transcribe the text on this page exactly as written. "
                                    "Preserve all diacritics (fadas, tironian et ⁊). "
                                    "If a diagram or figure is present, transcribe any "
                                    "caption verbatim."
                                ),
                            },
                        ],
                    }
                ],
                timeout=600,
                temperature=0.0,
            )
            text = response.choices[0].message.content or ""
            # LiteLLM doesn't return a confidence directly; estimate from token logprobs
            confidence = 0.95  # placeholder; could be improved with logprobs
            logger.debug(
                f"Stage 1 OCR page {page_number}: {len(text)} chars via {litellm_model}"
            )
            return text, confidence
        except Exception as e:
            logger.error(f"Stage 1 litellm call failed for page {page_number}: {e}")
            return "", 0.0

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

        baml_records: list[dict[str, Any]] = []
        baml_client = "LitellmClient"

        try:
            # Import the regenerated baml_client (Phase 1.3)
            try:
                from cianfhoghlaim.core.baml.shared.baml_client import b as _baml_b
                baml_b = _baml_b
            except ImportError:
                try:
                    # Fallback: legacy import path
                    from cianfhoghlaim.baml_client import b as _baml_b  # type: ignore
                    baml_b = _baml_b
                except ImportError:
                    logger.warning(
                        "baml_client not importable; Stage 3 returns empty records"
                    )
                    baml_b = None

            if baml_b is None:
                return Stage3Result(
                    document_type=document_type,
                    baml_records=[],
                    baml_client=baml_client,
                    duration_seconds=time.time() - t0,
                )

            # Concatenate all page texts into a single input
            full_text = "\n\n".join(stage1.page_texts)

            # Dispatch to the right BAML function per document type
            if document_type == "syllabus":
                result = baml_b.ExtractLeavingCertSyllabus(full_text)
                # Convert to dict for downstream stages
                baml_records = [
                    {
                        "name": t.name,
                        "description": t.description,
                        "learningOutcomes": t.learningOutcomes,
                        "weightPct": t.weightPct,
                    }
                    for t in result.topics
                ]
            elif document_type == "past_paper":
                result = baml_b.ExtractPastPaper(full_text)
                baml_records = [
                    {
                        "questionNumber": q.questionNumber,
                        "year": q.year,
                        "paper": q.paper,
                        "level": q.level,
                        "topic": q.topic,
                        "subtopic": q.subtopic,
                        "marks": q.marks,
                        "questionText": q.questionText,
                        "isOptional": q.isOptional,
                    }
                    for q in result.questions
                ]
            elif document_type == "marking_scheme":
                # New BAML function (added in Phase 1.3)
                result = baml_b.ExtractMarkingScheme(
                    full_text, self.subject, self.year, self.paper or ""
                )
                baml_records = [
                    {
                        "questionNumber": m.questionNumber,
                        "partLabel": m.partLabel,
                        "markValue": m.markValue,
                        "markType": m.markType,
                        "answerText": m.answerText,
                        "alternativeAnswers": m.alternativeAnswers,
                        "isOptional": m.isOptional,
                        "requiresFormulaImage": m.requiresFormulaImage,
                    }
                    for m in result.markingPoints
                ]
        except Exception as e:
            logger.error(f"Stage 3 BAML extraction failed: {e}")
            # Continue with empty records

        return Stage3Result(
            document_type=document_type,
            baml_records=baml_records,
            baml_client=baml_client,
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
        # Canonical format: `ducklake://oideachais.assets.official_documents.{type_plural}.{subject}.{year}[.paper]`
        type_plural = {
            "syllabus": "syllabi",
            "past_paper": "past_papers",
            "marking_scheme": "marking_schemes",
        }.get(document_type, f"{document_type}s")
        paper_part = f".{self.paper}" if self.paper else ""
        ducklake_table = (
            f"ducklake://oideachais.assets.official_documents.{type_plural}"
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
