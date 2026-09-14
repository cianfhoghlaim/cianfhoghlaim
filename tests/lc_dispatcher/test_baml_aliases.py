"""Smoke test for Phase 22: BAML_FUNCTION_ALIASES map.

Per Plan 16-29 recovery. Verifies:

  1. The alias file exists.
  2. The module imports + exposes ``BAML_FUNCTION_ALIASES``,
     ``canonical_baml_function``, ``is_known_baml_function``, and
     ``strip_baml_prefix``.
  3. The map contains ≥ 25 entries (the spec target).
  4. The critical canonical mappings are correct:
       - ``ExtractJCSpec`` (legacy) → ``ExtractJCSubjectSpec``
       - ``ExtractCurriculumSpec`` (legacy) → ``ExtractUKQualSpec``
       - ``ExtractCurriculumSyllabus`` → ``ExtractCurriculumSyllabus``
  5. The helper functions round-trip correctly.
  6. The per-stage helper index is sane.

Per the safety rules, this test is SAFE to apply — it only inspects
the in-memory dict.
"""
from __future__ import annotations

import importlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ALIASES_PATH = (
    REPO_ROOT
    / "orchestration" / "defs" / "2_materials" / "_base" / "baml_aliases.py"
)


def test_aliases_file_exists() -> None:
    """The BAML alias module file exists at the canonical path."""
    assert ALIASES_PATH.is_file(), (
        f"Phase 22 foundation: {ALIASES_PATH} missing — was the alias "
        "module reverted?"
    )


def test_aliases_module_importable() -> None:
    """The alias module imports and exposes the canonical symbols."""
    import sys
    sys.path.insert(0, str(REPO_ROOT))
    mod = importlib.import_module(
        "orchestration.defs.2_materials._base.baml_aliases"
    )
    for attr in (
        "BAML_FUNCTION_ALIASES",
        "BAML_FUNCTIONS_BY_STAGE",
        "canonical_baml_function",
        "is_known_baml_function",
        "strip_baml_prefix",
    ):
        assert hasattr(mod, attr), (
            f"Phase 22 foundation: `baml_aliases` missing export `{attr}`."
        )


def test_aliases_map_has_at_least_25_entries() -> None:
    """The spec target: ≥ 25 alias entries."""
    import sys
    sys.path.insert(0, str(REPO_ROOT))
    mod = importlib.import_module(
        "orchestration.defs.2_materials._base.baml_aliases"
    )
    n = len(mod.BAML_FUNCTION_ALIASES)
    assert n >= 25, (
        f"Phase 22 foundation: expected ≥25 alias entries, got {n}."
    )


def test_critical_aliases_present() -> None:
    """The must-have mappings (legacy → canonical) are correct."""
    import sys
    sys.path.insert(0, str(REPO_ROOT))
    mod = importlib.import_module(
        "orchestration.defs.2_materials._base.baml_aliases"
    )
    aliases = mod.BAML_FUNCTION_ALIASES

    # Legacy JC v1 → BIEP v3 (per junior_cycle.py:_baml_extract)
    assert aliases.get("ExtractJCSpec") == "ExtractJCSubjectSpec", (
        "Phase 22 foundation: ExtractJCSpec must map to ExtractJCSubjectSpec"
    )

    # Legacy England → BIEP v3 (per
    # dlt_sources/british_isles/england/education/*/syllabus_source.py)
    assert aliases.get("ExtractCurriculumSpec") == "ExtractUKQualSpec", (
        "Phase 22 foundation: ExtractCurriculumSpec must map to "
        "ExtractUKQualSpec"
    )

    # Canonical LC names pass through
    assert aliases.get("ExtractCurriculumSyllabus") == "ExtractCurriculumSyllabus"
    assert aliases.get("ExtractJCCurriculum") == "ExtractJCCurriculum"
    assert aliases.get("ExtractJCShortCourse") == "ExtractJCShortCourse"
    assert aliases.get("ExtractCBADescriptor") == "ExtractCBADescriptor"
    assert aliases.get("ExtractUKQualSpec") == "ExtractUKQualSpec"


def test_strip_baml_prefix() -> None:
    """`strip_baml_prefix` removes the leading `b.` (per the existing
    pattern in `northern_ireland_assets.py`)."""
    import sys
    sys.path.insert(0, str(REPO_ROOT))
    mod = importlib.import_module(
        "orchestration.defs.2_materials._base.baml_aliases"
    )
    assert mod.strip_baml_prefix("b.ExtractCurriculumSyllabus") == "ExtractCurriculumSyllabus"
    assert mod.strip_baml_prefix("ExtractCurriculumSyllabus") == "ExtractCurriculumSyllabus"
    assert mod.strip_baml_prefix("b.") == ""
    assert mod.strip_baml_prefix("") == ""


def test_canonical_baml_function() -> None:
    """`canonical_baml_function` resolves aliases + strips the `b.` prefix."""
    import sys
    sys.path.insert(0, str(REPO_ROOT))
    mod = importlib.import_module(
        "orchestration.defs.2_materials._base.baml_aliases"
    )
    # Bare legacy
    assert mod.canonical_baml_function("ExtractJCSpec") == "ExtractJCSubjectSpec"
    # With prefix
    assert mod.canonical_baml_function("b.ExtractJCSpec") == "ExtractJCSubjectSpec"
    # Already canonical
    assert mod.canonical_baml_function("ExtractCurriculumSyllabus") == "ExtractCurriculumSyllabus"
    # Unknown — returned as-is (bare)
    assert mod.canonical_baml_function("b.SomeUnknownFn") == "SomeUnknownFn"
    assert mod.canonical_baml_function("SomeUnknownFn") == "SomeUnknownFn"


def test_is_known_baml_function() -> None:
    """`is_known_baml_function` matches both canonical and legacy names."""
    import sys
    sys.path.insert(0, str(REPO_ROOT))
    mod = importlib.import_module(
        "orchestration.defs.2_materials._base.baml_aliases"
    )
    assert mod.is_known_baml_function("b.ExtractCurriculumSyllabus") is True
    assert mod.is_known_baml_function("ExtractCurriculumSyllabus") is True
    assert mod.is_known_baml_function("b.ExtractJCSpec") is True  # legacy
    assert mod.is_known_baml_function("b.NotARealFunction") is False
    assert mod.is_known_baml_function("NotARealFunction") is False


def test_baml_functions_by_stage() -> None:
    """The per-stage helper index covers all 5 stages (lc, jc, gcse, a-level, lca)."""
    import sys
    sys.path.insert(0, str(REPO_ROOT))
    mod = importlib.import_module(
        "orchestration.defs.2_materials._base.baml_aliases"
    )
    stages = mod.BAML_FUNCTIONS_BY_STAGE
    for stage in ("lc", "jc", "gcse", "a-level", "lca"):
        assert stage in stages, (
            f"Phase 22 foundation: stage `{stage}` missing from "
            f"BAML_FUNCTIONS_BY_STAGE."
        )


def test_registry_loader_canonical_names_all_aliased() -> None:
    """The 5 canonical BAML function names emitted by
    ``dlt_sources/british_isles/_cross/registry_loader.py`` all resolve
    via the alias map.
    """
    import sys
    sys.path.insert(0, str(REPO_ROOT))
    mod = importlib.import_module(
        "orchestration.defs.2_materials._base.baml_aliases"
    )

    registry_names = [
        "ExtractCurriculumSyllabus",
        "ExtractJCCurriculum",
        "ExtractJCShortCourse",
        "ExtractCBADescriptor",
        "ExtractUKQualSpec",
    ]
    for name in registry_names:
        assert mod.is_known_baml_function(name), (
            f"Phase 22 foundation: registry-emitted `{name}` not in alias "
            f"map."
        )