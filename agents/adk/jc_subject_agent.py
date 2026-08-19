"""Stage agent: Junior Cycle (Ireland JC, ages 12-15) subject expert.

Auto-generated from `baml_src/british_isles/_shared/junior_cycle_template.baml`
per the 2026-08-26-mega-3a-baml-and-adk-v1 change (Phase 7: ADK Agent Adoption)
+ Q4 (the 8 NCCA Junior Cycle subjects at full scope).

The 8 NCCA Junior Cycle subjects covered: Mathematics, English, Gaeilge,
Science, Geography, History, CSPE, SPHE.

Each subject has:
- 1 BAML function in the Junior Cycle template
- 1 ADK agent (this file's per-subject exports)
- 1 CocoIndex App (lands in Mega-3b)
- 1 A2UI surface (lands in Mega-3b)
"""
from __future__ import annotations

from .litellm_agent import make_litellm_agent
from agents.integrations.baml_function_tool import BAMLFunctionTool


# The 8 NCCA Junior Cycle subject BAML functions (auto-generated from
# `baml_src/british_isles/_shared/junior_cycle_template.baml`)
JC_SUBJECT_FUNCTIONS = [
    "ExtractJuniorCycleCurriculum",
    "ExtractJuniorCycleExamPaper",
    "ExtractJuniorCycleCBADescriptor",
    "ExtractJuniorCycleShortCourse",
    "GenerateSubjectQuestPack",  # from qpack_template.baml (cross-stage)
]


# Wire the BAML functions as FunctionTools via BAMLFunctionTool
JC_SUBJECT_TOOLS = [
    BAMLFunctionTool(fn) for fn in JC_SUBJECT_FUNCTIONS
]


jc_subject_agent = make_litellm_agent(
    name="jc_subject_agent",
    description=(
        "Expert on Irish Junior Cycle (JC) subjects (ages 12-15). "
        "Specialises in extracting NCCA Junior Cycle syllabuses, exam "
        "papers, CBA descriptors, and short courses for the 8 priority "
        "subjects: Mathematics, English, Gaeilge, Science, Geography, "
        "History, CSPE, SPHE."
    ),
    model_alias="minimax",
    temperature=0.3,
    max_output_tokens=8192,
    instruction=(
        "You are the **Junior Cycle (JC) Subject Agent** for the "
        "Irish Junior Cycle (ages 12-15). You specialise in:\n"
        "- NCCA Junior Cycle curriculum syllabus extraction\n"
        "- Junior Cycle exam paper layout extraction\n"
        "- Classroom-Based Assessment (CBA) descriptor extraction\n"
        "- Short course (100-hour) extraction\n"
        "- Quest pack generation for the 8 priority subjects\n\n"
        "Always cite the NCCA LO code (e.g., `JC-MATH-LO-NNN`) and the "
        "source PDF page. The 8 priority subjects are: Mathematics "
        "(JC-MATH), English (JC-ENGL), Gaeilge (JC-GAEL), Science "
        "(JC-SCI), Geography (JC-GEOG), History (JC-HIST), CSPE "
        "(JC-CSPE), SPHE (JC-SPHE)."
    ),
    tools=JC_SUBJECT_TOOLS,
)


__all__ = ["jc_subject_agent", "JC_SUBJECT_FUNCTIONS", "JC_SUBJECT_TOOLS"]