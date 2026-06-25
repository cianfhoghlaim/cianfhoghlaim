"""
DuckDB-based cache for architecture documents.

Uses SerialDatabaseExecutor for thread-safe single-threaded access.
"""

import hashlib
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from .types import ArchDocument, CacheConfig, RepoType

logger = logging.getLogger(__name__)


class ArchDocCache:
    """
    Cache for architecture documents using DuckDB.

    IMPORTANT: DuckDB is SINGLE_THREADED_ONLY.
    All operations go through SerialDatabaseExecutor.
    """

    def __init__(self, config: CacheConfig | None = None):
        self.config = config or CacheConfig()
        self._db = None
        self._executor = None

    async def _get_executor(self):
        """Get or create the serial database executor."""
        if self._executor is None:
            try:
                from sruth.oideachais.core.storage.serial_executor import get_executor
                self._executor = await get_executor()
            except ImportError:
                # Fallback for standalone usage
                logger.warning("SerialDatabaseExecutor not available, cache disabled")
                return None
        return self._executor

    async def _init_db(self) -> None:
        """Initialize the database schema."""
        executor = await self._get_executor()
        if executor is None:
            return

        import duckdb

        db_path = str(self.config.db_path)

        async def init():
            conn = duckdb.connect(db_path)
            conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.config.table_name} (
                    cache_key VARCHAR PRIMARY KEY,
                    repo_path VARCHAR,
                    repo_type VARCHAR,
                    git_sha VARCHAR,
                    document JSON,
                    created_at TIMESTAMP,
                    expires_at TIMESTAMP
                )
            """)
            conn.close()

        await executor.run(init)

    def _compute_cache_key(
        self,
        repo_path: str | Path,
        git_sha: str | None,
    ) -> str:
        """Compute a cache key for a repo."""
        key_parts = [str(repo_path)]
        if git_sha:
            key_parts.append(git_sha)
        key_str = ":".join(key_parts)
        return hashlib.sha256(key_str.encode()).hexdigest()[:32]

    async def get(
        self,
        repo_path: str | Path,
        git_sha: str | None = None,
    ) -> ArchDocument | None:
        """Get a cached document if available and not expired."""
        if not self.config.enabled:
            return None

        executor = await self._get_executor()
        if executor is None:
            return None

        await self._init_db()

        import duckdb

        cache_key = self._compute_cache_key(repo_path, git_sha)
        db_path = str(self.config.db_path)
        now = datetime.utcnow()

        async def query():
            conn = duckdb.connect(db_path)
            result = conn.execute(
                f"""
                SELECT document FROM {self.config.table_name}
                WHERE cache_key = ?
                AND expires_at > ?
                """,
                [cache_key, now],
            ).fetchone()
            conn.close()
            return result

        result = await executor.run(query)

        if result:
            doc_json = result[0]
            if isinstance(doc_json, str):
                doc_dict = json.loads(doc_json)
            else:
                doc_dict = doc_json
            return self._dict_to_document(doc_dict)

        return None

    async def set(
        self,
        repo_path: str | Path,
        document: ArchDocument,
        git_sha: str | None = None,
    ) -> None:
        """Cache a document."""
        if not self.config.enabled:
            return

        executor = await self._get_executor()
        if executor is None:
            return

        await self._init_db()

        import duckdb

        cache_key = self._compute_cache_key(repo_path, git_sha)
        db_path = str(self.config.db_path)
        now = datetime.utcnow()
        expires_at = now + timedelta(hours=self.config.ttl_hours)
        doc_json = json.dumps(self._document_to_dict(document))

        async def insert():
            conn = duckdb.connect(db_path)
            conn.execute(
                f"""
                INSERT OR REPLACE INTO {self.config.table_name}
                (cache_key, repo_path, repo_type, git_sha, document, created_at, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    cache_key,
                    str(repo_path),
                    document.repo_type.value,
                    git_sha,
                    doc_json,
                    now,
                    expires_at,
                ],
            )
            conn.close()

        await executor.run(insert)
        logger.info(f"Cached document for {repo_path} (expires: {expires_at})")

    async def invalidate(
        self,
        repo_path: str | Path,
        git_sha: str | None = None,
    ) -> None:
        """Invalidate a cached document."""
        executor = await self._get_executor()
        if executor is None:
            return

        await self._init_db()

        import duckdb

        cache_key = self._compute_cache_key(repo_path, git_sha)
        db_path = str(self.config.db_path)

        async def delete():
            conn = duckdb.connect(db_path)
            conn.execute(
                f"DELETE FROM {self.config.table_name} WHERE cache_key = ?",
                [cache_key],
            )
            conn.close()

        await executor.run(delete)

    async def cleanup_expired(self) -> int:
        """Remove expired entries. Returns count of removed entries."""
        executor = await self._get_executor()
        if executor is None:
            return 0

        await self._init_db()

        import duckdb

        db_path = str(self.config.db_path)
        now = datetime.utcnow()

        async def cleanup():
            conn = duckdb.connect(db_path)
            result = conn.execute(
                f"DELETE FROM {self.config.table_name} WHERE expires_at < ? RETURNING cache_key",
                [now],
            ).fetchall()
            conn.close()
            return len(result)

        count = await executor.run(cleanup)
        logger.info(f"Cleaned up {count} expired cache entries")
        return count

    def _document_to_dict(self, doc: ArchDocument) -> dict[str, Any]:
        """Convert document to dict for JSON storage."""
        return {
            "title": doc.title,
            "repo_type": doc.repo_type.value,
            "description": doc.description,
            "sections": [
                {
                    "title": s.title,
                    "content": s.content,
                    "prompt_template": s.prompt_template,
                    "mermaid_diagram": s.mermaid_diagram,
                    "metadata": s.metadata,
                }
                for s in doc.sections
            ],
            "generated_at": doc.generated_at.isoformat(),
            "git_sha": doc.git_sha,
            "repo_path": doc.repo_path,
            "languages": doc.languages,
            "dependencies": doc.dependencies,
            "metadata": doc.metadata,
        }

    def _dict_to_document(self, data: dict[str, Any]) -> ArchDocument:
        """Convert dict back to document."""
        from .types import ArchSection

        return ArchDocument(
            title=data["title"],
            repo_type=RepoType(data["repo_type"]),
            description=data["description"],
            sections=[
                ArchSection(
                    title=s["title"],
                    content=s["content"],
                    prompt_template=s.get("prompt_template"),
                    mermaid_diagram=s.get("mermaid_diagram"),
                    metadata=s.get("metadata", {}),
                )
                for s in data["sections"]
            ],
            generated_at=datetime.fromisoformat(data["generated_at"]),
            git_sha=data.get("git_sha"),
            repo_path=data.get("repo_path"),
            languages=data.get("languages", {}),
            dependencies=data.get("dependencies", []),
            metadata=data.get("metadata", {}),
        )
