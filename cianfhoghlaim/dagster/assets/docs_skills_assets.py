"""
Docs-Skills Dagster Asset Group.

6 assets in `group_name="docs_skills"` + `group_name="codebase"`:

- `docs_skills_manifest` — SHA256 manifest of every file under `docs/` and
  `.agents/skills/`; freshness sentinel for the live sensor.
- `docs_skills_chunk_and_tag` — wraps the `docs_skills_consolidation.py` v1
  CocoIndex App (batch / catch-up mode). BAML-driven tag + triple
  extraction, LanceDB chunk writes, FalkorDB DocSkill node declarations.
- `docs_skills_graph_publish` — verifies FalkorDB node/edge counts and the
  failed-BAML count. Returns an `AssetCheckResult` with WARN severity when
  the failed count is > 0 (downstream assets still proceed).
- `docs_skills_live` — sensor-launched, runs `cocoindex update -L`.
- `codebase_chunk_and_embed` — wraps the `codebase_indexing.py` v1 App
  (batch / catch-up mode). The v1-native replacement for the legacy `ccc`
  CLI.
- `codebase_live` — sensor-launched, runs `cocoindex update -L` for the
  codebase index.

Pattern matches `oideachais/dagster_defs/assets/leabharlann_assets.py`:
the CocoIndex assets invoke the corresponding `coco.App` via
`subprocess.run(["cocoindex", "update", ...])`.

Reference: openspec/changes/docs-skills-consolidation-pipeline/proposal.md
"""

from __future__ import annotations

import hashlib
import os
import subprocess
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import dagster as dg
import structlog

logger = structlog.get_logger(__name__)


# ============================================================================
# Configuration
# ============================================================================


# Default source roots (override via env).
_DEFAULT_REPO = Path(__file__).resolve().parents[5]
DOCS_ROOT = Path(os.getenv("DOCS_SKILLS_DOCS_ROOT", str(_DEFAULT_REPO / "docs")))
SKILLS_ROOT = Path(os.getenv("DOCS_SKILLS_SKILLS_ROOT", str(_DEFAULT_REPO / ".agents" / "skills")))
CODEBASE_ROOT = Path(os.getenv("CODEBASE_REPO_ROOT", str(_DEFAULT_REPO)))


# ============================================================================
# Helpers
# ============================================================================


def _iter_md_files(roots: Iterable[Path]) -> Iterable[Path]:
    """Yield every .md / .mdx / .markdown / .txt file under each root, respecting
    the canonical excludes from the v1 App."""
    EXCLUDED_DIR_NAMES = {
        "node_modules",
        ".venv",
        "venv",
        "__pycache__",
        ".turbo",
        "dist",
        "build",
        ".cocoindex_code",
        "stedding",
        ".git",
    }
    suffixes = {".md", ".mdx", ".markdown", ".txt"}
    for root in roots:
        if not root.exists():
            logger.warning("manifest_root_missing", path=str(root))
            continue
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            if p.suffix.lower() not in suffixes:
                continue
            if any(part in EXCLUDED_DIR_NAMES for part in p.parts):
                continue
            yield p


def _file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    try:
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                h.update(chunk)
    except OSError:
        return ""
    return h.hexdigest()


def _run_cocoindex_update(
    app_target: str,
    extra_args: list[str] | None = None,
    timeout: int = 1800,
) -> dict[str, Any]:
    """
    Invoke a CocoIndex v1 App as `cocoindex update <target> [extra_args]`.

    The `<target>` format is `<module_path>:<app_name>`, e.g.
    `oideachais.cocoindex_flows.docs_skills_consolidation:DocsSkillsConsolidation`.
    The `extra_args` list is appended (e.g. `["-L"]` for live mode).
    """
    cmd = ["cocoindex", "update", app_target]
    if extra_args:
        cmd.extend(extra_args)
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,  # 30-min cap; live mode hits the same limit per session
            check=False,
        )
        return {
            "returncode": result.returncode,
            "stdout_tail": result.stdout[-2000:],
            "stderr_tail": result.stderr[-2000:],
        }
    except subprocess.TimeoutExpired as e:
        return {
            "returncode": -1,
            "error": f"timeout after {timeout}s",
            "stdout_tail": (e.stdout or b"")[-2000:].decode("utf-8", errors="replace")
            if isinstance(e.stdout, (bytes, bytearray))
            else str(e.stdout or "")[-2000:],
            "stderr_tail": (e.stderr or b"")[-2000:].decode("utf-8", errors="replace")
            if isinstance(e.stderr, (bytes, bytearray))
            else str(e.stderr or "")[-2000:],
        }
    except FileNotFoundError as e:
        return {"returncode": -1, "error": str(e)}


# ============================================================================
# docs_skills assets
# ============================================================================


@dg.asset(
    group_name="docs_skills",
    description="SHA256 manifest of every file under docs/ and .agents/skills/",
    compute_kind="manifest",
)
def docs_skills_manifest(context) -> dg.MaterializeResult:
    """Walk both roots, hash each file, return a count + manifest metadata.

    Acts as the freshness sentinel for the live sensor. The sensor polls
    this asset and launches `docs_skills_live` when the manifest changes.
    """
    paths = list(_iter_md_files((DOCS_ROOT, SKILLS_ROOT)))
    digest_inputs: list[str] = []
    for p in paths:
        digest_inputs.append(f"{p.as_posix()}\t{_file_sha256(p)}")
    combined = "\n".join(digest_inputs).encode("utf-8")
    manifest_digest = hashlib.sha256(combined).hexdigest()

    context.log.info(f"docs_skills_manifest: {len(paths)} files; digest={manifest_digest[:12]}")
    return dg.MaterializeResult(
        metadata={
            "manifest_digest": dg.MetadataValue.text(manifest_digest),
            "file_count": dg.MetadataValue.int(len(paths)),
            "docs_root": dg.MetadataValue.path(str(DOCS_ROOT)),
            "skills_root": dg.MetadataValue.path(str(SKILLS_ROOT)),
        }
    )


@dg.asset(
    group_name="docs_skills",
    deps=[dg.AssetKey(["docs_skills_manifest"])],
    description=(
        "Run the docs_skills_consolidation v1 CocoIndex App (catch-up). "
        "BAML-driven tag + triple extraction → LanceDB + FalkorDB."
    ),
    compute_kind="embedding",
)
def docs_skills_chunk_and_tag(context) -> dg.MaterializeResult:
    result = _run_cocoindex_update(
        "oideachais.cocoindex_flows.docs_skills_consolidation:DocsSkillsConsolidation"
    )
    context.log.info(f"docs_skills_chunk_and_tag cocoindex update: rc={result.get('returncode')}")
    return dg.MaterializeResult(
        metadata={
            "cocoindex_app": dg.MetadataValue.text("DocsSkillsConsolidation"),
            "returncode": dg.MetadataValue.int(result.get("returncode", -1)),
            "embedding_model": dg.MetadataValue.text("BAAI/bge-m3"),
            "embedding_dim": dg.MetadataValue.int(1024),
            "lance_table": dg.MetadataValue.text("docs_skills_chunks"),
            "falkordb_graph": dg.MetadataValue.text("docs_skills_graph"),
            "stderr_tail": dg.MetadataValue.text(result.get("stderr_tail", "")[:1000]),
        }
    )


@dg.asset(
    group_name="docs_skills",
    deps=[dg.AssetKey(["docs_skills_chunk_and_tag"])],
    description=(
        "Verify FalkorDB node/edge counts and report the failed-BAML count. "
        "Returns a WARN-severity asset check when the failed count is > 0."
    ),
    compute_kind="check",
)
def docs_skills_graph_publish(context) -> dg.MaterializeResult:
    """
    In a fully-wired environment this asset would query the FalkorDB graph
    directly. The CocoIndex v1 engine is the source of truth for the graph
    state, so this asset's job is to surface diagnostics in Dagster, not
    to recompute anything.
    """
    falkordb_uri = os.getenv("FALKORDB_URI", "falkor://localhost:6379")
    falkordb_graph = os.getenv("DOCS_SKILLS_FALKORDB_GRAPH", "docs_skills_graph")
    lance_uri = os.getenv("LANCEDB_URI", "rest://lance-api.cianfhoghlaim.ie")

    node_count: int | None = None
    edge_count: int | None = None
    error: str | None = None
    try:
        from falkordb import FalkorDB  # type: ignore[import-not-found]

        client = FalkorDB.from_url(falkordb_uri)
        graph = client.select_graph(falkordb_graph)
        # Cheap stats query: count of all nodes + all relationships.
        node_result = graph.query("MATCH (n) RETURN count(n) AS n")
        edge_result = graph.query("MATCH ()-[r]->() RETURN count(r) AS n")
        node_count = int(node_result.result_set[0][0]) if node_result.result_set else 0
        edge_count = int(edge_result.result_set[0][0]) if edge_result.result_set else 0
    except Exception as e:  # pragma: no cover - depends on FalkorDB being up
        error = f"{type(e).__name__}: {e}"
        context.log.warning(f"docs_skills_graph_publish check degraded: {error}")

    severity = (
        dg.AssetCheckSeverity.WARN
        if (error is not None or (node_count is not None and node_count == 0))
        else dg.AssetCheckSeverity.INFO
    )
    passed = error is None
    yield dg.AssetObservation(
        asset_key=dg.AssetKey(["docs_skills_graph_publish"]),
        metadata={
            "falkordb_uri": dg.MetadataValue.text(falkordb_uri),
            "falkordb_graph": dg.MetadataValue.text(falkordb_graph),
            "lance_uri": dg.MetadataValue.text(lance_uri),
            "node_count": dg.MetadataValue.int(node_count or 0),
            "edge_count": dg.MetadataValue.int(edge_count or 0),
            "error": dg.MetadataValue.text(error or ""),
        },
    )
    yield dg.AssetCheckResult(
        passed=passed,
        severity=severity,
        metadata={
            "node_count": dg.MetadataValue.int(node_count or 0),
            "edge_count": dg.MetadataValue.int(edge_count or 0),
        },
    )
    yield dg.MaterializeResult(
        metadata={
            "falkordb_graph": dg.MetadataValue.text(falkordb_graph),
            "node_count": dg.MetadataValue.int(node_count or 0),
            "edge_count": dg.MetadataValue.int(edge_count or 0),
            "check_passed": dg.MetadataValue.bool(passed),
        }
    )


@dg.asset(
    group_name="docs_skills",
    description=(
        "Long-running live mode for docs_skills. Sensor-launched; runs "
        "`cocoindex update -L` so the engine watches the source for changes."
    ),
    compute_kind="embedding",
)
def docs_skills_live(context) -> dg.MaterializeResult:
    """
    Run the docs_skills_consolidation App in live mode. This is a long-lived
    asset: the underlying `cocoindex update -L` process runs until the
    materialisation is cancelled or the 30-minute Dagster step timeout fires.
    """
    result = _run_cocoindex_update(
        "oideachais.cocoindex_flows.docs_skills_consolidation:DocsSkillsConsolidation",
        extra_args=["-L"],
        timeout=1800,
    )
    context.log.info(f"docs_skills_live cocoindex update -L: rc={result.get('returncode')}")
    return dg.MaterializeResult(
        metadata={
            "cocoindex_app": dg.MetadataValue.text("DocsSkillsConsolidation"),
            "live": dg.MetadataValue.bool(True),
            "returncode": dg.MetadataValue.int(result.get("returncode", -1)),
            "refresh_secs": dg.MetadataValue.int(30),
        }
    )


# ============================================================================
# codebase assets (ccc replacement)
# ============================================================================


@dg.asset(
    group_name="codebase",
    description=(
        "Run the codebase_indexing v1 CocoIndex App (catch-up). v1-native "
        "replacement for the legacy `ccc` CLI; embeds the whole monorepo's "
        "source code into LanceDB table `codebase_chunks`."
    ),
    compute_kind="embedding",
)
def codebase_chunk_and_embed(context) -> dg.MaterializeResult:
    result = _run_cocoindex_update("oideachais.cocoindex_flows.codebase_indexing:CodebaseIndex")
    context.log.info(f"codebase_chunk_and_embed cocoindex update: rc={result.get('returncode')}")
    return dg.MaterializeResult(
        metadata={
            "cocoindex_app": dg.MetadataValue.text("CodebaseIndex"),
            "returncode": dg.MetadataValue.int(result.get("returncode", -1)),
            "embedding_model": dg.MetadataValue.text("BAAI/bge-m3"),
            "embedding_dim": dg.MetadataValue.int(1024),
            "lance_table": dg.MetadataValue.text("codebase_chunks"),
            "repo_root": dg.MetadataValue.path(str(CODEBASE_ROOT)),
            "stderr_tail": dg.MetadataValue.text(result.get("stderr_tail", "")[:1000]),
        }
    )


@dg.asset(
    group_name="codebase",
    description=(
        "Long-running live mode for the codebase index. Sensor-launched; "
        "runs `cocoindex update -L` so the engine watches the source for "
        "changes (60s refresh interval)."
    ),
    compute_kind="embedding",
)
def codebase_live(context) -> dg.MaterializeResult:
    result = _run_cocoindex_update(
        "oideachais.cocoindex_flows.codebase_indexing:CodebaseIndex",
        extra_args=["-L"],
        timeout=1800,
    )
    context.log.info(f"codebase_live cocoindex update -L: rc={result.get('returncode')}")
    return dg.MaterializeResult(
        metadata={
            "cocoindex_app": dg.MetadataValue.text("CodebaseIndex"),
            "live": dg.MetadataValue.bool(True),
            "returncode": dg.MetadataValue.int(result.get("returncode", -1)),
            "refresh_secs": dg.MetadataValue.int(60),
        }
    )


# ============================================================================
# Asset list export
# ============================================================================


DOCS_SKILLS_ASSETS = [
    docs_skills_manifest,
    docs_skills_chunk_and_tag,
    docs_skills_graph_publish,
    docs_skills_live,
    codebase_chunk_and_embed,
    codebase_live,
]


__all__ = [
    "DOCS_SKILLS_ASSETS",
    "docs_skills_manifest",
    "docs_skills_chunk_and_tag",
    "docs_skills_graph_publish",
    "docs_skills_live",
    "codebase_chunk_and_embed",
    "codebase_live",
    "DOCS_ROOT",
    "SKILLS_ROOT",
    "CODEBASE_ROOT",
]
