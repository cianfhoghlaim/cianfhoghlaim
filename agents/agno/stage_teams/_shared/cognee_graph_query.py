"""Shared sub-agent: CogneeGraphQuery.

Cross-stage knowledge graph query via the Cognee REST API.
"""
from __future__ import annotations

import os


class CogneeGraphQuery:
    """Wraps the Cognee REST search API.

    Real implementation: thin wrapper around
        POST {COGNEE_BASE}/v1/search
        body: { "query": ..., "datasets": ["oideachais.aistear", ...] }
    """

    def __init__(self, dataset: str = "oideachais.senior_cycle", *, base: str | None = None) -> None:
        self.dataset = dataset
        self.base = base or os.getenv("COGNEE_BASE", "http://lakehouse-cognee:8000")

    def search(self, query: str, *, search_type: str = "GRAPH_COMPLETION", top_k: int = 10) -> dict:
        return {
            "query": query,
            "dataset": self.dataset,
            "search_type": search_type,
            "top_k": top_k,
            "results": [],
            "message": "Stub: real implementation calls Cognee REST API",
        }

    def cognify(self) -> dict:
        """Trigger a cognify pass on this dataset."""
        return {
            "dataset": self.dataset,
            "status": "queued",
            "message": "Stub: real implementation calls cognee.cognify()",
        }
