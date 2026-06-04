"""
Job definitions for indexing and knowledge graph pipelines.

Jobs group assets for coordinated execution.
"""

from __future__ import annotations

from dagster import (
    AssetSelection,
    define_asset_job,
)


# Full indexing pipeline
full_indexing_job = define_asset_job(
    name="full_indexing_pipeline",
    selection=AssetSelection.groups("indexing"),
    description="Run all indexing operations (code + docs to LanceDB + Memgraph)",
)

# Knowledge graph only
knowledge_graph_job = define_asset_job(
    name="knowledge_graph_pipeline",
    selection=AssetSelection.groups("knowledge"),
    description="Run Cognee and Graphiti knowledge graph processing",
)

# Vector index only (fast)
vector_index_job = define_asset_job(
    name="vector_index_only",
    selection=AssetSelection.keys("code_vector_index", "docs_vector_index"),
    description="Update vector indexes only (no graph processing)",
)

# Complete pipeline (indexing + knowledge)
complete_pipeline_job = define_asset_job(
    name="complete_indexing_pipeline",
    selection=(
        AssetSelection.groups("indexing")
        | AssetSelection.groups("knowledge")
    ),
    description="Run full indexing and knowledge graph pipeline",
)


# List of all jobs
indexing_jobs = [
    full_indexing_job,
    knowledge_graph_job,
    vector_index_job,
    complete_pipeline_job,
]
