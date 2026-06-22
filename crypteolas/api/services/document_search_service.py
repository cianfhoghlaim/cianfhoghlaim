"""
Document Search Service for Crypteolas.

Provides semantic search for whitepapers, audits, and protocol documentation.
"""

from pathlib import Path
from typing import Any

import lancedb
from sentence_transformers import SentenceTransformer


class DocumentSearchService:
    """Service for document semantic search."""

    def __init__(self, uri: str, embedding_model: str = "BAAI/bge-m3"):
        """Initialize LanceDB connection for document search."""
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

    async def search_whitepapers(
        self,
        query: str,
        protocol: str | None = None,
        limit: int = 10,
    ) -> list[dict]:
        """Search whitepaper content."""
        try:
            table = self.db.open_table("document_embeddings")
            query_embedding = self._embed(query)

            search = table.search(query_embedding, vector_column_name="text_embedding")
            search = search.where("doc_type = 'whitepaper'")

            if protocol:
                search = search.where(f"protocol = '{protocol}'")

            results = search.limit(limit).to_list()

            return [
                {
                    "id": r.get("id", ""),
                    "text": r.get("text", ""),
                    "protocol": r.get("protocol", ""),
                    "section": r.get("section", ""),
                    "score": 1.0 - r.get("_distance", 0),
                    "doc_type": "whitepaper",
                    "metadata": {
                        "page": r.get("page"),
                        "url": r.get("url"),
                    },
                }
                for r in results
            ]
        except Exception:
            return []

    async def search_audits(
        self,
        query: str,
        protocol: str | None = None,
        auditor: str | None = None,
        severity: str | None = None,
        limit: int = 10,
    ) -> list[dict]:
        """Search audit reports."""
        try:
            table = self.db.open_table("document_embeddings")
            query_embedding = self._embed(query)

            search = table.search(query_embedding, vector_column_name="text_embedding")
            search = search.where("doc_type = 'audit'")

            if protocol:
                search = search.where(f"protocol = '{protocol}'")
            if auditor:
                search = search.where(f"auditor = '{auditor}'")
            if severity:
                search = search.where(f"severity = '{severity}'")

            results = search.limit(limit).to_list()

            return [
                {
                    "id": r.get("id", ""),
                    "text": r.get("text", ""),
                    "protocol": r.get("protocol", ""),
                    "auditor": r.get("auditor", ""),
                    "finding_title": r.get("finding_title", ""),
                    "severity": r.get("severity", ""),
                    "score": 1.0 - r.get("_distance", 0),
                    "doc_type": "audit",
                    "metadata": {
                        "status": r.get("status"),
                        "audit_date": r.get("audit_date"),
                        "url": r.get("url"),
                    },
                }
                for r in results
            ]
        except Exception:
            return []

    async def search_documentation(
        self,
        query: str,
        protocol: str | None = None,
        doc_section: str | None = None,
        limit: int = 10,
    ) -> list[dict]:
        """Search protocol documentation."""
        try:
            table = self.db.open_table("document_embeddings")
            query_embedding = self._embed(query)

            search = table.search(query_embedding, vector_column_name="text_embedding")
            search = search.where("doc_type = 'documentation'")

            if protocol:
                search = search.where(f"protocol = '{protocol}'")
            if doc_section:
                search = search.where(f"section = '{doc_section}'")

            results = search.limit(limit).to_list()

            return [
                {
                    "id": r.get("id", ""),
                    "text": r.get("text", ""),
                    "protocol": r.get("protocol", ""),
                    "section": r.get("section", ""),
                    "score": 1.0 - r.get("_distance", 0),
                    "doc_type": "documentation",
                    "metadata": {
                        "url": r.get("url"),
                        "last_updated": r.get("last_updated"),
                    },
                }
                for r in results
            ]
        except Exception:
            return []

    async def search_all(
        self,
        query: str,
        protocol: str | None = None,
        doc_types: list[str] | None = None,
        limit: int = 20,
    ) -> list[dict]:
        """Search across all document types."""
        try:
            table = self.db.open_table("document_embeddings")
            query_embedding = self._embed(query)

            search = table.search(query_embedding, vector_column_name="text_embedding")

            filter_conditions = []
            if protocol:
                filter_conditions.append(f"protocol = '{protocol}'")
            if doc_types:
                type_filter = " OR ".join([f"doc_type = '{t}'" for t in doc_types])
                filter_conditions.append(f"({type_filter})")

            if filter_conditions:
                search = search.where(" AND ".join(filter_conditions))

            results = search.limit(limit).to_list()

            return [
                {
                    "id": r.get("id", ""),
                    "text": r.get("text", ""),
                    "protocol": r.get("protocol", ""),
                    "doc_type": r.get("doc_type", ""),
                    "section": r.get("section", ""),
                    "score": 1.0 - r.get("_distance", 0),
                    "metadata": {
                        "url": r.get("url"),
                        "auditor": r.get("auditor"),
                        "severity": r.get("severity"),
                    },
                }
                for r in results
            ]
        except Exception:
            return []

    async def get_protocol_documents(
        self,
        protocol: str,
    ) -> dict:
        """Get all documents for a protocol."""
        try:
            table = self.db.open_table("document_embeddings")
            df = table.to_pandas()
            protocol_df = df[df["protocol"] == protocol]

            return {
                "protocol": protocol,
                "whitepapers": len(protocol_df[protocol_df["doc_type"] == "whitepaper"]),
                "audits": len(protocol_df[protocol_df["doc_type"] == "audit"]),
                "documentation": len(protocol_df[protocol_df["doc_type"] == "documentation"]),
                "total_chunks": len(protocol_df),
                "auditors": protocol_df[protocol_df["doc_type"] == "audit"]["auditor"].unique().tolist(),
            }
        except Exception:
            return {
                "protocol": protocol,
                "whitepapers": 0,
                "audits": 0,
                "documentation": 0,
                "total_chunks": 0,
                "auditors": [],
            }

    def list_indexed_protocols(self) -> list[str]:
        """List all indexed protocols."""
        try:
            table = self.db.open_table("document_embeddings")
            result = table.to_pandas()["protocol"].unique().tolist()
            return [p for p in result if p]
        except Exception:
            return []

    def list_auditors(self) -> list[str]:
        """List all auditors in the system."""
        try:
            table = self.db.open_table("document_embeddings")
            df = table.to_pandas()
            auditors = df[df["doc_type"] == "audit"]["auditor"].unique().tolist()
            return [a for a in auditors if a]
        except Exception:
            return []
