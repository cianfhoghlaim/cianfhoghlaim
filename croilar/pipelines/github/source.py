"""GitHub REST API Source for Portfolio.

Adapted from github-intelligence pipeline for portfolio repository insights.
Fetches repository metadata, languages, READMEs, and recent commits.

Usage:
    from pipelines.github import run_github_pipeline

    load_info = run_github_pipeline(username="Yedya")
"""

import os
from typing import Any, Iterator

import dlt
from dlt.sources.rest_api import RESTAPIConfig, rest_api_resources

# Aleyum GitHub username
ALEYUM_GITHUB_USERNAME = "Yedya"


@dlt.source(name="github_repos")
def github_repos_source(
    username: str = ALEYUM_GITHUB_USERNAME,
    access_token: str = dlt.secrets.value,
    include_forks: bool = False,
) -> Iterator[Any]:
    """DLT source for GitHub user repositories.

    Args:
        username: GitHub username
        access_token: GitHub personal access token (from secrets.toml)
        include_forks: Whether to include forked repositories

    Yields:
        DLT resources for repositories and related data
    """
    # Get token from env if not in secrets
    if not access_token:
        access_token = os.environ.get("GITHUB_ACCESS_TOKEN", "")

    config: RESTAPIConfig = {
        "client": {
            "base_url": "https://api.github.com",
            "auth": {"type": "bearer", "token": access_token} if access_token else None,
            "headers": {"Accept": "application/vnd.github.v3+json"},
        },
        "resources": [
            {
                "name": "repositories",
                "endpoint": {
                    "path": f"users/{username}/repos",
                    "method": "GET",
                    "params": {
                        "per_page": 100,
                        "sort": "updated",
                        "direction": "desc",
                        "type": "owner",  # Only owned repos, not forks
                    },
                    "paginator": {"type": "header_link"},
                },
                "primary_key": "id",
                "write_disposition": "merge",
            },
        ],
    }

    yield from rest_api_resources(config)


@dlt.resource(name="repository_languages", write_disposition="merge", primary_key=["repo_id", "language"])
def get_repo_languages(
    repos: list[dict[str, Any]],
    access_token: str = "",
) -> Iterator[dict[str, Any]]:
    """Fetch language breakdown for repositories.

    Args:
        repos: List of repository dicts with 'id', 'full_name', 'languages_url'
        access_token: GitHub access token

    Yields:
        Language data for each repository
    """
    import requests

    headers = {"Accept": "application/vnd.github.v3+json"}
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

    for repo in repos:
        repo_id = repo.get("id")
        languages_url = repo.get("languages_url", "")

        if not languages_url:
            continue

        try:
            response = requests.get(languages_url, headers=headers)
            if response.status_code == 200:
                languages = response.json()
                total_bytes = sum(languages.values())

                for language, bytes_count in languages.items():
                    yield {
                        "repo_id": repo_id,
                        "repo_name": repo.get("name", ""),
                        "language": language,
                        "bytes": bytes_count,
                        "percentage": (bytes_count / total_bytes * 100) if total_bytes > 0 else 0,
                    }

        except Exception as e:
            print(f"Error fetching languages for {repo.get('name')}: {e}")


@dlt.resource(name="repository_readmes", write_disposition="merge", primary_key="repo_id")
def get_repo_readmes(
    repos: list[dict[str, Any]],
    access_token: str = "",
) -> Iterator[dict[str, Any]]:
    """Fetch README content for repositories.

    Args:
        repos: List of repository dicts
        access_token: GitHub access token

    Yields:
        README data for each repository
    """
    import base64

    import requests

    headers = {
        "Accept": "application/vnd.github.v3+json",
    }
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

    for repo in repos:
        repo_id = repo.get("id")
        full_name = repo.get("full_name", "")

        if not full_name:
            continue

        readme_url = f"https://api.github.com/repos/{full_name}/readme"

        try:
            response = requests.get(readme_url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", "")

                # Decode base64 content
                if content:
                    try:
                        decoded = base64.b64decode(content).decode("utf-8")
                    except Exception:
                        decoded = ""
                else:
                    decoded = ""

                yield {
                    "repo_id": repo_id,
                    "repo_name": repo.get("name", ""),
                    "readme_content": decoded,
                    "readme_size": data.get("size", 0),
                    "readme_path": data.get("path", ""),
                }

        except Exception as e:
            print(f"Error fetching README for {full_name}: {e}")


@dlt.resource(name="recent_commits", write_disposition="merge", primary_key="sha")
def get_recent_commits(
    repos: list[dict[str, Any]],
    access_token: str = "",
    days_back: int = 90,
) -> Iterator[dict[str, Any]]:
    """Fetch recent commits for repositories.

    Args:
        repos: List of repository dicts
        access_token: GitHub access token
        days_back: Number of days of history to fetch

    Yields:
        Commit data for each repository
    """
    import pendulum
    import requests

    headers = {"Accept": "application/vnd.github.v3+json"}
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

    since_date = pendulum.now().subtract(days=days_back).to_iso8601_string()

    for repo in repos:
        repo_id = repo.get("id")
        full_name = repo.get("full_name", "")

        if not full_name:
            continue

        commits_url = f"https://api.github.com/repos/{full_name}/commits"
        params = {
            "since": since_date,
            "per_page": 100,
        }

        try:
            response = requests.get(commits_url, headers=headers, params=params)
            if response.status_code == 200:
                commits = response.json()

                for commit in commits:
                    commit_data = commit.get("commit", {})
                    author = commit_data.get("author", {})

                    yield {
                        "sha": commit.get("sha", ""),
                        "repo_id": repo_id,
                        "repo_name": repo.get("name", ""),
                        "message": commit_data.get("message", ""),
                        "author_name": author.get("name", ""),
                        "author_email": author.get("email", ""),
                        "authored_date": author.get("date", ""),
                        "url": commit.get("html_url", ""),
                    }

        except Exception as e:
            print(f"Error fetching commits for {full_name}: {e}")


def run_github_pipeline(
    username: str = ALEYUM_GITHUB_USERNAME,
    destination: str = "duckdb",
    dataset_name: str = "github_data",
    fetch_languages: bool = True,
    fetch_readmes: bool = True,
    fetch_commits: bool = True,
) -> Any:
    """Run the GitHub portfolio pipeline.

    Args:
        username: GitHub username
        destination: DLT destination
        dataset_name: Dataset name
        fetch_languages: Whether to fetch language breakdown
        fetch_readmes: Whether to fetch README content
        fetch_commits: Whether to fetch recent commits

    Returns:
        LoadInfo from the pipeline run
    """
    access_token = os.environ.get("GITHUB_ACCESS_TOKEN", "")

    pipeline = dlt.pipeline(
        pipeline_name=f"github_{username}",
        destination=destination,
        dataset_name=dataset_name,
        progress="log",
    )

    # Run main source to get repositories
    source = github_repos_source(username=username, access_token=access_token)
    load_info = pipeline.run(source)

    print(f"Repositories load: {load_info}")

    # Query loaded repos for secondary resources
    with pipeline.sql_client() as client:
        result = client.execute_sql(
            f"SELECT id, name, full_name, languages_url FROM {dataset_name}.repositories"
        )
        repos = [
            {
                "id": row[0],
                "name": row[1],
                "full_name": row[2],
                "languages_url": row[3],
            }
            for row in result
        ]

    if not repos:
        print("No repositories found")
        return load_info

    # Fetch additional data
    if fetch_languages:
        languages_resource = get_repo_languages(repos=repos, access_token=access_token)
        lang_info = pipeline.run(languages_resource)
        print(f"Languages load: {lang_info}")

    if fetch_readmes:
        readmes_resource = get_repo_readmes(repos=repos, access_token=access_token)
        readme_info = pipeline.run(readmes_resource)
        print(f"READMEs load: {readme_info}")

    if fetch_commits:
        commits_resource = get_recent_commits(repos=repos, access_token=access_token)
        commits_info = pipeline.run(commits_resource)
        print(f"Commits load: {commits_info}")

    return load_info


if __name__ == "__main__":
    # Example usage
    load_info = run_github_pipeline(
        username=ALEYUM_GITHUB_USERNAME,
        fetch_languages=True,
        fetch_readmes=True,
        fetch_commits=True,
    )
