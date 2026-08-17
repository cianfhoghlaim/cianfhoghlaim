"""LC Applied Mathematics Agent — the per-subject agent for Ireland LC Applied Mathematics.

Per the 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1 change
(Phase 8 - 60 per-subject agents).
"""

from __future__ import annotations

import logging
from typing import Any

from ..litellm_agent import litellm_model
from .base import SubjectAgentBase

logger = logging.getLogger(__name__)


# The canonical 13 CopilotKit actions for the Applied Mathematics agent
APPLIED_MATHEMATICS_ACTIONS = [
    "get_syllabus_topics",
    "get_exam_papers",
    "get_marking_schemes",
    "get_topic_detail",
    "get_cross_jurisdictional_equivalences",
    "semantic_search",
    "extract_syllabus_from_pdf",
    "save_annotation",
    "track_progress",
    "get_study_plan",
    "compare_curricula",
    "get_glossary_term",
    "extract_learning_outcome",
]


# The canonical Applied Mathematics agent config
applied_mathematics_agent = SubjectAgentBase(
    stage="lc",
    subject="applied_mathematics",
    display_name="Applied Mathematics",
    ncca_code="LC-APM-LO",
    spec_code="",
    languages=("en", "ga"),
    board="",
    baml_function="ExtractCurriculumSyllabus(text, subject='applied_mathematics')",
    cocoindex_app="ireland_lc_applied_mathematics_untiered_en_embedding",
    notebook_path="notebooks/lc/applied_mathematics.py",
    web_integration={
        "app": "cianfhoghlaim",
        "route": "/lc/applied_mathematics",
        "subject_agent_cards": True,
        "homepage_chat_routing": True,
    },
)


__all__ = ["applied_mathematics_agent", "APPLIED_MATHEMATICS_ACTIONS"]
