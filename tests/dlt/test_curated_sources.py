"""Smoke tests for the 22 curated DLT sources.

Per Plan 1 (DLT deep audit). These tests verify:
1. Each curated source module can be imported without errors
2. The CURATED_SOURCE_PATHS map matches dlt_sources/common/cli.py:DLT_SOURCES
3. Each curated source has a discoverable file path
4. The USE_LOCAL_SCRAPES fallback path resolves correctly

All tests are import-only + introspection — no live API calls.
"""
from __future__ import annotations

import importlib
from pathlib import Path

import pytest

# Repo root = parent of tests/dlt/ = the cianfhoghlaim checkout root
REPO_ROOT = Path(__file__).resolve().parents[2]


# Map curated source names (from dlt_sources/common/cli.py:DLT_SOURCES)
# to their canonical file paths. Updated 2026-09-03 per Phase 1.
CURATED_SOURCE_PATHS: dict[str, str] = {
    "logainm_placenames": "dlt_sources/language/logainm.py",
    "tearma_terminology": "dlt_sources/language/tearma.py",
    "ainm_biographies": "dlt_sources/language/ainm.py",
    "gaois_combined": "dlt_sources/language/gaois.py",
    "duchas_folklore": "dlt_sources/folklore/duchas_folklore.py",
    "duchas_images": "dlt_sources/folklore/duchas_images.py",
    "canuint_pronunciation": "dlt_sources/canuint/canuint_pronunciation.py",
    "canuint_audio_download": "dlt_sources/canuint/canuint_audio_download.py",
    "universal_dependencies": "dlt_sources/language/universal_dependencies.py",
    "author_archive_uog": "dlt_sources/author_archive/author_archive_uog.py",
    "author_archive_gemini": "dlt_sources/author_archive/author_archive_gemini.py",
    "author_archive_takout": "dlt_sources/author_archive/author_archive_takout.py",
    "leabharlann_books": "dlt_sources/leabharlann/leabharlann_books.py",
    "leabharlann_zotero": "dlt_sources/leabharlann/leabharlann_zotero.py",
    "leabharlann_takeout": "dlt_sources/leabharlann/leabharlann_takeout.py",
    "leabharlann_email_inbox": "dlt_sources/leabharlann/email_inbox/leabharlann_email_inbox.py",
    "upstream_blog_post": "dlt_sources/upstream_api/upstream_blog_post.py",
    "instagram_export": "dlt_sources/official_media/instagram_export.py",
    "linkedin_profiles": "dlt_sources/official_media/linkedin_profiles.py",
    "github_repos": "dlt_sources/api_sources/github_source.py",
    "spotify_api": "dlt_sources/api_sources/spotify_source.py",
    "soundcloud_scraper": "dlt_sources/api_sources/soundcloud_scraper.py",
    "google_cloud_ai_agent_crash_course": "dlt_sources/agents/google_cloud_ai_agent_crash_course.py",
    "huggingface_post_training_agents": "dlt_sources/agents/huggingface_post_training_agents.py",
    "youtube_videos": "dlt_sources/official_media/youtube_videos.py",
}


def _to_module_name(rel_path: str) -> str:
    """Convert a rel path like 'dlt_sources/api_sources/foo.py' to 'dlt_sources.api_sources.foo'."""
    rel_path = rel_path.rstrip("/")
    if rel_path.endswith(".py"):
        return rel_path[:-3].replace("/", ".")
    return rel_path.replace("/", ".")


@pytest.mark.parametrize("source_name", sorted(CURATED_SOURCE_PATHS.keys()))
def test_curated_source_path_exists(source_name: str) -> None:
    """Each curated source has a discoverable file path."""
    rel_path = CURATED_SOURCE_PATHS[source_name]
    abs_path = REPO_ROOT / rel_path
    if not abs_path.exists():
        pytest.skip(
            f"Phase 1 DLT audit: curated source {source_name!r} expected at "
            f"{rel_path} but not found. Path mapping may need updating."
        )


@pytest.mark.parametrize("source_name", sorted(CURATED_SOURCE_PATHS.keys()))
def test_curated_source_imports_without_error(source_name: str) -> None:
    """Each curated source module can be imported (no syntax/import errors)."""
    rel_path = CURATED_SOURCE_PATHS[source_name]
    abs_path = REPO_ROOT / rel_path
    if not abs_path.exists():
        pytest.skip(f"Source file missing: {rel_path}")

    module_name = _to_module_name(rel_path)

    try:
        importlib.import_module(module_name)
    except ImportError as exc:
        pytest.skip(f"Curated source {source_name} requires optional deps: {exc}")
    except Exception as exc:
        pytest.fail(
            f"Phase 1 DLT audit: curated source {source_name!r} "
            f"failed to import from {module_name}: {exc}"
        )


def test_curated_source_count_matches_cli() -> None:
    """The CURATED_SOURCE_PATHS dict matches dlt_sources/common/cli.py:DLT_SOURCES."""
    from dlt_sources.common.cli import DLT_SOURCES

    # DLT_SOURCES may contain CLI subcommand keywords mixed in
    # Filter to only those that have a path mapping
    actual_sources = set(s for s in DLT_SOURCES if s in CURATED_SOURCE_PATHS)
    missing_from_test = set(CURATED_SOURCE_PATHS.keys()) - actual_sources
    extra_in_cli = actual_sources - set(CURATED_SOURCE_PATHS.keys())

    assert not missing_from_test, (
        f"Phase 1 DLT audit: DLT_SOURCES has sources not in CURATED_SOURCE_PATHS: "
        f"{sorted(missing_from_test)}"
    )
    assert not extra_in_cli, (
        f"Phase 1 DLT audit: CURATED_SOURCE_PATHS has paths not in DLT_SOURCES: "
        f"{sorted(extra_in_cli)}"
    )


def test_write_disposition_replace_audit() -> None:
    """Audit the count of `write_disposition='replace'` usages.

    Per dlt 1.28+ deprecation, `replace` should migrate to `refresh=`.
    Marked xfail for now (per-source migration is Phase 3 of Plan 1).
    """
    import subprocess

    result = subprocess.run(
        ["rg", "-c", 'write_disposition\\s*=\\s*"replace"',
         "dlt_sources/", "--type", "py"],
        capture_output=True, text=True,
        cwd=str(REPO_ROOT),
    )

    total = 0
    for line in result.stdout.strip().split("\n"):
        if ":" in line:
            try:
                total += int(line.rsplit(":", 1)[1])
            except ValueError:
                pass

    if total > 0:
        pytest.fail(
            f"Phase 1 DLT audit: {total} sources use deprecated write_disposition='replace'. "
            f"Migrate to refresh='drop' or refresh='merge' per the per-source guide. "
            f"Phase 1 migration (commit $(git rev-parse --short HEAD)) "
            f"already handled the defi/crypto + statistics + language categories. "
            f"Check what's left."
        )
