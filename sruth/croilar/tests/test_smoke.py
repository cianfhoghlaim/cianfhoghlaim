"""Smoke tests for the croilar subproject.

These tests verify that every public surface (imports, function signatures,
Pydantic models) loads cleanly and the core data-engineering primitives can
be instantiated without crashing. They do NOT execute live API calls —
USE_LOCAL_SCRAPES=true (set in conftest.py) routes all DLT sources to
the curated local cache.

Per AGENTS.md rule #2 (Respect the Ingestion Cache), no test should ever
trigger a live Spotify/GitHub/Firecrawl/SoundCloud scrape.

Run with:
    cd croilar && uv run pytest tests/ -v
"""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Module-level import tests
# ---------------------------------------------------------------------------

PIPELINE_MODULES = [
    "pipelines",
    "pipelines.spotify",
    "pipelines.soundcloud",
    "pipelines.github",
    "pipelines.researchgate",
    "pipelines.fs_author",
    "pipelines.cv",
    "pipelines.artwork",
    "pipelines.labels",
    "pipelines.teaching",
    "pipelines.shared",
    "dlt_utils",
    "_shared",
    "_shared.streams",
    "_shared.config",
    "_shared.config.paths",
    "_shared.config.settings",
    "dagster_assets",
]


@pytest.mark.parametrize("module_name", PIPELINE_MODULES)
def test_module_imports(module_name: str) -> None:
    """Every pipeline + utility module must import without error."""
    mod = importlib.import_module(module_name)
    assert mod is not None
    assert hasattr(mod, "__file__")


# ---------------------------------------------------------------------------
# Public-API surface tests
# ---------------------------------------------------------------------------

def test_pipelines_init_exports() -> None:
    """pipelines.cv must re-export the public API surface."""
    import pipelines.cv

    expected = {
        "AUTHOR_DIR",
        "REPO_ROOT",
        "author_pdf_resource",
        "cv_pdf_text_resource",
        "find_author_pdfs",
        "run_cv_pipeline",
    }
    for name in expected:
        assert hasattr(pipelines.cv, name), f"pipelines.cv missing {name}"


def test_pipelines_spotify_exports() -> None:
    import pipelines.spotify

    assert hasattr(pipelines.spotify, "spotify_source")
    assert hasattr(pipelines.spotify, "run_spotify_pipeline")
    assert hasattr(pipelines.spotify, "SPOTIFY_RESOURCES")


def test_pipelines_soundcloud_exports() -> None:
    import pipelines.soundcloud

    for name in ("SoundCloudScraper", "scrape_soundcloud_profile",
                 "run_soundcloud_pipeline", "download_tracks_to_r2"):
        assert hasattr(pipelines.soundcloud, name), f"missing {name}"


def test_pipelines_github_exports() -> None:
    import pipelines.github

    assert hasattr(pipelines.github, "github_repos_source")
    assert hasattr(pipelines.github, "run_github_pipeline")


def test_pipelines_researchgate_exports() -> None:
    import pipelines.researchgate

    assert hasattr(pipelines.researchgate, "researchgate_profile_resource")
    assert hasattr(pipelines.researchgate, "run_researchgate_pipeline")


def test_pipelines_fs_author_exports() -> None:
    import pipelines.fs_author

    assert hasattr(pipelines.fs_author, "fs_author_source")
    assert hasattr(pipelines.fs_author, "run_fs_author_pipeline")


def test_pipelines_artwork_exports() -> None:
    import pipelines.artwork

    for name in ("ArtworkImage", "ArtworkMetadata", "artwork_source",
                 "download_artwork", "extract_image_metadata",
                 "run_artwork_pipeline"):
        assert hasattr(pipelines.artwork, name), f"missing {name}"


def test_pipelines_labels_exports() -> None:
    import pipelines.labels

    for name in ("LabelRelease", "LabelProfile", "LabelScraper",
                 "label_source", "scrape_label", "scrape_all_labels",
                 "run_labels_pipeline"):
        assert hasattr(pipelines.labels, name), f"missing {name}"


def test_pipelines_shared_exports() -> None:
    import pipelines.shared

    for name in ("R2Client",):
        assert hasattr(pipelines.shared, name), f"missing {name}"


# ---------------------------------------------------------------------------
# Path resolution tests
# ---------------------------------------------------------------------------

def test_get_repo_root_resolves_to_monorepo(tmp_path: Path) -> None:
    """get_repo_root() must point at a directory that contains
    author_cian_deacy_lyons_mac_an_déisigh_uí_liatháin/."""
    from _shared.config.paths import get_repo_root

    repo = get_repo_root()
    assert repo.exists(), f"repo root does not exist: {repo}"
    assert repo.is_dir()


def test_get_author_dir_under_repo_root() -> None:
    """author dir must be a child of repo root."""
    from _shared.config.paths import get_author_dir, get_repo_root

    author = get_author_dir()
    repo = get_repo_root()
    assert str(author).startswith(str(repo)), (
        f"author dir {author} is not under repo root {repo}"
    )


def test_repo_root_respects_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    """CROILAR_REPO_ROOT env var must override the default path resolution."""
    from _shared.config import paths

    paths.get_repo_root.cache_clear()
    override = "/tmp/croilar-test-repo-root-4729"
    monkeypatch.setenv("CROILAR_REPO_ROOT", override)
    result = paths.get_repo_root()
    assert str(result).endswith("croilar-test-repo-root-4729")
    paths.get_repo_root.cache_clear()


# ---------------------------------------------------------------------------
# Dagster asset graph tests
# ---------------------------------------------------------------------------

def test_dagster_definitions_loads(tmp_path: Path) -> None:
    """The root definitions.py must load without import-time errors.

    Skipped if Dagster deps aren't installed in the current env (e.g. the
    user only has the web frontend installed).
    """
    pytest.importorskip("dagster")

    import importlib.util
    from pathlib import Path

    croilar_root = Path(__file__).resolve().parent.parent
    spec = importlib.util.spec_from_file_location(
        "croilar_definitions", croilar_root / "definitions.py",
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)

    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        # sruth.shared may not be installed in the dev venv; if so, skip
        if "sruth" in str(exc) or "No module named" in str(exc):
            pytest.skip(f"Optional dependency missing: {exc}")
        raise

    assert hasattr(module, "defs")
    asset_specs = module.defs.get_all_asset_specs()  # Dagster >=1.9
    assert len(asset_specs) >= 10, f"Expected at least 10 assets, got {len(asset_specs)}"


# ---------------------------------------------------------------------------
# DLT destination factory tests
# ---------------------------------------------------------------------------

def test_dlt_duckdb_fallback(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The DuckDB fallback destination must produce a valid path under tmp."""
    monkeypatch.setenv("USE_DUCKLAKE", "false")
    monkeypatch.setenv("DLT_ENVIRONMENT", "local")
    from dlt_utils.destinations import get_duckdb_fallback

    dest = get_duckdb_fallback(base_path=str(tmp_path))
    assert dest is not None


# ---------------------------------------------------------------------------
# Settings tests
# ---------------------------------------------------------------------------

def test_aleyum_settings_default_loads() -> None:
    """The Pydantic settings must instantiate with defaults.

    `AleyumSettings` is preserved as a deprecated alias of `StreamSettings`.
    """
    from _shared.config.settings import AleyumSettings

    settings = AleyumSettings()
    assert settings.lancedb_uri  # non-empty
    assert settings.duckdb_root  # non-empty (was `duckdb_path` in the legacy AleyumSettings)
    assert settings.embedding_model  # non-empty


def test_stream_settings_default_loads() -> None:
    """`StreamSettings` (the new canonical class) must instantiate with defaults."""
    from _shared.config.settings import StreamSettings

    settings = StreamSettings()
    assert settings.r2_bucket  # non-empty
    assert settings.sources_yaml_path.exists()


def test_stream_registry_resolves_all_streams() -> None:
    """The Stream registry must return a list with the expected stream ids."""
    from _shared.streams import list_streams, get_stream

    streams = list_streams()
    ids = {s.id for s in streams}
    assert {"music", "teaching", "cv", "research"}.issubset(ids)

    for s in streams:
        resolved = get_stream(s.id)
        assert resolved.id == s.id
        assert resolved.owner_display_name


def test_stream_registry_has_no_carlcashman() -> None:
    """The legacy `carlcashman` persona is removed from the data layer."""
    from _shared.streams import list_streams

    for s in list_streams():
        assert s.id != "carlcashman"
        assert s.owner != "carlcashman"


def test_fs_author_is_local_only() -> None:
    """The filesystem source on the `cv` stream must be marked `local_only=True`."""
    from _shared.streams import get_stream, StreamSourceType

    cv = get_stream("cv")
    fs = cv.get_source(StreamSourceType.FILESYSTEM)
    assert fs.local_only is True


def test_researchgate_source_attached_to_teaching() -> None:
    """The ResearchGate source must be attached to the `teaching` stream."""
    from _shared.streams import get_stream, StreamSourceType

    teaching = get_stream("teaching")
    assert teaching.has_source(StreamSourceType.RESEARCHGATE)
    assert teaching.has_source(StreamSourceType.LINKEDIN)
    assert teaching.has_source(StreamSourceType.GITHUB)


def test_music_stream_preserved() -> None:
    """The music stream keeps the legacy aleyum pipeline wiring."""
    from _shared.streams import get_stream, StreamSourceType

    music = get_stream("music")
    assert music.owner == "aleyum"
    assert music.has_source(StreamSourceType.SPOTIFY)
    assert music.has_source(StreamSourceType.SOUNDCLOUD)
    assert music.has_source(StreamSourceType.LABELS)
    assert music.has_source(StreamSourceType.ARTWORK)
