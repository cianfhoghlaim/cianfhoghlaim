"""
Main Dagster definitions entry point for codeolas.

Combines both ingestion and indexing pipelines into a unified
Definitions object. This is the main entry point for running
Dagster with the codeolas project.

Usage:
    # Start Dagster webserver
    cd /path/to/codeolas
    DAGSTER_HOME=. dagster dev -m definitions

    # Run specific job
    dagster job execute -j github_api_job
    dagster job execute -j full_indexing_pipeline

    # Materialize specific assets
    dagster asset materialize --select "github_api_*"
    dagster asset materialize --select "code_vector_index"
"""

from __future__ import annotations

import os
from pathlib import Path

import yaml
from dagster import Definitions
from dagster_embedded_elt.dlt import DagsterDltResource

# Import ingestion pipeline components
from pipelines.dagster.assets.github_api_assets import github_api_assets
from pipelines.dagster.assets.crawl_assets import crawl_assets
from pipelines.dagster.assets.files_assets import files_assets
from pipelines.dagster.jobs import ingestion_jobs
from pipelines.dagster.schedules import ingestion_schedules
from pipelines.dagster.resources.duckdb_resource import DuckDBResource
from pipelines.dagster.resources.ducklake_resource import DuckLakeResource

# Import indexing pipeline components
from pipelines.defs.indexing.code_vectors import code_vector_index
from pipelines.defs.indexing.docs_vectors import docs_vector_index
from pipelines.defs.indexing.docs_graph import docs_graph_index
from pipelines.defs.knowledge.cognee_extraction import cognee_knowledge_graph
from pipelines.defs.knowledge.graphiti_temporal import graphiti_temporal_graph
from pipelines.defs.jobs import indexing_jobs
from pipelines.defs.schedules import indexing_schedules
from pipelines.defs.sensors import indexing_sensors
from pipelines.defs._resources import indexing_resources


def load_repos_config() -> dict:
    """Load repository configuration from repos.yaml."""
    config_path = Path(__file__).parent / "config" / "repos.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)


def get_destination_mode() -> str:
    """Get destination mode from configuration."""
    config = load_repos_config()
    return config.get("destination", {}).get("mode", "local")


def build_all_resources() -> dict:
    """Build all resource definitions.

    Combines ingestion resources (DLT, DuckDB/DuckLake) with
    indexing resources (LanceDB, Memgraph, FalkorDB).

    Returns:
        Dictionary of resource name to resource instance
    """
    dest_mode = get_destination_mode()
    config = load_repos_config()

    resources = {
        "dlt": DagsterDltResource(),
    }

    # Add destination resource
    if dest_mode == "production":
        resources["destination"] = DuckLakeResource(
            pg_host=os.getenv("DUCKLAKE_PG_HOST", "localhost"),
            pg_database=os.getenv("DUCKLAKE_PG_DATABASE", "ducklake"),
            pg_user=os.getenv("DUCKLAKE_PG_USER", ""),
            pg_password=os.getenv("DUCKLAKE_PG_PASSWORD", ""),
            s3_endpoint=os.getenv("S3_ENDPOINT", ""),
            s3_bucket=os.getenv("S3_BUCKET", "codeolas-data"),
            s3_access_key=os.getenv("S3_ACCESS_KEY_ID", ""),
            s3_secret_key=os.getenv("S3_SECRET_ACCESS_KEY", ""),
        )
    else:
        db_path = config.get("databases", {}).get("duckdb", {}).get(
            "path", "./data/github_intelligence.duckdb"
        )
        resources["destination"] = DuckDBResource(database_path=db_path)

    # Add indexing resources
    resources.update(indexing_resources)

    return resources


# Collect all assets
all_assets = [
    # Ingestion assets
    *github_api_assets,
    *crawl_assets,
    *files_assets,
    # Indexing assets
    code_vector_index,
    docs_vector_index,
    docs_graph_index,
    # Knowledge graph assets
    cognee_knowledge_graph,
    graphiti_temporal_graph,
]

# Collect all jobs
all_jobs = [
    *ingestion_jobs,
    *indexing_jobs,
]

# Collect all schedules
all_schedules = [
    *ingestion_schedules,
    *indexing_schedules,
]

# Create unified definitions
defs = Definitions(
    assets=all_assets,
    jobs=all_jobs,
    schedules=all_schedules,
    sensors=indexing_sensors,
    resources=build_all_resources(),
)
