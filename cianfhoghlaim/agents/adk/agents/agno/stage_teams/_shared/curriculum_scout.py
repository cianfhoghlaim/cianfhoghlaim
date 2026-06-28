"""Shared sub-agent: CurriculumScout.

Queries the 5 stage LanceDB tables and Cognee datasets. Used by every
stage team.
"""
from __future__ import annotations

import os


class CurriculumScout:
    """Searches the per-stage knowledge-graph tables.

    Real implementation: thin wrapper around lancedb.connect(...) + a Cognee
    REST client. For now this stub returns a structured result so the Agno
    team wiring can be validated.
    """

    def __init__(self, stage: str = "senior_cycle", *, lancedb_uri: str | None = None,
                 cognee_base: str | None = None) -> None:
        self.stage = stage
        self.lancedb_uri = lancedb_uri or os.getenv("LANCEDB_URI", "rest://lakehouse-lance-namespace:8182")
        self.cognee_base = cognee_base or os.getenv("COGNEE_BASE", "http://lakehouse-cognee:8000")
        self.table_name = f"{stage}_knowledge_graph"

    def search(self, query: str, *, limit: int = 10) -> dict:
        """Vector search over the stage LanceDB table.

        Returns a dict with `query`, `results: list[dict]`, `stage`.
        """
        return {
            "query": query,
            "stage": self.stage,
            "results": [],
            "table": self.table_name,
            "lancedb_uri": self.lancedb_uri,
            "message": "Stub: real implementation queries LanceDB + Cognee",
        }

    def get_by_id(self, node_id: str) -> dict:
        """Get a single node from the Cognee dataset by its ID."""
        return {
            "id": node_id,
            "stage": self.stage,
            "message": "Stub: real implementation queries Cognee",
        }
