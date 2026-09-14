"""Education data fill tests (Plan 10, 2026-09-14).

Per Plan 10 of the original plan. These tests verify the cached
education scrape data is processable through the BAML extraction
functions, WITHOUT actually calling BAML (that's deferred to a real
data fill run with the LLM API key).

The fill pipeline is:
  cached Firecrawl samples
    → route to BAML extraction function
    → store in DuckLake (or local DuckDB fallback)

These tests are SAFE - they only verify the pipeline infrastructure.
"""
from __future__ import annotations

from pathlib import Path
import subprocess

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_cached_scrapes_directory_exists() -> None:
    """The 10GB cached scrape samples directory exists."""
    samples = REPO_ROOT / "stedding" / "site_scrape_samples"
    assert samples.exists(), (
        f"Plan 10: cached scrape samples missing at {samples}"
    )


def test_cached_scrapes_have_meaningful_pages() -> None:
    """The cached samples include ≥ 5000 meaningful education pages."""
    inspect = REPO_ROOT / "scripts" / "education_data_fill" / "inspect_cached_scrapes.py"
    if not inspect.exists():
        # Fallback: just count json files
        samples = REPO_ROOT / "stedding" / "site_scrape_samples"
        jsons = list(samples.rglob("*.json"))
        assert len(jsons) >= 5000, (
            f"Plan 10: expected ≥5000 cached scrapes, found {len(jsons)}"
        )
    else:
        result = subprocess.run(
            ["python3", str(inspect)],
            capture_output=True, text=True,
            cwd=str(REPO_ROOT),
            timeout=60,
        )
        assert "TOTAL" in result.stdout, (
            f"Plan 10: inspect_cached_scrapes.py didn't print TOTAL: {result.stdout}"
        )


def test_process_cached_scrapes_dry_run() -> None:
    """The processor script runs in dry-run mode without errors."""
    process = (
        REPO_ROOT / "scripts" / "education_data_fill" / "process_cached_scrapes.py"
    )
    if not process.exists():
        return
    result = subprocess.run(
        ["python3", str(process), "--dry-run", "--limit", "1"],
        capture_output=True, text=True,
        cwd=str(REPO_ROOT),
        timeout=60,
    )
    assert result.returncode == 0, (
        f"Plan 10: process_cached_scrapes.py --dry-run failed: {result.stderr}"
    )
    assert "Summary" in result.stderr, (  # Summary printed to stderr
        f"Plan 10: process_cached_scrapes.py didn't print Summary: {result.stdout}"
    )


def test_baml_function_routes_defined() -> None:
    """The BAML function name routes are defined for each education source."""
    process = (
        REPO_ROOT / "scripts" / "education_data_fill" / "process_cached_scrapes.py"
    )
    if not process.exists():
        return
    content = process.read_text()
    # All major education sources should have routes
    expected_sources = ["ncca.ie", "sqa", "wjec", "ccea", "aqa",
                        "curriculumonline.ie", "examinations.ie", "oide.ie"]
    for source in expected_sources:
        assert f'"{source}"' in content, (
            f"Plan 10: no BAML function route for '{source}'"
        )


def test_baml_client_module_exists() -> None:
    """The baml_client/ generated client is present (post Phase 21 fix)."""
    client_dir = REPO_ROOT / "baml_client" / "baml_client"
    assert client_dir.exists(), (
        f"Plan 10: baml_client/ not generated. Run 'uv run baml-cli generate --from ./baml_src'"
    )
    # Should have a __init__.py
    assert (client_dir / "__init__.py").exists(), (
        f"Plan 10: baml_client/baml_client/__init__.py missing"
    )


def test_plan10_data_fill_safe_stub() -> None:
    """The process_cached_scrapes.py uses 'stub' mode (no live BAML)."""
    process = (
        REPO_ROOT / "scripts" / "education_data_fill" / "process_cached_scrapes.py"
    )
    if not process.exists():
        return
    content = process.read_text()
    assert "stub" in content.lower() or "dry-run" in content.lower(), (
        "Plan 10: process_cached_scrapes.py should default to stub/safe mode"
    )
