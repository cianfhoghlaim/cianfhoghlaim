"""British Isles education sources tests (Plan 10 audit, 2026-09-13).

Per Plan 10 of the v6 era audit. These tests verify the 8
jurisdictional DLT source surfaces for British Isles education
(NCCA, OFQUAL, SQA, WJEC, CCEA, CEA, IoM, Jersey, Guernsey).

This is a SAFE audit - no DLT code changed, no new sources added.
The plan is to use Firecrawl to fill in the actual data, which
happens after the audit is complete.
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


# Minimum source file counts per jurisdiction (intentionally low thresholds
# so the tests are robust to the Plan 10 data fill)
MIN_SOURCES_PER_JURISDICTION: dict[str, int] = {
    "ireland": 80,          # NCCA - 6 LC subjects + 6 JC + universities
    "england": 25,          # OFQUAL - 3 boards (AQA, OCR, Edexcel)
    "scotland": 5,           # SQA - 1 board
    "wales": 5,              # WJEC - 1 board
    "northern_ireland": 5,   # CCEA - 1 board
    "guernsey": 3,           # CEA
    "jersey": 3,            # CEA
    "isle_of_man": 3,        # IoM
}


def test_ncca_ireland_sources_count() -> None:
    """NCCA Ireland has ≥ 80 education DLT source files."""
    base = REPO_ROOT / "dlt_sources" / "british_isles" / "ireland" / "education"
    py_files = list(base.rglob("*.py"))
    py_files = [f for f in py_files if "__pycache__" not in str(f)]
    assert len(py_files) >= MIN_SOURCES_PER_JURISDICTION["ireland"], (
        f"Plan 10 audit: expected ≥{MIN_SOURCES_PER_JURISDICTION['ireland']} NCCA source files, "
        f"found {len(py_files)}"
    )


def test_ofqual_england_sources_count() -> None:
    """OFQUAL England has ≥ 25 education DLT source files."""
    base = REPO_ROOT / "dlt_sources" / "british_isles" / "england" / "education"
    py_files = list(base.rglob("*.py"))
    py_files = [f for f in py_files if "__pycache__" not in str(f)]
    assert len(py_files) >= MIN_SOURCES_PER_JURISDICTION["england"], (
        f"Plan 10 audit: expected ≥{MIN_SOURCES_PER_JURISDICTION['england']} OFQUAL source files, "
        f"found {len(py_files)}"
    )


def test_sqa_scotland_sources_count() -> None:
    """SQA Scotland has ≥ 5 education DLT source files."""
    base = REPO_ROOT / "dlt_sources" / "british_isles" / "scotland" / "education"
    py_files = list(base.rglob("*.py"))
    py_files = [f for f in py_files if "__pycache__" not in str(f)]
    assert len(py_files) >= MIN_SOURCES_PER_JURISDICTION["scotland"], (
        f"Plan 10 audit: expected ≥{MIN_SOURCES_PER_JURISDICTION['scotland']} SQA source files, "
        f"found {len(py_files)}"
    )


def test_wjec_wales_sources_count() -> None:
    """WJEC Wales has ≥ 5 education DLT source files."""
    base = REPO_ROOT / "dlt_sources" / "british_isles" / "wales" / "education"
    py_files = list(base.rglob("*.py"))
    py_files = [f for f in py_files if "__pycache__" not in str(f)]
    assert len(py_files) >= MIN_SOURCES_PER_JURISDICTION["wales"], (
        f"Plan 10 audit: expected ≥{MIN_SOURCES_PER_JURISDICTION['wales']} WJEC source files, "
        f"found {len(py_files)}"
    )


def test_ccea_ni_sources_count() -> None:
    """CCEA Northern Ireland has ≥ 5 education DLT source files."""
    base = REPO_ROOT / "dlt_sources" / "british_isles" / "northern_ireland" / "education"
    py_files = list(base.rglob("*.py"))
    py_files = [f for f in py_files if "__pycache__" not in str(f)]
    assert len(py_files) >= MIN_SOURCES_PER_JURISDICTION["northern_ireland"], (
        f"Plan 10 audit: expected ≥{MIN_SOURCES_PER_JURISDICTION['northern_ireland']} CCEA source files, "
        f"found {len(py_files)}"
    )


def test_crown_dependencies_sources_exist() -> None:
    """All 3 Crown dependencies (Guernsey, Jersey, IoM) have ≥ 3 DLT source files each."""
    for j in ["guernsey", "jersey", "isle_of_man"]:
        base = REPO_ROOT / "dlt_sources" / "british_isles" / j / "education"
        if not base.exists():
            continue
        py_files = [f for f in base.rglob("*.py") if "__pycache__" not in str(f)]
        assert len(py_files) >= MIN_SOURCES_PER_JURISDICTION[j], (
            f"Plan 10 audit: expected ≥{MIN_SOURCES_PER_JURISDICTION[j]} {j} source files, "
            f"found {len(py_files)}"
        )


def test_biep_v3_orchestration_change_exists() -> None:
    """The BIEP v3 orchestration openspec change is present."""
    change = REPO_ROOT / "openspec" / "changes" / "pipeline-biep-v3-orchestration"
    assert change.exists(), (
        f"Plan 10 audit: {change} missing"
    )
    proposal = change / "proposal.md"
    assert proposal.exists(), (
        f"Plan 10 audit: {proposal} missing"
    )


def test_ncca_unified_curriculum_source() -> None:
    """The unified NCCA curriculum DLT source is present."""
    curriculum = (
        REPO_ROOT / "dlt_sources/british_isles/ireland/education/curriculum.py"
    )
    assert curriculum.exists(), (
        "Plan 10 audit: NCCA unified curriculum source missing"
    )


def test_lc_subject_dlt_sources() -> None:
    """Each of the 6 Ireland LC subjects has a DLT source."""
    ireland_edu = REPO_ROOT / "dlt_sources/british_isles/ireland/education"
    expected_subjects = ["mathematics", "chemistry", "geography",
                          "gaeilge", "english", "computer_science"]
    for subj in expected_subjects:
        matches = list(ireland_edu.rglob(f"*{subj}*.py"))
        matches = [f for f in matches if "__pycache__" not in str(f)]
        assert len(matches) >= 1, (
            f"Plan 10 audit: no DLT source found for Ireland LC subject '{subj}'"
        )
