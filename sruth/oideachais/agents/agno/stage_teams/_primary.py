"""Cianfhoghlaim Oideachais Primary Stage team."""
from __future__ import annotations

from agno.agent import Agent

from ._shared.baml_client import get_baml_client


def primary_team(model, db, shared_tools):
    """Primary team — 12 curriculum areas, 4 stages (infants→6th)."""
    return Agent(
        name="Cianfhoghlaim Primary Team",
        model=model,
        role="Primary curriculum navigator for 12 areas (English, Irish, Mathematics, SESE, Arts, etc.) across 4 stages.",
        tools=[*shared_tools],
        instructions=[
            "Cover 12 curriculum areas: English, Irish, Mathematics, SESE (Science, History, Geography), Visual Arts, Music, Drama, PE, SPHE, Religion.",
            "Stages: Junior Infants, Senior Infants, First/Second, Third/Fourth, Fifth/Sixth.",
            "Use ExtractPrimaryFramework() for structured extraction from NCCA docs.",
            "Use ExtractPrimaryLearningOutcomes() for outcome-per-strand-level.",
            "Always respond in BOTH English and Irish.",
            "Cite NCCA Primary Curriculum as the source.",
        ],
        db=db,
        description="Primary curriculum — 12 areas, 4 stages, NCCA framework.",
    )


def primary_subject_team(subject: str, model):
    """Subject-specific agent for a Primary curriculum area."""
    return Agent(
        name=f"Cianfhoghlaim Primary — {subject}",
        model=model,
        role=f"Expert on the {subject} Primary Curriculum area.",
        instructions=[
            f"Focus on the {subject} curriculum area only.",
            "Map strands, strand units, and learning outcomes.",
            "Always respond in BOTH English and Irish.",
        ],
        description=f"Primary {subject} curriculum expert.",
    )
