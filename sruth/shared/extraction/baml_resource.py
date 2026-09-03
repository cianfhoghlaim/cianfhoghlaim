"""BAML Extraction Resource for type-safe structured extraction.

Provides type-safe extraction using BAML schemas defined in baml_src/.

Available Extractors (from oideachas.baml):
- ExtractSyllabus: Curriculum specification extraction
- ExtractExamPaper: Exam paper structure extraction
- ExtractMarkingScheme: Marking scheme extraction
- BuildCurriculumGraph: Concept graph from syllabi
- ExtractCelticLanguageContent: Celtic language educational content
- ExtractExamMaterialsList: SEC archive metadata extraction

Usage:
    @asset(resource_defs={"baml": baml_resource()})
    async def extract_syllabus(baml: BAMLExtractionResource, pdf_text: str):
        result = await baml.extract_syllabus(pdf_text, metadata={"subject": "Chemistry"})
        return result
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, TypeVar, Generic

import dagster as dg
import structlog

try:
    from pydantic import Field
except ImportError:
    from dagster import Field

logger = structlog.get_logger(__name__)

T = TypeVar("T")


@dataclass
class BAMLExtractionResult(Generic[T]):
    """Result of BAML extraction."""

    data: T
    schema_name: str
    model_used: str
    tokens_used: int
    validation_passed: bool = True
    success: bool = True
    error: str | None = None
    raw_response: str | None = None


class BAMLExtractionResource(dg.ConfigurableResource):
    """Type-safe extraction using BAML schemas.

    Wraps BAML-generated clients to provide Dagster resource interface
    for curriculum document extraction.

    Schemas (from baml_src/oideachas.baml):
    - SyllabusExtraction: Subject specs, learning outcomes, assessment
    - ExamPaperExtraction: Paper structure, questions, sections
    - MarkingSchemeExtraction: Mark allocation, acceptable answers
    - CurriculumGraph: Concept relationships across syllabi
    - CelticLanguageContent: Vocabulary, grammar, cultural context
    - ExamMaterialMetadata: SEC archive listings

    Example:
        @asset(resource_defs={"baml": baml_resource()})
        async def extract_curriculum(baml: BAMLExtractionResource):
            with open("syllabus.pdf", "rb") as f:
                text = pdf_to_text(f.read())

            result = await baml.extract_syllabus(
                text,
                metadata={"subject": "Chemistry", "level": "SeniorCycle"}
            )

            if result.success:
                return result.data
            else:
                raise Exception(result.error)
    """

    # BAML configuration
    schema_path: str = Field(
        default_factory=lambda: os.getenv("BAML_SCHEMA_PATH", "./baml_src"),
        description="Path to BAML schema directory",
    )

    # Default client (from BAML config)
    default_client: str = Field(
        default="Claude",
        description="Default BAML client to use",
    )

    # LiteLLM fallback
    use_litellm_fallback: bool = Field(
        default=True,
        description="Use LiteLLM when BAML client unavailable",
    )

    litellm_base_url: str = Field(
        default_factory=lambda: os.getenv("LITELLM_BASE_URL", "http://localhost:4000"),
        description="LiteLLM base URL for fallback",
    )

    litellm_model: str = Field(
        default="extract",
        description="LiteLLM model for extraction fallback",
    )

    # Request configuration
    max_tokens: int = Field(
        default=8192,
        description="Maximum tokens for extraction response",
    )

    temperature: float = Field(
        default=0.0,
        description="Temperature (0 for deterministic extraction)",
    )

    timeout: float = Field(
        default=120.0,
        description="Request timeout in seconds",
    )

    def _get_baml_client(self) -> Any:
        """Get BAML client (lazy import).

        Returns:
            BAML client module or None if not available
        """
        try:
            from baml_client import b
            return b
        except ImportError:
            logger.warning(
                "baml_client_not_available",
                message="Install: pip install baml-py && baml-cli generate",
            )
            return None

    async def _fallback_extract(
        self,
        content: str,
        schema_name: str,
        schema_hint: dict[str, Any] | None = None,
        metadata: str | None = None,
    ) -> tuple[dict[str, Any], int]:
        """Fallback extraction using LiteLLM when BAML unavailable.

        Args:
            content: Document content
            schema_name: Name of target schema
            schema_hint: Optional schema definition
            metadata: Additional metadata

        Returns:
            Tuple of (extracted_data, tokens_used)
        """
        import json

        try:
            import litellm
        except ImportError:
            raise ImportError("litellm required for fallback extraction")

        # Build prompt based on schema
        prompts = {
            "SyllabusExtraction": (
                "Extract structured syllabus information including: "
                "subject_name, level, aims, objectives, learning_outcomes, "
                "strands, assessment components, prerequisites."
            ),
            "ExamPaperExtraction": (
                "Extract exam paper structure including: "
                "subject, level, year, duration, total_marks, "
                "sections with questions, topics covered."
            ),
            "MarkingSchemeExtraction": (
                "Extract marking scheme including: "
                "subject, level, year, mark allocations per question, "
                "acceptable answers, examiner notes."
            ),
            "CelticLanguageContent": (
                "Extract Celtic language educational content including: "
                "vocabulary, grammar points, cultural references, "
                "pronunciation notes, CEFR level."
            ),
            "ExamMaterialMetadata": (
                "Extract exam material metadata including: "
                "subject, year, level, material_type, pdf_url, "
                "language, paper_number."
            ),
        }

        prompt = prompts.get(schema_name, f"Extract structured data as {schema_name}")

        if metadata:
            prompt += f"\n\nMetadata: {metadata}"

        prompt += f"\n\nContent:\n{content}\n\nReturn valid JSON."

        response = await litellm.acompletion(
            model=self.litellm_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            timeout=self.timeout,
            api_base=self.litellm_base_url,
            response_format={"type": "json_object"},
        )

        text = response.choices[0].message.content
        tokens = response.usage.total_tokens if response.usage else 0

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            import re
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                data = json.loads(match.group())
            else:
                data = {"raw_text": text}

        return data, tokens

    async def extract_syllabus(
        self,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> BAMLExtractionResult[Any]:
        """Extract curriculum syllabus structure.

        Extracts:
        - Subject identification (name, code, level, area)
        - Aims and objectives
        - Learning outcomes with strand organization
        - Assessment structure and weightings
        - Prerequisites and recommended hours

        Args:
            content: Document text content
            metadata: Additional context (subject, level, etc.)

        Returns:
            BAMLExtractionResult with SyllabusExtraction data
        """
        baml = self._get_baml_client()
        metadata_str = str(metadata) if metadata else ""

        try:
            if baml:
                result = await baml.ExtractSyllabus(content, metadata_str)
                return BAMLExtractionResult(
                    data=result,
                    schema_name="SyllabusExtraction",
                    model_used=self.default_client,
                    tokens_used=0,  # BAML doesn't expose token count
                    validation_passed=True,
                    success=True,
                )
            else:
                data, tokens = await self._fallback_extract(
                    content, "SyllabusExtraction", metadata=metadata_str
                )
                return BAMLExtractionResult(
                    data=data,
                    schema_name="SyllabusExtraction",
                    model_used=self.litellm_model,
                    tokens_used=tokens,
                    validation_passed=False,  # Not validated by BAML
                    success=True,
                )

        except Exception as e:
            logger.error("syllabus_extraction_failed", error=str(e))
            return BAMLExtractionResult(
                data={},
                schema_name="SyllabusExtraction",
                model_used="none",
                tokens_used=0,
                validation_passed=False,
                success=False,
                error=str(e),
            )

    async def extract_exam_paper(
        self,
        content: str,
    ) -> BAMLExtractionResult[Any]:
        """Extract exam paper structure.

        Extracts:
        - Paper identification (subject, level, year, session)
        - Duration and total marks
        - Sections with questions and marks
        - Topics covered and skills tested

        Args:
            content: Exam paper text content

        Returns:
            BAMLExtractionResult with ExamPaperExtraction data
        """
        baml = self._get_baml_client()

        try:
            if baml:
                result = await baml.ExtractExamPaper(content)
                return BAMLExtractionResult(
                    data=result,
                    schema_name="ExamPaperExtraction",
                    model_used=self.default_client,
                    tokens_used=0,
                    validation_passed=True,
                    success=True,
                )
            else:
                data, tokens = await self._fallback_extract(
                    content, "ExamPaperExtraction"
                )
                return BAMLExtractionResult(
                    data=data,
                    schema_name="ExamPaperExtraction",
                    model_used=self.litellm_model,
                    tokens_used=tokens,
                    validation_passed=False,
                    success=True,
                )

        except Exception as e:
            logger.error("exam_paper_extraction_failed", error=str(e))
            return BAMLExtractionResult(
                data={},
                schema_name="ExamPaperExtraction",
                model_used="none",
                tokens_used=0,
                validation_passed=False,
                success=False,
                error=str(e),
            )

    async def extract_marking_scheme(
        self,
        content: str,
    ) -> BAMLExtractionResult[Any]:
        """Extract marking scheme structure.

        Extracts:
        - Subject, level, year
        - Mark allocations per question
        - Marking points and alternatives
        - Common errors and examiner comments

        Args:
            content: Marking scheme text content

        Returns:
            BAMLExtractionResult with MarkingSchemeExtraction data
        """
        baml = self._get_baml_client()

        try:
            if baml:
                result = await baml.ExtractMarkingScheme(content)
                return BAMLExtractionResult(
                    data=result,
                    schema_name="MarkingSchemeExtraction",
                    model_used=self.default_client,
                    tokens_used=0,
                    validation_passed=True,
                    success=True,
                )
            else:
                data, tokens = await self._fallback_extract(
                    content, "MarkingSchemeExtraction"
                )
                return BAMLExtractionResult(
                    data=data,
                    schema_name="MarkingSchemeExtraction",
                    model_used=self.litellm_model,
                    tokens_used=tokens,
                    validation_passed=False,
                    success=True,
                )

        except Exception as e:
            logger.error("marking_scheme_extraction_failed", error=str(e))
            return BAMLExtractionResult(
                data={},
                schema_name="MarkingSchemeExtraction",
                model_used="none",
                tokens_used=0,
                validation_passed=False,
                success=False,
                error=str(e),
            )

    async def extract_celtic_content(
        self,
        content: str,
        language: str = "ga",
    ) -> BAMLExtractionResult[Any]:
        """Extract Celtic language educational content.

        Extracts:
        - Vocabulary and terminology
        - Grammar points and structures
        - Cultural and historical context
        - Pronunciation and orthography notes
        - CEFR level mapping

        Args:
            content: Document text content
            language: Target language ("ga", "cy", "gd")

        Returns:
            BAMLExtractionResult with CelticLanguageContent data
        """
        baml = self._get_baml_client()

        try:
            if baml:
                result = await baml.ExtractCelticLanguageContent(content, language)
                return BAMLExtractionResult(
                    data=result,
                    schema_name="CelticLanguageContent",
                    model_used=self.default_client,
                    tokens_used=0,
                    validation_passed=True,
                    success=True,
                )
            else:
                data, tokens = await self._fallback_extract(
                    content,
                    "CelticLanguageContent",
                    metadata=f"language: {language}",
                )
                return BAMLExtractionResult(
                    data=data,
                    schema_name="CelticLanguageContent",
                    model_used=self.litellm_model,
                    tokens_used=tokens,
                    validation_passed=False,
                    success=True,
                )

        except Exception as e:
            logger.error("celtic_content_extraction_failed", error=str(e))
            return BAMLExtractionResult(
                data={},
                schema_name="CelticLanguageContent",
                model_used="none",
                tokens_used=0,
                validation_passed=False,
                success=False,
                error=str(e),
            )

    async def extract_exam_materials_list(
        self,
        results_page: str,
    ) -> BAMLExtractionResult[list[Any]]:
        """Extract exam materials metadata from SEC archive page.

        Extracts list of:
        - Subject, year, level
        - Material type (paper, marking_scheme, examiner_report)
        - PDF URL and title
        - Language and paper number

        Args:
            results_page: HTML content of SEC archive results page

        Returns:
            BAMLExtractionResult with list of ExamMaterialMetadata
        """
        baml = self._get_baml_client()

        try:
            if baml:
                result = await baml.ExtractExamMaterialsList(results_page)
                return BAMLExtractionResult(
                    data=result,
                    schema_name="ExamMaterialMetadata[]",
                    model_used=self.default_client,
                    tokens_used=0,
                    validation_passed=True,
                    success=True,
                )
            else:
                data, tokens = await self._fallback_extract(
                    results_page, "ExamMaterialMetadata"
                )
                # Ensure we have a list
                if isinstance(data, dict) and "materials" in data:
                    data = data["materials"]
                elif not isinstance(data, list):
                    data = [data]

                return BAMLExtractionResult(
                    data=data,
                    schema_name="ExamMaterialMetadata[]",
                    model_used=self.litellm_model,
                    tokens_used=tokens,
                    validation_passed=False,
                    success=True,
                )

        except Exception as e:
            logger.error("exam_materials_extraction_failed", error=str(e))
            return BAMLExtractionResult(
                data=[],
                schema_name="ExamMaterialMetadata[]",
                model_used="none",
                tokens_used=0,
                validation_passed=False,
                success=False,
                error=str(e),
            )

    async def build_curriculum_graph(
        self,
        syllabi: list[Any],
    ) -> BAMLExtractionResult[Any]:
        """Build concept graph from multiple syllabi.

        Creates:
        - Concept nodes with subject, level, strand
        - Prerequisite and extension relationships
        - Cross-subject connections
        - Bottleneck and foundation concepts

        Args:
            syllabi: List of SyllabusExtraction objects

        Returns:
            BAMLExtractionResult with CurriculumGraph data
        """
        baml = self._get_baml_client()

        try:
            if baml:
                result = await baml.BuildCurriculumGraph(syllabi)
                return BAMLExtractionResult(
                    data=result,
                    schema_name="CurriculumGraph",
                    model_used=self.default_client,
                    tokens_used=0,
                    validation_passed=True,
                    success=True,
                )
            else:
                import json
                syllabi_str = json.dumps(
                    [s if isinstance(s, dict) else s.__dict__ for s in syllabi]
                )
                data, tokens = await self._fallback_extract(
                    syllabi_str, "CurriculumGraph"
                )
                return BAMLExtractionResult(
                    data=data,
                    schema_name="CurriculumGraph",
                    model_used=self.litellm_model,
                    tokens_used=tokens,
                    validation_passed=False,
                    success=True,
                )

        except Exception as e:
            logger.error("curriculum_graph_build_failed", error=str(e))
            return BAMLExtractionResult(
                data={},
                schema_name="CurriculumGraph",
                model_used="none",
                tokens_used=0,
                validation_passed=False,
                success=False,
                error=str(e),
            )

    def classify_document_type(
        self,
        content: str,
    ) -> str:
        """Classify document type for routing to correct extractor.

        Args:
            content: First ~1000 chars of document

        Returns:
            Document type: "syllabus", "exam_paper", "marking_scheme",
            "examiner_report", "guidelines", "unknown"
        """
        content_lower = content.lower()[:2000]

        # Check for syllabus/specification indicators
        if any(term in content_lower for term in [
            "learning outcome", "strand", "curriculum",
            "specification", "syllabus", "aims and objectives",
            "siollabas", "curaclam", "torthaí foghlama",
        ]):
            return "syllabus"

        # Check for exam paper indicators
        if any(term in content_lower for term in [
            "leaving certificate", "junior certificate",
            "section a", "answer all questions", "total marks",
            "ardteistiméireacht", "scrúdú", "freagair gach ceist",
        ]):
            return "exam_paper"

        # Check for marking scheme indicators
        if any(term in content_lower for term in [
            "marking scheme", "mark allocation", "examiner",
            "scéim marcála", "leithdháileadh marcanna",
        ]):
            return "marking_scheme"

        # Check for examiner report
        if any(term in content_lower for term in [
            "examiner report", "chief examiner", "candidate performance",
            "tuairisc an scrúdaitheora",
        ]):
            return "examiner_report"

        # Check for guidelines
        if any(term in content_lower for term in [
            "guidelines", "teacher", "notes for",
            "treoirlínte", "nótaí do mhúinteoirí",
        ]):
            return "guidelines"

        return "unknown"


# Resource factory function
def baml_resource(**kwargs) -> BAMLExtractionResource:
    """Factory for BAML extraction resource.

    Usage:
        @asset(resource_defs={"baml": baml_resource()})
        async def extract_curriculum(baml: BAMLExtractionResource):
            result = await baml.extract_syllabus(content)
            return result.data
    """
    return BAMLExtractionResource(**kwargs)
