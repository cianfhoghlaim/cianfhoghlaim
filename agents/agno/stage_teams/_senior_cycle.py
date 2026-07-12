"""Cianfhoghlaim Oideachais Senior Cycle Stage team."""
from __future__ import annotations

from agno.agent import Agent


def senior_cycle_team(model, db, shared_tools):
    """Senior Cycle team — 40+ Leaving Cert subjects, exam papers, marking schemes, rubric scoring."""
    return Agent(
        name="Cianfhoghlaim Senior Cycle Team",
        model=model,
        role="Senior Cycle curriculum and examination expert for 40+ Leaving Certificate subjects (Higher, Ordinary, Foundation).",
        tools=[*shared_tools],
        instructions=[
            "Cover 40+ Leaving Certificate subjects: Irish, English, Mathematics, Applied Mathematics, Accounting, Agricultural Science, Agricultural Economics, Ancient Greek, Arabic, Art, Biology, Business, Chemistry, Classical Studies, Computer Science, Construction Studies, DCG, Economics, Engineering, French, Gaeilge, Geography, German, Hebrew Studies, History, Home Economics, Italian, Japanese, Latin, LCVP, Link Modules, Music, PE, Physics, Physics & Chemistry, Politics & Society, Religious Education, Russian, Spanish, Technology.",
            "Levels: Higher, Ordinary, Foundation (Mathematics, Irish).",
            "Use ExtractCurriculumFromDocument() for syllabus specification extraction.",
            "Use ExtractExamPaperStructure() for question-by-question paper analysis.",
            "Use ExtractMarkingScheme() for SEC marking scheme extraction.",
            "Use ExtractSubjectRubric() to surface the marking rubric for a subject.",
            "Use ScoreEssayAgainstRubric() to grade essay-style questions.",
            "Use CompareMarkingSchemes() to compare marking approaches across years.",
            "Always respond in BOTH English and Irish.",
            "Cite SEC (State Examinations Commission) as the source for exam materials.",
        ],
        db=db,
        description="Senior Cycle — 40+ Leaving Cert subjects, SEC exam papers, marking schemes, rubric scoring.",
    )


def lc_subject_team(subject: str, model):
    """Subject-specific agent for a Leaving Certificate subject."""
    return Agent(
        name=f"Cianfhoghlaim LC — {subject}",
        model=model,
        role=f"Expert on the Leaving Certificate {subject} syllabus and examinations.",
        instructions=[
            f"Focus on the Leaving Certificate {subject} syllabus only.",
            "Extract syllabus aims, objectives, and learning outcomes.",
            "Analyse SEC exam papers for question patterns and mark allocations.",
            "Apply subject-specific rubric for essay and long-answer grading.",
            "Track examination trends and recurring question types.",
            f"For Irish-medium students, provide {subject} terminology in both languages.",
            "Always respond in BOTH English and Irish.",
        ],
        description=f"Leaving Certificate {subject} — syllabus, exam papers, rubric scoring.",
    )
