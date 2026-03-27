"""GitHub API assets using DLT with parallel execution.

Creates Dagster assets that wrap DLT sources for GitHub API ingestion.
Uses a factory pattern to generate one asset per (repo, resource) pair,
enabling parallel execution across endpoints.

Example:
    The assets are built at module load time from config/repos.yaml.
    Each repository with `modes.api: true` gets assets for its
    configured resources (issues, pull_requests, etc.).

    Run with:
        dagster asset materialize --select "github_api_*"
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

import dlt
import yaml
from dagster import AssetExecutionContext
from dagster_embedded_elt.dlt import DagsterDltResource, dlt_assets

if TYPE_CHECKING:
    pass


def load_repos_config() -> dict[str, Any]:
    """Load repository configuration from repos.yaml."""
    config_path = Path(__file__).parent.parent.parent / "config" / "repos.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)


def get_destination_name() -> str:
    """Get destination based on configuration."""
    config = load_repos_config()
    dest_mode = config.get("destination", {}).get("mode", "local")

    # Both local and production use DuckDB as the DLT destination
    # Production syncs to DuckLake after DLT writes
    return "duckdb"


def get_database_path() -> str:
    """Get the DuckDB database path from config."""
    config = load_repos_config()
    return config.get("databases", {}).get("duckdb", {}).get(
        "path", "./data/github_intelligence.duckdb"
    )


def make_repo_api_assets(repo_key: str, repo_config: dict[str, Any]) -> list:
    """Factory function to create API assets for a repository.

    Creates separate assets for each GitHub resource type to enable
    parallel execution across endpoints.

    Args:
        repo_key: Configuration key for the repository
        repo_config: Repository configuration from repos.yaml

    Returns:
        List of Dagster assets for this repository's API resources
    """
    owner = repo_config["owner"]
    repo = repo_config["repo"]
    api_config = repo_config.get("api_config", {})
    resources = api_config.get("resources", ["issues", "pull_requests", "commits"])
    incremental_config = api_config.get("incremental", {})

    assets = []

    for resource_name in resources:
        asset = _make_single_resource_asset(
            repo_key=repo_key,
            owner=owner,
            repo=repo,
            resource_name=resource_name,
            incremental_config=incremental_config,
        )
        if asset is not None:
            assets.append(asset)

    return assets


def _make_single_resource_asset(
    repo_key: str,
    owner: str,
    repo: str,
    resource_name: str,
    incremental_config: dict[str, Any],
):
    """Create a single asset for one GitHub resource.

    Args:
        repo_key: Configuration key for the repository
        owner: GitHub owner
        repo: GitHub repository name
        resource_name: Name of the GitHub resource (issues, pull_requests, etc.)
        incremental_config: Incremental loading configuration

    Returns:
        A Dagster asset definition
    """
    import pendulum

    from pipelines.github_api.source import github_api_source

    # Calculate initial value for incremental loading
    days_back = incremental_config.get("days_back", 30)
    cursor_path = incremental_config.get("cursor_path", "updated_at")
    initial_value = pendulum.now().subtract(days=days_back).to_iso8601_string()

    # Allow override via environment variable
    env_var = f"GITHUB_{resource_name.upper()}_INITIAL_VALUE"
    initial_value = os.getenv(env_var, initial_value)

    # Create the DLT source for this single resource
    try:
        source = github_api_source(
            owner=owner,
            repo=repo,
            resources=[resource_name],
        )
    except Exception:
        # Skip if source creation fails (e.g., missing token)
        return None

    # Apply incremental hints if the resource supports it
    resource_attr = f"{owner}_{repo}_{resource_name}"
    if hasattr(source, resource_attr):
        try:
            getattr(source, resource_attr).apply_hints(
                incremental=dlt.sources.incremental(
                    cursor_path=cursor_path,
                    initial_value=initial_value,
                )
            )
        except Exception:
            pass  # Some resources don't support incremental

    # Create unique pipeline name
    pipeline_name = f"github_{owner}_{repo}_{resource_name}"
    dataset_name = f"github_{owner}_{repo}"

    @dlt_assets(
        dlt_source=source,
        dlt_pipeline=dlt.pipeline(
            pipeline_name=pipeline_name,
            dataset_name=dataset_name,
            destination=get_destination_name(),
            progress="log",
        ),
        name=f"github_api_{repo_key}_{resource_name}",
        group_name=f"github_api_{repo_key}",
    )
    def _asset(context: AssetExecutionContext, dlt: DagsterDltResource):
        context.log.info(f"Loading {resource_name} for {owner}/{repo}")
        yield from dlt.run(context=context)

    return _asset


def build_all_github_api_assets() -> list:
    """Build all GitHub API assets from configuration.

    Reads config/repos.yaml and creates assets for each repository
    that has `modes.api: true`.

    Returns:
        List of all GitHub API assets
    """
    try:
        config = load_repos_config()
    except FileNotFoundError:
        return []

    all_assets = []

    for repo_key, repo_config in config.get("repositories", {}).items():
        modes = repo_config.get("modes", {})

        # Only create API assets if API mode is enabled
        if modes.get("api", False):
            repo_assets = make_repo_api_assets(repo_key, repo_config)
            all_assets.extend(repo_assets)

    return all_assets


# Build assets at module load time
github_api_assets = build_all_github_api_assets()
