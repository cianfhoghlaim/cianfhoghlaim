"""
API Endpoint Indexing CocoIndex v1 App.

Indexes the HTTP route surface area of the Cianfhoghlaim monorepo. Each
row in the `api_endpoints` LanceDB table is one route handler. The
embeddings enable semantic search across the full HTTP API surface.

Detected frameworks (round 7 phase 2):

- **FastAPI** (Python): `@app.get`, `@app.post`, `@app.put`, etc.,
  plus `@router.<verb>` for APIRouter sub-routers
- **Hono** (TypeScript): `app.get(`, `app.post(`, `hono.get(`,
  plus `new Hono()` chains
- **TanStack Start**: `createFileRoute(`, `createServerFileRoute(`
- **Convex** (HTTP actions): `httpAction(` decorators

Each row carries: framework, method, path, file_path, line_number,
handler_name, summary, embedding.

Reference: this is the v1-native replacement for the v0 grep at
`codeolas/cocoindex_flows/api_indexing.py:scan_api_endpoints()`.
The v0 implementation had no embedding; v1 enables semantic search.

Operational contract:
- Live mode (`cocoindex update -L ...`) is supported.
- Excludes mirror the codebase_indexing.py excludes.
- The v1 App uses `asyncio.to_thread` to run the regex scan (it's
  CPU-bound; we don't want to block the event loop).
- Embeddings via the shared BGE-M3 model (1024 dims).
"""

from __future__ import annotations

import asyncio
import datetime
import os
import pathlib
import re
from collections.abc import AsyncIterator
from dataclasses import dataclass
from enum import Enum
from typing import Annotated, Any, ClassVar

import structlog

logger = structlog.get_logger(__name__)

# CocoIndex is optional — degrade gracefully if not installed.
try:
    import cocoindex as coco  # type: ignore[import-not-found]
    from cocoindex.connectors import (  # type: ignore[import-not-found]
        lancedb,  # type: ignore[import-not-found]
        localfs,  # type: ignore[import-not-found]
    )
    from cocoindex.ops.sentence_transformers import (  # type: ignore[import-not-found]
        SentenceTransformerEmbedder,
    )
    from cocoindex.resources.file import (  # type: ignore[import-not-found]
        PatternFilePathMatcher,
    )

    COCOINDEX_AVAILABLE = True
except ImportError as e:
    logger.warning("cocoindex_v1_not_available: %s", e)
    COCOINDEX_AVAILABLE = False
    coco = None  # type: ignore[assignment]
    lancedb = None  # type: ignore[assignment]
    localfs = None  # type: ignore[assignment]
    SentenceTransformerEmbedder = None  # type: ignore[assignment]
    PatternFilePathMatcher = None  # type: ignore[assignment]


# =============================================================================
# Configuration
# =============================================================================


LANCEDB_URI = os.getenv("LANCEDB_URI", "rest://lance-api.cianfhoghlaim.ie")
EMBED_MODEL = os.getenv("API_EMBED_MODEL", "BAAI/bge-m3")
EMBED_DIM = 1024
REFRESH_INTERVAL = datetime.timedelta(seconds=int(os.getenv("API_REFRESH_SECS", "300")))
LANCEDB_TABLE = "api_endpoints"
TOP_K = 20

DEFAULT_REPO_ROOT = pathlib.Path(
    os.getenv(
        "API_REPO_ROOT",
        str(pathlib.Path(__file__).resolve().parents[5]),
    )
)

LANCE_DB: Any = "lance_db_api"
EMBEDDER: Any = "embedder_api"


# =============================================================================
# Framework enum
# =============================================================================


class ApiFramework(str, Enum):
    FASTAPI = "fastapi"
    HONO = "hono"
    TANSTACK_START = "tanstack_start"
    CONVEX_HTTP = "convex_http"
    UNKNOWN = "unknown"


class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"
    WEBSOCKET = "WEBSOCKET"
    UNKNOWN = "UNKNOWN"


# =============================================================================
# Regex catalogue
# =============================================================================


# FastAPI: @app.get("/path"), @router.post('/path'), @app_xyz.get("/path")
_FASTAPI_RE = re.compile(
    r"""
    @
    (?P<router>[A-Za-z_][A-Za-z0-9_]*)
    \.
    (?P<verb>get|post|put|patch|delete|options|head|websocket)
    \s*\(
    \s*
    (?P<path>
        "(?:[^"\\]|\\.)*"
        |
        '(?:[^'\\]|\\.)*'
    )
    """,
    re.VERBOSE,
)

# Hono: app.get('/path', handler), hono.post('/path', ...), router.delete(...)
_HONO_RE = re.compile(
    r"""
    (?P<router>[A-Za-z_][A-Za-z0-9_]*)
    \.
    (?P<verb>get|post|put|patch|delete|options|head|use|on)
    \s*\(
    \s*
    (?P<path>
        "(?:[^"\\]|\\.)*"
        |
        '(?:[^'\\]|\\.)*'
    )
    """,
    re.VERBOSE,
)

# TanStack Start: createFileRoute('/path')({ ... }) or createServerFileRoute(...)
_TANSTACK_RE = re.compile(
    r"""
    (?P<verb>createFileRoute|createServerFileRoute)
    \s*\(
    \s*
    (?P<path>
        "(?:[^"\\]|\\.)*"
        |
        '(?:[^'\\]|\\.)*'
    )
    """,
    re.VERBOSE,
)

# Convex HTTP actions: httpAction(async () => {...})
_CONVEX_HTTP_RE = re.compile(
    r"""
    (?P<verb>httpAction)
    \s*\(
    """,
    re.VERBOSE,
)

EXCLUDED_ROUTERS = {
    # Python builtins
    "logging",
    "json",
    "re",
    "os",
    "sys",
    "time",
    "datetime",
    "pathlib",
    "asyncio",
    "collections",
    "typing",
    "dataclasses",
    "enum",
    # Test/utility routers
    "mock_router",
    "test_app",
}


# =============================================================================
# Data model
# =============================================================================


@dataclass
class ApiEndpoint:
    """One HTTP route handler in the Cianfhoghlaim monorepo."""

    id: str
    framework: str
    method: str
    path: str
    file_path: str
    line_number: int
    handler_name: str
    summary: str
    embedding: Annotated[Any, EMBEDDER]  # type: ignore[valid-type]

    __emd5_fields__: ClassVar[tuple[str, ...]] = ("summary",)


# =============================================================================
# Scan helpers (CPU-bound; called via asyncio.to_thread)
# =============================================================================


def _scan_file_for_endpoints(file_path: pathlib.Path) -> list[ApiEndpoint]:
    """Synchronously scan a single source file for HTTP endpoints."""
    try:
        text = file_path.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        return []

    endpoints: list[ApiEndpoint] = []
    rel_path = str(file_path)

    # FastAPI
    for match in _FASTAPI_RE.finditer(text):
        router = match.group("router")
        if router in EXCLUDED_ROUTERS or router.startswith("test_"):
            continue
        verb = match.group("verb").upper()
        path = match.group("path").strip("'\"")
        line_number = text[: match.start()].count("\n") + 1
        handler_name = _find_handler_name(text, match.end())
        endpoints.append(
            ApiEndpoint(
                id=f"fastapi:{verb}:{path}:{rel_path}:{line_number}",
                framework=ApiFramework.FASTAPI.value,
                method=verb,
                path=path,
                file_path=rel_path,
                line_number=line_number,
                handler_name=handler_name,
                summary=f"FastAPI {verb} {path} in {rel_path}:{line_number}",
                embedding=None,  # type: ignore[arg-type]
            )
        )

    # Hono
    for match in _HONO_RE.finditer(text):
        router = match.group("router")
        verb = match.group("verb").upper()
        if verb in {"USE", "ON"}:
            # Hono middleware; not a route. Skip.
            continue
        path = match.group("path").strip("'\"")
        # Only count if it looks like a path (starts with / or has a known
        # dynamic prefix). Skip bare method calls like `app.get(thing)`.
        if not path.startswith("/"):
            continue
        line_number = text[: match.start()].count("\n") + 1
        handler_name = _find_handler_name(text, match.end())
        endpoints.append(
            ApiEndpoint(
                id=f"hono:{verb}:{path}:{rel_path}:{line_number}",
                framework=ApiFramework.HONO.value,
                method=verb,
                path=path,
                file_path=rel_path,
                line_number=line_number,
                handler_name=handler_name,
                summary=f"Hono {verb} {path} in {rel_path}:{line_number}",
                embedding=None,  # type: ignore[arg-type]
            )
        )

    # TanStack Start
    for match in _TANSTACK_RE.finditer(text):
        verb_raw = match.group("verb")
        path = match.group("path").strip("'\"")
        line_number = text[: match.start()].count("\n") + 1
        kind = (
            "createFileRoute"
            if verb_raw == "createFileRoute"
            else "createServerFileRoute"
        )
        # Methods are declared inside the .methods(...) call which
        # follows — we record the route declaration, not the method set.
        endpoints.append(
            ApiEndpoint(
                id=f"tanstack:{kind}:{path}:{rel_path}:{line_number}",
                framework=ApiFramework.TANSTACK_START.value,
                method=HttpMethod.UNKNOWN.value,
                path=path,
                file_path=rel_path,
                line_number=line_number,
                handler_name=kind,
                summary=f"TanStack Start {kind} {path} in {rel_path}:{line_number}",
                embedding=None,  # type: ignore[arg-type]
            )
        )

    # Convex HTTP actions (no path — Convex exposes them under /api/<name>)
    for match in _CONVEX_HTTP_RE.finditer(text):
        line_number = text[: match.start()].count("\n") + 1
        handler_name = _find_handler_name(text, match.end())
        endpoints.append(
            ApiEndpoint(
                id=f"convex_http:HTTP_ACTION:{rel_path}:{line_number}",
                framework=ApiFramework.CONVEX_HTTP.value,
                method=HttpMethod.UNKNOWN.value,
                path="/api/<convex_action>",
                file_path=rel_path,
                line_number=line_number,
                handler_name=handler_name,
                summary=(
                    f"Convex HTTP action in {rel_path}:{line_number} "
                    f"({handler_name})"
                ),
                embedding=None,  # type: ignore[arg-type]
            )
        )

    return endpoints


def _find_handler_name(text: str, offset: int) -> str:
    """Best-effort: look 200 chars after the route declaration for
    a Python/TS function name on the same logical statement."""
    window = text[offset : offset + 200]
    # Python: def handler_name(...)
    py = re.search(r"def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", window)
    if py:
        return py.group(1)
    # TypeScript: const handler_name = async (...) => ...
    #   or function handler_name(...)
    ts = re.search(
        r"(?:function|const)\s+([A-Za-z_][A-Za-z0-9_]*)\s*[=(]",
        window,
    )
    if ts:
        return ts.group(1)
    return "<anonymous>"


def _walk_repo_for_endpoints(repo_root: pathlib.Path) -> list[ApiEndpoint]:
    """Walk the repo, scan each .py/.ts/.tsx/.js/.jsx file for endpoints."""
    endpoints: list[ApiEndpoint] = []
    candidates: list[pathlib.Path] = []
    for ext in ("*.py", "*.ts", "*.tsx", "*.js", "*.jsx"):
        for p in repo_root.rglob(ext):
            # Mirror the codebase_indexing.py excludes
            sp = str(p)
            if any(
                seg in sp
                for seg in (
                    "/.venv/",
                    "/venv/",
                    "/node_modules/",
                    "/__pycache__/",
                    "/target/",
                    "/dist/",
                    "/build/",
                    "/.turbo/",
                    "/.cocoindex_code/",
                    "/stedding/",
                    "/.git/",
                    "/docs/cocoindex/",
                )
            ):
                continue
            candidates.append(p)
    for p in candidates:
        endpoints.extend(_scan_file_for_endpoints(p))
    return endpoints


# =============================================================================
# v1 App
# =============================================================================


def _make_app():  # noqa: ANN202
    """Construct the api_indexing v1 App. Returns None when cocoindex is missing."""
    if not COCOINDEX_AVAILABLE:
        return None

    @coco.lifespan
    async def api_lifespan(  # type: ignore[no-redef]
        builder: coco.EnvironmentBuilder,  # type: ignore[valid-type]
    ) -> AsyncIterator[None]:
        from cocoindex.connectors.lancedb import (  # type: ignore[import-not-found]
            LanceAsyncConnection,
        )

        lance_conn = await LanceAsyncConnection.connect(LANCEDB_URI)
        builder.provide(LANCE_DB, lance_conn)
        builder.provide(
            EMBEDDER,
            SentenceTransformerEmbedder(EMBED_MODEL),
        )
        yield

    @coco.fn
    async def api_app_main(  # type: ignore[no-redef]
        repo_root: pathlib.Path,
    ) -> None:
        target_table = await lancedb.mount_table_target(
            LANCE_DB,  # type: ignore[arg-type]
            table_name=LANCEDB_TABLE,
            table_schema=await lancedb.TableSchema.from_class(
                ApiEndpoint, primary_key=["id"]
            ),
        )
        # Walk the repo in a thread (CPU-bound regex scan).
        endpoints = await asyncio.to_thread(_walk_repo_for_endpoints, repo_root)
        # Upsert in chunks of 100 to respect the HNSW rule.
        for i in range(0, len(endpoints), 100):
            batch = endpoints[i : i + 100]
            await target_table.upsert(batch)

    return coco.App(
        coco.AppConfig(name="ApiIndex"),
        api_app_main,
        repo_root=DEFAULT_REPO_ROOT,
    )


api_app = _make_app()


# =============================================================================
# Query helpers
# =============================================================================


async def search_api_endpoints(
    query: str,
    framework: str | None = None,
    method: str | None = None,
    limit: int = TOP_K,
) -> list[dict[str, Any]]:
    """Semantic search over the API surface.

    Example: `await search_api_endpoints("agent memory add", limit=5)`
    will return the top-5 endpoints semantically related to adding
    memory, optionally filtered by framework (e.g. `fastapi`).
    """
    if not COCOINDEX_AVAILABLE or api_app is None:
        return []
    embedder = coco.use_context(EMBEDDER)  # type: ignore[arg-type]
    conn = coco.use_context(LANCE_DB)  # type: ignore[arg-type]
    query_vec = await embedder.embed(query)
    table = await conn.open_table(LANCEDB_TABLE)
    search = table.search(query_vec, vector_column_name="embedding")
    conditions: list[str] = []
    if framework:
        conditions.append(f"framework = '{framework}'")
    if method:
        conditions.append(f"method = '{method.upper()}'")
    if conditions:
        search = search.where(" AND ".join(conditions))
    rows = await search.limit(limit).to_list()
    for r in rows:
        r["score"] = 1.0 - r.get("_distance", 0.0)
    return rows


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    "COCOINDEX_AVAILABLE",
    "LANCEDB_URI",
    "EMBED_MODEL",
    "EMBED_DIM",
    "REFRESH_INTERVAL",
    "LANCEDB_TABLE",
    "TOP_K",
    "DEFAULT_REPO_ROOT",
    "ApiFramework",
    "HttpMethod",
    "ApiEndpoint",
    "_scan_file_for_endpoints",
    "_walk_repo_for_endpoints",
    "search_api_endpoints",
]
if COCOINDEX_AVAILABLE and api_app is not None:
    __all__.append("api_app")
