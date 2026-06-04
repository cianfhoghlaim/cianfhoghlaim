"""File processing assets for local and S3 sources.

Creates Dagster assets for ingesting files from local filesystem
or S3-compatible storage into DuckDB.

Example:
    Assets are built from config/repos.yaml for repositories
    with `modes.files: true` and a configured `files_config`.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

import dlt
import yaml
from dagster import AssetExecutionContext
from dagster_embedded_elt.dlt import DagsterDltResource, dlt_assets
from dlt.sources.filesystem import filesystem, read_parquet, read_jsonl

if TYPE_CHECKING:
    pass


def load_repos_config() -> dict[str, Any]:
    """Load repository configuration from repos.yaml."""
    config_path = Path(__file__).parent.parent.parent / "config" / "repos.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)


def create_local_files_source(
    path: str,
    patterns: list[str],
):
    """Create a DLT source for local files.

    Args:
        path: Local directory path
        patterns: List of glob patterns to match

    Returns:
        DLT source generator
    """
    @dlt.source(name="local_files")
    def local_files_source():
        """Local filesystem source."""
        for pattern in patterns:
            # Create file resource with appropriate reader
            if pattern.endswith(".parquet"):
                files_resource = filesystem(
                    bucket_url=path,
                    file_glob=pattern,
                )
                yield (files_resource | read_parquet()).with_name(
                    f"files_{pattern.replace('*', 'all').replace('.', '_')}"
                )
            elif pattern.endswith(".jsonl"):
                files_resource = filesystem(
                    bucket_url=path,
                    file_glob=pattern,
                )
                yield (files_resource | read_jsonl()).with_name(
                    f"files_{pattern.replace('*', 'all').replace('.', '_')}"
                )
            else:
                # For other files, just list metadata
                yield filesystem(
                    bucket_url=path,
                    file_glob=pattern,
                )

    return local_files_source()


def create_s3_files_source(
    bucket_url: str,
    patterns: list[str],
):
    """Create a DLT source for S3 files.

    Args:
        bucket_url: S3 bucket URL (s3://bucket-name/prefix)
        patterns: List of glob patterns to match

    Returns:
        DLT source generator
    """
    @dlt.source(name="s3_files")
    def s3_files_source():
        """S3 filesystem source."""
        for pattern in patterns:
            if pattern.endswith(".parquet"):
                files_resource = filesystem(
                    bucket_url=bucket_url,
                    file_glob=pattern,
                )
                yield (files_resource | read_parquet()).with_name(
                    f"s3_{pattern.replace('*', 'all').replace('.', '_')}"
                )
            elif pattern.endswith(".jsonl"):
                files_resource = filesystem(
                    bucket_url=bucket_url,
                    file_glob=pattern,
                )
                yield (files_resource | read_jsonl()).with_name(
                    f"s3_{pattern.replace('*', 'all').replace('.', '_')}"
                )
            else:
                yield filesystem(
                    bucket_url=bucket_url,
                    file_glob=pattern,
                )

    return s3_files_source()


def make_files_asset(repo_key: str, repo_config: dict[str, Any]):
    """Factory function to create files asset for a repository.

    Args:
        repo_key: Configuration key for the repository
        repo_config: Repository configuration from repos.yaml

    Returns:
        Dagster asset or None if files not configured
    """
    owner = repo_config["owner"]
    repo = repo_config["repo"]
    files_config = repo_config.get("files_config", {})

    if not files_config:
        return None

    source_type = files_config.get("source_type", "local")
    path = files_config.get("path", "")
    patterns = files_config.get("patterns", ["*.parquet"])

    if not path:
        return None

    if source_type == "s3":
        source = create_s3_files_source(path, patterns)
    else:
        source = create_local_files_source(path, patterns)

    @dlt_assets(
        dlt_source=source,
        dlt_pipeline=dlt.pipeline(
            pipeline_name=f"files_{owner}_{repo}",
            dataset_name=f"files_{owner}_{repo}",
            destination="duckdb",
            progress="log",
        ),
        name=f"files_{repo_key}",
        group_name=f"files_{repo_key}",
    )
    def _files_asset(context: AssetExecutionContext, dlt: DagsterDltResource):
        context.log.info(f"Processing files for {owner}/{repo} from {path}")
        yield from dlt.run(context=context)

    return _files_asset


def build_all_files_assets() -> list:
    """Build all files assets from configuration.

    Returns:
        List of files assets
    """
    try:
        config = load_repos_config()
    except FileNotFoundError:
        return []

    all_assets = []

    for repo_key, repo_config in config.get("repositories", {}).items():
        modes = repo_config.get("modes", {})

        # Only create files assets if files mode is enabled
        if modes.get("files", False):
            asset_def = make_files_asset(repo_key, repo_config)
            if asset_def:
                all_assets.append(asset_def)

    return all_assets


# Build assets at module load time
files_assets = build_all_files_assets()
