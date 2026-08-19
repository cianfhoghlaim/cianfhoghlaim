"""Canonical extraction dataset factory (Plan 4).

Per the 2026-08-15-meaisinfoghlaim-ireland-england-roadmap (Plan 4).

build_extraction_dataset(jurisdiction, stage, subject, board, language, year)
-> DatasetConfig

Mirrors the dlt_sources/british_isles/ireland/education/junior_cycle_subjects/
_factory.py pattern. Generates the canonical extraction config for a
single (jurisdiction, stage, subject, board, language, year) cohort:

  - Looks up the cohort in the CohortRegistry (Plan 4 module 2)
  - Resolves the syllabus + exam PDF URLs (BIEP v3 source URLs)
  - Determines the dlt source module + the BAML functions to invoke
  - Sets the RAGAS + bilingual coverage thresholds (defaults: 0.95 each)

Generalisable: same factory works for Scotland / Wales / NI / Jersey /
Guernsey / IoM rollouts.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Iterable

from meaisinfhoghlaim.alignment.schema import (
    Board,
    CohortRow,
    DatasetConfig,
    LanguagePair,
    QualificationLevel,
)
from meaisinfhoghlaim.datasets.cohort_registry import CohortRegistry

logger = logging.getLogger(__name__)


# The canonical BAML function set per (stage, jurisdiction) tuple.
# Per the BIEP v3 spec, each cohort runs a canonical extraction path.
_BAML_FUNCTIONS_PER_STAGE: dict = {
    (QualificationLevel.LC, "ireland"): [
        "ExtractCurriculumSyllabus",
        "ExtractExamPaperLayout",
        "ExtractMarkingSchemeGuideline",
        "ExtractCrossLinguisticConcept",
        "ExtractSyllabusDiagram",
    ],
    (QualificationLevel.GCSE, "england"): [
        "ExtractUKQualSpec",  # the generic England BAML function
        "ExtractCurriculumSyllabus",
        "ExtractExamPaperLayout",
        "ExtractMarkingSchemeGuideline",
    ],
    (QualificationLevel.A_LEVEL, "england"): [
        "ExtractUKQualSpec",
        "ExtractCurriculumSyllabus",
        "ExtractExamPaperLayout",
        "ExtractMarkingSchemeGuideline",
    ],
    (QualificationLevel.JC, "ireland"): [
        "ExtractCurriculumSyllabus",
        "ExtractExamPaperLayout",
        "ExtractCrossLinguisticConcept",
    ],
    # Scotland + Wales + NI fallbacks (Plan 4 generalisable)
    (QualificationLevel.NATIONAL_5, "scotland"): ["ExtractUKQualSpec"],
    (QualificationLevel.HIGHER, "scotland"): ["ExtractUKQualSpec"],
    (QualificationLevel.ADVANCED_HIGHER, "scotland"): ["ExtractUKQualSpec"],
}


# The canonical OCR backend per (stage, jurisdiction).
_OCR_BACKEND_PER_STAGE: dict = {
    (QualificationLevel.LC, "ireland"): "paddleocr",
    (QualificationLevel.GCSE, "england"): "docling",
    (QualificationLevel.A_LEVEL, "england"): "olmmocr",
}


def build_extraction_dataset(
    jurisdiction: str,
    stage: str | QualificationLevel,
    subject: str,
    board: str | Board = Board.NONE,
    language: str = "en",
    year: int = 2026,
    cohort_registry: CohortRegistry | None = None,
    ragas_threshold: float = 0.95,
    bilingual_coverage_threshold: float = 0.95,
) -> DatasetConfig:
    """Build the canonical extraction dataset config for a cohort.

    Args:
        jurisdiction: e.g. 'ireland', 'england'
        stage: 'lc' | 'gcse' | 'a_level' | 'jc' | 'national_5' | 'higher' | 'advanced_higher'
        subject: e.g. 'chemistry', 'mathematics'
        board: e.g. 'aqa', 'ocr', 'edexcel', Board.NONE
        language: default 'en'; for Ireland set to 'ga' to get a GA cohort
        year: the extraction target year (default 2026)
        cohort_registry: optional CohortRegistry (defaults to the canonical one)
        ragas_threshold: BIEP v3 faithfulness gate (default 0.95)
        bilingual_coverage_threshold: BIEP v3 bilingual coverage gate (default 0.95)

    Returns:
        DatasetConfig with all the canonical wiring for the cohort
    """
    # 1. Normalize the stage enum
    if isinstance(stage, str):
        stage_enum = QualificationLevel(stage)
    else:
        stage_enum = stage

    # 2. Normalize the board enum
    if isinstance(board, str):
        try:
            board_enum = Board(board)
        except ValueError:
            board_enum = Board.NONE
    else:
        board_enum = board

    # 3. Look up the cohort in the registry (or create a placeholder)
    registry = cohort_registry or CohortRegistry()
    cohort_row = registry.get_or_create(
        jurisdiction=jurisdiction,
        stage=stage_enum,
        subject=subject,
        board=board_enum,
        language=language,
        year=year,
    )

    # 4. Determine the BAML function set
    baml_functions = _BAML_FUNCTIONS_PER_STAGE.get(
        (stage_enum, jurisdiction),
        ["ExtractUKQualSpec"],  # safe default
    )

    # 5. Determine the OCR backend
    ocr_backend = _OCR_BACKEND_PER_STAGE.get(
        (stage_enum, jurisdiction),
        "olmmocr",  # safe default
    )

    # 6. Determine the canonical syllabus + exam PDF URLs
    syllabus_pdf_urls = [
        f"https://ncca.ie/syllabus/{stage_enum.value}-{subject}-{year}.pdf"
        if jurisdiction == "ireland"
        else f"https://www.gov.uk/government/publications/{stage_enum.value}-{subject}-{year}"
    ]
    exam_pdf_urls = [
        f"https://www.examinations.ie/archive/exam-papers/{year}/{subject}_{stage_enum.value}_paper_{i}.pdf"
        if jurisdiction == "ireland"
        else f"https://www.aqa.org.uk/find-past-papers/{subject}/{year}/{stage_enum.value}"
        for i in range(1, 4)  # 3 papers per cohort by default
    ]

    # 7. Determine the canonical dlt source name
    dlt_source_name = (
        f"dlt_sources.british_isles.{jurisdiction}.education."
        f"{stage_enum.value}.{subject}"
    )

    # 8. Bilingual-aware: if language is 'ga' or the registry has a language_pair,
    # add the bilingual extraction pipeline
    if cohort_row.language_pair:
        baml_functions = list(baml_functions) + ["ExtractCrossLinguisticConcept"]

    return DatasetConfig(
        cohort=cohort_row,
        syllabus_pdf_urls=syllabus_pdf_urls,
        exam_pdf_urls=exam_pdf_urls,
        dlt_source_name=dlt_source_name,
        baml_functions=baml_functions,
        parallel_extractions=4,  # BIEP v3 default
        ocr_backend=ocr_backend,
        ragas_threshold=ragas_threshold,
        bilingual_coverage_threshold=bilingual_coverage_threshold,
    )


__all__ = ["build_extraction_dataset", "CohortRow", "DatasetConfig"]
