"""Dagster definitions for the ingestion pipeline.

This module combines all assets, resources, jobs, and schedules into
a single Definitions object for the Dagster daemon.

Usage:
    # Start Dagster webserver
    cd /path/to/codeolas
    DAGSTER_HOME=. dagster dev -m dagster.definitions

    # Run specific job
    dagster job execute -j github_api_job
"""

from __future__ import annotations

import os
from pathlib import Path

import yaml
from dagster import Definitions, EnvVar
from dagster_embedded_elt.dlt import DagsterDltResource

from .assets.github_api_assets import github_api_assets
from .jobs import ingestion_jobs
from .resources.duckdb_resource import DuckDBResource
from .resources.ducklake_resource import DuckLakeResource
from .schedules import ingestion_schedules


def load_repos_config() -> dict:
    """Load repository configuration from repos.yaml."""
    # config/ is a sibling of pipelines/ inside the crypteolas package root.
    config_path = Path(__file__).parent.parent.parent / "config" / "repos.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)


def get_destination_mode() -> str:
    """Get destination mode from configuration."""
    config = load_repos_config()
    return config.get("destination", {}).get("mode", "local")


def build_resources() -> dict:
    """Build resource definitions based on configuration.

    Returns:
        Dictionary of resource name to resource instance
    """
    dest_mode = get_destination_mode()

    resources = {
        "dlt": DagsterDltResource(),
    }

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
        config = load_repos_config()
        db_path = config.get("databases", {}).get("duckdb", {}).get(
            "path", "./data/github_intelligence.duckdb"
        )
        resources["destination"] = DuckDBResource(database_path=db_path)

    return resources


# Collect all assets
all_assets = [
    *github_api_assets,
]

# Create definitions
defs = Definitions(
    assets=all_assets,
    jobs=ingestion_jobs,
    schedules=ingestion_schedules,
    resources=build_resources(),
)
