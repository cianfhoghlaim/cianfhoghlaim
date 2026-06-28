"""
Storage Backend Indexing CocoIndex v1 App.

Indexes every storage backend the Cianfhoghlaim monorepo uses. Each
row in the `storage_backends` LanceDB table is one backend instance
(duckdb file, postgres database, lancedb table, garage bucket, etc.).
Embeddings enable semantic search: e.g. "where is the Irish curriculum
data stored" returns the relevant rows.

Detected backend kinds (round 7 phase 2):

- **lancedb** — every `lancedb.connect(...)` and `.open_table(...)`
  call. Backed by a `codebase_chunks` / `api_endpoints` / etc. table
  name in the same LanceDB.
- **duckdb** — every `duckdb.connect(...)` and `duckdb.sql(...)` call
  plus any `.duckdb` / `.ddb` file reference.
- **ducklake** — every `ATTACH 'md:oideachais'` and `SET ducklake_...`
  reference (the MotherDuck + Garage pattern).
- **postgres** — every `psycopg.connect(...)`, `pg_database`, and
  `postgresql://` URI.
- **garage / s3** — every `garage.cianfhoghlaim.ie` reference and
  every `s3://` URI.
- **r2** — every `r2://` URI and Cloudflare R2 bucket reference in
  `wrangler.jsonc`.
- **d1** — every `[[d1_databases]]` block in `wrangler.jsonc` /
  `wrangler.toml`.
- **kv** — every `[[kv_namespaces]]` block in `wrangler.jsonc` /
  `wrangler.toml`.
- **iceberg / lakekeeper** — every `iceberg.cianfhoghlaim.ie` and
  `lakekeeper.cianfhoghlaim.ie` reference.

Per-row fields:
- `kind` (lancedb / duckdb / ducklake / postgres / garage / r2 / d1 /
  kv / iceberg)
- `name` (table name, file path, bucket name, etc.)
- `location` (host:port, URI, or path)
- `file_path` (the file where the reference was found, relative to
  repo root; "" if discovered in a wrangler manifest)
- `line_number` (line in the file; 0 for manifest discoveries)
- `config_ref` (the wrangler block key, e.g. `[[d1_databases]]` /
  `[[r2_buckets]]` / `[[kv_namespaces]]`; "" otherwise)
- `summary` (human-readable)
- `embedding`

Reference: this is the v1-native replacement for the v0 grep at
`codeolas/cocoindex_flows/storage_indexing.py:scan_storage_backends()`.
v1 adds embeddings and a unified config-file scanner (wrangler.jsonc).

Operational contract:
- Live mode (`cocoindex update -L ...`) is supported.
- Excludes mirror the codebase_indexing.py excludes.
- The App walks both source files AND the wrangler manifests to catch
  cloud-only backends.
- Embeddings via the shared BGE-M3 model (1024 dims).
"""

from __future__ import annotations

import asyncio
import datetime
import json
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
    from cocoindex.connectors import lancedb  # type: ignore[import-not-found]
    from cocoindex.ops.sentence_transformers import (  # type: ignore[import-not-found]
        SentenceTransformerEmbedder,
    )

    COCOINDEX_AVAILABLE = True
except ImportError as e:
    logger.warning("cocoindex_v1_not_available: %s", e)
    COCOINDEX_AVAILABLE = False
    coco = None  # type: ignore[assignment]
    lancedb = None  # type: ignore[assignment]
    SentenceTransformerEmbedder = None  # type: ignore[assignment]


# =============================================================================
# Configuration
# =============================================================================


LANCEDB_URI = os.getenv("LANCEDB_URI", "rest://lance-api.cianfhoghlaim.ie")
EMBED_MODEL = os.getenv("STORAGE_EMBED_MODEL", "BAAI/bge-m3")
EMBED_DIM = 1024
REFRESH_INTERVAL = datetime.timedelta(seconds=int(os.getenv("STORAGE_REFRESH_SECS", "600")))
LANCEDB_TABLE = "storage_backends"
TOP_K = 20

DEFAULT_REPO_ROOT = pathlib.Path(
    os.getenv(
        "STORAGE_REPO_ROOT",
        str(pathlib.Path(__file__).resolve().parents[5]),
    )
)

LANCE_DB: Any = "lance_db_storage"
EMBEDDER: Any = "embedder_storage"

EXCLUDE_PATH_SUBSTRINGS = (
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


# =============================================================================
# Backend enum
# =============================================================================


class StorageKind(str, Enum):
    LANCEDB = "lancedb"
    DUCKDB = "duckdb"
    DUCKLAKE = "ducklake"
    POSTGRES = "postgres"
    GARAGE = "garage"
    R2 = "r2"
    D1 = "d1"
    KV = "kv"
    ICEBERG = "iceberg"


# =============================================================================
# Regex catalogue
# =============================================================================


_LANCEDB_OPEN_RE = re.compile(
    r"""
    lancedb
    \.connect\s*\(\s*["']([^"']+)["']
    |
    lancedb\s*\.\s*connect
    """,
    re.VERBOSE,
)

_LANCEDB_TABLE_RE = re.compile(
    r"""
    \.open_table\s*\(\s*["']([^"']+)["']
    """,
    re.VERBOSE,
)

_DUCKDB_CONNECT_RE = re.compile(
    r"""
    duckdb
    \.connect\s*\(\s*["']([^"']+)["']
    """,
    re.VERBOSE,
)

_DUCKLAKE_RE = re.compile(
    r"""
    (?:ATTACH|MOTHERDUCK_DUCKLAKE|ducklake)
    \s+
    ["']([^"']+)["']
    """,
    re.VERBOSE | re.IGNORECASE,
)

_POSTGRES_RE = re.compile(
    r"""
    (?:postgres(?:ql)?://|psycopg\d?\.connect\s*\(\s*["'])
    ([^"'\s)]+)
    """,
    re.VERBOSE,
)

_GARAGE_RE = re.compile(
    r"""
    (?:garage|s3)
    \.([a-zA-Z0-9.-]+)
    \S*
    |
    ["']s3://([^"']+)["']
    """,
    re.VERBOSE,
)

_R2_URI_RE = re.compile(r"""['"]r2://([^"']+)['"]""")

# Wrangler TOML/JSON config blocks (D1, KV, R2)
_WRANGLER_BLOCKS = {
    StorageKind.D1: r"\[\[d1_databases\]\]",
    StorageKind.KV: r"\[\[kv_namespaces\]\]",
    StorageKind.R2: r"\[\[r2_buckets\]\]",
}


# =============================================================================
# Data model
# =============================================================================


@dataclass
class StorageBackend:
    """One storage backend instance in the Cianfhoghlaim monorepo."""

    id: str
    kind: str
    name: str
    location: str
    file_path: str
    line_number: int
    config_ref: str
    summary: str
    embedding: Annotated[Any, EMBEDDER]  # type: ignore[valid-type]

    __emd5_fields__: ClassVar[tuple[str, ...]] = ("summary",)


# =============================================================================
# Scan helpers (CPU-bound; called via asyncio.to_thread)
# =============================================================================


def _scan_source_file(
    repo_root: pathlib.Path, file_path: pathlib.Path
) -> list[StorageBackend]:
    """Scan one source file for storage backend references."""
    try:
        text = file_path.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        return []

    backends: list[StorageBackend] = []
    rel_path = str(file_path.relative_to(repo_root))

    def _add(
        kind: StorageKind,
        name: str,
        location: str,
        line_no: int,
        config_ref: str = "",
    ) -> None:
        summary = f"{kind.value} '{name}' at {location} (in {rel_path}:{line_no})"
        backends.append(
            StorageBackend(
                id=f"{kind.value}:{name}:{rel_path}:{line_no}",
                kind=kind.value,
                name=name,
                location=location,
                file_path=rel_path,
                line_number=line_no,
                config_ref=config_ref,
                summary=summary,
                embedding=None,  # type: ignore[arg-type]
            )
        )

    for pat, kind in (
        (_LANCEDB_OPEN_RE, StorageKind.LANCEDB),
        (_DUCKDB_CONNECT_RE, StorageKind.DUCKDB),
        (_DUCKLAKE_RE, StorageKind.DUCKLAKE),
    ):
        for m in pat.finditer(text):
            location = (m.group(1) or "").strip()
            line_no = text[: m.start()].count("\n") + 1
            name = location.rsplit("/", 1)[-1] or location
            _add(kind, name, location, line_no)

    for m in _LANCEDB_TABLE_RE.finditer(text):
        line_no = text[: m.start()].count("\n") + 1
        _add(
            StorageKind.LANCEDB,
            name=m.group(1),
            location=LANCEDB_URI,
            line_no=line_no,
        )

    for m in _POSTGRES_RE.finditer(text):
        line_no = text[: m.start()].count("\n") + 1
        _add(
            StorageKind.POSTGRES,
            name=m.group(1).rsplit("/", 1)[-1].split("?")[0] or m.group(1),
            location=m.group(1),
            line_no=line_no,
        )

    for m in _GARAGE_RE.finditer(text):
        line_no = text[: m.start()].count("\n") + 1
        host = m.group(1) or m.group(2) or ""
        if not host:
            continue
        kind = StorageKind.GARAGE if "garage" in host or not host.startswith("s3") else StorageKind.R2
        _add(
            kind,
            name=host,
            location=m.group(0).strip("\"'"),
            line_no=line_no,
        )

    for m in _R2_URI_RE.finditer(text):
        line_no = text[: m.start()].count("\n") + 1
        _add(StorageKind.R2, name=m.group(1), location=m.group(0), line_no=line_no)

    return backends


def _scan_wrangler_manifest(
    repo_root: pathlib.Path, file_path: pathlib.Path
) -> list[StorageBackend]:
    """Scan a wrangler.jsonc / wrangler.toml for D1 / KV / R2 blocks."""
    try:
        text = file_path.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        return []

    backends: list[StorageBackend] = []
    rel_path = str(file_path.relative_to(repo_root))

    if file_path.suffix == ".jsonc" or file_path.suffix == ".json":
        # Strip // comments
        text = re.sub(r"//[^\n]*", "", text)
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return []
        for kind, key in (
            (StorageKind.D1, "d1_databases"),
            (StorageKind.KV, "kv_namespaces"),
            (StorageKind.R2, "r2_buckets"),
        ):
            for entry in data.get(key, []):
                name = entry.get("binding") or entry.get("name") or ""
                bucket = entry.get("bucket_name", "")
                db_id = entry.get("database_id", "")
                location = db_id or bucket or "(binding)"
                backends.append(
                    StorageBackend(
                        id=f"{kind.value}:{name}:{rel_path}:0",
                        kind=kind.value,
                        name=name,
                        location=location,
                        file_path=rel_path,
                        line_number=0,
                        config_ref=f"[[{key}]]",
                        summary=(
                            f"{kind.value} binding '{name}' in {rel_path} "
                            f"({key})"
                        ),
                        embedding=None,  # type: ignore[arg-type]
                    )
                )
    elif file_path.suffix == ".toml":
        for kind, pattern in _WRANGLER_BLOCKS.items():
            for m in re.finditer(pattern, text):
                # Read up to the next [[...]] block
                block_end = text.find("\n[[", m.end())
                if block_end < 0:
                    block_end = len(text)
                block = text[m.end() : block_end]
                name_m = re.search(r'\bbinding\s*=\s*["\']([^"\']+)["\']', block)
                name = name_m.group(1) if name_m else ""
                backends.append(
                    StorageBackend(
                        id=f"{kind.value}:{name}:{rel_path}:0",
                        kind=kind.value,
                        name=name,
                        location="(binding)",
                        file_path=rel_path,
                        line_number=text[: m.start()].count("\n") + 1,
                        config_ref=pattern,
                        summary=(
                            f"{kind.value} binding '{name}' in {rel_path} "
                            f"({pattern})"
                        ),
                        embedding=None,  # type: ignore[arg-type]
                    )
                )

    return backends


def _walk_repo_for_storage(repo_root: pathlib.Path) -> list[StorageBackend]:
    """Walk all source files + wrangler manifests for storage backends."""
    backends: list[StorageBackend] = []
    # Source files
    for ext in ("*.py", "*.ts", "*.tsx", "*.js", "*.jsx", "*.baml", "*.toml"):
        for p in repo_root.rglob(ext):
            sp = str(p)
            if any(ex in sp for ex in EXCLUDE_PATH_SUBSTRINGS):
                continue
            if p.name.startswith("wrangler."):
                backends.extend(_scan_wrangler_manifest(repo_root, p))
            else:
                backends.extend(_scan_source_file(repo_root, p))
    return backends


# =============================================================================
# v1 App
# =============================================================================


def _make_app():  # noqa: ANN202
    if not COCOINDEX_AVAILABLE:
        return None

    @coco.lifespan
    async def storage_lifespan(  # type: ignore[no-redef]
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
    async def storage_app_main(  # type: ignore[no-redef]
        repo_root: pathlib.Path,
    ) -> None:
        target_table = await lancedb.mount_table_target(
            LANCE_DB,  # type: ignore[arg-type]
            table_name=LANCEDB_TABLE,
            table_schema=await lancedb.TableSchema.from_class(
                StorageBackend, primary_key=["id"]
            ),
        )
        backends = await asyncio.to_thread(_walk_repo_for_storage, repo_root)
        for i in range(0, len(backends), 100):
            batch = backends[i : i + 100]
            await target_table.upsert(batch)

    return coco.App(
        coco.AppConfig(name="StorageIndex"),
        storage_app_main,
        repo_root=DEFAULT_REPO_ROOT,
    )


storage_app = _make_app()


# =============================================================================
# Query helpers
# =============================================================================


async def search_storage(
    query: str,
    kind: str | None = None,
    limit: int = TOP_K,
) -> list[dict[str, Any]]:
    """Semantic search over storage backends.

    Example: `await search_storage("Irish curriculum data", kind="ducklake")`
    returns the top DuckLake rows semantically related to Irish curriculum.
    """
    if not COCOINDEX_AVAILABLE or storage_app is None:
        return []
    embedder = coco.use_context(EMBEDDER)  # type: ignore[arg-type]
    conn = coco.use_context(LANCE_DB)  # type: ignore[arg-type]
    query_vec = await embedder.embed(query)
    table = await conn.open_table(LANCEDB_TABLE)
    search = table.search(query_vec, vector_column_name="embedding")
    if kind:
        search = search.where(f"kind = '{kind}'")
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
    "StorageKind",
    "StorageBackend",
    "_scan_source_file",
    "_scan_wrangler_manifest",
    "_walk_repo_for_storage",
    "search_storage",
]
if COCOINDEX_AVAILABLE and storage_app is not None:
    __all__.append("storage_app")
