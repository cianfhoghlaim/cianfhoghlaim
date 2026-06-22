"""
Asset definitions for the ingestion pipeline.

Assets are organized by data source mode:
- github_api_assets: GitHub REST API data
- code_repo_assets: Repository code cloning
- crawl_assets: Website/documentation crawling
- files_assets: Local/S3 file processing
"""

from .github_api_assets import github_api_assets

__all__ = [
    "github_api_assets",
]
