"""England BAML extraction package (BIEP v2).

Re-exports the 5 BAML extraction functions for the England pipeline
(per the 2026-07-21-biep-v2-england-aqa-ocr-baml-pipeline-v1 change).

The canonical BAML files are at:
    baml_src/british_isles/england/education/{curriculum_syllabus,exam_paper_layout,marking_scheme,subject_taxonomy,ensembled_extraction}.baml
"""
from __future__ import annotations

try:
    from cianfhoghlaim.baml_client.types import (  # type: ignore[import-not-found]
        AQAQualSpec as _AQAQualSpec,
        OCRQualSpec as _OCRQualSpec,
        EdexcelQualSpec as _EdexcelQualSpec,
        AQAExamPaper as _AQAExamPaper,
        AQAMarkingScheme as _AQAMarkingScheme,
        EnsembleConsensus as _EnsembleConsensus,
        EnsemblePathOutput as _EnsemblePathOutput,
        ExamBoard as _ExamBoard,
        QualificationLevel as _QualificationLevel,
        GCSEAQASubject as _GCSEAQASubject,
        ALevelAQASubject as _ALevelAQASubject,
        AssessmentObjective as _AssessmentObjective,
        UKExamSection as _UKExamSection,
        UKQuestion as _UKQuestion,
        GradeBoundary as _GradeBoundary,
        UKQuestionType as _UKQuestionType,
    )
    __all__ = [
        "AQAQualSpec",
        "OCRQualSpec",
        "EdexcelQualSpec",
        "AQAExamPaper",
        "AQAMarkingScheme",
        "EnsembleConsensus",
        "EnsemblePathOutput",
        "ExamBoard",
        "QualificationLevel",
        "GCSEAQASubject",
        "ALevelAQASubject",
        "AssessmentObjective",
        "UKExamSection",
        "UKQuestion",
        "GradeBoundary",
        "UKQuestionType",
    ]
except ImportError:
    __all__: list[str] = []
