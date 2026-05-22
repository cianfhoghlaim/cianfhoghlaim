"""
Curriculum Service for Tuath.

Provides Celtic curriculum search across Irish, Welsh, and Scottish Gaelic.
"""

from pathlib import Path
from typing import Any

import lancedb
from sentence_transformers import SentenceTransformer


class CurriculumService:
    """Service for Celtic curriculum search."""

    def __init__(self, uri: str, embedding_model: str = "BAAI/bge-m3"):
        """Initialize LanceDB connection for curriculum search."""
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
        """Get or load embedding model (BGE-M3 for multilingual Celtic)."""
        if self._model is None:
            self._model = SentenceTransformer(self.embedding_model_name)
        return self._model

    def _embed(self, text: str) -> list[float]:
        """Generate embedding for text."""
        return self.model.encode(text).tolist()

    async def search_curriculum(
        self,
        query: str,
        nation: str | None = None,
        level: str | None = None,
        subject: str | None = None,
        limit: int = 10,
    ) -> list[dict]:
        """Search curriculum content across Celtic nations."""
        try:
            table = self.db.open_table("curriculum_embeddings")
            query_embedding = self._embed(query)

            search = table.search(query_embedding, vector_column_name="text_embedding")

            filter_conditions = []
            if nation:
                filter_conditions.append(f"nation = '{nation}'")
            if level:
                filter_conditions.append(f"level = '{level}'")
            if subject:
                filter_conditions.append(f"subject = '{subject}'")

            if filter_conditions:
                search = search.where(" AND ".join(filter_conditions))

            results = search.limit(limit).to_list()

            return [
                {
                    "id": r.get("id", ""),
                    "text": r.get("text", ""),
                    "nation": r.get("nation", ""),
                    "level": r.get("level", ""),
                    "subject": r.get("subject", ""),
                    "learning_outcome": r.get("learning_outcome", ""),
                    "score": 1.0 - r.get("_distance", 0),
                    "metadata": {
                        "strand": r.get("strand"),
                        "curriculum_code": r.get("curriculum_code"),
                        "language": r.get("language"),
                    },
                }
                for r in results
            ]
        except Exception:
            return []

    async def search_irish_curriculum(
        self,
        query: str,
        level: str | None = None,
        limit: int = 10,
    ) -> list[dict]:
        """Search Irish (NCCA) curriculum."""
        return await self.search_curriculum(
            query=query,
            nation="ireland",
            level=level,
            limit=limit,
        )

    async def search_welsh_curriculum(
        self,
        query: str,
        level: str | None = None,
        limit: int = 10,
    ) -> list[dict]:
        """Search Welsh (WJEC) curriculum."""
        return await self.search_curriculum(
            query=query,
            nation="wales",
            level=level,
            limit=limit,
        )

    async def search_scottish_curriculum(
        self,
        query: str,
        level: str | None = None,
        limit: int = 10,
    ) -> list[dict]:
        """Search Scottish Gaelic (SQA) curriculum."""
        return await self.search_curriculum(
            query=query,
            nation="scotland",
            level=level,
            limit=limit,
        )

    async def get_learning_outcomes(
        self,
        subject: str,
        nation: str,
        level: str | None = None,
    ) -> list[dict]:
        """Get learning outcomes for a subject."""
        try:
            table = self.db.open_table("curriculum_embeddings")
            df = table.to_pandas()

            filtered = df[(df["subject"] == subject) & (df["nation"] == nation)]
            if level:
                filtered = filtered[filtered["level"] == level]

            return [
                {
                    "learning_outcome": row["learning_outcome"],
                    "level": row["level"],
                    "strand": row.get("strand", ""),
                    "curriculum_code": row.get("curriculum_code", ""),
                }
                for _, row in filtered.iterrows()
            ]
        except Exception:
            return []

    async def get_curriculum_by_level(
        self,
        nation: str,
        level: str,
    ) -> dict:
        """Get curriculum overview by level."""
        try:
            table = self.db.open_table("curriculum_embeddings")
            df = table.to_pandas()

            filtered = df[(df["nation"] == nation) & (df["level"] == level)]

            subjects = filtered["subject"].unique().tolist()
            total_outcomes = len(filtered)

            return {
                "nation": nation,
                "level": level,
                "subjects": subjects,
                "total_outcomes": total_outcomes,
                "strands": filtered["strand"].dropna().unique().tolist(),
            }
        except Exception:
            return {
                "nation": nation,
                "level": level,
                "subjects": [],
                "total_outcomes": 0,
                "strands": [],
            }

    async def find_prerequisite_outcomes(
        self,
        learning_outcome: str,
        nation: str,
        limit: int = 5,
    ) -> list[dict]:
        """Find prerequisite learning outcomes for a given outcome."""
        try:
            table = self.db.open_table("curriculum_embeddings")
            query_embedding = self._embed(learning_outcome)

            search = table.search(query_embedding, vector_column_name="text_embedding")
            search = search.where(f"nation = '{nation}'")

            results = search.limit(limit + 1).to_list()

            prerequisites = []
            for r in results:
                if r.get("learning_outcome") != learning_outcome:
                    prerequisites.append({
                        "learning_outcome": r.get("learning_outcome", ""),
                        "level": r.get("level", ""),
                        "subject": r.get("subject", ""),
                        "similarity": 1.0 - r.get("_distance", 0),
                    })

            return prerequisites[:limit]
        except Exception:
            return []

    def list_nations(self) -> list[str]:
        """List all available nations."""
        try:
            table = self.db.open_table("curriculum_embeddings")
            result = table.to_pandas()["nation"].unique().tolist()
            return [n for n in result if n]
        except Exception:
            return []

    def list_levels(self, nation: str | None = None) -> list[str]:
        """List all levels, optionally filtered by nation."""
        try:
            table = self.db.open_table("curriculum_embeddings")
            df = table.to_pandas()
            if nation:
                df = df[df["nation"] == nation]
            result = df["level"].unique().tolist()
            return [l for l in result if l]
        except Exception:
            return []

    def list_subjects(self, nation: str | None = None) -> list[str]:
        """List all subjects, optionally filtered by nation."""
        try:
            table = self.db.open_table("curriculum_embeddings")
            df = table.to_pandas()
            if nation:
                df = df[df["nation"] == nation]
            result = df["subject"].unique().tolist()
            return [s for s in result if s]
        except Exception:
            return []
