"""Cianfhoghlaim Oideachais stage teams — Agno multi-agent orchestration.

5 Agno `Team` instances keyed on the 5 educational stages, with
stage-specific sub-agents and 4 shared sub-agents. Replaces the single
6-agent `education_team.py` with a thin compatibility shim.

This is the v1 factory. Subject-specific teams (50+ Senior Cycle) are
defined in `subject_teams/`.
"""
from __future__ import annotations

import os
from pathlib import Path

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from agno.team import Team

from ._shared.curriculum_scout import CurriculumScout
from ._shared.translation_agent import TranslationAgent
from ._shared.cognee_graph_query import CogneeGraphQuery
from ._shared.source_citer import SourceCiter

STORAGE_DIR = Path(os.getenv("AGNO_STORAGE_DIR", "./storage/sessions"))
STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def get_model(model_type: str = "default"):
    if model_type == "irish":
        return OpenAIChat(id=os.getenv("AGNO_IRISH_MODEL", "litellm/irish"))
    return OpenAIChat(id=os.getenv("AGNO_DEFAULT_MODEL", "litellm/gemini-2.0-flash"))


# -----------------------------------------------------------------------------
# Aistear team
# -----------------------------------------------------------------------------
aistear_team = Team(
    name="Cianfhoghlaim Aistear Team",
    model=get_model(),
    members=[
        Agent(
            name="ThemeNavigator",
            model=get_model(),
            role="Discovers the 4 Aistear themes and links them to the underlying principles.",
            tools=[CurriculumScout(stage="aistear"), CogneeGraphQuery(dataset="oideachais.aistear")],
            instructions=[
                "Navigate the 4 Aistear themes: Well-being, Identity & Belonging, Communicating, Exploring & Thinking.",
                "Always respond in BOTH English and Irish.",
                "Cite the NCCA Aistear framework as the source.",
            ],
        ),
        Agent(
            name="PrincipleMapper",
            model=get_model(),
            role="Maps Aistear principles to learning goals across the 4 age bands.",
            tools=[CurriculumScout(stage="aistear")],
            instructions=["Map each principle to learning goals per age band."],
        ),
        Agent(
            name="NaionraFinder",
            model=get_model(),
            role="Finds the nearest Irish-medium pre-school (naíonra) for a given Eircode or county.",
            tools=[CurriculumScout(stage="aistear")],
        ),
        Agent(
            name="ParentTipGenerator",
            model=get_model(),
            role="Generates daily bilingual parenting tips based on the Aistear learning goals.",
            tools=[TranslationAgent(), SourceCiter()],
        ),
    ],
    db=SqliteDb(session_table="aistear_team_sessions", db_file=str(STORAGE_DIR / "aistear.db")),
    description="Aistear (early childhood) team — 4 themes, 4 age bands, naíonra finder, parent tips.",
)


# -----------------------------------------------------------------------------
# Tertiary team
# -----------------------------------------------------------------------------
tertiary_team = Team(
    name="Cianfhoghlaim Tertiary Team",
    model=get_model(),
    members=[
        Agent(
            name="CAOCourseFinder",
            model=get_model(),
            role="Finds CAO courses that match the applicant's LC subjects and predicted points.",
            tools=[CurriculumScout(stage="tertiary")],
        ),
        Agent(
            name="QQIFETLadder",
            model=get_model(),
            role="Maps QQI FET Level 5/6 awards to CAO Level 7/8 ladder destinations.",
            tools=[CurriculumScout(stage="tertiary")],
        ),
        Agent(
            name="ApprenticeshipAdvisor",
            model=get_model(),
            role="Recommends Apprenticeship programmes as alternative pathways to CAO courses.",
            tools=[CurriculumScout(stage="tertiary")],
        ),
        Agent(
            name="MatriculationCheck",
            model=get_model("irish"),
            role="Audits an applicant's LC grades against NUI/HEI matriculation rules.",
            tools=[CurriculumScout(stage="tertiary")],
        ),
        Agent(
            name="ApplicationTimelineGuide",
            model=get_model(),
            role="Surfaces the CAO open/close/round dates for the current application year.",
        ),
        Agent(
            name="HEIComparer",
            model=get_model(),
            role="Compares two HEIs on a given programme (fees, NFQ, modules, placement).",
            tools=[CurriculumScout(stage="tertiary")],
        ),
    ],
    db=SqliteDb(session_table="tertiary_team_sessions", db_file=str(STORAGE_DIR / "tertiary.db")),
    description="Tertiary team — CAO, QQI-FET, Apprenticeship, NUI/HEI matriculation, application timeline.",
)


# -----------------------------------------------------------------------------
# Compatibility shim — replaces the single education_team.py
# -----------------------------------------------------------------------------
def make_team(stage: str) -> Team:
    """Resolve the right Agno Team for a given stage."""
    registry = {
        "aistear": aistear_team,
        "primary": None,        # TODO: wire primary_team
        "junior_cycle": None,   # TODO: wire junior_cycle_team
        "senior_cycle": None,   # TODO: wire senior_cycle_team
        "tertiary": tertiary_team,
    }
    team = registry.get(stage)
    if team is None:
        raise NotImplementedError(f"Stage team '{stage}' not yet wired (PRs welcome)")
    return team
