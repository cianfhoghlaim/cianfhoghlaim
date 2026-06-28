"""Shared BAML client factory for Agno stage teams.

Provides a singleton BAML sync client and convenience wrappers that
expose BAML functions as Agno-compatible tool callables.
"""
from __future__ import annotations

from functools import lru_cache

from baml_client.runtime import DoNotUseDirectlyCallManager
from baml_client.sync_client import BamlSyncClient


@lru_cache(maxsize=1)
def get_baml_client() -> BamlSyncClient:
    """Return the singleton BAML sync client."""
    return BamlSyncClient(DoNotUseDirectlyCallManager({}))


# ---------------------------------------------------------------------------
# Aistear
# ---------------------------------------------------------------------------
def extract_aistear_framework(text: str, language: str = "en") -> dict:
    """Extract Aistear themes, principles, and learning goals from NCCA framework text."""
    client = get_baml_client()
    result = client.ExtractAistearFramework(text=text, language=language)
    return result.model_dump() if hasattr(result, "model_dump") else result


# ---------------------------------------------------------------------------
# Primary
# ---------------------------------------------------------------------------
def extract_primary_framework(text: str, stage: str, area: str) -> dict:
    """Extract Primary curriculum area details from NCCA framework text."""
    client = get_baml_client()
    result = client.ExtractPrimaryFramework(text=text, stage=stage, area=area)
    return result.model_dump() if hasattr(result, "model_dump") else result


# ---------------------------------------------------------------------------
# Junior Cycle
# ---------------------------------------------------------------------------
def extract_jc_spec(text: str, subject: str) -> dict:
    """Extract Junior Cycle subject specification."""
    client = get_baml_client()
    result = client.ExtractJCSpec(text=text, subject=subject)
    return result.model_dump() if hasattr(result, "model_dump") else result


def extract_cba_descriptor(text: str, task_name: str) -> dict:
    """Extract CBA task descriptor from specification text."""
    client = get_baml_client()
    result = client.ExtractCBADescriptor(text=text, task_name=task_name)
    return result.model_dump() if hasattr(result, "model_dump") else result


# ---------------------------------------------------------------------------
# Senior Cycle
# ---------------------------------------------------------------------------
def extract_curriculum_from_document(document_text: str, subject: str, level: str) -> dict:
    client = get_baml_client()
    result = client.ExtractCurriculumFromDocument(
        document_text=document_text, subject=subject, level=level
    )
    return result.model_dump() if hasattr(result, "model_dump") else result


def extract_exam_paper_structure(document_text: str, subject: str, year: int, level: str, paper_number: int = 1) -> dict:
    client = get_baml_client()
    result = client.ExtractExamPaperStructure(
        document_text=document_text, subject=subject, year=year, level=level, paper_number=paper_number
    )
    return result.model_dump() if hasattr(result, "model_dump") else result


def extract_marking_scheme(document_text: str, subject: str, year: int, level: str) -> dict:
    client = get_baml_client()
    result = client.ExtractMarkingScheme(
        document_text=document_text, subject=subject, year=year, level=level
    )
    return result.model_dump() if hasattr(result, "model_dump") else result


def extract_subject_rubric(subject: str, level: str, exam_years: list[int]) -> dict:
    client = get_baml_client()
    result = client.ExtractSubjectRubric(subject=subject, level=level, exam_years=exam_years)
    return result.model_dump() if hasattr(result, "model_dump") else result


def score_essay_against_rubric(essay_text: str, subject: str, level: str, rubric_text: str) -> dict:
    client = get_baml_client()
    result = client.ScoreEssayAgainstRubric(
        essay_text=essay_text, subject=subject, level=level, rubric_text=rubric_text
    )
    return result.model_dump() if hasattr(result, "model_dump") else result


# ---------------------------------------------------------------------------
# Tertiary
# ---------------------------------------------------------------------------
def extract_cao_course_list(page_markdown: str, year: int) -> list[dict]:
    client = get_baml_client()
    result = client.ExtractCAOCourseList(page_markdown=page_markdown, year=year)
    return result.model_dump() if hasattr(result, "model_dump") else result


def extract_matriculation_rules(page_markdown: str, institution: str) -> list[dict]:
    client = get_baml_client()
    result = client.ExtractMatriculationRules(page_markdown=page_markdown, institution=institution)
    return result.model_dump() if hasattr(result, "model_dump") else result


def audit_matriculation(
    applicant_grades: dict, institution: str, course_code: str
) -> dict:
    client = get_baml_client()
    result = client.AuditMatriculation(
        applicant_grades=applicant_grades, institution=institution, course_code=course_code
    )
    return result.model_dump() if hasattr(result, "model_dump") else result


def extract_application_timeline(page_markdown: str, year: int) -> dict:
    client = get_baml_client()
    result = client.ExtractApplicationTimeline(page_markdown=page_markdown, year=year)
    return result.model_dump() if hasattr(result, "model_dump") else result


def extract_apprenticeship_listings(page_markdown: str) -> list[dict]:
    client = get_baml_client()
    result = client.ExtractApprenticeshipListings(page_markdown=page_markdown)
    return result.model_dump() if hasattr(result, "model_dump") else result


def estimate_course_points(
    course_code: str, historical_points: list[int], applicant_profile: dict
) -> dict:
    client = get_baml_client()
    result = client.EstimateCoursePoints(
        course_code=course_code, historical_points=historical_points, applicant_profile=applicant_profile
    )
    return result.model_dump() if hasattr(result, "model_dump") else result


# ---------------------------------------------------------------------------
# Cross-stage
# ---------------------------------------------------------------------------
def extract_learning_outcome_relationships(
    source_outcome: dict, target_outcomes: list[dict], subject_context: str
) -> dict:
    client = get_baml_client()
    result = client.ExtractLearningOutcomeRelationships(
        source_outcome=source_outcome, target_outcomes=target_outcomes, subject_context=subject_context
    )
    return result.model_dump() if hasattr(result, "model_dump") else result
