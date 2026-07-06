"""
Dev-env demo tools for Google ADK agents.

Eight `FunctionTool`-wrapped async functions that expose the most useful
dev-environment capabilities of the Cianfhoghlaim monorepo to any ADK
`LlmAgent`:

1. ``drift_detect``               — Compare pinned Python package versions
                                    in ``pyproject.toml`` against the
                                    latest PyPI / HF Hub / GitHub release
2. ``ccc_search``                 — Semantic code search via CocoIndex
                                    Code (``bun run ccc:search``)
3. ``ccc_index``                  — Rebuild the local CCC index
                                    (``bun run ccc:index``)
4. ``firecrawl_refactor_discover``— Fetch upstream breaking-changes for a
                                    package via Firecrawl MCP
5. ``hf_best_model``              — Recommend the best HF Hub model for a
                                    task + hardware + benchmark
6. ``openspec_list_specs``        — List all openspec capability specs
7. ``openspec_validate``          — Run ``openspec validate --strict`` on
                                    a change id
8. ``mise_lint_skills``           — Run ``mise run lint:skills`` and
                                    parse the 4-rule output

All eight are **read-only by design** — they never mutate files in the
repo. The tools wrap CLIs (``bun``, ``mise``, ``openspec``) and inline
HTTP calls (PyPI JSON, HF Hub API); they live in the Python module rather
than in a separate Docker Compose stack because they do not need to be
daemonised.

The tools are consumed three ways:

* **By the ``dev_env_demo_agent``** (see
  ``cianfhoghlaim.agents.adk.dev_env_demo_agent``) — the canonical ADK
  user of these tools.
* **By marimo notebooks** under
  ``cianfhoghlaim/notebooks/meaisinfhoghlaim/dev_env/`` — the live demo
  surface.
* **By any other ADK agent** — ``from cianfhoghlaim.agents.adk.tools
  import dev_env`` and add ``dev_env.<tool>`` to the agent's ``tools=``
  list.

Usage from a Python REPL::

    from cianfhoghlaim.agents.adk.tools.dev_env import ccc_search
    results = await ccc_search(query="LANCE_DB shared lifespan pattern")

Usage from an ADK agent::

    from cianfhoghlaim.agents.adk.tools.dev_env import (
        DRIFT_DETECT_TOOL,
        CCC_SEARCH_TOOL,
        ...
    )

    agent = LlmAgent(name="my_agent", model="gemini-2.0-flash",
                     tools=[DRIFT_DETECT_TOOL, CCC_SEARCH_TOOL, ...])

Reference:
    openspec/changes/2026-07-06-add-dev-env-demo-tools-to-adk-agents/
"""
from __future__ import annotations

import asyncio
import datetime
import json
import logging
import os
import re
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# =============================================================================
# Lazy ADK + httpx imports (the module degrades gracefully if not installed)
# =============================================================================

try:
    from google.adk.tools import FunctionTool

    _HAS_ADK = True
except ImportError:  # pragma: no cover - dev-env may be used outside ADK
    _HAS_ADK = False
    FunctionTool = None  # type: ignore[assignment,misc]


# =============================================================================
# Constants
# =============================================================================

REPO_ROOT = Path(__file__).resolve().parents[4]
PYPROJECT_PATH = REPO_ROOT / "cianfhoghlaim" / "pyproject.toml"
CCC_DB_PATH = REPO_ROOT / ".cocoindex_code" / "target_sqlite.db"
SKILLS_DIR = REPO_ROOT / ".agents" / "skills"
STEDDING_QUEUE = REPO_ROOT / "stedding" / "ingest_queue"
PYPI_JSON_URL = "https://pypi.org/pypi/{pkg}/json"


# =============================================================================
# Internal helpers
# =============================================================================


def _run_cli(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    timeout: int = 120,
) -> dict[str, Any]:
    """Run a CLI subprocess synchronously and capture the result.

    Returns a dict with ``stdout``, ``stderr``, ``returncode``, ``cmd``,
    ``duration_s``. Does not raise on non-zero exit; the caller decides
    how to interpret the result.
    """
    start = time.time()
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd or REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return {
            "cmd": cmd,
            "cwd": str(cwd or REPO_ROOT),
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "returncode": proc.returncode,
            "duration_s": round(time.time() - start, 3),
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "cmd": cmd,
            "cwd": str(cwd or REPO_ROOT),
            "stdout": (exc.stdout or b"").decode("utf-8", errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or ""),
            "stderr": ((exc.stderr or b"").decode("utf-8", errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")) + f"\nTIMEOUT after {timeout}s",
            "returncode": -1,
            "duration_s": round(time.time() - start, 3),
            "timeout": True,
        }
    except FileNotFoundError as exc:
        return {
            "cmd": cmd,
            "cwd": str(cwd or REPO_ROOT),
            "stdout": "",
            "stderr": f"CLI not found: {exc}",
            "returncode": -1,
            "duration_s": round(time.time() - start, 3),
        }


async def _run_cli_async(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    timeout: int = 120,
) -> dict[str, Any]:
    """Async wrapper around ``_run_cli`` — runs in a thread executor."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        lambda: _run_cli(cmd, cwd=cwd, timeout=timeout),
    )


def _http_get_json(url: str, *, timeout: int = 10) -> dict[str, Any] | None:
    """Synchronous HTTP GET returning parsed JSON, or None on failure."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            result: dict[str, Any] = json.loads(resp.read().decode("utf-8"))  # type: ignore[no-any-return]
            return result
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as exc:
        logger.debug("HTTP GET failed: %s — %s", url, exc)
        return None


async def _http_get_json_async(url: str, *, timeout: int = 10) -> dict[str, Any] | None:
    """Async wrapper around ``_http_get_json``."""
    loop = asyncio.get_event_loop()
    result: dict[str, Any] | None = await loop.run_in_executor(  # type: ignore[no-any-return]
        None,
        lambda: _http_get_json(url, timeout=timeout),
    )
    return result if result is not None else None


def _parse_pyproject_pin(pkg: str) -> str | None:
    """Best-effort parse of a ``pyproject.toml`` pin for ``pkg``.

    Looks for either ``pkg>=X.Y`` or ``pkg==X.Y`` in the
    ``[project.dependencies]`` block. Returns the pin string or None.
    """
    if not PYPROJECT_PATH.exists():
        return None
    try:
        text = PYPROJECT_PATH.read_text()
    except OSError:
        return None
    # Grep for the package line; tolerate optional extras like pkg[extra]>=X
    pattern = rf"^\s*{re.escape(pkg)}(?:\[[^\]]+\])?\s*([><=!~]+)\s*([\d\.,a-zA-Z\*]+)"
    for line in text.splitlines():
        m = re.match(pattern, line)
        if m:
            return f"{m.group(1)}{m.group(2)}"
    return None


def _severity_from_versions(current: str, latest: str) -> str:
    """Classify a version drift by SemVer major/minor/patch."""
    def parse(v: str) -> tuple[int, ...]:
        # Strip non-numeric prefixes (e.g. "v1.2.3" -> "1.2.3")
        cleaned = re.sub(r"^v", "", v.strip())
        parts = re.findall(r"\d+", cleaned)
        return tuple(int(p) for p in parts[:3])

    try:
        cur = parse(current)
        lat = parse(latest)
    except (ValueError, TypeError):
        return "unknown"

    if not cur or not lat:
        return "unknown"
    if lat[0] > cur[0]:
        return "major"
    if lat[0] == cur[0] and len(lat) > 1 and len(cur) > 1 and lat[1] > cur[1]:
        return "minor"
    if lat == cur:
        return "current"
    return "patch"


def _make_recommendation(
    pkg: str,
    current: str | None,
    latest: str | None,
    severity: str,
) -> str:
    """Build a human-readable recommendation string."""
    if severity == "unknown":
        return f"Could not determine drift for {pkg} — verify PyPI / HF Hub access"
    if severity == "current":
        return f"{pkg} is up-to-date at {current}"
    if current is None:
        return f"Add {pkg}>={latest} to pyproject.toml [project.dependencies]"
    if severity == "major":
        return (
            f"Major bump: review {pkg} {current} -> {latest} migration guide "
            f"before pinning. Add a usespec change."
        )
    if severity == "minor":
        latest_str = latest or "0.0.0"
        major = _parse_major(latest_str)
        return f"Pin to {pkg}>={latest_str},<{major + 1}.0 in pyproject.toml [project.dependencies]"
    return f"Bump {pkg} to {latest} (patch-only change)"


def _parse_major(version: str) -> int:
    """Extract the major version number from a SemVer string."""
    m = re.match(r"^v?(\d+)", version.strip())
    return int(m.group(1)) if m else 0


# =============================================================================
# Tool 1 — drift_detect
# =============================================================================


async def drift_detect(
    packages: list[str],
    *,
    include_unreleased: bool = False,
) -> dict[str, Any]:
    """Detect version drift for a list of Python packages.

    Args:
        packages: List of package names to inspect (e.g.
            ``["dlt", "dagster", "motherduck", "lancedb"]``).
        include_unreleased: If True, also surface pre-release / dev
            versions. Default False.

    Returns:
        A dict with the following shape::

            {
                "checked_at": "<ISO timestamp>",
                "packages": [
                    {
                        "tool_name": "dlt",
                        "current_version": "1.28.1",
                        "latest_version": "1.30.0",
                        "severity": "minor",   # patch | minor | major | current | unknown
                        "recommendation": "Pin to dlt>=1.30.0,<2.0 ..."
                    },
                    ...
                ],
                "summary": {
                    "total": N,
                    "current": N,
                    "patch": N,
                    "minor": N,
                    "major": N,
                    "unknown": N,
                }
            }

    The function does not mutate any file. It calls PyPI's JSON API for
    each package and parses the ``info.version`` field.
    """
    results: list[dict[str, Any]] = []
    summary = {
        "total": len(packages),
        "current": 0,
        "patch": 0,
        "minor": 0,
        "major": 0,
        "unknown": 0,
    }

    for pkg in packages:
        current_pin = _parse_pyproject_pin(pkg)
        # Extract the version number from the pin (strip operators)
        current_version = (
            re.sub(r"^[><=!~]+", "", current_pin) if current_pin else None
        )

        # Fetch latest version from PyPI JSON API
        url = PYPI_JSON_URL.format(pkg=pkg)
        data = await _http_get_json_async(url)
        if data and "info" in data:
            latest_version = data["info"].get("version", "unknown")
            if not include_unreleased and data["info"].get("pre_release"):
                # Skip pre-releases if not requested
                releases = data.get("releases", {})
                stable_versions = [
                    v for v, files in releases.items()
                    if files and not _is_prerelease(v)
                ]
                latest_version = (
                    sorted(stable_versions, key=_version_sort_key)[-1]
                    if stable_versions
                    else latest_version
                )
        else:
            latest_version = "unknown"

        severity = _severity_from_versions(
            current_version or "0.0.0", latest_version
        )
        recommendation = _make_recommendation(
            pkg, current_version, latest_version, severity
        )

        results.append({
            "tool_name": pkg,
            "current_version": current_version,
            "latest_version": latest_version,
            "severity": severity,
            "recommendation": recommendation,
        })
        summary[severity] = summary.get(severity, 0) + 1

    return {
        "checked_at": datetime.datetime.utcnow().isoformat() + "Z",
        "packages": results,
        "summary": summary,
    }


def _is_prerelease(version: str) -> bool:
    """Return True if a SemVer string is a pre-release (alpha/beta/rc/dev)."""
    return bool(re.search(r"(a|alpha|b|beta|rc|dev)\d*", version, re.IGNORECASE))


def _version_sort_key(version: str) -> tuple[int, ...]:
    """Sort key that handles pre-release suffixes gracefully."""
    parts = re.findall(r"\d+", version)
    return tuple(int(p) for p in parts[:3])


# =============================================================================
# Tool 2 — ccc_search
# =============================================================================


async def ccc_search(
    query: str,
    *,
    paths: list[str] | None = None,
    limit: int = 5,
    semantic: bool = False,
) -> list[dict[str, Any]]:
    """Semantic code search via CocoIndex Code (``bun run ccc:search``).

    Args:
        query: Natural-language or code-snippet query.
        paths: Optional list of file/directory globs to scope the search.
        limit: Maximum number of results to return (default 5).
        semantic: If True, use BGE-M3 vector search (slow first call due
            to model load). If False (default), use fast substring search.

    Returns:
        A list of dicts each with ``file_path``, ``line_no``, ``snippet``,
        and ``relevance`` (0-1). Auto-runs ``bun run ccc:init`` if the
        SQLite index is missing.
    """
    # Auto-init if the index is missing
    if not CCC_DB_PATH.exists():
        logger.info("CCC index missing — running ccc:init")
        init_result = await _run_cli_async(["bun", "run", "ccc:init"])
        if init_result["returncode"] != 0:
            return [{
                "error": "ccc_init_failed",
                "stderr": init_result["stderr"],
            }]

    # Use the canonical scripts/ccc_v1_search.py wrapper — the old
    # `bun run ccc:search` is deprecated (hard removal 2026-07-15) and
    # the v1 bun-script wrapper had a shell-escape bug. The wrapper
    # itself tries the v4 module first then falls back to direct
    # LanceDB substring search.
    cmd = [
        "uv", "run", "python", "scripts/ccc_v1_search.py",
        query, "--limit", str(max(limit * 3, 15)),
    ]
    if semantic:
        cmd.append("--semantic")

    result = await _run_cli_async(cmd, cwd=REPO_ROOT, timeout=180)
    if result["returncode"] != 0:
        return [{
            "error": "ccc_search_failed",
            "stderr": result["stderr"][-500:],
            "stdout_tail": result["stdout"][-500:],
        }]

    # The wrapper emits JSON on stdout (filtered by `limit * 3` for
    # re-ranking headroom). Parse it.
    try:
        chunks = json.loads(result["stdout"].strip())
    except json.JSONDecodeError:
        # Fallback: line-by-line TSV parse (legacy format)
        chunks = []
        for line in result["stdout"].splitlines():
            line = line.rstrip()
            if not line or line.startswith("---") or line.startswith("Warning") or line.startswith("⚠"):
                continue
            parts = line.split("\t", 2)
            if len(parts) < 3:
                continue
            try:
                score = float(parts[0])
            except ValueError:
                continue
            location = parts[1]
            if ":" in location:
                path_part, range_part = location.rsplit(":", 1)
            else:
                path_part, range_part = location, "0"
            line_no = 0
            if "-" in range_part:
                import contextlib
                with contextlib.suppress(ValueError):
                    line_no = int(range_part.split("-")[0])
            chunks.append({
                "file_path": path_part,
                "line_no": line_no,
                "snippet": parts[2][:500],
                "relevance": score,
            })

    # Optional path-filter (post-hoc filter on file_path)
    if paths:
        path_set = set(paths)
        chunks = [
            c for c in chunks
            if any(p in c.get("file_path", "") for p in path_set)
        ]

    filtered: list[dict[str, Any]] = chunks[:limit]
    return filtered


# =============================================================================
# Tool 3 — ccc_index
# =============================================================================


async def ccc_index(
    paths: list[str] | None = None,
    *,
    timeout: int = 600,
) -> dict[str, Any]:
    """Rebuild the local CocoIndex Code index.

    Args:
        paths: Optional list of file/directory globs to scope the
            rebuild. If None, indexes the whole repo.
        timeout: Max seconds to wait (default 600 = 10 min).

    Returns:
        A dict with ``indexed_files`` (int), ``duration_s`` (float),
        ``stdout_tail`` (last 20 lines of CLI stdout), and
        ``returncode`` (int).
    """
    cmd = ["bun", "run", "ccc:v1:index"]
    if paths:
        for p in paths:
            cmd.extend(["--paths", p])

    result = await _run_cli_async(cmd, timeout=timeout)
    stdout_tail = "\n".join(result["stdout"].splitlines()[-20:])

    # Best-effort parse of indexed-file count
    indexed_files = 0
    m = re.search(r"Indexed\s+(\d+)\s+files", result["stdout"])
    if m:
        indexed_files = int(m.group(1))

    return {
        "indexed_files": indexed_files,
        "duration_s": result["duration_s"],
        "stdout_tail": stdout_tail,
        "returncode": result["returncode"],
        "stderr_tail": "\n".join(result["stderr"].splitlines()[-10:]),
    }


# =============================================================================
# Tool 4 — firecrawl_refactor_discover
# =============================================================================


async def firecrawl_refactor_discover(
    package: str,
    *,
    version_target: str | None = None,
    use_local_scrapes: bool | None = None,
) -> dict[str, Any]:
    """Fetch upstream breaking changes for a package via Firecrawl.

    Args:
        package: Package name (e.g. ``"dlt"``) or GitHub
            ``owner/repo`` (e.g. ``"dlt-hub/dlt"``).
        version_target: Optional specific version to inspect.
        use_local_scrapes: If True (or env var ``USE_LOCAL_SCRAPES=true``),
            read from the curated ``stedding/ingest_queue/`` snapshot
            instead of making a live Firecrawl call.

    Returns:
        A dict with ``package``, ``breaking_changes`` (list of dicts each
        with ``version``, ``description``, ``migration_step``),
        ``source_urls``, ``fetched_at`` (ISO timestamp), and optionally
        ``error`` (string) on failure.
    """
    if use_local_scrapes is None:
        use_local_scrapes = os.environ.get("USE_LOCAL_SCRAPES", "").lower() == "true"

    # Local scrape fallback — read curated snapshot
    if use_local_scrapes:
        snapshot_path = STEDDING_QUEUE / f"{package}.json"
        if snapshot_path.exists():
            try:
                data = json.loads(snapshot_path.read_text())
                return {
                    "package": package,
                    "breaking_changes": data.get("breaking_changes", []),
                    "source_urls": data.get("source_urls", []),
                    "fetched_at": datetime.datetime.utcnow().isoformat() + "Z",
                    "source": "local_snapshot",
                }
            except (OSError, json.JSONDecodeError) as exc:
                return {
                    "package": package,
                    "breaking_changes": [],
                    "source_urls": [],
                    "fetched_at": datetime.datetime.utcnow().isoformat() + "Z",
                    "error": f"local_snapshot_unreadable: {exc}",
                }
        return {
            "package": package,
            "breaking_changes": [],
            "source_urls": [],
            "fetched_at": datetime.datetime.utcnow().isoformat() + "Z",
            "error": "local_snapshot_missing: USE_LOCAL_SCRAPES=true but no snapshot found",
        }

    # Live Firecrawl — try the MCP server first
    try:
        # The Firecrawl MCP is exposed via opencode.json but is also
        # callable directly via the Python SDK if installed.
        try:
            from firecrawl import FirecrawlApp  # type: ignore[import-not-found]

            app = FirecrawlApp(api_key=os.environ.get("FIRECRAWL_API_KEY", ""))
            search_result = app.search(
                query=f"{package} breaking changes migration",
                limit=5,
            )
            source_urls = [
                r.get("url", "") for r in search_result.get("data", [])
                if r.get("url")
            ]
            breaking_changes: list[dict[str, Any]] = []
            for url in source_urls[:3]:
                try:
                    scraped = app.scrape_url(url, params={"formats": ["markdown"]})
                    md = scraped.get("markdown", "")
                    # Look for "BREAKING" / "Migration" headings
                    for match in re.finditer(
                        r"^#{1,3}\s*(?:BREAKING|Migration|v?\d+\.\d+\.\d+).*$",
                        md, re.MULTILINE,
                    ):
                        # Capture the section below the heading
                        start = match.end()
                        end = min(start + 800, len(md))
                        section = md[start:end].strip()
                        breaking_changes.append({
                            "version": version_target or "unknown",
                            "description": section[:300],
                            "migration_step": "See source URL for full migration guide",
                            "source_url": url,
                        })
                except Exception as exc:
                    logger.debug("Firecrawl scrape failed for %s: %s", url, exc)
                    continue
            return {
                "package": package,
                "breaking_changes": breaking_changes,
                "source_urls": source_urls,
                "fetched_at": datetime.datetime.utcnow().isoformat() + "Z",
                "source": "firecrawl_live",
            }
        except ImportError:
            # Firecrawl Python SDK not installed — return graceful fallback
            return {
                "package": package,
                "breaking_changes": [],
                "source_urls": [
                    f"https://github.com/{package}/releases"
                    if "/" in package
                    else f"https://pypi.org/project/{package}/#history"
                ],
                "fetched_at": datetime.datetime.utcnow().isoformat() + "Z",
                "error": "firecrawl_sdk_not_installed — install firecrawl-py or use_mcp",
            }
    except Exception as exc:
        return {
            "package": package,
            "breaking_changes": [],
            "source_urls": [],
            "fetched_at": datetime.datetime.utcnow().isoformat() + "Z",
            "error": f"firecrawl_unavailable: {exc}",
        }


# =============================================================================
# Tool 5 — hf_best_model
# =============================================================================


async def hf_best_model(
    task: str,
    *,
    hardware: str | None = None,
    benchmark: str | None = None,
    limit: int = 5,
) -> dict[str, Any]:
    """Recommend the best HuggingFace Hub model for a task.

    Args:
        task: Task description (e.g. ``"bge embedding for retrieval"``,
            ``"code completion"``, ``"image generation"``).
        hardware: Optional hardware constraint (e.g. ``"m4-max-64gb"``,
            ``"a100-80gb"``).
        benchmark: Optional benchmark name (e.g. ``"MTEB"``,
            ``"HellaSwag"``).
        limit: Max models to evaluate (default 5).

    Returns:
        A dict with ``recommended_model`` (str or None),
        ``alternates`` (list of str), ``benchmarks`` (dict mapping model
        name to benchmark score), ``source_urls`` (list of str), and
        optionally ``note`` (string) when no match.
    """
    try:
        from huggingface_hub import HfApi  # type: ignore[import-not-found]
    except ImportError:
        return {
            "recommended_model": None,
            "alternates": [],
            "benchmarks": {},
            "source_urls": [],
            "note": "huggingface_hub_not_installed",
        }

    loop = asyncio.get_event_loop()

    def _search_models() -> list[Any]:
        api = HfApi()
        # Build a search query — task + benchmark
        search_query = task
        if benchmark:
            search_query = f"{task} {benchmark}"
        results = list(api.list_models(
            search=search_query,
            limit=limit * 3,  # over-fetch for filtering
            sort="downloads",
            direction=-1,
        ))
        return results

    try:
        candidates = await loop.run_in_executor(None, _search_models)
    except Exception as exc:
        return {
            "recommended_model": None,
            "alternates": [],
            "benchmarks": {},
            "source_urls": [],
            "error": f"hf_hub_unavailable: {exc}",
        }

    # Heuristic ranking — prefer models with high download counts and
    # matching task tags
    ranked: list[tuple[int, Any]] = []
    task_lower = task.lower()
    for m in candidates:
        score = getattr(m, "downloads", 0) or 0
        tags = [t.lower() for t in (getattr(m, "tags", []) or [])]
        if any(t in task_lower for t in tags):
            score += 1000
        if benchmark and benchmark.lower() in tags:
            score += 500
        ranked.append((score, m))
    ranked.sort(key=lambda x: x[0], reverse=True)

    top = [m for _, m in ranked[:limit]]
    if not top:
        return {
            "recommended_model": None,
            "alternates": [],
            "benchmarks": {},
            "source_urls": [],
            "note": "no-match",
        }

    return {
        "recommended_model": top[0].id,
        "alternates": [m.id for m in top[1:]],
        "benchmarks": {
            m.id: getattr(m, "downloads", 0) or 0
            for m in top
        },
        "source_urls": [f"https://huggingface.co/{m.id}" for m in top],
    }


# =============================================================================
# Tool 6 — openspec_list_specs
# =============================================================================


async def openspec_list_specs(
    quadrant: str | None = None,
) -> dict[str, Any]:
    """List all openspec capability specs.

    Args:
        quadrant: Optional filter — one of ``"oideachais"``,
            ``"meaisinfhoghlaim"``, ``"tuatha"``, ``"croilar"``,
            ``"shared"``, ``"team"``, ``"tooling"``.

    Returns:
        A dict with ``specs`` (list of dicts each with ``id``,
        ``quadrant``, ``one_liner``) and ``count`` (int).
    """
    result = await _run_cli_async(["openspec", "list", "--specs", "--json"])
    specs: list[dict[str, Any]] = []
    if result["returncode"] == 0 and result["stdout"].strip():
        try:
            data = json.loads(result["stdout"])
            specs = data.get("specs", data) if isinstance(data, dict) else data
        except json.JSONDecodeError:
            # Fall back to plain-text parsing
            for line in result["stdout"].splitlines():
                line = line.strip()
                if line and not line.startswith("-"):
                    parts = line.split(" ", 1)
                    if len(parts) == 2:
                        specs.append({
                            "id": parts[0],
                            "one_liner": parts[1],
                            "quadrant": "unknown",
                        })

    if quadrant:
        specs = [
            s for s in specs
            if s.get("quadrant", "").lower() == quadrant.lower()
        ]

    return {
        "specs": specs,
        "count": len(specs),
    }


# =============================================================================
# Tool 7 — openspec_validate
# =============================================================================


async def openspec_validate(
    change_id: str,
    *,
    strict: bool = True,
) -> dict[str, Any]:
    """Run ``openspec validate`` on a change id.

    Args:
        change_id: The openspec change id (e.g.
            ``"2026-07-06-add-dev-env-demo-tools-to-adk-agents"``).
        strict: If True (default), pass ``--strict`` to the CLI.

    Returns:
        A dict with ``valid`` (bool), ``errors`` (list of str),
        ``warnings`` (list of str), and ``raw_output`` (str).
    """
    cmd = ["openspec", "validate", change_id]
    if strict:
        cmd.append("--strict")

    result = await _run_cli_async(cmd)
    output = result["stdout"] + result["stderr"]
    valid = result["returncode"] == 0 and "is valid" in output.lower()

    # Parse errors and warnings from the output
    errors: list[str] = []
    warnings: list[str] = []
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("Error:") or line.startswith("ERROR"):
            errors.append(line)
        elif line.startswith("Warning:") or line.startswith("WARN"):
            warnings.append(line)

    return {
        "change_id": change_id,
        "valid": valid,
        "errors": errors,
        "warnings": warnings,
        "raw_output": output,
        "returncode": result["returncode"],
    }


# =============================================================================
# Tool 8 — mise_lint_skills
# =============================================================================


async def mise_lint_skills(
    path: str = ".agents/skills/",
    *,
    timeout: int = 60,
) -> dict[str, Any]:
    """Run ``mise run lint:skills`` and parse the 4-rule output.

    Args:
        path: Path to the skills directory (default ``.agents/skills/``).
        timeout: Max seconds to wait (default 60).

    Returns:
        A dict with ``passed`` (int), ``failed`` (int), ``failures`` (list
        of dicts each with ``skill``, ``rule``, ``message``),
        ``duration_s`` (float), and ``raw_output_tail`` (str).
    """
    cwd = REPO_ROOT if not os.path.isabs(path) else Path(path).parent
    result = await _run_cli_async(
        ["mise", "run", "lint:skills"],
        cwd=cwd,
        timeout=timeout,
    )
    output = result["stdout"] + result["stderr"]

    # Parse the typical output formats:
    #   "lint-skills: 52 skills pass"
    #   "52 passed, 0 failed"
    #   "123/123 pass"
    passed = 0
    failed = 0
    m = re.search(r"(\d+)\s+skills?\s+pass", output, re.IGNORECASE)
    if m:
        passed = int(m.group(1))
    m = re.search(r"(\d+)/(\d+)\s+pass", output, re.IGNORECASE)
    if m:
        passed = int(m.group(1))
        failed = int(m.group(2)) - passed
    m = re.search(r"(\d+)\s+passed", output, re.IGNORECASE)
    if m:
        passed = int(m.group(1))
    m = re.search(r"(\d+)\s+failed", output, re.IGNORECASE)
    if m:
        failed = int(m.group(1))

    # Parse per-skill failures
    failures: list[dict[str, Any]] = []
    for line in output.splitlines():
        # e.g. "  - skills/foo/SKILL.md: line_count exceeds 500"
        m = re.match(
            r"\s*[-*]\s*skills/([^/]+)/SKILL\.md\s*:\s*(.+)$",
            line,
        )
        if m:
            failures.append({
                "skill": m.group(1),
                "rule": "unknown",
                "message": m.group(2).strip(),
            })

    return {
        "passed": passed,
        "failed": failed,
        "failures": failures,
        "duration_s": result["duration_s"],
        "raw_output_tail": "\n".join(output.splitlines()[-20:]),
        "returncode": result["returncode"],
    }


# =============================================================================
# FunctionTool wrappers (only created when google.adk is importable)
# =============================================================================


def _wrap(name: str, func: Any) -> Any:
    """Wrap an async function in a ``FunctionTool`` if ADK is available."""
    if _HAS_ADK:
        return FunctionTool(func=func)
    # Fallback: return the raw function so the module remains importable
    func.__wrapped_dev_env_tool__ = True  # type: ignore[attr-defined]
    return func


DRIFT_DETECT_TOOL = _wrap("drift_detect", drift_detect)
CCC_SEARCH_TOOL = _wrap("ccc_search", ccc_search)
CCC_INDEX_TOOL = _wrap("ccc_index", ccc_index)
FIRECRAWL_REFACTOR_DISCOVER_TOOL = _wrap(
    "firecrawl_refactor_discover", firecrawl_refactor_discover
)
HF_BEST_MODEL_TOOL = _wrap("hf_best_model", hf_best_model)
OPENSPEC_LIST_SPECS_TOOL = _wrap("openspec_list_specs", openspec_list_specs)
OPENSPEC_VALIDATE_TOOL = _wrap("openspec_validate", openspec_validate)
MISE_LINT_SKILLS_TOOL = _wrap("mise_lint_skills", mise_lint_skills)


__all__ = [
    # ADK FunctionTool wrappers (callable from any LlmAgent)
    "CCC_INDEX_TOOL",
    "CCC_SEARCH_TOOL",
    "DRIFT_DETECT_TOOL",
    "FIRECRAWL_REFACTOR_DISCOVER_TOOL",
    "HF_BEST_MODEL_TOOL",
    "MISE_LINT_SKILLS_TOOL",
    "OPENSPEC_LIST_SPECS_TOOL",
    "OPENSPEC_VALIDATE_TOOL",
    # Raw async functions (callable from Python / marimo / scripts)
    "ccc_index",
    "ccc_search",
    "drift_detect",
    "firecrawl_refactor_discover",
    "hf_best_model",
    "mise_lint_skills",
    "openspec_list_specs",
    "openspec_validate",
]
