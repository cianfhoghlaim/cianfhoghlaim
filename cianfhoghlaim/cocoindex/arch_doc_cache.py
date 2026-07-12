"""
arch_doc_cache — v1 CocoIndex primitive (Phase 0 of
`2026-07-14-multimodal-code-and-media-intel-v1`).

Ported from the archived `códeolas`
(`stedding/dev/cianfhoghlaim copy/sruth/códeolas/generators/reposwarm/cache.py:ArchDocCache`).

The archived cache was DuckDB-backed (single-threaded via
`SerialDatabaseExecutor`), keyed by `(repo_path, git_sha)` with a TTL.
The v1 primitive keeps the same DuckDB-by-git-SHA contract but wraps
the executor inside a CocoIndex `ContextKey` + a small async API.

The `ArchDoc` dataclass carries the 4-section doc the `repo_arch_docs`
App synthesises (Overview / Components / Data Layer / Dependencies)
plus the Mermaid diagram + the metadata used by the MCP tool
`arch_doc_for_repo` to short-circuit a re-generation.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import structlog

from ._lifespan import COCOINDEX_AVAILABLE

# CocoIndex is optional — degrade gracefully if not installed.
try:
    import cocoindex as coco  # type: ignore[import-not-found]

    COCOINDEX_AVAILABLE_LOCAL = COCOINDEX_AVAILABLE
except ImportError:  # pragma: no cover
    coco = None  # type: ignore[assignment]
    COCOINDEX_AVAILABLE_LOCAL = False

logger = structlog.get_logger(__name__)


# not-a-flow: this primitive uses DuckDB directly per the archived
# codeolas pattern and never writes to a LanceDB table. The Phase 4
# `repo_arch_docs` App emits one row to the `repo_arch_docs` LanceDB
# table per `(repo_path, git_sha)`; the cache check happens before the
# App writes, so the App's R4 contract is unaffected.
# See `openspec/changes/2026-07-14-multimodal-code-and-media-intel-v1/proposal.md`
# "Phase 0 — Port the archived codeolas primitives".


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


DEFAULT_DB_PATH = Path(
    os.getenv(
        "ARCH_DOC_CACHE_DB_PATH",
        str(Path.home() / ".cache" / "cianfhoghlaim" / "arch_doc_cache.duckdb"),
    )
)
DEFAULT_TABLE_NAME = "arch_doc_cache_v1"
DEFAULT_TTL_HOURS = int(os.getenv("ARCH_DOC_CACHE_TTL_HOURS", "168"))  # 7 days


@dataclass(frozen=True)
class CacheConfig:
    """Cache configuration."""

    db_path: Path = DEFAULT_DB_PATH
    table_name: str = DEFAULT_TABLE_NAME
    ttl_hours: int = DEFAULT_TTL_HOURS
    enabled: bool = True


# ---------------------------------------------------------------------------
# ArchDoc dataclass (the cached value)
# ---------------------------------------------------------------------------


@dataclass
class ArchSection:
    """One section of an architecture doc."""

    title: str
    content: str
    prompt_template: str | None = None
    mermaid_diagram: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ArchDoc:
    """The cached architecture document for one `(repo_path, git_sha)` tuple."""

    title: str
    repo_path: str
    git_sha: str | None
    repo_type: str
    description: str
    sections: list[ArchSection]
    languages: dict[str, int]
    dependencies: list[str]
    generated_at: datetime
    mermaid_diagram: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize for JSON storage."""
        return {
            "title": self.title,
            "repo_path": self.repo_path,
            "git_sha": self.git_sha,
            "repo_type": self.repo_type,
            "description": self.description,
            "sections": [
                {
                    "title": s.title,
                    "content": s.content,
                    "prompt_template": s.prompt_template,
                    "mermaid_diagram": s.mermaid_diagram,
                    "metadata": s.metadata,
                }
                for s in self.sections
            ],
            "languages": self.languages,
            "dependencies": self.dependencies,
            "generated_at": self.generated_at.isoformat(),
            "mermaid_diagram": self.mermaid_diagram,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ArchDoc:
        """Deserialize from JSON."""
        return cls(
            title=data["title"],
            repo_path=data["repo_path"],
            git_sha=data.get("git_sha"),
            repo_type=data["repo_type"],
            description=data.get("description", ""),
            sections=[
                ArchSection(
                    title=s["title"],
                    content=s["content"],
                    prompt_template=s.get("prompt_template"),
                    mermaid_diagram=s.get("mermaid_diagram"),
                    metadata=s.get("metadata", {}),
                )
                for s in data.get("sections", [])
            ],
            languages=dict(data.get("languages", {})),
            dependencies=list(data.get("dependencies", [])),
            generated_at=datetime.fromisoformat(data["generated_at"]),
            mermaid_diagram=data.get("mermaid_diagram"),
            metadata=dict(data.get("metadata", {})),
        )


# ---------------------------------------------------------------------------
# ContextKey (R1 conformance: uses the shared cocoindex import surface)
# ---------------------------------------------------------------------------


if COCOINDEX_AVAILABLE_LOCAL and coco is not None:
    ARCH_DOC_CACHE = coco.ContextKey[CacheConfig]("oideachais_arch_doc_cache")  # type: ignore[index]
else:
    ARCH_DOC_CACHE = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# The cache (DuckDB, single-threaded per the archived contract)
# ---------------------------------------------------------------------------


def _compute_cache_key(repo_path: str | Path, git_sha: str | None) -> str:
    """Stable cache key (matches the archived implementation)."""
    parts = [str(repo_path)]
    if git_sha:
        parts.append(git_sha)
    raw = ":".join(parts).encode()
    return hashlib.sha256(raw).hexdigest()[:32]


def _ensure_schema(conn: Any, table_name: str) -> None:
    """Create the cache table if it doesn't exist."""
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            cache_key VARCHAR PRIMARY KEY,
            repo_path VARCHAR,
            repo_type VARCHAR,
            git_sha VARCHAR,
            doc_json JSON,
            created_at TIMESTAMP,
            expires_at TIMESTAMP
        )
        """
    )


async def _init_db(config: CacheConfig) -> None:
    """Create the cache DB file + schema if missing."""
    db_path = Path(config.db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    import duckdb

    conn = duckdb.connect(str(db_path))
    try:
        _ensure_schema(conn, config.table_name)
    finally:
        conn.close()


async def arch_doc_cache_get(
    repo_path: str | Path,
    git_sha: str | None,
    config: CacheConfig | None = None,
) -> ArchDoc | None:
    """Return the cached ArchDoc for `(repo_path, git_sha)` if it exists and is fresh.

    Returns None on cache miss, on expiry, or when caching is disabled.
    """
    cfg = config or CacheConfig()
    if not cfg.enabled:
        return None

    await _init_db(cfg)
    import duckdb

    cache_key = _compute_cache_key(repo_path, git_sha)
    now = datetime.now()

    conn = duckdb.connect(str(cfg.db_path))
    try:
        row = conn.execute(
            f"""
            SELECT doc_json FROM {cfg.table_name}
            WHERE cache_key = ?
              AND expires_at > ?
            """,
            [cache_key, now],
        ).fetchone()
    finally:
        conn.close()

    if not row:
        return None

    doc_data = row[0]
    if isinstance(doc_data, str):
        doc_data = json.loads(doc_data)
    return ArchDoc.from_dict(doc_data)


async def arch_doc_cache_set(
    repo_path: str | Path,
    doc: ArchDoc,
    git_sha: str | None,
    config: CacheConfig | None = None,
) -> None:
    """Cache an ArchDoc for `(repo_path, git_sha)` with the configured TTL."""
    cfg = config or CacheConfig()
    if not cfg.enabled:
        return

    await _init_db(cfg)
    import duckdb

    cache_key = _compute_cache_key(repo_path, git_sha)
    now = datetime.now()
    expires_at = now + timedelta(hours=cfg.ttl_hours)
    doc_json = json.dumps(doc.to_dict())

    conn = duckdb.connect(str(cfg.db_path))
    try:
        conn.execute(
            f"""
            INSERT OR REPLACE INTO {cfg.table_name}
            (cache_key, repo_path, repo_type, git_sha, doc_json, created_at, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                cache_key,
                str(repo_path),
                doc.repo_type,
                git_sha,
                doc_json,
                now,
                expires_at,
            ],
        )
    finally:
        conn.close()

    logger.info(
        "arch_doc_cache.set",
        repo_path=str(repo_path),
        git_sha=git_sha,
        expires_at=expires_at.isoformat(),
    )


async def arch_doc_cache_invalidate(
    repo_path: str | Path,
    git_sha: str | None,
    config: CacheConfig | None = None,
) -> None:
    """Remove the cache entry for `(repo_path, git_sha)` (if any)."""
    cfg = config or CacheConfig()
    if not cfg.enabled:
        return

    await _init_db(cfg)
    import duckdb

    cache_key = _compute_cache_key(repo_path, git_sha)
    conn = duckdb.connect(str(cfg.db_path))
    try:
        conn.execute(
            f"DELETE FROM {cfg.table_name} WHERE cache_key = ?",
            [cache_key],
        )
    finally:
        conn.close()

    logger.info(
        "arch_doc_cache.invalidated",
        repo_path=str(repo_path),
        git_sha=git_sha,
    )


async def arch_doc_cache_cleanup_expired(
    config: CacheConfig | None = None,
) -> int:
    """Remove expired entries. Returns the count of removed rows."""
    cfg = config or CacheConfig()
    if not cfg.enabled:
        return 0

    await _init_db(cfg)
    import duckdb

    now = datetime.now()
    conn = duckdb.connect(str(cfg.db_path))
    try:
        rows = conn.execute(
            f"DELETE FROM {cfg.table_name} WHERE expires_at < ? RETURNING cache_key",
            [now],
        ).fetchall()
    finally:
        conn.close()

    count = len(rows)
    if count:
        logger.info("arch_doc_cache.cleaned_up_expired", count=count)
    return count


# ---------------------------------------------------------------------------
# v1 App stub (R2 conformance)
# ---------------------------------------------------------------------------


if COCOINDEX_AVAILABLE_LOCAL and coco is not None:
    arch_doc_cache_app = coco.App(coco.AppConfig(name="ArchDocCache"))  # type: ignore[attr-defined]
else:  # pragma: no cover
    arch_doc_cache_app = None


__all__ = [
    "ARCH_DOC_CACHE",
    "ArchDoc",
    "ArchSection",
    "CacheConfig",
    "arch_doc_cache_app",
    "arch_doc_cache_cleanup_expired",
    "arch_doc_cache_get",
    "arch_doc_cache_invalidate",
    "arch_doc_cache_set",
]
