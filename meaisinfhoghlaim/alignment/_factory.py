"""Canonical alignment factory (Plan 3 + Plan 2).

Per the 2026-08-15-meaisinfoghlaim-ireland-england-roadmap.

The factory pattern: ``build_alignment(jurisdiction, stage, subject, board) -> Alignment``
mirrors the canonical dlt_sources ``_factory.py`` pattern. Used to construct
the right alignment collaborator per cohort.

Generalisable: same factory works for Scotland / Wales / NI /
Jersey / Guernsey / IoM rollouts.
"""

from __future__ import annotations

from typing import Any

from meaisinfoghlaim.alignment.bilingual_concept_registry import BilingualConceptRegistry
from meaisinfoghlaim.alignment.bilingual_extraction import BilingualExtractionOrchestrator
from meaisinfoghlaim.alignment.bilingual_topic_graph_edges import BilingualTopicGraphEdgeEmitter
from meaisinfoghlaim.alignment.board_diff import BoardDiffer
from meaisinfoghlaim.alignment.cross_jurisdiction_diff import CrossJurisdictionDiffer
from meaisinfoghlaim.alignment.cross_qualification_gap_analysis import CrossQualificationGapAnalyzer
from meaisinfoghlaim.alignment.cross_qualification_search import CrossQualificationSearcher
from meaisinfoghlaim.alignment.cross_qualification_subject_map import (
    CrossQualificationSubjectMap,
)
from meaisinfoghlaim.alignment.cross_qualification_topic_alignment import (
    CrossQualificationTopicAligner,
)
from meaisinfoghlaim.alignment.diagram_indexer import DiagramIndexer
from meaisinfoghlaim.alignment.exam_marking_alignment import ExamMarkingAligner
from meaisinfoghlaim.alignment.qualification_normalizer import QualificationNormalizer
from meaisinfoghlaim.alignment.topic_graph import (
    BilingualTopicGraphBuilder,
    TopicGraphBuilder,
)
from meaisinfoghlaim.evaluation.bilingual_coverage_audit import BilingualCoverageAuditor
from meaisinfoghlaim.evaluation.cross_qualification_gap_analysis_runtime import (
    CrossQualificationGapAnalyzerRuntime,
)
from meaisinfoghlaim.evaluation.diff_reporter import DiffReporter
from meaisinfoghlaim.evaluation.regression_baseline import (
    RegressionBaselineStore,
)


def build_alignment(jurisdiction: str, stage: str, subject: str, board=None) -> dict[str, Any]:
    """Build the canonical alignment collaborator set for a cohort.

    Args:
        jurisdiction: e.g. 'ireland', 'england', 'scotland'
        stage: e.g. 'lc', 'gcse', 'a_level'
        subject: e.g. 'mathematics', 'chemistry'
        board: e.g. 'aqa', 'ocr', 'edexcel', 'ccea'

    Returns:
        dict mapping collaborator name -> instance (TopicGraphBuilder,
        BilingualTopicGraphBuilder, ExamMarkingAligner, etc.)
    """
    # All collaborators are stateless beyond internal state
    # (the registry, emitter, etc. each have their own caches).
    return {
        "topic_graph_builder": TopicGraphBuilder(),
        "bilingual_topic_graph_builder": BilingualTopicGraphBuilder(),
        "exam_marking_aligner": ExamMarkingAligner(),
        "diagram_indexer": DiagramIndexer(),
        "extract_cross_linguistic_handler": None,  # BAML handler is lazy-loaded
        "bilingual_concept_registry": BilingualConceptRegistry(),
        "bilingual_extraction_orchestrator": BilingualExtractionOrchestrator(),
        "bilingual_topic_edge_emitter": BilingualTopicGraphEdgeEmitter(),
        "bilingual_coverage_auditor": BilingualCoverageAuditor(),
        "qualification_normalizer": QualificationNormalizer(),
        "board_differ": BoardDiffer(),
        "cross_jurisdiction_differ": CrossJurisdictionDiffer(),
        "cross_qualification_subject_map": CrossQualificationSubjectMap(),
        "cross_qualification_topic_aligner": CrossQualificationTopicAligner(),
        "cross_qualification_searcher": CrossQualificationSearcher(),
        "cross_qualification_gap_analyzer_runtime": CrossQualificationGapAnalyzerRuntime(),
        "regression_baseline_store": RegressionBaselineStore(),
        "diff_reporter": DiffReporter(),
        "cohort": {
            "jurisdiction": jurisdiction,
            "stage": stage,
            "subject": subject,
            "board": board,
        },
    }


__all__ = ["build_alignment"]
