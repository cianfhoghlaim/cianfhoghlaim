"""Tests for the 6-stage PDF processing pipeline (v4).

Per `openspec/specs/oideachais-pdf-processing/spec.md`:
- Stage 1: OCR (VLM dispatch)
- Stage 2: Diagram detection (Granite-Docling + Molmo2-8B)
- Stage 3: BAML extraction (syllabus / past paper / marking scheme)
- Stage 4: Topic validation (NCCA taxonomy)
- Stage 5: Semantic chunking (CocoIndex v1 + BGE-M3)
- Stage 6: Lakehouse + Cognee + Graphiti

The actual ML model calls are stubbed in v4 (the production deployment
will wire them up). These tests cover the structural correctness.
"""

from __future__ import annotations

import importlib.util
import os
import sys
import unittest
from pathlib import Path

# Add the repo root to sys.path so the `cianfhoghlaim` package is importable.
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)


def _load_module(name: str, path: Path):
    """Load a module directly from a file path, bypassing parent package __init__."""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load spec for {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# Load the 4 PDF pipeline modules directly, bypassing the parent
# `assets/__init__.py` which has heavy Dagster imports unavailable in
# this test environment.
_PIPELINE_DIR = (
    Path(__file__).resolve().parent.parent.parent
    / "assets" / "_oideachais_dagster_defs" / "assets" / "pdf_processing"
)
sys.modules.setdefault("pdf_processing", type(sys)("pdf_processing"))
sys.modules["pdf_processing.diagram_detector"] = _load_module(
    "pdf_processing.diagram_detector", _PIPELINE_DIR / "diagram_detector.py"
)
sys.modules["pdf_processing.topic_validator"] = _load_module(
    "pdf_processing.topic_validator", _PIPELINE_DIR / "topic_validator.py"
)
sys.modules["pdf_processing.semantic_chunker"] = _load_module(
    "pdf_processing.semantic_chunker", _PIPELINE_DIR / "semantic_chunker.py"
)
sys.modules["pdf_processing.pipeline"] = _load_module(
    "pdf_processing.pipeline", _PIPELINE_DIR / "pipeline.py"
)

# Now import the classes
from pdf_processing.diagram_detector import DiagramDetector, DiagramResult  # noqa: E402
from pdf_processing.topic_validator import TopicValidator, ValidationResult  # noqa: E402
from pdf_processing.semantic_chunker import SemanticChunker, ChunkResult  # noqa: E402
from pdf_processing.pipeline import (  # noqa: E402
    PDFProcessingPipeline,
    Stage1Result,
    Stage2Result,
    Stage3Result,
    Stage4Result,
    Stage5Result,
    Stage6Result,
)


class TestStage1OCRAwareSelection(unittest.TestCase):
    """Stage 1 — OCR (VLM dispatch)."""

    def test_pipeline_creation(self):
        """Pipeline must be creatable with (subject, year, paper)."""
        pipeline = PDFProcessingPipeline(
            subject="Mathematics", year=2024, paper="paper-1",
        )
        self.assertEqual(pipeline.subject, "Mathematics")
        self.assertEqual(pipeline.year, 2024)
        self.assertEqual(pipeline.paper, "paper-1")

    def test_stage1_selects_optimal_model(self):
        """Stage 1 must call select_ocr_backend and pick the right model."""
        pipeline = PDFProcessingPipeline(subject="Mathematics", year=2024)
        import tempfile
        with tempfile.NamedTemporaryFile(suffix="syllabus.pdf", delete=False) as tmp:
            tmp.write(b"x" * (10 * 1024 * 1024))  # 10 MB
            tmp_path = Path(tmp.name)

        try:
            result = pipeline.run(tmp_path, "syllabus")
            self.assertIsInstance(result.stage1, Stage1Result)
            # 10 MB syllabus should use gemma-4-26B-A4B
            self.assertEqual(result.stage1.selection.model.key, "gemma-4-26B-A4B")
        finally:
            tmp_path.unlink()


class TestStage2DiagramDetection(unittest.TestCase):
    """Stage 2 — Diagram detection."""

    def test_diagram_detector_creation(self):
        detector = DiagramDetector()
        self.assertEqual(
            detector.layout_model, "ibm-granite/granite-docling-258M",
        )
        self.assertEqual(detector.pointing_model, "allenai/Molmo2-8B")

    def test_diagram_detector_with_custom_models(self):
        detector = DiagramDetector(
            layout_model="custom/layout-model",
            pointing_model="custom/pointing-model",
        )
        self.assertEqual(detector.layout_model, "custom/layout-model")
        self.assertEqual(detector.pointing_model, "custom/pointing-model")

    def test_diagram_result_dataclass(self):
        result = DiagramResult(
            page_number=1,
            diagram_type="figure",
            bbox=(0.1, 0.2, 0.5, 0.6),
            caption="A diagram",
            caption_en="A diagram",
            caption_ga="Léaráid",
            confidence=0.95,
        )
        d = result.to_dict()
        self.assertEqual(d["page_number"], 1)
        self.assertEqual(d["diagram_type"], "figure")
        self.assertEqual(d["caption_ga"], "Léaráid")


class TestStage3BAMLExtraction(unittest.TestCase):
    """Stage 3 — BAML extraction."""

    def test_baml_records_for_syllabus(self):
        """Syllabus BAML records should have SyllabusTopic fields."""
        pipeline = PDFProcessingPipeline(subject="Mathematics", year=2024)
        import tempfile
        with tempfile.NamedTemporaryFile(suffix="syllabus.pdf", delete=False) as tmp:
            tmp.write(b"x" * 1024)
            tmp_path = Path(tmp.name)
        try:
            result = pipeline.run(tmp_path, "syllabus")
            # Stub returns empty list — but the result should be a Stage3Result
            self.assertIsInstance(result.stage3, Stage3Result)
            self.assertEqual(result.stage3.document_type, "syllabus")
            self.assertEqual(result.stage3.baml_client, "LitellmClient")
        finally:
            tmp_path.unlink()


class TestStage4TopicValidation(unittest.TestCase):
    """Stage 4 — Topic validation (NCCA taxonomy)."""

    def test_topic_validator_creation(self):
        validator = TopicValidator()
        self.assertEqual(validator.match_threshold, 0.95)

    def test_topic_validator_with_custom_threshold(self):
        validator = TopicValidator(match_threshold=0.85)
        self.assertEqual(validator.match_threshold, 0.85)

    def test_validate_empty_records(self):
        validator = TopicValidator()
        validated, n_pass, n_fail, mismatched = validator.validate_records([])
        self.assertEqual(validated, [])
        self.assertEqual(n_pass, 0)
        self.assertEqual(n_fail, 0)
        self.assertEqual(mismatched, [])

    def test_validate_records_exact_match(self):
        """An exact topic match should pass."""
        validator = TopicValidator(ncca_taxonomy=[
            {"name": "Differentiation", "subject": "Mathematics"},
        ])
        records = [{"topic": "Differentiation", "questionNumber": 1}]
        validated, n_pass, n_fail, mismatched = validator.validate_records(records)
        self.assertEqual(n_pass, 1)
        self.assertEqual(n_fail, 0)
        self.assertTrue(validated[0]["topic_validated"])

    def test_validate_records_no_match(self):
        """A non-matching topic should fail."""
        validator = TopicValidator(ncca_taxonomy=[
            {"name": "Differentiation", "subject": "Mathematics"},
        ])
        records = [{"topic": "Quantum Entanglement", "questionNumber": 1}]
        validated, n_pass, n_fail, mismatched = validator.validate_records(records)
        self.assertEqual(n_pass, 0)
        self.assertEqual(n_fail, 1)
        self.assertFalse(validated[0]["topic_validated"])


class TestStage5SemanticChunking(unittest.TestCase):
    """Stage 5 — Semantic chunking."""

    def test_chunker_creation(self):
        chunker = SemanticChunker()
        self.assertEqual(chunker.embedder, "BAAI/bge-m3")
        self.assertEqual(chunker.BGE_DIM, 1024)

    def test_chunk_syllabus(self):
        chunker = SemanticChunker()
        records = [
            {
                "name": "Differentiation",
                "description": "Calculus of derivatives",
                "learningOutcomes": ["LO1", "LO2"],
                "weightPct": 25,
            },
        ]
        chunks, n_by_type = chunker.chunk("syllabus", records, [])
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0].chunk_type, "topic")
        self.assertIn("Differentiation", chunks[0].text)
        self.assertEqual(n_by_type.get("topic", 0), 1)

    def test_chunk_past_paper(self):
        chunker = SemanticChunker()
        records = [
            {
                "questionNumber": 1,
                "year": 2024,
                "subject": "Mathematics",
                "paper": "paper-1",
                "level": "H",
                "topic": "Differentiation",
                "marks": 25,
                "questionText": "Find the derivative of x^2",
                "isOptional": False,
            },
        ]
        chunks, n_by_type = chunker.chunk("past_paper", records, [])
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0].chunk_type, "question")
        self.assertEqual(chunks[0].metadata["question_number"], 1)
        self.assertEqual(n_by_type.get("question", 0), 1)

    def test_chunk_marking_scheme(self):
        chunker = SemanticChunker()
        records = [
            {
                "questionNumber": 1,
                "subject": "Mathematics",
                "year": 2024,
                "paper": "paper-1",
                "markValue": 25,
                "markType": "M1A1",
                "answerText": "Apply the power rule",
                "isOptional": False,
                "requiresFormulaImage": False,
            },
        ]
        chunks, n_by_type = chunker.chunk("marking_scheme", records, [])
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0].chunk_type, "marking_point")
        self.assertEqual(n_by_type.get("marking_point", 0), 1)


class TestStage6Lakehouse(unittest.TestCase):
    """Stage 6 — Lakehouse + Cognee + Graphiti."""

    def test_stage6_ducklake_table_name(self):
        """The DuckLake table name should be in the canonical format."""
        pipeline = PDFProcessingPipeline(subject="Mathematics", year=2024, paper="paper-1")
        import tempfile
        with tempfile.NamedTemporaryFile(suffix="syllabus.pdf", delete=False) as tmp:
            tmp.write(b"x" * 1024)
            tmp_path = Path(tmp.name)

        try:
            result = pipeline.run(tmp_path, "syllabus")
            self.assertIn("ducklake://oideachais.assets.official_documents", result.stage6.ducklake_table)
            self.assertIn("Mathematics", result.stage6.ducklake_table)
            self.assertIn("2024", result.stage6.ducklake_table)
        finally:
            tmp_path.unlink()

    def test_stage6_graphiti_episode(self):
        """The Graphiti episode must be populated with the right fields."""
        pipeline = PDFProcessingPipeline(subject="Mathematics", year=2024)
        import tempfile
        with tempfile.NamedTemporaryFile(suffix="syllabus.pdf", delete=False) as tmp:
            tmp.write(b"x" * 1024)
            tmp_path = Path(tmp.name)

        try:
            result = pipeline.run(tmp_path, "syllabus")
            episode = result.stage6.graphiti_episode
            self.assertEqual(episode["type"], "syllabus")
            self.assertEqual(episode["subject"], "Mathematics")
            self.assertEqual(episode["year"], 2024)
        finally:
            tmp_path.unlink()


class TestEndToEndPipeline(unittest.TestCase):
    """End-to-end test: run the full 6-stage pipeline."""

    def test_run_full_pipeline_syllabus(self):
        pipeline = PDFProcessingPipeline(subject="Mathematics", year=2024)
        import tempfile
        with tempfile.NamedTemporaryFile(suffix="syllabus.pdf", delete=False) as tmp:
            tmp.write(b"x" * 1024)
            tmp_path = Path(tmp.name)

        try:
            result = pipeline.run(tmp_path, "syllabus")
            # All 6 stages should have run
            self.assertIsInstance(result.stage1, Stage1Result)
            self.assertIsInstance(result.stage2, Stage2Result)
            self.assertIsInstance(result.stage3, Stage3Result)
            self.assertIsInstance(result.stage4, Stage4Result)
            self.assertIsInstance(result.stage5, Stage5Result)
            self.assertIsInstance(result.stage6, Stage6Result)
            # Total duration should be tracked
            self.assertGreaterEqual(result.total_duration_seconds, 0.0)
        finally:
            tmp_path.unlink()

    def test_run_full_pipeline_marking_scheme(self):
        pipeline = PDFProcessingPipeline(subject="Mathematics", year=2024, paper="paper-1")
        import tempfile
        with tempfile.NamedTemporaryFile(suffix="marking_scheme.pdf", delete=False) as tmp:
            tmp.write(b"x" * 1024)
            tmp_path = Path(tmp.name)

        try:
            result = pipeline.run(tmp_path, "marking_scheme")
            self.assertEqual(result.document_type, "marking_scheme")
            self.assertIn("marking_schemes", result.stage6.ducklake_table)
        finally:
            tmp_path.unlink()


if __name__ == "__main__":
    unittest.main()
