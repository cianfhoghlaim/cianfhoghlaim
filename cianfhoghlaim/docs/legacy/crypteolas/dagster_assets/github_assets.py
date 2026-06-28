"""
GitHub Assets for Crypteolas.

Ingests repository data, issues, PRs, and commits using DLT.
Uses DuckLake destination for concurrency-safe parallel writes.
"""

import os
from pathlib import Path

import yaml
from dagster import (
    AssetExecutionContext,
    MetadataValue,
    StaticPartitionsDefinition,
    asset,
)

from dlt_utils import create_pipeline


def load_repo_config() -> list[dict]:
    """Load repository configuration from YAML."""
    config_path = Path(__file__).parent.parent / "config" / "repos.yaml"
    if config_path.exists():
        with open(config_path) as f:
            config = yaml.safe_load(f)
            return config.get("repositories", [])
    return []


def _get_repo_full_names() -> list[str]:
    """Extract repo full names (owner/repo) from config for static partitions."""
    config_path = Path(__file__).parent.parent / "config" / "repos.yaml"
    if config_path.exists():
        with open(config_path) as f:
            config = yaml.safe_load(f)
            repos_config = config.get("repositories", {})
            # Flatten nested categories (defi, l2, infrastructure, sdks) into full names
            full_names = []
            for category_repos in repos_config.values():
                if isinstance(category_repos, list):
                    for repo in category_repos:
                        if isinstance(repo, dict) and "owner" in repo and "repo" in repo:
                            full_names.append(f"{repo['owner']}/{repo['repo']}")
            if full_names:
                return full_names
    # Fallback defaults
    return [
        "Uniswap/v4-core", "Uniswap/v3-core", "aave/aave-v3-core",
        "compound-finance/compound-protocol", "curvefi/curve-contract",
        "makerdao/dss", "lidofinance/lido-dao", "ethereum/go-ethereum",
    ]


# Static partitions from config
repo_partitions = StaticPartitionsDefinition(_get_repo_full_names())


@asset(
    partitions_def=repo_partitions,
    group_name="github",
    description="Raw GitHub repository metadata and file listings",
)
def github_repo_data(context: AssetExecutionContext) -> dict:
    """Fetch repository metadata and file tree."""
    from dlt_sources.github.github_source import github_source

    repo_full_name = context.partition_key

    pipeline = create_pipeline(
        project="crypteolas",
        pipeline_name="github_repos",
        dataset_name="github",
    )

    # github_source expects repos as a list with boolean flags
    source = github_source(
        repos=[repo_full_name],
        include_issues=False,
        include_prs=False,
        include_commits=False,
        include_workflows=False,
    )

    info = pipeline.run(source)

    context.add_output_metadata({
        "repo": repo_full_name,
        "rows_loaded": MetadataValue.int(len(info.loads_ids) if info.loads_ids else 0),
        "pipeline_name": pipeline.pipeline_name,
    })

    return {
        "repo": repo_full_name,
        "status": "success",
        "rows": len(info.loads_ids) if info.loads_ids else 0,
    }


@asset(
    partitions_def=repo_partitions,
    group_name="github",
    description="GitHub issues and issue comments",
)
def github_issues(context: AssetExecutionContext) -> dict:
    """Fetch repository issues and comments."""
    from dlt_sources.github.github_source import github_source

    repo_full_name = context.partition_key

    pipeline = create_pipeline(
        project="crypteolas",
        pipeline_name="github_issues",
        dataset_name="github",
    )

    source = github_source(
        repos=[repo_full_name],
        include_issues=True,
        include_prs=False,
        include_commits=False,
        include_workflows=False,
    )

    info = pipeline.run(source)

    context.add_output_metadata({
        "repo": repo_full_name,
        "rows_loaded": MetadataValue.int(len(info.loads_ids) if info.loads_ids else 0),
    })

    return {
        "repo": repo_full_name,
        "status": "success",
    }


@asset(
    partitions_def=repo_partitions,
    group_name="github",
    description="GitHub pull requests and PR reviews",
)
def github_pull_requests(context: AssetExecutionContext) -> dict:
    """Fetch pull requests and reviews."""
    from dlt_sources.github.github_source import github_source

    repo_full_name = context.partition_key

    pipeline = create_pipeline(
        project="crypteolas",
        pipeline_name="github_prs",
        dataset_name="github",
    )

    source = github_source(
        repos=[repo_full_name],
        include_issues=False,
        include_prs=True,
        include_commits=False,
        include_workflows=False,
    )

    info = pipeline.run(source)

    context.add_output_metadata({
        "repo": repo_full_name,
        "rows_loaded": MetadataValue.int(len(info.loads_ids) if info.loads_ids else 0),
    })

    return {
        "repo": repo_full_name,
        "status": "success",
    }


@asset(
    partitions_def=repo_partitions,
    group_name="github",
    description="GitHub commit history",
)
def github_commits(context: AssetExecutionContext) -> dict:
    """Fetch commit history."""
    from dlt_sources.github.github_source import github_source

    repo_full_name = context.partition_key

    pipeline = create_pipeline(
        project="crypteolas",
        pipeline_name="github_commits",
        dataset_name="github",
    )

    source = github_source(
        repos=[repo_full_name],
        include_issues=False,
        include_prs=False,
        include_commits=True,
        include_workflows=False,
    )

    info = pipeline.run(source)

    context.add_output_metadata({
        "repo": repo_full_name,
        "rows_loaded": MetadataValue.int(len(info.loads_ids) if info.loads_ids else 0),
    })

    return {
        "repo": repo_full_name,
        "status": "success",
    }


@asset(
    partitions_def=repo_partitions,
    group_name="github",
    deps=["github_repo_data"],
    description="Cloned repository code content for semantic indexing",
)
def github_code_content(context: AssetExecutionContext) -> dict:
    """Clone and extract code content for embedding."""
    import subprocess
    import tempfile

    repo_full_name = context.partition_key
    clone_url = f"https://github.com/{repo_full_name}.git"

    with tempfile.TemporaryDirectory() as tmpdir:
        result = subprocess.run(
            ["git", "clone", "--depth", "1", clone_url, tmpdir],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            context.log.warning(f"Failed to clone {repo_full_name}: {result.stderr}")
            return {"repo": repo_full_name, "status": "failed", "files": 0}

        code_files = []
        for ext in [".py", ".rs", ".sol", ".ts", ".js", ".go"]:
            code_files.extend(Path(tmpdir).rglob(f"*{ext}"))

        pipeline = create_pipeline(
            project="crypteolas",
            pipeline_name="github_code",
            dataset_name="github",
        )

        code_records = []
        for file_path in code_files[:500]:
            try:
                content = file_path.read_text(errors="ignore")
                rel_path = str(file_path.relative_to(tmpdir))
                code_records.append({
                    "repo": repo_full_name,
                    "file_path": rel_path,
                    "content": content[:50000],
                    "language": file_path.suffix[1:],
                    "size_bytes": len(content),
                })
            except Exception:
                continue

        if code_records:
            pipeline.run(code_records, table_name="code_files")

        context.add_output_metadata({
            "repo": repo_full_name,
            "files_indexed": len(code_records),
        })

        return {
            "repo": repo_full_name,
            "status": "success",
            "files": len(code_records),
        }


@asset(
    group_name="github",
    description="Aggregate GitHub statistics across all repos",
)
def github_aggregate_stats(
    context: AssetExecutionContext,
    github_repo_data: dict,
    github_issues: dict,
    github_pull_requests: dict,
) -> dict:
    """Compute aggregate statistics across all GitHub data."""
    import duckdb

    db_path = os.environ.get("DUCKDB_PATH", "storage/duckdb/crypteolas.duckdb")
    conn = duckdb.connect(db_path)

    try:
        stats = {}

        # Query repositories table (created by github_source)
        try:
            repo_count = conn.execute(
                "SELECT COUNT(DISTINCT full_name) FROM github.repositories"
            ).fetchone()
            stats["total_repos"] = repo_count[0] if repo_count else 0
        except Exception:
            stats["total_repos"] = 0

        try:
            issue_count = conn.execute(
                "SELECT COUNT(*) FROM github.issues"
            ).fetchone()
            stats["total_issues"] = issue_count[0] if issue_count else 0
        except Exception:
            stats["total_issues"] = 0

        try:
            pr_count = conn.execute(
                "SELECT COUNT(*) FROM github.pull_requests"
            ).fetchone()
            stats["total_prs"] = pr_count[0] if pr_count else 0
        except Exception:
            stats["total_prs"] = 0

        context.add_output_metadata({
            "total_repos": stats["total_repos"],
            "total_issues": stats["total_issues"],
            "total_prs": stats["total_prs"],
        })

        return stats
    finally:
        conn.close()
