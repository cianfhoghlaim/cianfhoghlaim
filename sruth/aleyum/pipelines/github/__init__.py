"""GitHub Pipeline.

DLT source for GitHub repository data, adapted from github-intelligence.
Fetches repository metadata, languages, and commits for portfolio projects.
"""

from pipelines.github.source import github_repos_source, run_github_pipeline

__all__ = ["github_repos_source", "run_github_pipeline"]
