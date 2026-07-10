"""
Configuration File Indexing CocoIndex v1 App.

Indexes every configuration file in the Cianfhoghlaim monorepo. Each
row in the `config_files` LanceDB table is one config file. Embeddings
enable semantic search: e.g. "where do I configure the Dagster port"
returns the relevant wrangler / compose / mise / turbo / package.json
rows.

Detected config kinds (round 7 phase 2):

- **docker-compose** — every `docker-compose*.yml`, `compose.yaml`
- **mise** — the root `mise.toml` and per-package `mise.toml` files
- **package** — every `package.json` (bun workspace members)
- **pyproject** — every `pyproject.toml` (uv workspace members)
- **turbo** — the root `turbo.json` and per-package variants
- **wrangler** — every `wrangler.jsonc` / `wrangler.toml` (CF workers
  + D1 + KV + R2)
- **env** — every `.env.example`, `.infisical.env`
- **k8s** — every `*.k8s.yaml`, `kustomization.yaml`
- **pulumi** — every `Pulumi.yaml`, `Pulumi.<stack>.yaml`
- **dg** — the `dg.toml` (Dagster code-location manifest)
- **github** — every `.github/workflows/*.yml` (CI workflows)
- **justfile** — every `justfile`

Per-row fields:
- `file_path` (relative to repo root)
- `kind` (one of the kinds above)
- `parse_status` (parsed / failed / empty)
- `summary` (human-readable, e.g. "wrangler.jsonc with 2 D1 bindings
  + 1 KV namespace + 3 R2 buckets")
- `package_count` (0 for non-workspace configs)
- `embedding`

Reference: this is the v1-native replacement for the v0 grep at
`codeolas/cocoindex_flows/config_indexing.py`. v1 adds embeddings
+ workspace-aware metadata (package_count, etc.) and a structured
summary derived from the parsed config.

Operational contract:
- Live mode (`cocoindex update -L ...`) is supported.
- Excludes mirror the codebase_indexing.py excludes.
- The App walks the repo for known config filenames AND any
  `wrangler.jsonc` / `wrangler.toml`.
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
EMBED_MODEL = os.getenv("CONFIG_EMBED_MODEL", "BAAI/bge-m3")
EMBED_DIM = 1024
REFRESH_INTERVAL = datetime.timedelta(seconds=int(os.getenv("CONFIG_REFRESH_SECS", "900")))
LANCEDB_TABLE = "config_files"
TOP_K = 15

DEFAULT_REPO_ROOT = pathlib.Path(
    os.getenv(
        "CONFIG_REPO_ROOT",
        str(pathlib.Path(__file__).resolve().parents[5]),
    )
)

LANCE_DB: Any = "lance_db_config"
EMBEDDER: Any = "embedder_config"

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
# Config kind enum
# =============================================================================


class ConfigKind(str, Enum):
    DOCKER_COMPOSE = "docker-compose"
    MISE = "mise"
    PACKAGE = "package"
    PYPROJECT = "pyproject"
    TURBO = "turbo"
    WRANGLER = "wrangler"
    ENV = "env"
    K8S = "k8s"
    PULUMI = "pulumi"
    DG = "dg"
    GITHUB = "github"
    JUSTFILE = "justfile"
    UNKNOWN = "unknown"


# Filename → kind mapping (first-match wins)
_FILENAME_KIND_MAP = [
    ("mise.toml", ConfigKind.MISE),
    ("turbo.json", ConfigKind.TURBO),
    ("pyproject.toml", ConfigKind.PYPROJECT),
    ("package.json", ConfigKind.PACKAGE),
    ("wrangler.jsonc", ConfigKind.WRANGLER),
    ("wrangler.toml", ConfigKind.WRANGLER),
    ("dg.toml", ConfigKind.DG),
    ("justfile", ConfigKind.JUSTFILE),
    ("Pulumi.yaml", ConfigKind.PULUMI),
    ("docker-compose.yml", ConfigKind.DOCKER_COMPOSE),
    ("docker-compose.yaml", ConfigKind.DOCKER_COMPOSE),
    ("compose.yaml", ConfigKind.DOCKER_COMPOSE),
    ("compose.yml", ConfigKind.DOCKER_COMPOSE),
    (".env.example", ConfigKind.ENV),
    (".infisical.env", ConfigKind.ENV),
]


# =============================================================================
# Data model
# =============================================================================


@dataclass
class ConfigFile:
    """One config file in the Cianfhoghlaim monorepo."""

    id: str
    file_path: str
    kind: str
    parse_status: str
    summary: str
    package_count: int
    embedding: Annotated[Any, EMBEDDER]  # type: ignore[valid-type]

    __emd5_fields__: ClassVar[tuple[str, ...]] = ("summary",)


# =============================================================================
# Scan helpers (CPU-bound; called via asyncio.to_thread)
# =============================================================================


def _classify(file_path: pathlib.Path) -> ConfigKind:
    """Map a file path to a ConfigKind based on its name."""
    name = file_path.name
    # Docker compose is special: any `docker-compose*.yml` or `compose.y*ml`
    if name.startswith("docker-compose") and name.endswith((".yml", ".yaml")):
        return ConfigKind.DOCKER_COMPOSE
    if name in ("compose.yaml", "compose.yml"):
        return ConfigKind.DOCKER_COMPOSE
    if name.startswith("wrangler."):
        return ConfigKind.WRANGLER
    for fname, kind in _FILENAME_KIND_MAP:
        if name == fname:
            return kind
    if name.endswith(".k8s.yaml") or name == "kustomization.yaml":
        return ConfigKind.K8S
    if (
        file_path.parent == file_path.parent.parent / ".github" / "workflows"
        and name.endswith((".yml", ".yaml"))
    ):
        return ConfigKind.GITHUB
    return ConfigKind.UNKNOWN


def _summarize(file_path: pathlib.Path, kind: ConfigKind) -> tuple[str, int, str]:
    """Return (summary, package_count, parse_status) for a config file."""
    try:
        text = file_path.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        return (f"{kind.value} {file_path.name} (unreadable)", 0, "failed")

    if not text.strip():
        return (f"{kind.value} {file_path.name} (empty)", 0, "empty")

    pkg_count = 0
    try:
        if kind == ConfigKind.WRANGLER:
            # Strip // comments
            text_clean = re.sub(r"//[^\n]*", "", text)
            data = json.loads(text_clean)
            d1 = len(data.get("d1_databases", []))
            kv = len(data.get("kv_namespaces", []))
            r2 = len(data.get("r2_buckets", []))
            summary = (
                f"{file_path.name}: D1×{d1} KV×{kv} R2×{r2}"
            )
        elif kind == ConfigKind.PYPROJECT:
            data = _safe_toml(text)
            deps_raw = data.get("project", {}).get("dependencies", [])
            # `dependencies` can be a list[str] (uv) or a dict
            # (legacy poetry). Coerce to a list for the count.
            n_deps = (
                len(deps_raw) if isinstance(deps_raw, list) else len(deps_raw)
            )
            summary = (
                f"{file_path.name}: {n_deps} deps, "
                f"{len(data.get('tool', {}))} tool configs"
            )
        elif kind == ConfigKind.PACKAGE:
            data = json.loads(text)
            deps = list(data.get("dependencies", {}).keys())
            ws = data.get("workspaces", [])
            pkg_count = len(ws) if isinstance(ws, list) else 1
            summary = (
                f"{file_path.name}: {len(deps)} deps, "
                f"{pkg_count} workspaces"
            )
        elif kind == ConfigKind.TURBO:
            data = json.loads(text)
            tasks = list(data.get("tasks", {}).keys())
            summary = f"{file_path.name}: turbo tasks {','.join(tasks[:6])}"
        elif kind == ConfigKind.MISE:
            data = _safe_toml(text)
            tools = list(data.get("tools", {}).keys())
            summary = f"{file_path.name}: mise tools {','.join(tools[:6])}"
        elif kind == ConfigKind.DOCKER_COMPOSE:
            # Cheap heuristic: count `services:` keys
            svcs = re.findall(r"^ {2}(\w[\w-]*):$", text, flags=re.MULTILINE)
            summary = f"{file_path.name}: {len(svcs)} services"
        elif kind == ConfigKind.DG:
            data = _safe_toml(text)
            locs = [loc.strip() for loc in data.get("code_locations", [])]
            pkg_count = len(locs)
            summary = (
                f"{file_path.name}: {len(locs)} Dagster code locations"
            )
        elif kind == ConfigKind.PULUMI:
            data = _safe_yaml(text)
            summary = f"{file_path.name}: pulumi project"
        elif kind == ConfigKind.K8S:
            data = _safe_yaml(text)
            kind_str = data.get("kind", "Unknown") if isinstance(data, dict) else "?"
            summary = f"{file_path.name}: k8s {kind_str}"
        elif kind == ConfigKind.GITHUB:
            data = _safe_yaml(text)
            on_keys = (
                list(data.get("on", data.get(True, {})).keys())
                if isinstance(data, dict)
                else []
            )
            jobs = (
                list(data.get("jobs", {}).keys())
                if isinstance(data, dict)
                else []
            )
            summary = (
                f"{file_path.name}: triggers {on_keys[:3]}, "
                f"jobs {jobs[:3]}"
            )
        elif kind == ConfigKind.JUSTFILE:
            recipes = re.findall(r"^([a-zA-Z_][\w-]*):", text, flags=re.MULTILINE)
            summary = f"{file_path.name}: {len(recipes)} recipes"
        else:
            summary = f"{file_path.name}: {len(text)} bytes"
    except Exception as e:  # noqa: BLE001
        return (f"{kind.value} {file_path.name} (parse failed: {e})", 0, "failed")

    return (summary, pkg_count, "parsed")


def _safe_toml(text: str) -> dict[str, Any]:
    """Try tomllib first; fall back to a very small subset parser."""
    try:
        import tomllib
        return tomllib.loads(text)
    except ImportError:
        return _tiny_toml(text)


def _tiny_toml(text: str) -> dict[str, Any]:
    """A 30-line TOML subset parser — only [section] tables + key=value
    pairs. Used as a graceful fallback if tomllib is unavailable
    (e.g. Python 3.10)."""
    out: dict[str, Any] = {}
    section = out
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            sec = line[1:-1].strip()
            if sec not in out:
                out[sec] = {}
            section = out[sec]
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip()
            if v.startswith('"') and v.endswith('"'):
                v = v[1:-1]
            elif v.startswith("'") and v.endswith("'"):
                v = v[1:-1]
            elif v.startswith("["):
                v = _parse_inline_array(v)
            else:
                try:
                    v = int(v)
                except ValueError:
                    try:
                        v = float(v)
                    except ValueError:
                        v = v
            section[k] = v
    return out


def _parse_inline_array(v: str) -> list[str]:
    """Parse `["a", "b", "c"]` style arrays."""
    inner = v.strip("[]")
    parts: list[str] = []
    for piece in inner.split(","):
        piece = piece.strip().strip("'\"")
        if piece:
            parts.append(piece)
    return parts


def _safe_yaml(text: str) -> Any:
    """Try PyYAML; fall back to None on failure."""
    try:
        import yaml  # type: ignore[import-not-found]
        return yaml.safe_load(text)
    except Exception:  # noqa: BLE001
        return None


def _walk_repo_for_config(repo_root: pathlib.Path) -> list[ConfigFile]:
    """Walk the repo, classify each file by name, summarise it."""
    configs: list[ConfigFile] = []
    seen: set[str] = set()
    # 1) Match by exact filename (fast, deterministic)
    for fname, kind in _FILENAME_KIND_MAP:
        for p in repo_root.rglob(fname):
            sp = str(p)
            if any(ex in sp for ex in EXCLUDE_PATH_SUBSTRINGS):
                continue
            rel = str(p.relative_to(repo_root))
            if rel in seen:
                continue
            seen.add(rel)
            summary, pkg_count, status = _summarize(p, kind)
            configs.append(
                ConfigFile(
                    id=f"config:{rel}",
                    file_path=rel,
                    kind=kind.value,
                    parse_status=status,
                    summary=summary,
                    package_count=pkg_count,
                    embedding=None,  # type: ignore[arg-type]
                )
            )
    # 2) Pattern-match for docker-compose / k8s / github workflows
    for pat, kind in (
        ("docker-compose*.y*ml", ConfigKind.DOCKER_COMPOSE),
        ("compose.y*ml", ConfigKind.DOCKER_COMPOSE),
        ("*.k8s.yaml", ConfigKind.K8S),
        ("kustomization.yaml", ConfigKind.K8S),
    ):
        for p in repo_root.rglob(pat):
            sp = str(p)
            if any(ex in sp for ex in EXCLUDE_PATH_SUBSTRINGS):
                continue
            rel = str(p.relative_to(repo_root))
            if rel in seen:
                continue
            seen.add(rel)
            summary, pkg_count, status = _summarize(p, kind)
            configs.append(
                ConfigFile(
                    id=f"config:{rel}",
                    file_path=rel,
                    kind=kind.value,
                    parse_status=status,
                    summary=summary,
                    package_count=pkg_count,
                    embedding=None,  # type: ignore[arg-type]
                )
            )
    # 3) .github/workflows/*.yml
    gh_dir = repo_root / ".github" / "workflows"
    if gh_dir.is_dir():
        for p in gh_dir.rglob("*.yml"):
            sp = str(p)
            if any(ex in sp for ex in EXCLUDE_PATH_SUBSTRINGS):
                continue
            rel = str(p.relative_to(repo_root))
            if rel in seen:
                continue
            seen.add(rel)
            summary, pkg_count, status = _summarize(p, ConfigKind.GITHUB)
            configs.append(
                ConfigFile(
                    id=f"config:{rel}",
                    file_path=rel,
                    kind=ConfigKind.GITHUB.value,
                    parse_status=status,
                    summary=summary,
                    package_count=pkg_count,
                    embedding=None,  # type: ignore[arg-type]
                )
            )
    return configs


# =============================================================================
# v1 App
# =============================================================================


def _make_app():  # noqa: ANN202
    if not COCOINDEX_AVAILABLE:
        return None

    @coco.lifespan
    async def config_lifespan(  # type: ignore[no-redef]
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
    async def config_app_main(  # type: ignore[no-redef]
        repo_root: pathlib.Path,
    ) -> None:
        target_table = await lancedb.mount_table_target(
            LANCE_DB,  # type: ignore[arg-type]
            table_name=LANCEDB_TABLE,
            table_schema=await lancedb.TableSchema.from_class(
                ConfigFile, primary_key=["id"]
            ),
        )
        target_table.declare_vector_index(column="embedding")  # R4
        configs = await asyncio.to_thread(_walk_repo_for_config, repo_root)
        for i in range(0, len(configs), 100):
            batch = configs[i : i + 100]
            await target_table.upsert(batch)

    return coco.App(
        coco.AppConfig(name="ConfigIndex"),
        config_app_main,
        repo_root=DEFAULT_REPO_ROOT,
    )


config_app = _make_app()


# =============================================================================
# Query helpers
# =============================================================================


async def search_config(
    query: str,
    kind: str | None = None,
    limit: int = TOP_K,
) -> list[dict[str, Any]]:
    """Semantic search over config files.

    Example: `await search_config("Dagster port", kind="mise")`
    returns the top mise.toml rows semantically related to Dagster
    port configuration.
    """
    if not COCOINDEX_AVAILABLE or config_app is None:
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
    "ConfigKind",
    "ConfigFile",
    "_classify",
    "_summarize",
    "_walk_repo_for_config",
    "search_config",
]
if COCOINDEX_AVAILABLE and config_app is not None:
    __all__.append("config_app")
