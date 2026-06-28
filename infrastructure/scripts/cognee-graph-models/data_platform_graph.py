"""
data_platform_graph.py — Data Platform cluster graph model.

Cluster: docs-data-eng
Entities: DagsterAsset, DltPipeline, LakehouseTable, CocoIndexFlow,
          LanceDBIndex, SqlMeshModel

Cognee cognifies the docs-data-eng cluster (curriculum content +
Lakehouse architecture + BAML × DLT × Dagster matrix) into this
graph. The 6 entity types mirror the canonical 4 layers of the
Celtic Education Lakehouse:

  DagsterAsset      ← the 21 asset modules in sruth/oideachais/dagster_defs/
  DltPipeline       ← the 30+ dlt sources in sruth/oideachais/dlt_sources/
  LakehouseTable    ← the DuckLake/Iceberg tables (Postgres-cataloged)
  CocoIndexFlow     ← the 11 v1 Apps in sruth/oideachais/cocoindex_flows/
  LanceDBIndex      ← the HNSW vector indexes in sruth/oideachais/lancedb/
  SqlMeshModel      ← the SQLMesh transformations (deferred; no live models)

The cluster is consumed by:
- infrastructure/scripts/cognee-ingest-docs.py (1-call cognify)
- the docs-data-eng federated search (Cognee GRAPH_COMPLETION)
- the docs_skills_graph FalkorDB graph (the cross-cutting
  companion used by the 4-directory indexing change)
"""

from __future__ import annotations

# The 6 entity types for the Data Platform cluster
GRAPH_NODE_TYPES: tuple[str, ...] = (
    "DagsterAsset",
    "DltPipeline",
    "LakehouseTable",
    "CocoIndexFlow",
    "LanceDBIndex",
    "SqlMeshModel",
)

# The 8 edge types (relationships between the entity types)
GRAPH_EDGE_TYPES: tuple[str, ...] = (
    "DagsterAsset PRODUCES LakehouseTable",
    "DagsterAsset READS DltPipeline",
    "DagsterAsset READS CocoIndexFlow",
    "DltPipeline WRITES LakehouseTable",
    "CocoIndexFlow WRITES LanceDBIndex",
    "CocoIndexFlow READS LakehouseTable",
    "LanceDBIndex INDEXES LakehouseTable",
    "SqlMeshModel TRANSFORMS LakehouseTable",
)

# Cluster metadata
CLUSTER_NAME = "docs-data-eng"
CLUSTER_DESCRIPTION = (
    "The Celtic Education Lakehouse Engine: Dagster + DLT + DuckLake + "
    "LanceDB + CocoIndex v1 + BAML extraction."
)


def get_graph_model() -> dict[str, tuple[str, ...]]:
    """Return the cluster's graph model (nodes + edges).

    Returns
    -------
    dict[str, tuple[str, ...]]
        A dict with two keys:
        - "nodes": the 6 entity type names
        - "edges": the 8 relationship declarations
    """
    return {
        "nodes": GRAPH_NODE_TYPES,
        "edges": GRAPH_EDGE_TYPES,
    }
