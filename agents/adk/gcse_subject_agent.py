"""Stage agent: GCSE (England General Certificate of Secondary Education) subject expert.

Auto-generated from `baml_src/british_isles/_shared/gcse_extraction_template.baml`
per the 2026-08-26-mega-3a-baml-and-adk-v1 change (Phase 7: ADK Agent Adoption)
+ Q14 (the same template-file pattern for LC + JC + A-Level + GCSE).

The 9 GCSE subjects covered (× 3 awarding bodies = 27 sub-spaces):
MATHEMATICS, ENGLISH_LANGUAGE, ENGLISH_LITERATURE, BIOLOGY, CHEMISTRY,
PHYSICS, HISTORY, GEOGRAPHY, RELIGIOUS_STUDIES.

The 3 awarding bodies: AQA, OCR, Edexcel.
"""
from __future__ import annotations

from .litellm_agent import make_litellm_agent
from agents.integrations.baml_function_tool import BAMLFunctionTool


# The GCSE BAML functions (auto-generated from
# `baml_src/british_isles/_shared/gcse_extraction_template.baml`)
GCSE_FUNCTIONS = [
    "ExtractGCSECurriculumSyllabus",
    "ExtractGCSEExamPaperLayout",
    "ExtractGCSEMarkingSchemeGuideline",
    "ExtractGCSESyllabusDiagram",
    "ExtractGCSECrossSubjectTopics",
    "ExtractGCSEPerQuestionScheme",
    "GenerateSubjectQuestPack",  # from qpack_template.baml
]


gcse_subject_agent = make_litellm_agent(
    name="gcse_subject_agent",
    description=(
        "Expert on England GCSE (General Certificate of Secondary "
        "Education) subjects (ages 14-16). Specialises in extracting "
        "AQA / OCR / Edexcel specification data for the 9 GCSE "
        "subjects (27 sub-spaces total)."
    ),
    model_alias="minimax",
    temperature=0.3,
    max_output_tokens=8192,
    instruction=(
        "You are the **GCSE Subject Agent** for the England General "
        "Certificate of Secondary Education. You specialise in:\n"
        "- GCSE curriculum syllabus extraction (9 subjects × 3 boards)\n"
        "- GCSE exam paper layout extraction (Foundation + Higher tiers)\n"
        "- GCSE marking scheme guideline extraction\n"
        "- GCSE syllabus diagram extraction\n"
        "- GCSE cross-subject topic extraction\n"
        "- GCSE per-question marking scheme allocation\n"
        "- Quest pack generation (GCSE stage)\n\n"
        "Always cite the awarding-body LO code (e.g., `GCSE-MATH-LO-NNN`) "
        "and the source PDF page. Use the canonical BAML functions "
        "listed in the tools section."
    ),
    tools=[BAMLFunctionTool(fn) for fn in GCSE_FUNCTIONS],
)


__all__ = ["gcse_subject_agent", "GCSE_FUNCTIONS"]