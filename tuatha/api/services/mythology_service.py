"""
Mythology Service for Tuath.

Provides Celtic mythology and folklore content for NPC dialogue and quests.
"""

from pathlib import Path
from typing import Any

import lancedb
from sentence_transformers import SentenceTransformer


class MythologyService:
    """Service for Celtic mythology and folklore."""

    def __init__(self, uri: str, embedding_model: str = "BAAI/bge-m3"):
        """Initialize LanceDB connection for mythology search."""
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
        """Generate embedding for text."""
        return self.model.encode(text).tolist()

    async def search_mythology(
        self,
        query: str,
        tradition: str | None = None,
        entity_type: str | None = None,
        limit: int = 10,
    ) -> list[dict]:
        """Search mythology content."""
        try:
            table = self.db.open_table("mythology_embeddings")
            query_embedding = self._embed(query)

            search = table.search(query_embedding, vector_column_name="text_embedding")

            filter_conditions = []
            if tradition:
                filter_conditions.append(f"tradition = '{tradition}'")
            if entity_type:
                filter_conditions.append(f"entity_type = '{entity_type}'")

            if filter_conditions:
                search = search.where(" AND ".join(filter_conditions))

            results = search.limit(limit).to_list()

            return [
                {
                    "id": r.get("id", ""),
                    "name": r.get("name", ""),
                    "text": r.get("text", ""),
                    "tradition": r.get("tradition", ""),
                    "entity_type": r.get("entity_type", ""),
                    "score": 1.0 - r.get("_distance", 0),
                    "metadata": {
                        "cycle": r.get("cycle"),
                        "source": r.get("source"),
                        "related_figures": r.get("related_figures", []),
                    },
                }
                for r in results
            ]
        except Exception:
            return []

    async def get_deity(
        self,
        name: str,
        tradition: str | None = None,
    ) -> dict | None:
        """Get a specific deity by name."""
        try:
            table = self.db.open_table("mythology_embeddings")
            df = table.to_pandas()

            filtered = df[
                (df["name"].str.lower() == name.lower())
                & (df["entity_type"] == "deity")
            ]
            if tradition:
                filtered = filtered[filtered["tradition"] == tradition]

            if len(filtered) == 0:
                return None

            row = filtered.iloc[0]
            return {
                "name": row["name"],
                "tradition": row["tradition"],
                "text": row["text"],
                "attributes": row.get("attributes", []),
                "domains": row.get("domains", []),
                "related_figures": row.get("related_figures", []),
                "cycle": row.get("cycle"),
            }
        except Exception:
            return None

    async def get_story(
        self,
        title: str,
        tradition: str | None = None,
    ) -> dict | None:
        """Get a specific story by title."""
        try:
            table = self.db.open_table("mythology_embeddings")
            df = table.to_pandas()

            filtered = df[
                (df["name"].str.lower() == title.lower())
                & (df["entity_type"] == "story")
            ]
            if tradition:
                filtered = filtered[filtered["tradition"] == tradition]

            if len(filtered) == 0:
                return None

            row = filtered.iloc[0]
            return {
                "title": row["name"],
                "tradition": row["tradition"],
                "text": row["text"],
                "cycle": row.get("cycle"),
                "characters": row.get("characters", []),
                "themes": row.get("themes", []),
                "source": row.get("source"),
            }
        except Exception:
            return None

    async def get_npc_dialogue_context(
        self,
        npc_archetype: str,
        tradition: str,
        topic: str | None = None,
    ) -> list[dict]:
        """Get mythology context for NPC dialogue generation."""
        try:
            query = f"{npc_archetype} {topic or ''}"
            results = await self.search_mythology(
                query=query,
                tradition=tradition,
                limit=5,
            )

            return [
                {
                    "name": r["name"],
                    "text": r["text"][:500],
                    "entity_type": r["entity_type"],
                    "relevance": r["score"],
                }
                for r in results
            ]
        except Exception:
            return []

    async def get_quest_inspiration(
        self,
        theme: str,
        tradition: str,
        limit: int = 3,
    ) -> list[dict]:
        """Get mythology stories for quest inspiration."""
        try:
            results = await self.search_mythology(
                query=theme,
                tradition=tradition,
                entity_type="story",
                limit=limit,
            )

            return [
                {
                    "title": r["name"],
                    "summary": r["text"][:300],
                    "cycle": r["metadata"].get("cycle"),
                    "characters": r["metadata"].get("related_figures", []),
                    "relevance": r["score"],
                }
                for r in results
            ]
        except Exception:
            return []

    async def list_deities(
        self,
        tradition: str | None = None,
    ) -> list[dict]:
        """List all deities."""
        try:
            table = self.db.open_table("mythology_embeddings")
            df = table.to_pandas()

            filtered = df[df["entity_type"] == "deity"]
            if tradition:
                filtered = filtered[filtered["tradition"] == tradition]

            return [
                {
                    "name": row["name"],
                    "tradition": row["tradition"],
                    "domains": row.get("domains", []),
                }
                for _, row in filtered.iterrows()
            ]
        except Exception:
            return []

    async def list_stories_by_cycle(
        self,
        cycle: str,
        tradition: str | None = None,
    ) -> list[dict]:
        """List stories by mythological cycle."""
        try:
            table = self.db.open_table("mythology_embeddings")
            df = table.to_pandas()

            filtered = df[
                (df["entity_type"] == "story")
                & (df["cycle"] == cycle)
            ]
            if tradition:
                filtered = filtered[filtered["tradition"] == tradition]

            return [
                {
                    "title": row["name"],
                    "tradition": row["tradition"],
                    "summary": row["text"][:200] if row.get("text") else "",
                }
                for _, row in filtered.iterrows()
            ]
        except Exception:
            return []

    def list_traditions(self) -> list[str]:
        """List all Celtic traditions."""
        try:
            table = self.db.open_table("mythology_embeddings")
            result = table.to_pandas()["tradition"].unique().tolist()
            return [t for t in result if t]
        except Exception:
            return []

    def list_cycles(self, tradition: str | None = None) -> list[str]:
        """List mythological cycles."""
        try:
            table = self.db.open_table("mythology_embeddings")
            df = table.to_pandas()
            if tradition:
                df = df[df["tradition"] == tradition]
            result = df["cycle"].dropna().unique().tolist()
            return [c for c in result if c]
        except Exception:
            return []

    def list_entity_types(self) -> list[str]:
        """List all mythology entity types."""
        try:
            table = self.db.open_table("mythology_embeddings")
            result = table.to_pandas()["entity_type"].unique().tolist()
            return [e for e in result if e]
        except Exception:
            return []
