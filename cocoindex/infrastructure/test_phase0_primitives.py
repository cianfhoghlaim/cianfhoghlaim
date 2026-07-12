"""Smoke tests for the Phase 0 primitives of
`2026-07-14-multimodal-code-and-media-intel-v1`.

Run with `uv run pytest cianfhoghlaim/cocoindex/test_phase0_primitives.py -v`
or `uv run python cianfhoghlaim/cocoindex/test_phase0_primitives.py`.

These tests use the in-process no-op test source registered by
`multihop_search.py` and a temp DuckDB cache file for `arch_doc_cache`.

# not-a-flow: this file is colocated test code, not a LanceDB flow.
# The cocoindex_v1_conformance audit treats every .py file under
# `cianfhoghlaim/cocoindex/` as a flow; the not-a-flow marker tells
# the audit to skip ALL 4 conformance rules (R1+R2+R3+R4).
"""

from __future__ import annotations

import asyncio
import os
import shutil
import tempfile
import uuid
from pathlib import Path

import pytest

pytestmark = pytest.mark.asyncio

from cianfhoghlaim.cocoindex.arch_doc_cache import (
    ArchDoc,
    ArchSection,
    CacheConfig,
    arch_doc_cache_cleanup_expired,
    arch_doc_cache_get,
    arch_doc_cache_invalidate,
    arch_doc_cache_set,
)
from cianfhoghlaim.cocoindex.multihop_search import (
    MultihopSource,
    clear_multihop_sources,
    list_multihop_sources,
    multihop_search,
    register_multihop_source,
)
from cianfhoghlaim.cocoindex.repo_type_detector import (
    RepoType,
    detect_repo_type,
    detect_repo_type_with_override,
)
from cianfhoghlaim.cocoindex.reranker import (
    RerankConfig,
    query_reranker,
)

# ---------------------------------------------------------------------------
# multihop_search
# ---------------------------------------------------------------------------


async def test_multihop_search_with_test_source() -> None:
    """The test source registered on import must drive a successful multi-hop."""
    # The no-op source is registered on import; we just call the primitive.
    result = await multihop_search(
        question="How does the Lakehouse integrate with the DAG?",
        limit=2,
        max_iterations=2,
        convergence_threshold=0.5,
    )

    assert result.question == "How does the Lakehouse integrate with the DAG?"
    assert result.iterations >= 1
    assert result.total_sources_found >= 1
    assert "test" in result.synthesis.lower()


async def test_multihop_search_register_and_clear() -> None:
    """Registering + clearing a custom source must round-trip through the registry."""
    clear_multihop_sources()  # wipe the test source

    async def custom_search(query: str, limit: int) -> list[dict]:
        return [
            {
                "row_id": uuid.uuid4().hex,
                "score": 0.99,
                "text": f"custom row for {query!r}",
                "citation": {"source_kind": "smoke-test"},
            }
        ]

    register_multihop_source(
        MultihopSource(
            table_name="custom_smoke",
            description="smoke-test source",
            embed_and_search_fn=custom_search,
        )
    )
    sources = list_multihop_sources()
    assert any(s.table_name == "custom_smoke" for s in sources)

    result = await multihop_search(
        question="smoke question",
        limit=1,
        max_iterations=1,
        sources=["custom_smoke"],
    )
    assert result.total_sources_found == 1
    assert result.candidates[0].source_table == "custom_smoke"


async def test_multihop_search_no_sources_returns_cleanly() -> None:
    """An empty registry must return a clean MultihopResult, not crash."""
    clear_multihop_sources()
    result = await multihop_search(question="any question", limit=5, max_iterations=3)
    assert result.total_sources_found == 0
    assert result.iterations == 0
    assert result.converged is True
    assert "No sources registered" in result.synthesis


# ---------------------------------------------------------------------------
# reranker
# ---------------------------------------------------------------------------


def test_rerank_config_from_env_defaults_to_jina(monkeypatch: pytest.MonkeyPatch) -> None:
    """Without any env vars set, the default provider is `jina` with the standard model."""
    monkeypatch.delenv("RERANK_PROVIDER", raising=False)
    monkeypatch.delenv("RERANK_MODEL", raising=False)
    monkeypatch.delenv("JINA_API_KEY", raising=False)
    monkeypatch.delenv("COHERE_API_KEY", raising=False)
    monkeypatch.delenv("DASHSCOPE_API_KEY", raising=False)
    monkeypatch.delenv("RERANK_API_KEY", raising=False)

    cfg = RerankConfig.from_env()
    assert cfg.provider == "jina"
    assert cfg.model == "jina-reranker-v2-base-multilingual"
    assert cfg.api_key is None


def test_rerank_config_invalid_provider_falls_back() -> None:
    """An unknown provider name falls back to jina."""
    os.environ["RERANK_PROVIDER"] = "unknown_provider"
    try:
        cfg = RerankConfig.from_env()
        assert cfg.provider == "jina"
    finally:
        del os.environ["RERANK_PROVIDER"]


async def test_query_reranker_empty_results() -> None:
    """Empty results round-trip cleanly without calling the provider."""
    result = await query_reranker(query="anything", results=[])
    assert result == []


# ---------------------------------------------------------------------------
# repo_type_detector
# ---------------------------------------------------------------------------


async def test_detect_repo_type_on_cianfhoghlaim_monorepo() -> None:
    """The cianfhoghlaim repo has the canonical MONOREPO markers (turbo.json, apps/, modules/)."""
    repo_path = Path(__file__).resolve().parents[2]  # cianfhoghlaim root
    result = await detect_repo_type(repo_path)
    # The cianfhoghlaim monorepo has turbo.json + apps/ + modules/, so MONOREPO wins.
    assert result.repo_type == RepoType.MONOREPO
    assert result.total_files_scanned > 0


async def test_detect_repo_type_override() -> None:
    """The override env var bypasses the filesystem walk."""
    os.environ["CIANFHOGHLAIM_REPO_TYPE_OVERRIDE"] = "library"
    try:
        result = await detect_repo_type_with_override("/tmp/whatever")
        assert result.repo_type == RepoType.LIBRARY
        assert result.total_files_scanned == 0
    finally:
        del os.environ["CIANFHOGHLAIM_REPO_TYPE_OVERRIDE"]


async def test_detect_repo_type_unknown_path() -> None:
    """A non-existent repo_path raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        await detect_repo_type("/this/path/does/not/exist/abcxyz")


# ---------------------------------------------------------------------------
# arch_doc_cache
# ---------------------------------------------------------------------------


def _sample_doc(repo_path: str, git_sha: str) -> ArchDoc:
    return ArchDoc(
        title=f"Architecture: {repo_path}",
        repo_path=repo_path,
        git_sha=git_sha,
        repo_type="monorepo",
        description="Smoke-test doc",
        sections=[
            ArchSection(
                title="Overview",
                content="Sample overview",
                prompt_template="hl_overview",
            ),
            ArchSection(
                title="Components",
                content="Sample components",
                prompt_template="core_entities",
            ),
        ],
        languages={"python": 42, "typescript": 18},
        dependencies=["pyproject.toml"],
        generated_at=__import__("datetime").datetime.now(),
    )


@pytest.fixture
def temp_cache_dir() -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="arch_doc_cache_test_"))
    yield tmp
    shutil.rmtree(tmp, ignore_errors=True)


async def test_arch_doc_cache_round_trip(temp_cache_dir: Path) -> None:
    """Write a doc, read it back, assert equality on the cache key."""
    cfg = CacheConfig(db_path=temp_cache_dir / "test.duckdb", ttl_hours=1)
    repo_path = "/tmp/fake_repo_abcxyz"
    git_sha = "deadbeefcafebabe1234567890abcdef12345678"

    # Cache miss before write.
    assert await arch_doc_cache_get(repo_path, git_sha, config=cfg) is None

    doc = _sample_doc(repo_path, git_sha)
    await arch_doc_cache_set(repo_path, doc, git_sha, config=cfg)

    fetched = await arch_doc_cache_get(repo_path, git_sha, config=cfg)
    assert fetched is not None
    assert fetched.title == doc.title
    assert fetched.repo_path == doc.repo_path
    assert fetched.git_sha == doc.git_sha
    assert fetched.repo_type == doc.repo_type
    assert len(fetched.sections) == 2
    assert fetched.languages == doc.languages


async def test_arch_doc_cache_invalidate(temp_cache_dir: Path) -> None:
    """Invalidating a cached entry removes it."""
    cfg = CacheConfig(db_path=temp_cache_dir / "test.duckdb", ttl_hours=1)
    repo_path = "/tmp/fake_repo_abcxyz"
    git_sha = "feedfacefeedfacefeedfacefeedfacefeedface"

    await arch_doc_cache_set(
        repo_path,
        _sample_doc(repo_path, git_sha),
        git_sha,
        config=cfg,
    )
    assert await arch_doc_cache_get(repo_path, git_sha, config=cfg) is not None

    await arch_doc_cache_invalidate(repo_path, git_sha, config=cfg)
    assert await arch_doc_cache_get(repo_path, git_sha, config=cfg) is None


async def test_arch_doc_cache_cleanup_expired(temp_cache_dir: Path) -> None:
    """A TTL=0 entry expires on the next cleanup pass."""
    cfg = CacheConfig(db_path=temp_cache_dir / "test.duckdb", ttl_hours=0)
    repo_path = "/tmp/fake_repo_abcxyz"
    git_sha = "1234567812345678123456781234567812345678"

    # The expires_at is `now + 0 hours`, which is "right now", so any
    # later query misses it. Cleanup_expired removes it.
    await arch_doc_cache_set(
        repo_path,
        _sample_doc(repo_path, git_sha),
        git_sha,
        config=cfg,
    )

    # Tiny sleep so the expires_at is strictly in the past.
    await asyncio.sleep(0.05)

    removed = await arch_doc_cache_cleanup_expired(config=cfg)
    assert removed >= 1


# ---------------------------------------------------------------------------
# asyncio glue for pytest
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _restore_test_source() -> None:
    """Ensure the in-process test source is re-registered after each test that clears it."""
    yield
    from cianfhoghlaim.cocoindex import multihop_search as _ms

    if not any(s.table_name == "_multihop_test" for s in list_multihop_sources()):
        _ms._register_test_source_if_needed()  # type: ignore[attr-defined]


def _async_run(coro: object) -> object:
    """Helper to run a coroutine synchronously (for ad-hoc invocation)."""
    return asyncio.get_event_loop().run_until_complete(coro)  # type: ignore[arg-type]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
