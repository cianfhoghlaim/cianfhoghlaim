"""
DLT source for GitHub API - repositories, issues, PRs, commits, workflows.

API Reference: https://docs.github.com/en/rest

Provides access to:
- Repository metadata and content
- Issues and pull requests
- Commit history and diffs
- GitHub Actions workflows
- Code search results
"""

import os
from datetime import datetime, timezone
from typing import Any, Iterator

import dlt
import httpx

# GitHub API base URL
GITHUB_API_URL = "https://api.github.com"


def _get_client() -> httpx.Client:
    """Get HTTP client for GitHub API."""
    token = os.environ.get("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "sruth-crypteolas/1.0",
    }
    if token:
        headers["Authorization"] = f"token {token}"
    return httpx.Client(base_url=GITHUB_API_URL, timeout=30.0, headers=headers)


def _paginate(
    client: httpx.Client,
    endpoint: str,
    params: dict[str, Any] | None = None,
    max_pages: int = 10,
) -> Iterator[dict[str, Any]]:
    """Paginate through GitHub API results."""
    params = params or {}
    params.setdefault("per_page", 100)
    page = 1

    while page <= max_pages:
        params["page"] = page
        try:
            response = client.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()

            if isinstance(data, list):
                if not data:
                    break
                yield from data
            else:
                # Some endpoints return objects with items array
                items = data.get("items", [])
                if not items:
                    break
                yield from items

            # Check for next page via Link header
            link_header = response.headers.get("Link", "")
            if 'rel="next"' not in link_header:
                break
            page += 1

        except Exception as e:
            import logging
            logging.warning(f"GitHub API error for {endpoint}: {e}")
            break


def _get_repository(client: httpx.Client, owner: str, repo: str) -> dict[str, Any]:
    """Get repository metadata."""
    try:
        response = client.get(f"/repos/{owner}/{repo}")
        response.raise_for_status()
        data = response.json()
        return {
            "id": data.get("id"),
            "full_name": data.get("full_name"),
            "owner": owner,
            "name": repo,
            "description": data.get("description"),
            "language": data.get("language"),
            "topics": data.get("topics", []),
            "stars": data.get("stargazers_count"),
            "forks": data.get("forks_count"),
            "open_issues": data.get("open_issues_count"),
            "default_branch": data.get("default_branch"),
            "created_at": data.get("created_at"),
            "updated_at": data.get("updated_at"),
            "pushed_at": data.get("pushed_at"),
            "license": data.get("license", {}).get("spdx_id") if data.get("license") else None,
            "homepage": data.get("homepage"),
            "has_wiki": data.get("has_wiki"),
            "has_issues": data.get("has_issues"),
            "archived": data.get("archived"),
            "status": "success",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        import logging
        logging.warning(f"GitHub API error for {owner}/{repo}: {e}")
        return None


def _list_issues(
    client: httpx.Client,
    owner: str,
    repo: str,
    state: str = "all",
    max_pages: int = 5,
) -> Iterator[dict[str, Any]]:
    """List issues for a repository."""
    for issue in _paginate(
        client,
        f"/repos/{owner}/{repo}/issues",
        params={"state": state, "sort": "updated", "direction": "desc"},
        max_pages=max_pages,
    ):
        # Skip pull requests (they appear in issues endpoint too)
        if issue.get("pull_request"):
            continue

        yield {
            "id": issue.get("id"),
            "number": issue.get("number"),
            "owner": owner,
            "repo": repo,
            "title": issue.get("title"),
            "body": issue.get("body"),
            "state": issue.get("state"),
            "labels": [l.get("name") for l in issue.get("labels", [])],
            "author": issue.get("user", {}).get("login"),
            "assignees": [a.get("login") for a in issue.get("assignees", [])],
            "comments_count": issue.get("comments"),
            "created_at": issue.get("created_at"),
            "updated_at": issue.get("updated_at"),
            "closed_at": issue.get("closed_at"),
            "status": "success",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }


def _list_pull_requests(
    client: httpx.Client,
    owner: str,
    repo: str,
    state: str = "all",
    max_pages: int = 5,
) -> Iterator[dict[str, Any]]:
    """List pull requests for a repository."""
    for pr in _paginate(
        client,
        f"/repos/{owner}/{repo}/pulls",
        params={"state": state, "sort": "updated", "direction": "desc"},
        max_pages=max_pages,
    ):
        yield {
            "id": pr.get("id"),
            "number": pr.get("number"),
            "owner": owner,
            "repo": repo,
            "title": pr.get("title"),
            "body": pr.get("body"),
            "state": pr.get("state"),
            "draft": pr.get("draft"),
            "merged": pr.get("merged"),
            "labels": [l.get("name") for l in pr.get("labels", [])],
            "author": pr.get("user", {}).get("login"),
            "assignees": [a.get("login") for a in pr.get("assignees", [])],
            "reviewers": [r.get("login") for r in pr.get("requested_reviewers", [])],
            "head_ref": pr.get("head", {}).get("ref"),
            "base_ref": pr.get("base", {}).get("ref"),
            "head_sha": pr.get("head", {}).get("sha"),
            "additions": pr.get("additions"),
            "deletions": pr.get("deletions"),
            "changed_files": pr.get("changed_files"),
            "comments_count": pr.get("comments"),
            "review_comments_count": pr.get("review_comments"),
            "commits_count": pr.get("commits"),
            "mergeable": pr.get("mergeable"),
            "mergeable_state": pr.get("mergeable_state"),
            "created_at": pr.get("created_at"),
            "updated_at": pr.get("updated_at"),
            "closed_at": pr.get("closed_at"),
            "merged_at": pr.get("merged_at"),
            "status": "success",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }


def _list_commits(
    client: httpx.Client,
    owner: str,
    repo: str,
    branch: str | None = None,
    since: str | None = None,
    max_pages: int = 5,
) -> Iterator[dict[str, Any]]:
    """List commits for a repository."""
    params: dict[str, Any] = {}
    if branch:
        params["sha"] = branch
    if since:
        params["since"] = since

    for commit in _paginate(
        client, f"/repos/{owner}/{repo}/commits", params=params, max_pages=max_pages
    ):
        yield {
            "sha": commit.get("sha"),
            "owner": owner,
            "repo": repo,
            "message": commit.get("commit", {}).get("message"),
            "author_name": commit.get("commit", {}).get("author", {}).get("name"),
            "author_email": commit.get("commit", {}).get("author", {}).get("email"),
            "author_login": commit.get("author", {}).get("login") if commit.get("author") else None,
            "committer_name": commit.get("commit", {}).get("committer", {}).get("name"),
            "committer_login": (
                commit.get("committer", {}).get("login") if commit.get("committer") else None
            ),
            "committed_at": commit.get("commit", {}).get("committer", {}).get("date"),
            "authored_at": commit.get("commit", {}).get("author", {}).get("date"),
            "parents": [p.get("sha") for p in commit.get("parents", [])],
            "tree_sha": commit.get("commit", {}).get("tree", {}).get("sha"),
            "verified": commit.get("commit", {}).get("verification", {}).get("verified"),
            "stats_additions": commit.get("stats", {}).get("additions"),
            "stats_deletions": commit.get("stats", {}).get("deletions"),
            "stats_total": commit.get("stats", {}).get("total"),
            "status": "success",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }


def _list_workflows(
    client: httpx.Client,
    owner: str,
    repo: str,
    max_pages: int = 3,
) -> Iterator[dict[str, Any]]:
    """List GitHub Actions workflows and recent runs."""
    try:
        # Get workflows
        response = client.get(f"/repos/{owner}/{repo}/actions/workflows")
        response.raise_for_status()
        workflows = response.json().get("workflows", [])

        for workflow in workflows:
            workflow_id = workflow.get("id")

            # Get recent runs for this workflow
            runs_response = client.get(
                f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs",
                params={"per_page": 10},
            )
            runs_response.raise_for_status()
            runs = runs_response.json().get("workflow_runs", [])

            yield {
                "id": workflow_id,
                "owner": owner,
                "repo": repo,
                "name": workflow.get("name"),
                "path": workflow.get("path"),
                "state": workflow.get("state"),
                "created_at": workflow.get("created_at"),
                "updated_at": workflow.get("updated_at"),
                "recent_runs": [
                    {
                        "id": run.get("id"),
                        "status": run.get("status"),
                        "conclusion": run.get("conclusion"),
                        "run_number": run.get("run_number"),
                        "event": run.get("event"),
                        "created_at": run.get("created_at"),
                        "updated_at": run.get("updated_at"),
                    }
                    for run in runs[:5]
                ],
                "status": "success",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }

    except Exception as e:
        import logging
        logging.warning(f"GitHub workflows API error for {owner}/{repo}: {e}")


def _search_code(
    client: httpx.Client,
    query: str,
    repos: list[str] | None = None,
    language: str | None = None,
    max_pages: int = 5,
) -> Iterator[dict[str, Any]]:
    """Search code across repositories."""
    q_parts = [query]
    if repos:
        q_parts.extend([f"repo:{r}" for r in repos])
    if language:
        q_parts.append(f"language:{language}")

    full_query = " ".join(q_parts)

    for result in _paginate(
        client,
        "/search/code",
        params={"q": full_query, "sort": "indexed"},
        max_pages=max_pages,
    ):
        yield {
            "name": result.get("name"),
            "path": result.get("path"),
            "sha": result.get("sha"),
            "repo_full_name": result.get("repository", {}).get("full_name"),
            "repo_owner": result.get("repository", {}).get("owner", {}).get("login"),
            "repo_name": result.get("repository", {}).get("name"),
            "html_url": result.get("html_url"),
            "score": result.get("score"),
            "query": query,
            "status": "success",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }


def _get_file_content(
    client: httpx.Client,
    owner: str,
    repo: str,
    path: str,
    ref: str | None = None,
) -> dict[str, Any]:
    """Get file content from a repository."""
    try:
        params = {}
        if ref:
            params["ref"] = ref

        response = client.get(f"/repos/{owner}/{repo}/contents/{path}", params=params)
        response.raise_for_status()
        data = response.json()

        # Handle directory vs file
        if isinstance(data, list):
            return {
                "owner": owner,
                "repo": repo,
                "path": path,
                "type": "directory",
                "entries": [
                    {"name": e.get("name"), "type": e.get("type"), "path": e.get("path")}
                    for e in data
                ],
                "status": "success",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }

        import base64

        content = ""
        if data.get("encoding") == "base64" and data.get("content"):
            content = base64.b64decode(data.get("content")).decode("utf-8", errors="replace")

        return {
            "owner": owner,
            "repo": repo,
            "path": path,
            "sha": data.get("sha"),
            "name": data.get("name"),
            "type": data.get("type"),
            "size": data.get("size"),
            "encoding": data.get("encoding"),
            "content": content,
            "html_url": data.get("html_url"),
            "download_url": data.get("download_url"),
            "status": "success",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        import logging
        logging.warning(f"GitHub file content API error for {owner}/{repo}/{path}: {e}")
        return None


@dlt.source(name="github")
def github_source(
    repos: list[str],
    include_issues: bool = True,
    include_prs: bool = True,
    include_commits: bool = True,
    include_workflows: bool = True,
    max_pages: int = 5,
):
    """
    DLT source for GitHub repositories.

    Args:
        repos: List of repositories in "owner/repo" format
        include_issues: Include issues data
        include_prs: Include pull requests data
        include_commits: Include commit history
        include_workflows: Include GitHub Actions workflows
        max_pages: Maximum pages to fetch per resource

    Returns:
        DLT source with repositories, issues, pull_requests, commits, workflows resources
    """

    @dlt.resource(
        name="repositories",
        write_disposition="merge",
        primary_key=["id"],
    )
    def repositories():
        """Repository metadata."""
        with _get_client() as client:
            for repo_str in repos:
                parts = repo_str.split("/")
                if len(parts) != 2:
                    continue
                owner, repo = parts
                result = _get_repository(client, owner, repo)
                if result is not None:
                    yield result

    @dlt.resource(
        name="issues",
        write_disposition="merge",
        primary_key=["id"],
    )
    def issues():
        """Repository issues."""
        if not include_issues:
            return
        with _get_client() as client:
            for repo_str in repos:
                parts = repo_str.split("/")
                if len(parts) != 2:
                    continue
                owner, repo = parts
                yield from _list_issues(client, owner, repo, max_pages=max_pages)

    @dlt.resource(
        name="pull_requests",
        write_disposition="merge",
        primary_key=["id"],
    )
    def pull_requests():
        """Repository pull requests."""
        if not include_prs:
            return
        with _get_client() as client:
            for repo_str in repos:
                parts = repo_str.split("/")
                if len(parts) != 2:
                    continue
                owner, repo = parts
                yield from _list_pull_requests(client, owner, repo, max_pages=max_pages)

    @dlt.resource(
        name="commits",
        write_disposition="merge",
        primary_key=["sha"],
    )
    def commits():
        """Repository commits."""
        if not include_commits:
            return
        with _get_client() as client:
            for repo_str in repos:
                parts = repo_str.split("/")
                if len(parts) != 2:
                    continue
                owner, repo = parts
                yield from _list_commits(client, owner, repo, max_pages=max_pages)

    @dlt.resource(
        name="workflows",
        write_disposition="merge",
        primary_key=["id"],
    )
    def workflows():
        """GitHub Actions workflows."""
        if not include_workflows:
            return
        with _get_client() as client:
            for repo_str in repos:
                parts = repo_str.split("/")
                if len(parts) != 2:
                    continue
                owner, repo = parts
                yield from _list_workflows(client, owner, repo)

    return repositories, issues, pull_requests, commits, workflows


@dlt.source(name="github_code_search")
def github_code_search_source(
    query: str,
    repos: list[str] | None = None,
    language: str | None = None,
    fetch_content: bool = False,
    max_pages: int = 5,
):
    """
    DLT source for GitHub code search.

    Args:
        query: Search query
        repos: Optional list of repos to search within
        language: Optional language filter
        fetch_content: Whether to fetch file contents
        max_pages: Maximum pages of search results

    Returns:
        DLT source with search_results resource
    """

    @dlt.resource(
        name="code_search_results",
        write_disposition="replace",
        primary_key=["sha", "repo_full_name"],
    )
    def search_results():
        """Code search results."""
        with _get_client() as client:
            for result in _search_code(client, query, repos, language, max_pages):
                if fetch_content and result.get("status") == "success":
                    # Fetch file content
                    content = _get_file_content(
                        client,
                        result["repo_owner"],
                        result["repo_name"],
                        result["path"],
                    )
                    if content is not None:
                        result["content"] = content.get("content")
                yield result

    return search_results
