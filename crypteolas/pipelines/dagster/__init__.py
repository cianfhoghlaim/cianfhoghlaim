"""
Dagster ingestion pipeline for codeolas.

This package contains DLT-based assets for ingesting data from:
- GitHub REST API (issues, PRs, commits, workflows)
- Repository code (via git clone)
- Documentation websites (via Firecrawl/Crawl4AI)
- Local/S3 files

Destinations:
- DuckDB (local development)
- DuckLake (production with S3/R2 storage)
"""

from dagster.definitions import defs

__all__ = ["defs"]
