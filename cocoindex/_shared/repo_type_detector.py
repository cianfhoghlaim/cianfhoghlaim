"""
repo_type_detector — v1 CocoIndex primitive (Phase 0 of
`2026-07-14-multimodal-code-and-media-intel-v1`).

Ported from the archived `códeolas`
(`cocoindex/_shared/repo_type_detector.py:RepoTypeDetector` (was `stedding/dev/cianfhoghlaim copy/sruth/códeolas/generators/reposwarm/detector.py` pre-v7)).

The archived detector used 6 marker sets (BACKEND / FRONTEND / LIBRARY /
DATA_PIPELINE / INFRASTRUCTURE / MONOREPO) and a weighted-vote scoring
heuristic. The v1 primitive exposes the same heuristic as a
`@coco.fn(memo=True) async def detect_repo_type(repo_path) -> RepoType`
function, with the same weights (MONOREPO / DATA_PIPELINE / INFRASTRUCTURE
score 2; the others score 1) and the same `GENERIC` fallback when no
marker matches.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import structlog

from .._shared._lifespan import COCOINDEX_AVAILABLE

# CocoIndex is optional — degrade gracefully if not installed.
try:
    import cocoindex as coco  # type: ignore[import-not-found]

    COCOINDEX_AVAILABLE_LOCAL = COCOINDEX_AVAILABLE
except ImportError:  # pragma: no cover
    coco = None  # type: ignore[assignment]
    COCOINDEX_AVAILABLE_LOCAL = False

logger = structlog.get_logger(__name__)


# not-a-flow: this primitive exposes `@coco.fn(memo=True)` + `ContextKey`
# but never writes to a LanceDB table — it returns a string enum value
# that the `repo_arch_docs` App consumes.
# See `openspec/changes/2026-07-14-multimodal-code-and-media-intel-v1/proposal.md`
# "Phase 0 — Port the archived codeolas primitives".


# ---------------------------------------------------------------------------
# RepoType enum (5 entries — matches the proposal.md table)
# ---------------------------------------------------------------------------


class RepoType(str, Enum):
    """Canonical repo-type taxonomy for the `repo_arch_docs` App."""

    FRONTEND = "frontend"
    BACKEND = "backend"
    LIBRARY = "library"
    DATA_PIPELINE = "data_pipeline"
    INFRASTRUCTURE = "infrastructure"
    MONOREPO = "monorepo"
    GENERIC = "generic"

    @classmethod
    def default(cls) -> RepoType:
        """Default when no markers match. Maps to GENERIC."""
        return cls.GENERIC


# ---------------------------------------------------------------------------
# Marker sets (ported from the archived detector)
# ---------------------------------------------------------------------------


BACKEND_MARKERS = frozenset(
    {
        "manage.py",  # Django
        "wsgi.py",
        "asgi.py",
        "app.py",  # Flask
        "main.py",
        "server.py",
        "api/",
        "routes/",
        "controllers/",
        "services/",
        "Gemfile",  # Rails
        "config.ru",
        "go.mod",  # Go
        "cmd/",
        "internal/",
        "pom.xml",  # Java
        "build.gradle",
        "src/main/java",
    }
)

FRONTEND_MARKERS = frozenset(
    {
        "package.json",  # Could be either, but with these it's frontend
        "src/App.tsx",
        "src/App.jsx",
        "src/App.vue",
        "src/main.tsx",
        "src/main.ts",
        "src/index.tsx",
        "next.config.js",
        "next.config.mjs",
        "nuxt.config.ts",
        "vite.config.ts",
        "vite.config.js",
        "angular.json",
        "svelte.config.js",
        "components/",
        "pages/",
        "public/",
        "static/",
    }
)

LIBRARY_MARKERS = frozenset(
    {
        "setup.py",
        "pyproject.toml",
        "setup.cfg",
        "Cargo.toml",
        "lib/",
        "src/lib.rs",
        "index.d.ts",
        ".npmrc",
    }
)

DATA_PIPELINE_MARKERS = frozenset(
    {
        "dbt_project.yml",
        "dagster.yaml",
        "airflow/",
        "dags/",
        "pipelines/",
        "flows/",
        "etl/",
        "data/",
        "notebooks/",
        "cocoindex/",
        "dlt_sources/",
    }
)

INFRASTRUCTURE_MARKERS = frozenset(
    {
        "terraform/",
        "pulumi/",
        "ansible/",
        "kubernetes/",
        "k8s/",
        "helm/",
        "docker-compose.yaml",
        "docker-compose.yml",
        "Dockerfile",
        ".github/workflows/",
        "cloudbuild.yaml",
        "azure-pipelines.yml",
    }
)

MONOREPO_MARKERS = frozenset(
    {
        "pnpm-workspace.yaml",
        "lerna.json",
        "nx.json",
        "turbo.json",
        "rush.json",
        "packages/",
        "apps/",
        "modules/",
        "services/",
        "libs/",
    }
)

# Common ignore directories — same set the archived detector used.
_IGNORE_DIRS = frozenset({".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"})


# ---------------------------------------------------------------------------
# Dataclass return
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RepoTypeResult:
    """Result of `detect_repo_type()`."""

    repo_type: RepoType
    scores: dict[RepoType, int]
    total_files_scanned: int


# ---------------------------------------------------------------------------
# The v1 primitive
# ---------------------------------------------------------------------------


def _matches(rel_str: str, name: str, markers: frozenset[str]) -> bool:
    """Check whether `rel_str` or `name` matches any of the marker strings.

    For markers that end with `/` (directory markers), we check the
    substring. For file markers, we check exact equality on `name`.
    """
    for marker in markers:
        if marker.endswith("/"):
            if marker in rel_str:
                return True
        else:
            if name == marker:
                return True
    return False


async def detect_repo_type(repo_path: str | Path) -> RepoTypeResult:
    """Score the repo by structural markers and return the highest-scoring type.

    Ties are broken by the canonical order
    `MONOREPO > DATA_PIPELINE > INFRASTRUCTURE > BACKEND > FRONTEND > LIBRARY`.

    Args:
        repo_path: absolute or relative path to the repo root.

    Returns:
        `RepoTypeResult(repo_type, scores, total_files_scanned)`.
    """
    path = Path(repo_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"repo_path does not exist: {path}")

    scores: dict[RepoType, int] = dict.fromkeys(RepoType, 0)
    total = 0

    for candidate in path.rglob("*"):
        if not candidate.is_file():
            continue
        rel = candidate.relative_to(path)
        rel_str = str(rel).replace("\\", "/")
        if any(part in _IGNORE_DIRS for part in rel.parts):
            continue
        total += 1

        name = candidate.name

        # Weighted scoring per the archived heuristic:
        #   MONOREPO / DATA_PIPELINE / INFRASTRUCTURE → 2
        #   BACKEND / FRONTEND / LIBRARY → 1
        if _matches(rel_str, name, MONOREPO_MARKERS):
            scores[RepoType.MONOREPO] += 2
        if _matches(rel_str, name, DATA_PIPELINE_MARKERS):
            scores[RepoType.DATA_PIPELINE] += 2
        if _matches(rel_str, name, INFRASTRUCTURE_MARKERS):
            scores[RepoType.INFRASTRUCTURE] += 2
        if _matches(rel_str, name, BACKEND_MARKERS):
            scores[RepoType.BACKEND] += 1
        if _matches(rel_str, name, FRONTEND_MARKERS):
            scores[RepoType.FRONTEND] += 1
        if _matches(rel_str, name, LIBRARY_MARKERS):
            scores[RepoType.LIBRARY] += 1

    # Determine winner.
    max_score = max(scores.values())
    if max_score == 0:
        # No markers matched — fall back to the default.
        logger.info(
            "repo_type_detector.no_markers",
            repo_path=str(path),
            total_files=total,
        )
        return RepoTypeResult(
            repo_type=RepoType.default(),
            scores=scores,
            total_files_scanned=total,
        )

    # Tie-break by canonical order: MONOREPO > DATA_PIPELINE >
    # INFRASTRUCTURE > BACKEND > FRONTEND > LIBRARY.
    canonical_order = (
        RepoType.MONOREPO,
        RepoType.DATA_PIPELINE,
        RepoType.INFRASTRUCTURE,
        RepoType.BACKEND,
        RepoType.FRONTEND,
        RepoType.LIBRARY,
        RepoType.GENERIC,
    )
    for repo_type in canonical_order:
        if scores[repo_type] == max_score:
            logger.info(
                "repo_type_detector.detected",
                repo_path=str(path),
                repo_type=repo_type.value,
                score=max_score,
                total_files=total,
            )
            return RepoTypeResult(
                repo_type=repo_type,
                scores=scores,
                total_files_scanned=total,
            )

    # Unreachable — but keep the type-checker happy.
    return RepoTypeResult(
        repo_type=RepoType.default(),
        scores=scores,
        total_files_scanned=total,
    )


# ---------------------------------------------------------------------------
# v1 App stub (R2 conformance)
# ---------------------------------------------------------------------------


if COCOINDEX_AVAILABLE_LOCAL and coco is not None:
    repo_type_detector_app = coco.App(  # type: ignore[attr-defined]
        coco.AppConfig(name="RepoTypeDetector")
    )
else:  # pragma: no cover
    repo_type_detector_app = None


# Canonical cianfhoghlaim-monorepo marker (the env var override lets us
# skip the filesystem walk in CI when the answer is known). Read per-call
# so tests can monkeypatch `os.environ`.


async def detect_repo_type_with_override(
    repo_path: str | Path,
) -> RepoTypeResult:
    """Same as `detect_repo_type` but honours the `CIANFHOGHLAIM_REPO_TYPE_OVERRIDE` env var.

    Useful for the cianfhoghlaim monorepo itself: we know it's a MONOREPO.
    The env var is read per-call so tests can toggle it via `os.environ`.
    """
    override = os.getenv("CIANFHOGHLAIM_REPO_TYPE_OVERRIDE")
    if override:
        try:
            forced = RepoType(override)
        except ValueError:
            return await detect_repo_type(repo_path)
        scores = {t: (1 if t == forced else 0) for t in RepoType}
        return RepoTypeResult(
            repo_type=forced,
            scores=scores,
            total_files_scanned=0,
        )
    return await detect_repo_type(repo_path)


__all__ = [
    "BACKEND_MARKERS",
    "DATA_PIPELINE_MARKERS",
    "FRONTEND_MARKERS",
    "INFRASTRUCTURE_MARKERS",
    "LIBRARY_MARKERS",
    "MONOREPO_MARKERS",
    "RepoType",
    "RepoTypeResult",
    "detect_repo_type",
    "detect_repo_type_with_override",
    "repo_type_detector_app",
]
