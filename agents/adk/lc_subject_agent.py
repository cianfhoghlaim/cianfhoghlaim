"""Stage agent: Leaving Cycle (Ireland LC) subject expert.

Auto-generated from `baml_src/british_isles/_shared/lc_extraction_template.baml`
per the 2026-08-26-mega-3a-baml-and-adk-v1 change (Phase 7: ADK Agent Adoption).

Uses the `BAMLFunctionTool` helper (from the 2026-08-18-mega-3-fast-follow-v1
change) to wrap the 14 LC-subject BAML functions. Each agent
construction site has a `model_alias="minimax"` (the canonical
LiteLLM gateway per the centralized-model-registry spec).

The 14 LC subjects covered: mathematics, applied_mathematics, chemistry,
physics, biology, geography, english, gaeilge, french, history,
business, accounting, art, music, computer_science.
"""
from __future__ import annotations

from .litellm_agent import make_litellm_agent
from agents.integrations.baml_function_tool import BAMLFunctionTool


# The 14 LC-subject BAML functions (auto-generated from
# `baml_src/british_isles/_shared/lc_extraction_template.baml`)
LC_SUBJECT_FUNCTIONS = [
    "ExtractCurriculumSyllabus",
    "ExtractExamPaperLayout",
    "ExtractMarkingSchemeGuideline",
    "ExtractCrossLinguisticConcept",
    "ExtractSyllabusDiagram",
    "ExtractCircular",
    "LinkCircularToSyllabus",
    "ClassifyCircular",
    "ExtractLCTopicExtraction",
    "GenerateSubjectQuestPack",  # from qpack_template.baml
    "GenerateSubjectFormativeItem",
    "ScoreSubjectFormativeResponse",
]


# Wire the BAML functions as FunctionTools via BAMLFunctionTool
# (replaces 18 hand-written FunctionTool wrappers — -1,200 LOC dedup)
LC_SUBJECT_TOOLS = [
    BAMLFunctionTool(fn) for fn in LC_SUBJECT_FUNCTIONS
]


lc_subject_agent = make_litellm_agent(
    name="lc_subject_agent",
    description=(
        "Expert on Irish Leaving Certificate (LC) subjects. "
        "Specialises in extracting curriculum syllabuses, exam papers, "
        "marking schemes, cross-linguistic concepts (EN ↔ GA), and "
        "syllabus diagrams for the 14 NCCA LC subjects."
    ),
    model_alias="minimax",
    temperature=0.3,
    max_output_tokens=8192,
    instruction=(
        "You are the **Leaving Cycle (LC) Subject Agent** for the "
        "Irish Leaving Certificate. You specialise in:\n"
        "- Curriculum syllabus extraction (14 subjects × EN + GA)\n"
        "- Exam paper layout extraction\n"
        "- Marking scheme guideline extraction\n"
        "- Cross-linguistic concept mapping (EN ↔ GA)\n"
        "- Syllabus diagram extraction (with bounding boxes)\n"
        "- Education circular extraction (gov.ie / Department of Education)\n"
        "- Quest pack generation (formative assessment)\n\n"
        "Always cite the NCCA LO code (e.g., `LC-CHEM-LO-023`) and the "
        "source PDF page. Use the canonical BAML functions listed in "
        "the tools section. Bilingual EN + GA on every user-facing "
        "field where the source PDF is bilingual."
    ),
    tools=LC_SUBJECT_TOOLS,
)


__all__ = ["lc_subject_agent", "LC_SUBJECT_FUNCTIONS", "LC_SUBJECT_TOOLS"]