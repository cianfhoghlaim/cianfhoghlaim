"""LC Gaeilge Agent — the per-subject agent for Ireland LC Gaeilge (Irish).

Per the 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1 change
(Phase 8 - 60 per-subject agents).
"""

from __future__ import annotations

import logging
from typing import Any

from ..litellm_agent import litellm_model
from .base import SubjectAgentBase

logger = logging.getLogger(__name__)


# The canonical 13 CopilotKit actions for the Gaeilge agent
GAEILGE_ACTIONS = [
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


# The canonical Gaeilge agent config
gaeilge_agent = SubjectAgentBase(
    stage="lc",
    subject="gaeilge",
    display_name="Gaeilge",
    ncca_code="LC-GAEL-LO",
    spec_code="",
    languages=("ga",),
    board="",
    baml_function="ExtractCurriculumSyllabus(text, subject='gaeilge')",
    cocoindex_app="ireland_lc_gaeilge_untiered_en_embedding",
    notebook_path="notebooks/lc/gaeilge.py",
    web_integration={
        "app": "cianfhoghlaim",
        "route": "/lc/gaeilge",
        "subject_agent_cards": True,
        "homepage_chat_routing": True,
    },
)


__all__ = ["gaeilge_agent", "GAEILGE_ACTIONS"]
