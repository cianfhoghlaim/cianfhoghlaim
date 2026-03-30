"""Job definitions for the ingestion pipeline.

Jobs group assets for coordinated execution with specific configurations
like parallel execution via multiprocess executor.
"""

from __future__ import annotations

from dagster import (
    AssetSelection,
    define_asset_job,
    multiprocess_executor,
)


def build_ingestion_jobs() -> list:
    """Build all ingestion jobs.

    Returns:
        List of job definitions
    """
    # GitHub API job with parallel execution
    github_api_job = define_asset_job(
        name="github_api_job",
        selection=AssetSelection.groups("github_api_dlt-hub")
        | AssetSelection.groups("github_api_cocoindex")
        | AssetSelection.groups("github_api_cognee")
        | AssetSelection.groups("github_api_ibis")
        | AssetSelection.groups("github_api_marimo"),
        description="Fetch all GitHub API data with parallel execution",
        executor_def=multiprocess_executor.configured({
            "max_concurrent": 5,  # Parallel execution for API endpoints
        }),
    )

    # Full ingestion job (all modes)
    full_ingestion_job = define_asset_job(
        name="full_ingestion_job",
        selection=AssetSelection.all(),
        description="Run complete ingestion pipeline (all modes)",
    )

    return [github_api_job, full_ingestion_job]


# Build jobs at module load time
ingestion_jobs = build_ingestion_jobs()
