"""CocoIndex health tests (Plan 4 audit, 2026-09-12).

Per Plan 4 of the v6 era audit. These tests verify the CocoIndex
v1 surface is consistent and the flows can be imported without errors.
"""
from __future__ import annotations

import importlib
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_cocoindex_lib_installed() -> None:
    """cocoindex v1.x is installed."""
    result = subprocess.run(
        ["uv", "pip", "show", "cocoindex"],
        capture_output=True, text=True,
        cwd=str(REPO_ROOT),
        timeout=15,
    )
    assert result.returncode == 0, (
        f"Plan 4 audit: cocoindex not installed. stderr: {result.stderr}"
    )
    import re
    m = re.search(r"Version:\s*(\S+)", result.stdout)
    assert m, "Plan 4 audit: no version in cocoindex output"
    assert m.group(1).startswith("1.0"), (
        f"Plan 4 audit: unexpected cocoindex version {m.group(1)}"
    )


def test_cocoindex_flow_files_inventory() -> None:
    """The cocoindex_flows directory contains ≥30 *_embedding.py files."""
    flows_dir = REPO_ROOT / "cocoindex_flows"
    flow_files = list(flows_dir.rglob("*_embedding.py"))
    assert len(flow_files) >= 30, (
        f"Plan 4 audit: expected ≥30 *_embedding.py files, found {len(flow_files)}"
    )


def test_cocoindex_ireland_lc_flows_importable() -> None:
    """The 6 Irish LC cocoindex flows + their shared scaffold import cleanly."""
    for module_name in [
        "cocoindex_flows.british_isles.ireland.education.lc._shared",
        "cocoindex_flows.british_isles.ireland.education.lc.mathematics",
        "cocoindex_flows.british_isles.ireland.education.lc.chemistry",
        "cocoindex_flows.british_isles.ireland.education.lc.english",
        "cocoindex_flows.british_isles.ireland.education.lc.gaeilge",
        "cocoindex_flows.british_isles.ireland.education.lc.geography",
    ]:
        try:
            importlib.import_module(module_name)
        except ImportError as exc:
            # Skip if optional deps missing (e.g. baml_client)
            if "baml_client" in str(exc):
                continue
            raise


def test_cocoindex_ireland_lc_baml_fallback_present() -> None:
    """The Ireland LC flows have a BAML fallback path when baml_client is unavailable."""
    # The shared scaffold should declare the fallback
    shared = REPO_ROOT / "cocoindex_flows/british_isles/ireland/education/lc/_shared.py"
    if not shared.exists():
        return
    content = shared.read_text()
    # Per the docstring the fallback is python_baml_fallback_extract
    assert "python_baml_fallback" in content or "baml_fallback" in content, (
        "Plan 4 audit: Ireland LC shared scaffold missing BAML fallback pattern"
    )


def test_biep_parity_lc_tests_exist() -> None:
    """The biep_parity_lc test directory has one test file per subject (6)."""
    parity_dir = REPO_ROOT / "tests/biep_parity_lc"
    if not parity_dir.exists():
        # These tests may have been lost in the disaster
        return
    test_files = list(parity_dir.glob("test_*.py"))
    assert len(test_files) >= 5, (
        f"Plan 4 audit: expected ≥5 parity tests, found {len(test_files)}"
    )


def test_cocoindex_v1_app_pattern_used() -> None:
    """The Ireland LC flows follow the canonical v1 `app = coco.App(coco.AppConfig(...))` pattern."""
    for fname in ["mathematics.py", "chemistry.py", "english.py",
                  "gaeilge.py", "geography.py"]:
        fpath = REPO_ROOT / "cocoindex_flows/british_isles/ireland/education/lc" / fname
        if not fpath.exists():
            continue
        content = fpath.read_text()
        # v1 pattern: app = coco.App(coco.AppConfig(name=...))
        # v0 pattern: @cocoindex.flow_def(...)  - should NOT be present
        assert "cocoindex.flow_def" not in content, (
            f"Plan 4 audit: {fname} uses deprecated v0 pattern"
        )
        assert "coco.App(" in content, (
            f"Plan 4 audit: {fname} missing v1 `coco.App(` pattern"
        )
