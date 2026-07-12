"""
Cross-Flow Query Client for Lakehouse.

Enables unified search across all data flows:
- códeolas (code search)
- oideachas (curriculum search)
- crypteolas (protocol documentation)

Uses DuckLake for cross-table SQL queries and
LanceDB for unified vector search.

Architecture:
    Garage (S3) → Lakekeeper (Catalog) → DuckLake (SQL) → LanceDB (Vectors)
"""

import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

# Default paths
LANCEDB_URI = os.getenv("LANCEDB_URI", "./storage/data/lancedb")
DUCKLAKE_PATH = os.getenv("DUCKLAKE_PATH", "./storage/data/ducklake.ducklake")


class FlowType(str, Enum):
    """Available data flows."""
    CODEOLAS = "codeolas"
    OIDEACHAS = "oideachas"
    CRYPTEOLAS = "crypteolas"


@dataclass
class SearchResult:
    """A unified search result from any flow."""
    id: str
    flow: FlowType
    text: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CrossFlowConfig:
    """Configuration for cross-flow queries."""
    lancedb_uri: str = LANCEDB_URI
    ducklake_path: str = DUCKLAKE_PATH

    # Table names per flow
    tables: dict[FlowType, str] = field(default_factory=lambda: {
        FlowType.CODEOLAS: "codeolas_code_chunks",
        FlowType.OIDEACHAS: "celtic_curriculum_embeddings",
        FlowType.CRYPTEOLAS: "unified_embeddings",
    })

    # Embedding model (must be consistent across flows)
    embedding_model: str = "BAAI/bge-m3"
    embedding_dimension: int = 1024


class CrossFlowQueryClient:
    """
    Client for querying across multiple data flows.

    Provides:
    - Unified vector search across all flows
    - SQL queries via DuckLake
    - Flow-specific filtering
    - Result aggregation and ranking
    """

    def __init__(self, config: CrossFlowConfig | None = None):
        self.config = config or CrossFlowConfig()
        self._lancedb = None
        self._duckdb = None
        self._embedding_model = None

    def _get_lancedb(self):
        """Get LanceDB connection."""
        if self._lancedb is not None:
            return self._lancedb

        try:
            import lancedb
        except ImportError:
            raise ImportError("lancedb not installed. Run: pip install lancedb")

        self._lancedb = lancedb.connect(self.config.lancedb_uri)
        return self._lancedb

    def _get_duckdb(self):
        """Get DuckDB connection."""
        if self._duckdb is not None:
            return self._duckdb

        try:
            import duckdb
        except ImportError:
            raise ImportError("duckdb not installed. Run: pip install duckdb")

        self._duckdb = duckdb.connect(self.config.ducklake_path, read_only=True)
        return self._duckdb

    def _get_embedding_model(self):
        """Get embedding model for query encoding."""
        if self._embedding_model is not None:
            return self._embedding_model

        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError(
                "sentence-transformers not installed. "
                "Run: pip install sentence-transformers"
            )

        self._embedding_model = SentenceTransformer(self.config.embedding_model)
        return self._embedding_model

    def close(self):
        """Close all connections."""
        if self._duckdb:
            self._duckdb.close()
            self._duckdb = None
        self._lancedb = None
        self._embedding_model = None

    # =========================================================================
    # Vector Search
    # =========================================================================

    def search_across_flows(
        self,
        query: str,
        flows: list[FlowType] | None = None,
        limit: int = 20,
        similarity_threshold: float = 0.5,
    ) -> list[SearchResult]:
        """
        Search across all flows using vector similarity.

        Args:
            query: Natural language search query
            flows: List of flows to search (default: all)
            limit: Maximum results per flow
            similarity_threshold: Minimum similarity score

        Returns:
            Aggregated and ranked search results
        """
        flows = flows or list(FlowType)
        model = self._get_embedding_model()
        db = self._get_lancedb()

        # Encode query
        query_embedding = model.encode(query, normalize_embeddings=True)

        all_results = []

        for flow in flows:
            table_name = self.config.tables.get(flow)
            if not table_name:
                continue

            try:
                table = db.open_table(table_name)
            except Exception as e:
                logger.warning(f"Could not open table {table_name}: {e}")
                continue

            try:
                # Search
                results = (
                    table
                    .search(query_embedding)
                    .limit(limit)
                    .to_pandas()
                )

                # Convert to SearchResult
                for _, row in results.iterrows():
                    score = 1.0 - row.get("_distance", 1.0)
                    if score >= similarity_threshold:
                        all_results.append(SearchResult(
                            id=str(row.get("id", "")),
                            flow=flow,
                            text=row.get("text", ""),
                            score=score,
                            metadata=self._extract_metadata(row, flow),
                        ))

            except Exception as e:
                logger.warning(f"Search failed for {flow}: {e}")

        # Sort by score
        all_results.sort(key=lambda r: r.score, reverse=True)

        return all_results[:limit]

    def search_code(
        self,
        query: str,
        language: str | None = None,
        chunk_type: str | None = None,
        limit: int = 10,
    ) -> list[SearchResult]:
        """
        Search code specifically (códeolas flow).

        Args:
            query: Search query
            language: Filter by programming language
            chunk_type: Filter by chunk type (function, class, etc.)
            limit: Maximum results

        Returns:
            Code search results
        """
        return self._search_single_flow(
            query=query,
            flow=FlowType.CODEOLAS,
            filters={
                "language": language,
                "chunk_type": chunk_type,
            },
            limit=limit,
        )

    def search_curriculum(
        self,
        query: str,
        subject: str | None = None,
        level: str | None = None,
        language: str | None = None,
        limit: int = 10,
    ) -> list[SearchResult]:
        """
        Search curriculum content (oideachas flow).

        Args:
            query: Search query
            subject: Filter by subject (e.g., 'irish', 'mathematics')
            level: Filter by education level
            language: Filter by content language (e.g., 'en', 'ga')
            limit: Maximum results

        Returns:
            Curriculum search results
        """
        return self._search_single_flow(
            query=query,
            flow=FlowType.OIDEACHAS,
            filters={
                "subject": subject,
                "level": level,
                "language": language,
            },
            limit=limit,
        )

    def search_protocols(
        self,
        query: str,
        protocol: str | None = None,
        source_type: str | None = None,
        limit: int = 10,
    ) -> list[SearchResult]:
        """
        Search protocol documentation (crypteolas flow).

        Args:
            query: Search query
            protocol: Filter by protocol name
            source_type: Filter by source type
            limit: Maximum results

        Returns:
            Protocol documentation results
        """
        return self._search_single_flow(
            query=query,
            flow=FlowType.CRYPTEOLAS,
            filters={
                "protocol": protocol,
                "source_type": source_type,
            },
            limit=limit,
        )

    def _search_single_flow(
        self,
        query: str,
        flow: FlowType,
        filters: dict[str, Any],
        limit: int,
    ) -> list[SearchResult]:
        """Internal method for single-flow search."""
        model = self._get_embedding_model()
        db = self._get_lancedb()

        query_embedding = model.encode(query, normalize_embeddings=True)

        table_name = self.config.tables.get(flow)
        if not table_name:
            return []

        try:
            table = db.open_table(table_name)
        except Exception:
            return []

        # Build search with filters
        search = table.search(query_embedding).limit(limit)

        # Apply filters
        filter_conditions = []
        for key, value in filters.items():
            if value is not None:
                filter_conditions.append(f"{key} = '{value}'")

        if filter_conditions:
            search = search.where(" AND ".join(filter_conditions))

        try:
            results = search.to_pandas()
        except Exception:
            return []

        return [
            SearchResult(
                id=str(row.get("id", "")),
                flow=flow,
                text=row.get("text", ""),
                score=1.0 - row.get("_distance", 1.0),
                metadata=self._extract_metadata(row, flow),
            )
            for _, row in results.iterrows()
        ]

    def _extract_metadata(self, row, flow: FlowType) -> dict[str, Any]:
        """Extract relevant metadata based on flow type."""
        if flow == FlowType.CODEOLAS:
            return {
                "file_path": row.get("file_path"),
                "language": row.get("language"),
                "chunk_type": row.get("chunk_type"),
                "name": row.get("name"),
                "start_line": row.get("start_line"),
                "end_line": row.get("end_line"),
            }
        elif flow == FlowType.OIDEACHAS:
            return {
                "subject": row.get("subject"),
                "level": row.get("level"),
                "language": row.get("language"),
                "title": row.get("title"),
                "page_url": row.get("page_url"),
            }
        elif flow == FlowType.CRYPTEOLAS:
            return {
                "protocol": row.get("protocol"),
                "url": row.get("url"),
                "title": row.get("title"),
                "source_type": row.get("source_type"),
            }
        return {}

    # =========================================================================
    # SQL Queries via DuckLake
    # =========================================================================

    def execute_sql(self, query: str, params: dict | None = None) -> list[dict]:
        """
        Execute SQL query across DuckLake tables.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            List of result rows as dicts
        """
        conn = self._get_duckdb()
        result = conn.execute(query, params or {})
        columns = [desc[0] for desc in result.description]
        return [dict(zip(columns, row)) for row in result.fetchall()]

    def get_flow_stats(self) -> dict[FlowType, dict[str, Any]]:
        """
        Get statistics for each flow.

        Returns:
            Dict of flow -> stats
        """
        db = self._get_lancedb()
        stats = {}

        for flow, table_name in self.config.tables.items():
            try:
                table = db.open_table(table_name)
                df = table.to_pandas()

                stats[flow] = {
                    "table_name": table_name,
                    "row_count": len(df),
                    "columns": list(df.columns),
                }

                # Flow-specific stats
                if flow == FlowType.CODEOLAS and "language" in df.columns:
                    stats[flow]["languages"] = df["language"].value_counts().to_dict()
                elif flow == FlowType.OIDEACHAS and "subject" in df.columns:
                    stats[flow]["subjects"] = df["subject"].value_counts().to_dict()
                elif flow == FlowType.CRYPTEOLAS and "protocol" in df.columns:
                    stats[flow]["protocols"] = df["protocol"].value_counts().to_dict()

            except Exception as e:
                stats[flow] = {"error": str(e)}

        return stats

    def find_cross_references(
        self,
        entity_name: str,
        flows: list[FlowType] | None = None,
    ) -> dict[FlowType, list[SearchResult]]:
        """
        Find references to an entity across flows.

        Useful for understanding how concepts appear in different contexts.

        Args:
            entity_name: Name to search for (e.g., 'Chainlink', 'algebra')
            flows: Flows to search

        Returns:
            Dict of flow -> matching results
        """
        flows = flows or list(FlowType)
        results = {}

        for flow in flows:
            matches = self._search_single_flow(
                query=entity_name,
                flow=flow,
                filters={},
                limit=5,
            )
            results[flow] = matches

        return results


# =============================================================================
# Convenience Functions
# =============================================================================

# Singleton client
_cross_flow_client: CrossFlowQueryClient | None = None


def get_cross_flow_client(config: CrossFlowConfig | None = None) -> CrossFlowQueryClient:
    """Get cross-flow client singleton."""
    global _cross_flow_client
    if _cross_flow_client is None:
        _cross_flow_client = CrossFlowQueryClient(config)
    return _cross_flow_client


def search_all(
    query: str,
    limit: int = 20,
) -> list[SearchResult]:
    """
    Search across all flows.

    Args:
        query: Search query
        limit: Maximum results

    Returns:
        Unified search results
    """
    client = get_cross_flow_client()
    return client.search_across_flows(query, limit=limit)


def search_code(query: str, **kwargs) -> list[SearchResult]:
    """Search code in códeolas."""
    client = get_cross_flow_client()
    return client.search_code(query, **kwargs)


def search_curriculum(query: str, **kwargs) -> list[SearchResult]:
    """Search curriculum in oideachas."""
    client = get_cross_flow_client()
    return client.search_curriculum(query, **kwargs)


def search_protocols(query: str, **kwargs) -> list[SearchResult]:
    """Search protocols in crypteolas."""
    client = get_cross_flow_client()
    return client.search_protocols(query, **kwargs)


# =============================================================================
# CLI Entry Point
# =============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Cross-flow search client")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--flow", choices=["codeolas", "oideachas", "crypteolas", "all"],
                        default="all", help="Flow to search")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    client = get_cross_flow_client()

    if args.flow == "all":
        results = client.search_across_flows(args.query, limit=args.limit)
    elif args.flow == "codeolas":
        results = client.search_code(args.query, limit=args.limit)
    elif args.flow == "oideachas":
        results = client.search_curriculum(args.query, limit=args.limit)
    else:
        results = client.search_protocols(args.query, limit=args.limit)

    for i, result in enumerate(results, 1):
        print(f"\n{i}. [{result.flow.value}] Score: {result.score:.3f}")
        print(f"   ID: {result.id}")
        print(f"   Text: {result.text[:200]}...")
        print(f"   Metadata: {result.metadata}")

    client.close()
