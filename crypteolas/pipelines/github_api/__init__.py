"""GitHub REST API Pipeline.

Provides DLT sources and resources for ingesting GitHub data via REST API.
Follows patterns from small-data-sf-2025 workshop.
"""

from pipelines.github_api.source import github_api_source, make_github_source
from pipelines.github_api.resources import (
    GITHUB_RESOURCES,
    issues_resource,
    pull_requests_resource,
    commits_resource,
    workflow_runs_resource,
)

__all__ = [
    "github_api_source",
    "make_github_source",
    "GITHUB_RESOURCES",
    "issues_resource",
    "pull_requests_resource",
    "commits_resource",
    "workflow_runs_resource",
]
