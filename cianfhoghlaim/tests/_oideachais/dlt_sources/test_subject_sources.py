"""
Tests for per-subject DLT sources (Senior Cycle, Junior Cycle).

Tests the subject resource generation and basic DLT pipeline execution.

Run with: pytest tests/dlt_sources/test_subject_sources.py -v
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# ===========================================================================
# Subject Registry Tests
# ===========================================================================


class TestSubjectResources:
    """Tests for per-subject DLT resource generation."""

    def test_senior_cycle_source_creation(self) -> None:
        """Test Senior Cycle source can be created."""
        from cianfhoghlaim.dlt.british_isles.ireland.education.subjects.senior_cycle import senior_cycle_source

        source = senior_cycle_source(language="en")
        assert source is not None
        assert source.name == "senior_cycle_subjects"

    def test_junior_cycle_source_creation(self) -> None:
        """Test Junior Cycle source can be created."""
        from cianfhoghlaim.dlt.british_isles.ireland.education.subjects.junior_cycle import junior_cycle_source

        source = junior_cycle_source(language="en")
        assert source is not None
        assert source.name == "junior_cycle_subjects"

    def test_senior_cycle_has_cycle_resources(self) -> None:
        """Test Senior Cycle has cycle-level resources."""
        from cianfhoghlaim.dlt.british_isles.ireland.education.subjects.senior_cycle import senior_cycle_source

        source = senior_cycle_source(language="en")
        resource_names = [r.name for r in source.resources.values()]

        # Source uses cycle-level resources, not per-subject
        assert "senior_cycle_pages" in resource_names
        assert "senior_cycle_pdfs" in resource_names

    def test_junior_cycle_has_cycle_resources(self) -> None:
        """Test Junior Cycle has cycle-level resources."""
        from cianfhoghlaim.dlt.british_isles.ireland.education.subjects.junior_cycle import junior_cycle_source

        source = junior_cycle_source(language="en")
        resource_names = [r.name for r in source.resources.values()]

        # Source uses cycle-level resources, not per-subject
        assert "junior_cycle_pages" in resource_names
        assert "junior_cycle_pdfs" in resource_names

    def test_senior_cycle_subject_count(self) -> None:
        """Test Senior Cycle has expected number of subjects in registry."""
        from cianfhoghlaim.dlt.british_isles.ireland.education.subjects.senior_cycle import (
            SENIOR_CYCLE_SUBJECTS,
            senior_cycle_source,
        )

        source = senior_cycle_source(language="en")
        # Source has 2 resources (pages + pdfs for the cycle)
        assert len(source.resources) == 2
        assert len(SENIOR_CYCLE_SUBJECTS) >= 30  # Should have 30+ subjects

    def test_junior_cycle_subject_count(self) -> None:
        """Test Junior Cycle has expected number of subjects in registry."""
        from cianfhoghlaim.dlt.british_isles.ireland.education.subjects.junior_cycle import (
            JUNIOR_CYCLE_SUBJECTS,
            junior_cycle_source,
        )

        source = junior_cycle_source(language="en")
        # Source has 2 resources (pages + pdfs for the cycle)
        assert len(source.resources) == 2
        assert len(JUNIOR_CYCLE_SUBJECTS) >= 15  # Should have 15+ subjects

    def test_irish_language_source(self) -> None:
        """Test sources can be created with Irish language."""
        from cianfhoghlaim.dlt.british_isles.ireland.education.subjects.senior_cycle import senior_cycle_source

        source = senior_cycle_source(language="ga")
        assert source is not None

    def test_single_subject_source_creation(self) -> None:
        """Test creating a source for a single subject."""
        from cianfhoghlaim.dlt.british_isles.ireland.education.subjects.base import create_subject_source

        pages_resource, pdfs_resource = create_subject_source(
            subject="mathematics",
            cycle="senior_cycle",
            language="en",
        )

        assert pages_resource is not None
        assert pdfs_resource is not None
        assert pages_resource.name == "mathematics_pages"
        assert pdfs_resource.name == "mathematics_pdfs"


# ===========================================================================
# Base Functions Tests
# ===========================================================================


class TestBaseSubjectFunctions:
    """Tests for base subject crawl functions."""

    def test_crawl_subject_no_api_key(self) -> None:
        """Test crawl_subject returns error page when no API key."""
        from cianfhoghlaim.dlt.british_isles.ireland.education.subjects.base import crawl_subject

        with patch.dict(os.environ, {"FIRECRAWL_API_KEY": ""}, clear=False):
            results = list(crawl_subject("mathematics", "senior_cycle", "en"))

        # Should return CrawledPage objects with error status
        assert len(results) >= 1
        # CrawledPage objects have .status attribute
        assert results[0].status == "no_api_key"
        assert results[0].subject == "mathematics"

    def test_extract_pdfs_no_api_key(self) -> None:
        """Test extract_pdfs_from_subject returns empty when no API key."""
        from cianfhoghlaim.dlt.british_isles.ireland.education.subjects.base import extract_pdfs_from_subject

        with patch.dict(os.environ, {"FIRECRAWL_API_KEY": ""}, clear=False):
            results = list(extract_pdfs_from_subject("mathematics", "senior_cycle", "en"))

        # PDFs are only extracted from successful crawls, so empty when no API key
        assert len(results) == 0

    def test_crawled_page_dataclass(self) -> None:
        """Test CrawledPage dataclass."""
        from cianfhoghlaim.dlt.british_isles.ireland.education.subjects.base import CrawledPage, compute_content_hash

        content = "# Mathematics\n\nContent here"
        page = CrawledPage(
            url="https://curriculumonline.ie/Senior-Cycle/Mathematics",
            title="Mathematics",
            content=content,
            content_hash=compute_content_hash(content),
            cycle="senior_cycle",
            subject="mathematics",
            language="en",
            source="curriculumonline",
            document_type="specification",
        )

        data = page.to_dict()
        assert data["url"] == "https://curriculumonline.ie/Senior-Cycle/Mathematics"
        assert data["subject"] == "mathematics"
        assert data["cycle"] == "senior_cycle"
        assert data["content_hash"] == compute_content_hash(content)
        assert "crawled_at" in data

    def test_pdf_resource_dataclass(self) -> None:
        """Test PDFResource dataclass."""
        from cianfhoghlaim.dlt.british_isles.ireland.education.subjects.base import PDFResource

        pdf = PDFResource(
            url="https://curriculumonline.ie/docs/math_spec.pdf",
            cycle="senior_cycle",
            subject="mathematics",
            language="en",
            source="curriculumonline",
            document_type="specification",
        )

        data = pdf.to_dict()
        assert data["url"] == "https://curriculumonline.ie/docs/math_spec.pdf"
        assert data["document_type"] == "specification"
        assert data["source"] == "curriculumonline"
        assert "discovered_at" in data


# ===========================================================================
# Examinations Source Tests
# ===========================================================================


class TestExaminationsSource:
    """Tests for SEC examinations DLT source."""

    def test_examinations_source_creation(self) -> None:
        """Test examinations source can be created."""
        from cianfhoghlaim.dlt.british_isles.ireland.education.sec_examinations_browser import (
            sec_examinations_browser_source,
        )

        source = sec_examinations_browser_source(
            subjects=["mathematics"],
            years=[2024],
        )
        assert source is not None
        assert source.name == "sec_examinations_browser"

    def test_examinations_resources(self) -> None:
        """Test examinations source has expected resources."""
        from cianfhoghlaim.dlt.british_isles.ireland.education.sec_examinations_browser import (
            sec_examinations_browser_source,
        )

        source = sec_examinations_browser_source(
            subjects=["mathematics"],
            years=[2024],
        )
        resource_names = [r.name for r in source.resources.values()]

        assert "exam_papers" in resource_names
        assert "marking_schemes" in resource_names
        assert "examiner_reports" in resource_names

    def test_leaving_certificate_source(self) -> None:
        """Test Leaving Certificate convenience source."""
        from cianfhoghlaim.dlt.british_isles.ireland.education._examinations_helpers import leaving_certificate_source

        source = leaving_certificate_source(
            subjects=["mathematics", "english"],
            years=[2023, 2024],
        )
        assert source is not None

    def test_junior_cycle_exams_source(self) -> None:
        """Test Junior Cycle exams convenience source."""
        from cianfhoghlaim.dlt.british_isles.ireland.education._examinations_helpers import junior_cycle_exams_source

        source = junior_cycle_exams_source(
            subjects=["mathematics"],
            years=[2024],
        )
        assert source is not None


# ===========================================================================
# Mock Firecrawl Tests
# ===========================================================================


class TestMockFirecrawlIntegration:
    """Tests with mocked Firecrawl responses."""

    @pytest.fixture
    def mock_firecrawl_app(self) -> MagicMock:
        """Create a mock FirecrawlApp for v2 API."""
        mock = MagicMock()

        # Mock the crawl() method to return a CrawlJob-like response
        mock_crawl_result = MagicMock()
        mock_crawl_result.data = [
            {
                "markdown": "# Mathematics\n\nLearning outcomes...",
                "html": "<h1>Mathematics</h1>",
                "links": [
                    "https://curriculumonline.ie/docs/math_spec.pdf",
                    "https://curriculumonline.ie/docs/math_guide.pdf",
                ],
                "metadata": {
                    "url": "https://curriculumonline.ie/Senior-Cycle/Mathematics",
                    "title": "Mathematics - Leaving Certificate",
                    "description": "Mathematics curriculum specification",
                    "language": "en",
                },
            }
        ]
        mock.crawl.return_value = mock_crawl_result
        return mock

    def test_crawl_subject_with_mock(self, mock_firecrawl_app: MagicMock) -> None:
        """Test crawl_subject with mocked Firecrawl."""
        from cianfhoghlaim.dlt.british_isles.ireland.education.subjects.base import crawl_subject

        with patch.dict(os.environ, {"FIRECRAWL_API_KEY": "test_key"}):
            # FirecrawlApp is imported inside the function from firecrawl module
            with patch(
                "firecrawl.FirecrawlApp",
                return_value=mock_firecrawl_app,
            ):
                results = list(crawl_subject("mathematics", "senior_cycle", "en"))

        assert len(results) >= 1
        # With mock, should get success - results are CrawledPage objects
        assert any(r.status == "success" for r in results)

    def test_extract_pdfs_with_mock(self, mock_firecrawl_app: MagicMock) -> None:
        """Test extract_pdfs_from_subject with mocked Firecrawl."""
        from cianfhoghlaim.dlt.british_isles.ireland.education.subjects.base import extract_pdfs_from_subject

        with patch.dict(os.environ, {"FIRECRAWL_API_KEY": "test_key"}):
            # FirecrawlApp is imported inside the function from firecrawl module
            with patch(
                "firecrawl.FirecrawlApp",
                return_value=mock_firecrawl_app,
            ):
                results = list(extract_pdfs_from_subject("mathematics", "senior_cycle", "en"))

        # Should find PDFs from the mock response - results are PDFResource objects
        pdf_urls = [r.url for r in results if r.url.endswith(".pdf")]
        assert len(pdf_urls) >= 1


# ===========================================================================
# DLT Pipeline Integration Tests
# ===========================================================================


@pytest.mark.integration
class TestDLTPipelineIntegration:
    """Integration tests for DLT pipeline execution."""

    def test_run_single_subject_pipeline(self, dlt_pipeline: Any, temp_dir: Path) -> None:
        """Test running a pipeline with a single subject."""
        import dlt

        # Create a mock source that yields test data
        @dlt.source(name="test_curriculum")
        def test_source():
            @dlt.resource(name="mathematics_pages", write_disposition="replace")
            def mathematics_pages():
                yield {
                    "url": "https://curriculumonline.ie/test",
                    "subject": "mathematics",
                    "cycle": "senior_cycle",
                    "language": "en",
                    "title": "Test Mathematics",
                    "markdown": "# Test content",
                    "status": "success",
                }

            return mathematics_pages

        info = dlt_pipeline.run(test_source())

        assert info is not None
        assert info.has_failed_jobs is False

    def test_run_examinations_pipeline(self, dlt_pipeline: Any, temp_dir: Path) -> None:
        """Test running examinations pipeline with mock data."""
        import dlt

        @dlt.source(name="test_examinations")
        def test_source():
            @dlt.resource(name="exam_papers", write_disposition="replace")
            def exam_papers():
                yield {
                    "subject": "mathematics",
                    "year": 2024,
                    "level": "leaving_certificate",
                    "material_type": "paper",
                    "pdf_url": "https://examinations.ie/test.pdf",
                    "paper_number": 1,
                    "exam_level": "Higher",
                }

            return exam_papers

        info = dlt_pipeline.run(test_source())

        assert info is not None
        assert info.has_failed_jobs is False


# ===========================================================================
# BAML Schema Tests
# ===========================================================================


class TestBAMLSchemas:
    """Tests for BAML schema loading."""

    def test_curriculum_extraction_schema_exists(self) -> None:
        """Test curriculum_extraction.baml can be loaded."""
        baml_path = Path(__file__).parent.parent.parent / "baml_src" / "curriculum_extraction.baml"
        assert baml_path.exists(), f"BAML schema not found at {baml_path}"

    def test_baml_schema_contains_learning_outcome(self) -> None:
        """Test BAML schema contains LearningOutcome class."""
        baml_path = Path(__file__).parent.parent.parent / "baml_src" / "curriculum_extraction.baml"
        content = baml_path.read_text()

        assert "class EnhancedLearningOutcome" in content
        assert "class CurriculumSpecification" in content
        assert "class ExamPaper" in content


# ===========================================================================
# CocoIndex Flow Tests
# ===========================================================================


class TestCocoIndexFlows:
    """Tests for CocoIndex flow definitions."""

    def test_curriculum_extraction_flow_exists(self) -> None:
        """Test curriculum extraction flow module exists."""
        flow_path = (
            Path(__file__).parent.parent.parent
            / "cocoindex_flows"
            / "curriculum_specification_extraction.py"
        )
        assert flow_path.exists(), f"CocoIndex flow not found at {flow_path}"

    def test_flow_imports(self) -> None:
        """Test CocoIndex flow can be imported."""
        try:
            from cocoindex_flows.curriculum_specification_extraction import (
                CurriculumSpecificationFlow,
                ExamPaperExtractionFlow,
            )

            assert CurriculumSpecificationFlow is not None
            assert ExamPaperExtractionFlow is not None
        except ImportError as e:
            pytest.skip(f"CocoIndex flow import failed: {e}")
