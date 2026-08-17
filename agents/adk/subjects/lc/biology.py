"""LC Biology Agent — the per-subject agent for Ireland LC Biology.

Per the 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1 change
(Phase 8 - 60 per-subject agents).
"""

from __future__ import annotations

import logging
from typing import Any

from ..litellm_agent import litellm_model
from .base import SubjectAgentBase

logger = logging.getLogger(__name__)


# The canonical 13 CopilotKit actions for the Biology agent
BIOLOGY_ACTIONS = [
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


# The canonical Biology agent config
biology_agent = SubjectAgentBase(
    stage="lc",
    subject="biology",
    display_name="Biology",
    ncca_code="LC-BIO-LO",
    spec_code="",
    languages=("en", "ga"),
    board="",
    baml_function="ExtractCurriculumSyllabus(text, subject='biology')",
    cocoindex_app="ireland_lc_biology_untiered_en_embedding",
    notebook_path="notebooks/lc/biology.py",
    web_integration={
        "app": "cianfhoghlaim",
        "route": "/lc/biology",
        "subject_agent_cards": True,
        "homepage_chat_routing": True,
    },
)


__all__ = ["biology_agent", "BIOLOGY_ACTIONS"]
