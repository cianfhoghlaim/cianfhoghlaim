"""GitHub API Resource Definitions.

Defines REST API endpoint configurations for various GitHub resources.
These follow the RESTAPIConfig pattern from dlt's rest_api source.

Reference: https://docs.github.com/en/rest
"""

from typing import Any

# GitHub API resource configurations
# Each resource defines an endpoint with pagination, data selection, and merge keys

issues_resource: dict[str, Any] = {
    "name": "issues",
    "endpoint": {
        "path": "repos/{owner}/{repo}/issues",
        "method": "GET",
        "params": {
            "per_page": 100,
            "state": "all",
            "sort": "updated",
            "direction": "desc",
        },
        "paginator": {"type": "header_link"},
    },
    "primary_key": "id",
    "write_disposition": "merge",
}

pull_requests_resource: dict[str, Any] = {
    "name": "pull_requests",
    "endpoint": {
        "path": "repos/{owner}/{repo}/pulls",
        "method": "GET",
        "params": {
            "per_page": 100,
            "state": "all",
            "sort": "updated",
            "direction": "desc",
        },
        "paginator": {"type": "header_link"},
    },
    "primary_key": "id",
    "write_disposition": "merge",
}

commits_resource: dict[str, Any] = {
    "name": "commits",
    "endpoint": {
        "path": "repos/{owner}/{repo}/commits",
        "method": "GET",
        "params": {
            "per_page": 100,
        },
        "paginator": {"type": "header_link"},
    },
    "primary_key": "sha",
    "write_disposition": "merge",
}

workflow_runs_resource: dict[str, Any] = {
    "name": "workflow_runs",
    "endpoint": {
        "path": "repos/{owner}/{repo}/actions/runs",
        "method": "GET",
        "params": {
            "per_page": 100,
        },
        "data_selector": "workflow_runs",
        "paginator": {"type": "header_link"},
    },
    "primary_key": "id",
    "write_disposition": "merge",
}

workflows_resource: dict[str, Any] = {
    "name": "workflows",
    "endpoint": {
        "path": "repos/{owner}/{repo}/actions/workflows",
        "method": "GET",
        "params": {
            "per_page": 100,
        },
        "data_selector": "workflows",
        "paginator": {"type": "header_link"},
    },
    "primary_key": "id",
    "write_disposition": "merge",
}

releases_resource: dict[str, Any] = {
    "name": "releases",
    "endpoint": {
        "path": "repos/{owner}/{repo}/releases",
        "method": "GET",
        "params": {
            "per_page": 100,
        },
        "paginator": {"type": "header_link"},
    },
    "primary_key": "id",
    "write_disposition": "merge",
}

contributors_resource: dict[str, Any] = {
    "name": "contributors",
    "endpoint": {
        "path": "repos/{owner}/{repo}/contributors",
        "method": "GET",
        "params": {
            "per_page": 100,
        },
        "paginator": {"type": "header_link"},
    },
    "primary_key": "id",
    "write_disposition": "merge",
}

issue_comments_resource: dict[str, Any] = {
    "name": "issue_comments",
    "endpoint": {
        "path": "repos/{owner}/{repo}/issues/comments",
        "method": "GET",
        "params": {
            "per_page": 100,
            "sort": "updated",
            "direction": "desc",
        },
        "paginator": {"type": "header_link"},
    },
    "primary_key": "id",
    "write_disposition": "merge",
}

stargazers_resource: dict[str, Any] = {
    "name": "stargazers",
    "endpoint": {
        "path": "repos/{owner}/{repo}/stargazers",
        "method": "GET",
        "params": {
            "per_page": 100,
        },
        "paginator": {"type": "header_link"},
    },
    # Stargazers response depends on Accept header
    # Default returns array of user objects
    "primary_key": "id",
    "write_disposition": "merge",
}

repo_info_resource: dict[str, Any] = {
    "name": "repository",
    "endpoint": {
        "path": "repos/{owner}/{repo}",
        "method": "GET",
    },
    "primary_key": "id",
    "write_disposition": "merge",
}

# Mapping of resource names to their configurations
GITHUB_RESOURCES: dict[str, dict[str, Any]] = {
    "issues": issues_resource,
    "pull_requests": pull_requests_resource,
    "commits": commits_resource,
    "workflow_runs": workflow_runs_resource,
    "workflows": workflows_resource,
    "releases": releases_resource,
    "contributors": contributors_resource,
    "issue_comments": issue_comments_resource,
    "stargazers": stargazers_resource,
    "repository": repo_info_resource,
}


def get_resources_for_repo(
    owner: str,
    repo: str,
    resource_names: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Get resource configurations for a specific repository.

    Args:
        owner: GitHub repository owner
        repo: GitHub repository name
        resource_names: List of resource names to include (default: all)

    Returns:
        List of resource configurations with path parameters filled in
    """
    if resource_names is None:
        resource_names = list(GITHUB_RESOURCES.keys())

    resources = []
    for name in resource_names:
        if name not in GITHUB_RESOURCES:
            continue

        resource = GITHUB_RESOURCES[name].copy()
        endpoint = resource["endpoint"].copy()

        # Fill in path parameters
        endpoint["path"] = endpoint["path"].format(owner=owner, repo=repo)
        resource["endpoint"] = endpoint

        resources.append(resource)

    return resources
