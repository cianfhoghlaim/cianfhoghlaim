"""Stage agent: A-Level (England GCE Advanced Level) subject expert.

Auto-generated from `baml_src/british_isles/_shared/alevel_extraction_template.baml`
per the 2026-08-26-mega-3a-baml-and-adk-v1 change (Phase 7: ADK Agent Adoption)
+ Q14 (the same template-file pattern for LC + JC + A-Level + GCSE).

The 15 A-Level subjects covered (× 3 awarding bodies = 45 sub-spaces):
MATHEMATICS, FURTHER_MATHEMATICS, ENGLISH_LITERATURE, ENGLISH_LANGUAGE,
BIOLOGY, CHEMISTRY, PHYSICS, PSYCHOLOGY, HISTORY, GEOGRAPHY, ECONOMICS,
BUSINESS, HISTORY_OF_ART, POLITICS, SOCIOLOGY.

The 3 awarding bodies: AQA, OCR, Edexcel.
"""
from __future__ import annotations

from .litellm_agent import make_litellm_agent
from agents.integrations.baml_function_tool import BAMLFunctionTool


# The A-Level BAML functions (auto-generated from
# `baml_src/british_isles/_shared/alevel_extraction_template.baml`)
ALEVEL_FUNCTIONS = [
    "ExtractALevelCurriculumSyllabus",
    "ExtractALevelExamPaperLayout",
    "ExtractALevelMarkingSchemeGuideline",
    "ExtractALevelSyllabusDiagram",
    "ExtractALevelCrossSubjectTopics",
    "ExtractALevelPerQuestionScheme",
    "GenerateSubjectQuestPack",  # from qpack_template.baml
]


alevel_subject_agent = make_litellm_agent(
    name="alevel_subject_agent",
    description=(
        "Expert on England A-Level (GCE Advanced Level) subjects. "
        "Specialises in extracting AQA / OCR / Edexcel specification "
        "data for the 15 A-Level subjects (45 sub-spaces total)."
    ),
    model_alias="minimax",
    temperature=0.3,
    max_output_tokens=8192,
    instruction=(
        "You are the **A-Level Subject Agent** for the England GCE "
        "Advanced Level. You specialise in:\n"
        "- A-Level curriculum syllabus extraction (15 subjects × 3 boards)\n"
        "- A-Level exam paper layout extraction\n"
        "- A-Level marking scheme guideline extraction\n"
        "- A-Level syllabus diagram extraction\n"
        "- A-Level cross-subject topic extraction\n"
        "- A-Level per-question marking scheme allocation\n"
        "- Quest pack generation (A-Level stage)\n\n"
        "Always cite the awarding-body LO code (e.g., `AL-MATH-LO-NNN` "
        "for AQA, OCR, or Edexcel) and the source PDF page. Use the "
        "canonical BAML functions listed in the tools section."
    ),
    tools=[BAMLFunctionTool(fn) for fn in ALEVEL_FUNCTIONS],
)


__all__ = ["alevel_subject_agent", "ALEVEL_FUNCTIONS"]