"""Phase 22: BAML_FUNCTION_ALIASES map (re-applied 2026-09-14).

Per Plan 16-29 recovery. This module is the canonical registry of BAML
function name aliases — the single source of truth that maps the legacy
``baml_function`` strings emitted by
``dlt_sources/british_isles/_cross/registry_loader.py`` to the
canonical Phase 21 BIEP v3 BAML functions.

Per the safety rules, this module is SAFE to apply — it is pure
metadata (a dict + helper functions). It does NOT touch the 273 broken
BAML files (those are deferred to Phase 21).

Usage::

    from orchestration.defs.2_materials._base.baml_aliases import (
        BAML_FUNCTION_ALIASES,
        canonical_baml_function,
        is_known_baml_function,
    )

    canonical = canonical_baml_function("b.ExtractCurriculumSyllabus")
    # -> "ExtractCurriculumSyllabus"

Reference:
    openspec/changes/2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1/
"""

from __future__ import annotations

from typing import Final

__all__ = [
    "BAML_FUNCTION_ALIASES",
    "BAML_FUNCTIONS_BY_STAGE",
    "canonical_baml_function",
    "is_known_baml_function",
    "strip_baml_prefix",
]


# ---------------------------------------------------------------------------
# The canonical map
# ---------------------------------------------------------------------------

# Aliases are ordered: the most-recently-changed alias appears first so
# the test suite can detect regressions. Each key is a legacy / registry
# function name; each value is the canonical Phase 21 BIEP v3 name.
#
# Sources:
#  - dlt_sources/british_isles/_cross/registry_loader.py
#      (5 canonical names emitted by the registry rows)
#  - dlt_sources/british_isles/ireland/education/junior_cycle.py
#      (the v1 → v3 mapping in ``_baml_extract``)
#  - dlt_sources/british_isles/england/education/{aqa,ocr,edexcel,wjec,ccea}/
#      (legacy ``ExtractCurriculumSpec`` + per-board variants)
#  - dlt_sources/british_isles/ireland/education/curriculum.py
#      (legacy ``ExtractAllPdfMetadata`` etc.)
#  - dlt_sources/filesystem/{zotero,gemini_deep_research,university_of_galway,
#      lc6_cross_check}.py
#      (filesystem-adjacent BAML function names)

BAML_FUNCTION_ALIASES: Final[dict[str, str]] = {
    # === Legacy JC v1 → BIEP v3 ===
    "ExtractJCSpec":                 "ExtractJCSubjectSpec",
    "ExtractJCSubjectSpec":          "ExtractJCSubjectSpec",
    "ExtractJCCurriculum":           "ExtractJCCurriculum",
    "ExtractCBADescriptor":          "ExtractCBADescriptor",
    "ExtractJCShortCourse":          "ExtractJCShortCourse",
    "ExtractJCExamPaper":            "ExtractJCExamPaper",
    "ExtractPrimaryArea":            "ExtractPrimaryArea",

    # === Canonical LC (Ireland Leaving Certificate) ===
    "ExtractCurriculumSyllabus":     "ExtractCurriculumSyllabus",
    "ExtractLC6Syllabus":            "ExtractLC6Syllabus",
    "ExtractChemSyllabus":           "ExtractChemSyllabus",
    "ExtractExamPaperLayout":        "ExtractExamPaperLayout",
    "ExtractLearningOutcome":        "ExtractLearningOutcome",
    "ExtractAllPdfMetadata":         "ExtractAllPdfMetadata",

    # === Canonical LCA (Leaving Certificate Applied) ===
    "ExtractLCASyllabus":            "ExtractLCASyllabus",
    "ExtractLCAModule":              "ExtractLCAModule",
    "ExtractLCAVocationalPrep":      "ExtractLCAVocationalPrep",

    # === Canonical UK / England (GCSE / A-Level) ===
    "ExtractUKQualSpec":             "ExtractUKQualSpec",
    "ExtractCurriculumSpec":         "ExtractUKQualSpec",
    "ExtractGCSECurriculumSyllabus": "ExtractGCSECurriculumSyllabus",
    "ExtractALevelCurriculumSyllabus": "ExtractALevelCurriculumSyllabus",

    # === Canonical gov.ie circulars ===
    "ExtractCircular":               "ExtractCircular",
    "ExtractCitizensInfoArticle":    "ExtractCitizensInfoArticle",

    # === Canonical filesystem / 3rd-party ===
    "ExtractZoteroMetadata":         "ExtractZoteroMetadata",
    "ExtractGeminiReport":           "ExtractGeminiReport",
    "ExtractUoGArtifact":            "ExtractUoGArtifact",
    "ExtractWRCDecision":            "ExtractWRCDecision",
}


# ---------------------------------------------------------------------------
# Per-stage helper index — used by ``JurisdictionAssetsBase`` and
# ``build_jurisdiction_assets`` to pick a default BAML function per stage.
# ---------------------------------------------------------------------------

BAML_FUNCTIONS_BY_STAGE: Final[dict[str, str]] = {
    "lc":      "ExtractCurriculumSyllabus",
    "jc":      "ExtractJCCurriculum",
    "gcse":    "ExtractGCSECurriculumSyllabus",
    "a-level": "ExtractALevelCurriculumSyllabus",
    "lca":     "ExtractLCASyllabus",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def strip_baml_prefix(function_name: str) -> str:
    """Strip the canonical ``b.`` prefix from a BAML function name.

    Returns the bare function name regardless of whether the prefix was
    present. This matches the convention in
    ``orchestration/defs/2_materials/northern_ireland_education/``
    ``northern_ireland_assets.py`` (which calls
    ``row.baml_function.removeprefix("b.")``).
    """
    if function_name.startswith("b."):
        return function_name[len("b."):]
    return function_name


def canonical_baml_function(function_name: str) -> str:
    """Return the canonical BAML function name.

    If the input is in the alias map, return the canonical name.
    Otherwise, strip the ``b.`` prefix and return the input unchanged
    (the function is assumed to be already canonical).

    This is the canonical entrypoint used by ``_call_baml`` and
    ``build_jurisdiction_assets``.
    """
    bare = strip_baml_prefix(function_name)
    return BAML_FUNCTION_ALIASES.get(bare, bare)


def is_known_baml_function(function_name: str) -> bool:
    """Return ``True`` if the function name is in the alias map (or is its
    own canonical name after stripping the ``b.`` prefix).
    """
    bare = strip_baml_prefix(function_name)
    return bare in BAML_FUNCTION_ALIASES