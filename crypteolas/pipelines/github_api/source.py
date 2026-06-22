"""GitHub REST API Source.

Defines DLT sources for ingesting GitHub data via the REST API.
Follows patterns from small-data-sf-2025 workshop and dlt_lance.py example.

Usage:
    import dlt
    from pipelines.github_api import github_api_source

    pipeline = dlt.pipeline(
        pipeline_name="github_api",
        destination="duckdb",
        dataset_name="github_data",
    )

    source = github_api_source(owner="dlt-hub", repo="dlt")
    load_info = pipeline.run(source)
"""

from typing import Any, Iterator

import dlt
from dlt.sources.rest_api import RESTAPIConfig, rest_api_resources

from pipelines.github_api.resources import GITHUB_RESOURCES


@dlt.source(name="github_api")
def github_api_source(
    owner: str,
    repo: str,
    access_token: str = dlt.secrets.value,
    resources: list[str] | None = None,
) -> Iterator[Any]:
    """DLT source for GitHub REST API.

    Args:
        owner: GitHub repository owner
        repo: GitHub repository name
        access_token: GitHub personal access token (from secrets.toml)
        resources: List of resource names to include (default: issues, pull_requests, commits)

    Yields:
        DLT resources for each configured endpoint
    """
    if resources is None:
        resources = ["issues", "pull_requests", "commits"]

    # Build resource configurations for this repo
    resource_configs = []
    for name in resources:
        if name not in GITHUB_RESOURCES:
            continue

        resource = GITHUB_RESOURCES[name].copy()
        endpoint = resource.pop("endpoint").copy()

        # Fill in path parameters
        endpoint["path"] = endpoint["path"].format(owner=owner, repo=repo)

        resource_configs.append({
            "name": f"{owner}_{repo}_{name}",  # Unique name per repo
            "endpoint": endpoint,
            "primary_key": resource.get("primary_key", "id"),
            "write_disposition": resource.get("write_disposition", "merge"),
        })

    config: RESTAPIConfig = {
        "client": {
            "base_url": "https://api.github.com",
            "auth": {"type": "bearer", "token": access_token},
            "headers": {"Accept": "application/vnd.github.v3+json"},
        },
        "resources": resource_configs,
        "resource_defaults": {
            "primary_key": "id",
            "write_disposition": "merge",
        },
    }

    yield from rest_api_resources(config)


def make_github_source(
    owner: str,
    repo: str,
    access_token: str | None = None,
    resources: list[str] | None = None,
    days_back: int = 30,
) -> dlt.sources.DltSource:
    """Factory function to create a GitHub API source.

    This is an alternative pattern that allows more flexible configuration
    and can be used with incremental loading.

    Args:
        owner: GitHub repository owner
        repo: GitHub repository name
        access_token: GitHub personal access token
        resources: List of resource names to include
        days_back: Number of days back to fetch for incremental resources

    Returns:
        Configured DLT source
    """
    import os
    import pendulum

    # Get token from env if not provided
    if access_token is None:
        access_token = os.environ.get("GITHUB_ACCESS_TOKEN", "")

    if resources is None:
        resources = ["issues", "pull_requests", "commits", "workflow_runs"]

    # Calculate since date for incremental loading
    since_date = pendulum.now().subtract(days=days_back).to_iso8601_string()

    # Build resource configurations with incremental params
    resource_configs = []
    for name in resources:
        if name not in GITHUB_RESOURCES:
            continue

        resource = GITHUB_RESOURCES[name].copy()
        endpoint = resource.pop("endpoint").copy()

        # Fill in path parameters
        endpoint["path"] = endpoint["path"].format(owner=owner, repo=repo)

        # Add since parameter for resources that support it
        if name in ["issues", "pull_requests", "issue_comments"]:
            params = endpoint.get("params", {}).copy()
            params["since"] = since_date
            endpoint["params"] = params

        resource_configs.append({
            "name": name,
            "endpoint": endpoint,
            "primary_key": resource.get("primary_key", "id"),
            "write_disposition": resource.get("write_disposition", "merge"),
        })

    config: RESTAPIConfig = {
        "client": {
            "base_url": "https://api.github.com",
            "auth": {"type": "bearer", "token": access_token},
            "headers": {"Accept": "application/vnd.github.v3+json"},
        },
        "resources": resource_configs,
        "resource_defaults": {
            "primary_key": "id",
            "write_disposition": "merge",
        },
    }

    @dlt.source(name=f"github_{owner}_{repo}")
    def _source() -> Iterator[Any]:
        yield from rest_api_resources(config)

    return _source()


def run_github_pipeline(
    owner: str,
    repo: str,
    resources: list[str] | None = None,
    destination: str = "duckdb",
    dataset_name: str = "github_data",
) -> Any:
    """Run a GitHub API pipeline.

    Convenience function to quickly ingest GitHub data.

    Args:
        owner: GitHub repository owner
        repo: GitHub repository name
        resources: List of resource names to include
        destination: DLT destination (duckdb, lancedb, etc.)
        dataset_name: Name of the dataset in the destination

    Returns:
        LoadInfo from the pipeline run
    """
    pipeline = dlt.pipeline(
        pipeline_name=f"github_{owner}_{repo}",
        destination=destination,
        dataset_name=dataset_name,
        progress="log",
    )

    source = make_github_source(owner=owner, repo=repo, resources=resources)
    load_info = pipeline.run(source)

    print(load_info)
    return load_info


if __name__ == "__main__":
    # Example usage
    load_info = run_github_pipeline(
        owner="dlt-hub",
        repo="dlt",
        resources=["issues", "pull_requests"],
    )
