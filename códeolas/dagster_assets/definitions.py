"""
Dagster definitions for Códeolas code analysis flow.

Main entry point for running the Dagster pipeline:
    dagster dev -m sruth.códeolas.dagster_assets.definitions

Jobs:
- codeolas_indexing_job: Code indexing only (hourly)
- codeolas_full_pipeline_job: Full pipeline including graph and docs (daily)

Schedules:
- hourly_code_indexing: Code indexing every hour
- daily_architecture_docs: Full pipeline at 6 AM
- weekly_full_rebuild: Complete rebuild every Sunday

Resources:
- LanceDB for vector storage
- Memgraph for code relationships
"""

from dagster import (
    Definitions,
    define_asset_job,
    AssetSelection,
)

from .code_assets import codeolas_assets, code_chunks, code_graph, architecture_docs
from .schedules import codeolas_schedules


# =============================================================================
# Job Definitions
# =============================================================================

# Job for code indexing only (fast, runs hourly)
codeolas_indexing_job = define_asset_job(
    name="codeolas_indexing_job",
    selection=AssetSelection.assets(code_chunks),
    description="Index repository code into LanceDB",
)

# Job for full pipeline (code + graph + docs)
codeolas_full_pipeline_job = define_asset_job(
    name="codeolas_full_pipeline_job",
    selection=AssetSelection.assets(code_chunks, code_graph, architecture_docs),
    description="Full code analysis pipeline with graph and docs",
)

# Job for graph only (useful for testing)
codeolas_graph_job = define_asset_job(
    name="codeolas_graph_job",
    selection=AssetSelection.assets(code_graph),
    description="Build code relationship graph only",
)


# =============================================================================
# Resources
# =============================================================================

# Resources can be extended with custom LanceDB/Memgraph resources
# For now, assets handle their own connections
resources = {}


# =============================================================================
# Definitions
# =============================================================================

defs = Definitions(
    assets=codeolas_assets,
    jobs=[
        codeolas_indexing_job,
        codeolas_full_pipeline_job,
        codeolas_graph_job,
    ],
    schedules=codeolas_schedules,
    resources=resources,
)
