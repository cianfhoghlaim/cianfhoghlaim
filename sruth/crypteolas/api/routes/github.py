"""
GitHub Routes for Crypteolas API.

Provides GitHub data access endpoints.
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel
import structlog

logger = structlog.get_logger()

router = APIRouter()


class RepoRequest(BaseModel):
    """Repository request model."""

    owner: str
    repo: str


class SearchRequest(BaseModel):
    """GitHub search request model."""

    query: str
    repos: list[str] | None = None
    language: str | None = None
    limit: int = 20


@router.get("/repo/{owner}/{repo}")
async def get_repository(owner: str, repo: str):
    """
    Get repository metadata.

    Returns basic repository information.
    """
    try:
        from dlt_sources.github.github_source import _get_client, _get_repository  # type: ignore

        with _get_client() as client:
            result = _get_repository(client, owner, repo)
            return {"data": result, "status": "success"}
    except Exception as e:
        logger.error("Repository fetch error", error=str(e))
        return {"error": str(e), "status": "error"}


@router.get("/repo/{owner}/{repo}/issues")
async def get_repository_issues(
    owner: str,
    repo: str,
    state: str = Query("all", description="Issue state (open, closed, all)"),
    limit: int = Query(20, description="Result limit"),
):
    """
    Get repository issues.

    Returns recent issues with metadata.
    """
    try:
        from dlt_sources.github.github_source import _get_client, _list_issues  # type: ignore

        with _get_client() as client:
            issues = list(_list_issues(client, owner, repo, state=state, max_pages=limit // 10 + 1))
            return {"data": issues[:limit], "count": len(issues[:limit]), "status": "success"}
    except Exception as e:
        logger.error("Issues fetch error", error=str(e))
        return {"error": str(e), "status": "error"}


@router.get("/repo/{owner}/{repo}/prs")
async def get_repository_prs(
    owner: str,
    repo: str,
    state: str = Query("all", description="PR state (open, closed, all)"),
    limit: int = Query(20, description="Result limit"),
):
    """
    Get repository pull requests.

    Returns recent PRs with metadata.
    """
    try:
        from dlt_sources.github.github_source import _get_client, _list_pull_requests  # type: ignore

        with _get_client() as client:
            prs = list(
                _list_pull_requests(client, owner, repo, state=state, max_pages=limit // 10 + 1)
            )
            return {"data": prs[:limit], "count": len(prs[:limit]), "status": "success"}
    except Exception as e:
        logger.error("PRs fetch error", error=str(e))
        return {"error": str(e), "status": "error"}


@router.get("/repo/{owner}/{repo}/commits")
async def get_repository_commits(
    owner: str,
    repo: str,
    branch: str | None = Query(None, description="Branch name"),
    limit: int = Query(20, description="Result limit"),
):
    """
    Get repository commits.

    Returns recent commits with metadata.
    """
    try:
        from dlt_sources.github.github_source import _get_client, _list_commits  # type: ignore

        with _get_client() as client:
            commits = list(
                _list_commits(client, owner, repo, branch=branch, max_pages=limit // 10 + 1)
            )
            return {"data": commits[:limit], "count": len(commits[:limit]), "status": "success"}
    except Exception as e:
        logger.error("Commits fetch error", error=str(e))
        return {"error": str(e), "status": "error"}


@router.post("/search/code")
async def search_github_code(request: SearchRequest):
    """
    Search code across GitHub.

    Uses GitHub code search API.
    """
    try:
        from dlt_sources.github.github_source import _get_client, _search_code  # type: ignore

        with _get_client() as client:
            results = list(
                _search_code(
                    client,
                    request.query,
                    repos=request.repos,
                    language=request.language,
                    max_pages=request.limit // 10 + 1,
                )
            )
            return {
                "data": results[: request.limit],
                "count": len(results[: request.limit]),
                "status": "success",
            }
    except Exception as e:
        logger.error("Code search error", error=str(e))
        return {"error": str(e), "status": "error"}


@router.get("/repo/{owner}/{repo}/file")
async def get_file_content(
    owner: str,
    repo: str,
    path: str = Query(..., description="File path"),
    ref: str | None = Query(None, description="Git ref (branch, tag, commit)"),
):
    """
    Get file content from repository.

    Returns file content with metadata.
    """
    try:
        from dlt_sources.github.github_source import _get_client, _get_file_content  # type: ignore

        with _get_client() as client:
            result = _get_file_content(client, owner, repo, path, ref=ref)
            return {"data": result, "status": "success"}
    except Exception as e:
        logger.error("File fetch error", error=str(e))
        return {"error": str(e), "status": "error"}
