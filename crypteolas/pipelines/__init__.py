"""GitHub Intelligence Pipelines.

This package contains DLT pipelines for ingesting GitHub data:
- github_api: REST API ingestion (issues, PRs, commits, workflows)
- github_repo: Repository cloning and storage
- github_docs: Documentation scraping and processing
"""

from pipelines.github_api.source import github_api_source, make_github_source

__all__ = ["github_api_source", "make_github_source"]
