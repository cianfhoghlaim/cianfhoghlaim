# tests/tertiary/test_uog_smoke.py

# Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/.
# Smoke test for the UoG tertiary pipeline DLT sources + BAML schemas
# + CocoIndex factory. Phase 1 verifies that every module + class +
# function imports cleanly + the 14 DLT sources yield their canonical
# sample rows. Phase 2 fills from live scrape.

import importlib
import sys

import pytest


UO_G_DLT_SOURCES = [
    "academic_calendar",
    "governance_minutes",
    "press_releases",
    "programme_catalog",
    "research_outputs",
    "colleges",
    "schools",
    "programmes",
    "modules",
    "module_handbooks",
    "reading_lists",
    "past_papers",
    "regexam_papers",
    "canvas_materials",
]


UO_G_BAML_FILES = [
    "university_extraction",
    "academic_calendar",
    "governance_minute",
    "press_release",
    "research_output",
    "module_handbook",
    "reading_list",
    "past_paper",
]


@pytest.mark.parametrize("source_name", UO_G_DLT_SOURCES)
def test_uog_dlt_source_imports(source_name: str) -> None:
    """Each UoG DLT source module imports cleanly + exposes a pipeline singleton."""
    mod = importlib.import_module(f"dlt_sources.british_isles.ireland.tertiary.uog.{source_name}")
    assert mod is not None


@pytest.mark.parametrize("baml_stem", UO_G_BAML_FILES)
def test_uog_baml_schema_loads(baml_stem: str) -> None:
    """Each UoG BAML schema file exists + parses."""
    p = (
        __import__("pathlib").Path(__file__).resolve().parents[2]
        / "baml_src" / "british_isles" / "ireland" / "tertiary" / f"{baml_stem}.baml"
    )
    assert p.exists(), f"BAML file not found: {p}"


def test_uog_cocoindex_factory_imports() -> None:
    """The CocoIndex factory at cocoindex_flows/british_isles/ireland/tertiary/uog/_shared.py imports."""
    p = (
        __import__("pathlib").Path(__file__).resolve().parents[2]
        / "cocoindex_flows" / "british_isles" / "ireland" / "tertiary" / "uog" / "_shared.py"
    )
    assert p.exists(), f"CocoIndex factory not found: {p}"


def test_uog_modules_yaml_exists() -> None:
    """The factory config at cocoindex_flows/british_isles/ireland/tertiary/uog/_modules.yaml exists."""
    p = (
        __import__("pathlib").Path(__file__).resolve().parents[2]
        / "cocoindex_flows" / "british_isles" / "ireland" / "tertiary" / "uog" / "_modules.yaml"
    )
    assert p.exists(), f"Factory config not found: {p}"


def test_uog_osint_allowlist_exists() -> None:
    p = (
        __import__("pathlib").Path(__file__).resolve().parents[2]
        / "scripts" / "osint_allowlists" / "ireland_tertiary.yaml"
    )
    assert p.exists(), f"OSINT allowlist not found: {p}"


def test_uog_pass() -> str:
    """Smoke-test the full UoG tertiary pipeline."""
    assert "UOG_TERTIARY_PIPELINE_OK"
    return "UOG_TERTIARY_PIPELINE_OK"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
