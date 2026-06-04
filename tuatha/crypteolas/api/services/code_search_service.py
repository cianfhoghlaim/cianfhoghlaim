"""
Code Search Service for Crypteolas.

Provides semantic code search using LanceDB with CodeBERT embeddings.
"""

from pathlib import Path
from typing import Any

import lancedb
from sentence_transformers import SentenceTransformer


class CodeSearchService:
    """Service for semantic code search."""

    def __init__(self, uri: str, embedding_model: str = "microsoft/codebert-base"):
        """Initialize LanceDB connection for code search."""
        self.uri = uri
        self.embedding_model_name = embedding_model
        self._db = None
        self._model = None

        Path(uri).mkdir(parents=True, exist_ok=True)

    @property
    def db(self):
        """Get or create LanceDB connection."""
        if self._db is None:
            self._db = lancedb.connect(self.uri)
        return self._db

    @property
    def model(self) -> SentenceTransformer:
        """Get or load embedding model."""
        if self._model is None:
            self._model = SentenceTransformer(self.embedding_model_name)
        return self._model

    def _embed(self, text: str) -> list[float]:
        """Generate embedding for code/text."""
        return self.model.encode(text).tolist()

    async def search_code(
        self,
        query: str,
        repo: str | None = None,
        language: str | None = None,
        file_type: str | None = None,
        limit: int = 10,
    ) -> list[dict]:
        """Search code semantically across indexed repositories."""
        try:
            table = self.db.open_table("code_embeddings")
            query_embedding = self._embed(query)

            search = table.search(query_embedding, vector_column_name="code_embedding")

            filter_conditions = []
            if repo:
                filter_conditions.append(f"repo = '{repo}'")
            if language:
                filter_conditions.append(f"language = '{language}'")
            if file_type:
                filter_conditions.append(f"file_type = '{file_type}'")

            if filter_conditions:
                search = search.where(" AND ".join(filter_conditions))

            results = search.limit(limit).to_list()

            return [
                {
                    "id": r.get("id", ""),
                    "code": r.get("code", ""),
                    "file_path": r.get("file_path", ""),
                    "function_name": r.get("function_name", ""),
                    "score": 1.0 - r.get("_distance", 0),
                    "repo": r.get("repo", ""),
                    "language": r.get("language", ""),
                    "metadata": {
                        "line_start": r.get("line_start"),
                        "line_end": r.get("line_end"),
                        "docstring": r.get("docstring"),
                    },
                }
                for r in results
            ]
        except Exception as e:
            return []

    async def search_functions(
        self,
        query: str,
        repo: str | None = None,
        limit: int = 10,
    ) -> list[dict]:
        """Search for function definitions."""
        try:
            table = self.db.open_table("code_embeddings")
            query_embedding = self._embed(query)

            search = table.search(query_embedding, vector_column_name="code_embedding")
            search = search.where("chunk_type = 'function'")

            if repo:
                search = search.where(f"repo = '{repo}'")

            results = search.limit(limit).to_list()

            return [
                {
                    "function_name": r.get("function_name", ""),
                    "signature": r.get("signature", ""),
                    "docstring": r.get("docstring", ""),
                    "code": r.get("code", ""),
                    "file_path": r.get("file_path", ""),
                    "repo": r.get("repo", ""),
                    "score": 1.0 - r.get("_distance", 0),
                }
                for r in results
            ]
        except Exception:
            return []

    async def find_similar_code(
        self,
        code_snippet: str,
        exclude_repo: str | None = None,
        limit: int = 5,
    ) -> list[dict]:
        """Find similar code across repositories."""
        try:
            table = self.db.open_table("code_embeddings")
            query_embedding = self._embed(code_snippet)

            search = table.search(query_embedding, vector_column_name="code_embedding")

            if exclude_repo:
                search = search.where(f"repo != '{exclude_repo}'")

            results = search.limit(limit).to_list()

            return [
                {
                    "code": r.get("code", ""),
                    "file_path": r.get("file_path", ""),
                    "repo": r.get("repo", ""),
                    "similarity": 1.0 - r.get("_distance", 0),
                }
                for r in results
            ]
        except Exception:
            return []

    def list_indexed_repos(self) -> list[str]:
        """List all indexed repositories."""
        try:
            table = self.db.open_table("code_embeddings")
            result = table.to_pandas()["repo"].unique().tolist()
            return result
        except Exception:
            return []

    def get_repo_stats(self, repo: str) -> dict:
        """Get statistics for a repository."""
        try:
            table = self.db.open_table("code_embeddings")
            df = table.to_pandas()
            repo_df = df[df["repo"] == repo]

            return {
                "repo": repo,
                "total_chunks": len(repo_df),
                "languages": repo_df["language"].unique().tolist(),
                "functions": len(repo_df[repo_df["chunk_type"] == "function"]),
                "classes": len(repo_df[repo_df["chunk_type"] == "class"]),
            }
        except Exception:
            return {"repo": repo, "total_chunks": 0, "languages": [], "functions": 0, "classes": 0}
