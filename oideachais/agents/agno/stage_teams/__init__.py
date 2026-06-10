"""Cianfhoghlaim Oideachais stage teams — Agno multi-agent orchestration.

5 Agno Agents keyed on the 5 educational stages, with stage-specific
sub-agents and 4 shared sub-agents. BAML v0.222.0 client is wired for
all extraction functions.
"""
from __future__ import annotations

import os
from pathlib import Path

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat

from ._shared.baml_client import (
    audit_matriculation,
    estimate_course_points,
    extract_application_timeline,
    extract_apprenticeship_listings,
    extract_cao_course_list,
    extract_cba_descriptor,
    extract_curriculum_from_document,
    extract_exam_paper_structure,
    extract_jc_spec,
    extract_learning_outcome_relationships,
    extract_marking_scheme,
    extract_matriculation_rules,
    extract_subject_rubric,
    score_essay_against_rubric,
)
from ._shared.cognee_graph_query import CogneeGraphQuery
from ._shared.curriculum_scout import CurriculumScout
from ._shared.source_citer import SourceCiter
from ._shared.translation_agent import TranslationAgent
from ._junior_cycle import jc_subject_team, junior_cycle_team
from ._primary import primary_subject_team, primary_team
from ._senior_cycle import lc_subject_team, senior_cycle_team

STORAGE_DIR = Path(os.getenv("AGNO_STORAGE_DIR", "./storage/sessions"))
STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def get_model(model_type: str = "default"):
    if model_type == "irish":
        return OpenAIChat(id=os.getenv("AGNO_IRISH_MODEL", "litellm/irish"))
    return OpenAIChat(id=os.getenv("AGNO_DEFAULT_MODEL", "litellm/gemini-2.0-flash"))


# ── shared tools ──────────────────────────────────────────────────────────
_shared_tools = [TranslationAgent(), SourceCiter(), CogneeGraphQuery()]


# ═══════════════════════════════════════════════════════════════════════════
# Aistear team
# ═══════════════════════════════════════════════════════════════════════════
aistear_team = Agent(
    name="Cianfhoghlaim Aistear Team",
    model=get_model(),
    role="Navigates the 4 Aistear themes and links them to principles and learning goals across 4 age bands.",
    tools=[CurriculumScout(stage="aistear"), *_shared_tools],
    instructions=[
        "Navigate the 4 Aistear themes: Well-being, Identity & Belonging, Communicating, Exploring & Thinking.",
        "Map Aistear principles to learning goals per age band (babies, toddlers, young children).",
        "Find nearest naíonra (Irish-medium pre-school) for a given Eircode or county.",
        "Generate daily bilingual parenting tips from Aistear learning goals.",
        "Always respond in BOTH English and Irish.",
        "Cite the NCCA Aistear framework as the source.",
    ],
    db=SqliteDb(session_table="aistear_team_sessions", db_file=str(STORAGE_DIR / "aistear.db")),
    description="Aistear (early childhood) — 4 themes, 4 age bands, naíonra finder, parent tips.",
)


# ═══════════════════════════════════════════════════════════════════════════
# Primary team
# ═══════════════════════════════════════════════════════════════════════════
primary_team = primary_team(get_model(), SqliteDb(
    session_table="primary_team_sessions", db_file=str(STORAGE_DIR / "primary.db")
), _shared_tools)

# ═══════════════════════════════════════════════════════════════════════════
# Junior Cycle team
# ═══════════════════════════════════════════════════════════════════════════
junior_cycle_team = junior_cycle_team(get_model(), SqliteDb(
    session_table="jc_team_sessions", db_file=str(STORAGE_DIR / "junior_cycle.db")
), _shared_tools)

# ═══════════════════════════════════════════════════════════════════════════
# Senior Cycle team
# ═══════════════════════════════════════════════════════════════════════════
senior_cycle_team = senior_cycle_team(get_model(), SqliteDb(
    session_table="sc_team_sessions", db_file=str(STORAGE_DIR / "senior_cycle.db")
), _shared_tools)


# ═══════════════════════════════════════════════════════════════════════════
# Tertiary team
# ═══════════════════════════════════════════════════════════════════════════
tertiary_team = Agent(
    name="Cianfhoghlaim Tertiary Team",
    model=get_model(),
    role="Tertiary pathways expert — CAO, QQI-FET, Apprenticeship, NUI/HEI matriculation, application timeline, points estimation.",
    tools=[CurriculumScout(stage="tertiary"), *_shared_tools],
    instructions=[
        "Find CAO courses matching LC subjects and predicted points or midpoints.",
        "Map QQI FET Level 5/6 awards to CAO Level 7/8 ladder destinations.",
        "Recommend Apprenticeship programmes as alternative pathways.",
        "Audit LC grades against NUI/HEI matriculation rules.",
        "Surface CAO application timeline (open, close, Round 1, Round 2).",
        "Compare two HEIs on a given programme (fees, NFQ, modules, placement).",
        "Use ExtractCAOCourseList() for CAO course data from CAO.ie.",
        "Use ExtractMatriculationRules() for institution-specific entry requirements.",
        "Use AuditMatriculation() to check applicant grades against requirements.",
        "Use ExtractApplicationTimeline() for application dates.",
        "Use EstimateCoursePoints() for points prediction.",
        "Always respond in BOTH English and Irish.",
    ],
    db=SqliteDb(session_table="tertiary_team_sessions", db_file=str(STORAGE_DIR / "tertiary.db")),
    description="Tertiary — CAO, QQI-FET, Apprenticeship, NUI/HEI matriculation, application timeline.",
)


# ═══════════════════════════════════════════════════════════════════════════
# Registry
# ═══════════════════════════════════════════════════════════════════════════
def make_team(stage: str) -> Agent:
    """Resolve the right Agno Agent for a given educational stage."""
    registry = {
        "aistear": aistear_team,
        "primary": primary_team,
        "junior_cycle": junior_cycle_team,
        "senior_cycle": senior_cycle_team,
        "tertiary": tertiary_team,
    }
    team = registry.get(stage)
    if team is None:
        raise NotImplementedError(f"Stage team '{stage}' not found. Available: {list(registry)}")
    return team


# Subject-specific factory shortcuts
def make_subject_team(stage: str, subject: str) -> Agent:
    """Create a subject-specific agent for any stage."""
    model = get_model()
    if stage == "primary":
        return primary_subject_team(subject, model)
    elif stage == "junior_cycle":
        return jc_subject_team(subject, model)
    elif stage == "senior_cycle":
        return lc_subject_team(subject, model)
    raise NotImplementedError(f"Subject teams not available for stage '{stage}'")
