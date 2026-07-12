"""Cianfhoghlaim Oideachais Junior Cycle Stage team."""
from __future__ import annotations

from agno.agent import Agent


def junior_cycle_team(model, db, shared_tools):
    """Junior Cycle team — 18 subjects + 16 short courses + 2 CBAs."""
    return Agent(
        name="Cianfhoghlaim Junior Cycle Team",
        model=model,
        role="Junior Cycle curriculum navigator for 18 examination subjects and 16 short courses (CBA task extraction, specification analysis).",
        tools=[*shared_tools],
        instructions=[
            "Cover 18 Junior Cycle subjects: Art, Business Studies, CSPE, Classics, English, French, Gaeilge, Geography, German, Graphics, History, Home Economics, Italian, Mathematics, Music, Religious Education, Science, Spanish.",
            "Cover 16 NCCA short courses: Coding, Digital Media Literacy, Civic Action, Chinese Language, etc.",
            "Use ExtractJCSpec() for structured specification extraction.",
            "Use ExtractCBADescriptor() for Classroom-Based Assessment task details.",
            "Map each strand to its learning outcomes and achievement levels.",
            "Always respond in BOTH English and Irish.",
            "Cite NCCA Junior Cycle Specification as the source.",
        ],
        db=db,
        description="Junior Cycle — 18 subjects, 16 short courses, 2 CBAs, NCCA/State Exams Commission.",
    )


def jc_subject_team(subject: str, model):
    """Subject-specific agent for a Junior Cycle subject."""
    return Agent(
        name=f"Cianfhoghlaim JC — {subject}",
        model=model,
        role=f"Expert on the Junior Cycle {subject} specification.",
        instructions=[
            f"Focus on the Junior Cycle {subject} specification only.",
            "Extract strands, strand units, learning outcomes.",
            "Extract CBA 1 and CBA 2 task descriptors.",
            "Map to the 4 achievement levels: Exceptional, Above Expectations, In Line, Yet to Meet.",
            "Always respond in BOTH English and Irish.",
        ],
        description=f"Junior Cycle {subject} specification expert.",
    )
