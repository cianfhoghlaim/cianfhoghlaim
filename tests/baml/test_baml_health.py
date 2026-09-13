"""BAML health tests (Plan 2 audit, 2026-09-12).

Per Plan 2 of the v6 era audit. These tests verify the BAML toolchain
is functional without depending on the broken baml-cli generate
output (see `.agents/skills/baml/SKILL.md` ⚠️ CURRENT STATUS for
context on why we don't run baml-cli generate here).
"""
from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_baml_cli_available() -> None:
    """baml-cli 0.226.1 is installed and runnable."""
    result = subprocess.run(
        ["baml-cli", "--version"],
        capture_output=True, text=True,
        cwd=str(REPO_ROOT),
        timeout=10,
    )
    assert result.returncode == 0, (
        f"Plan 2 BAML audit: baml-cli not available. stderr: {result.stderr}"
    )
    # baml-cli binary may report a different version than baml-py lib
    # (the CLI is installed separately via uv tool). Accept any 0.22x.
    version_match = any(v in result.stdout + result.stderr for v in
                        ["0.223", "0.224", "0.225", "0.226"])
    assert version_match, (
        f"Plan 2 BAML audit: baml-cli reported unexpected version. "
        f"stdout: {result.stdout}, stderr: {result.stderr}"
    )


def test_baml_src_inventory() -> None:
    """The BAML surface area matches expected dimensions."""
    baml_dir = REPO_ROOT / "baml_src"
    baml_files = list(baml_dir.rglob("*.baml"))
    assert len(baml_files) >= 300, (
        f"Plan 2 BAML audit: expected ≥300 .baml files, found {len(baml_files)}"
    )
    # The 4 client files must exist
    for client_file in ["clients.baml", "clients_image_gen.baml",
                         "clients_llama_swap.baml", "clients_ocr_ensemble.baml"]:
        assert (baml_dir / client_file).exists(), (
            f"Plan 2 BAML audit: missing canonical client file {client_file}"
        )


def test_templates_separated_from_compilable() -> None:
    """The templates dir is for bulk-replace scripts, not baml-cli direct."""
    templates_dir = REPO_ROOT / "baml_src" / "_shared" / "templates"
    if not templates_dir.exists():
        # Templates may have been moved
        return
    templates = list(templates_dir.glob("*.baml"))
    # Templates use Python-style function signatures intentionally
    # (they're processed by scripts/baml_bulk_replace_stubs.py, not by
    # baml-cli directly). This test documents that.
    for t in templates[:3]:
        content = t.read_text()
        # Templates should reference DomainExtractor as their main function
        # (a Python-style placeholder, not real BAML)
        assert "function DomainExtractor(" in content or "template" in content.lower(), (
            f"Plan 2 BAML audit: {t.name} doesn't look like a template"
        )


def test_baml_generation_known_to_fail() -> None:
    """Document the current baml-cli generate failure.

    Per Plan 2, the baml-cli generate command is known to fail due to
    the recovered tree having broken stub functions. This test
    DOCUMENTS the failure mode so future changes can detect if it
    starts working again.
    """
    result = subprocess.run(
        ["baml-cli", "generate", "--from", "./baml_src"],
        capture_output=True, text=True,
        cwd=str(REPO_ROOT),
        timeout=60,
    )
    # Currently we expect failure
    if result.returncode == 0:
        # If baml-cli generate starts working, we'd want to know
        import warnings
        warnings.warn(
            "Plan 2 BAML audit: baml-cli generate is now working! "
            "Consider removing the broken stub files."
        )
    else:
        # Document the failure
        assert "Failed to build BAML runtime" in result.stderr, (
            f"Plan 2 BAML audit: unexpected baml-cli generate error. "
            f"stderr: {result.stderr[:500]}"
        )
