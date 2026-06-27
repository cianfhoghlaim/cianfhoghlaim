#!/usr/bin/env python3
"""
cognee-ingest-docs.py — 1-call cognify helper for the 7 typed clusters.

Cluster       graph_model_file
-----------   -----------------------------------------------
docs-data-eng infrastructure/scripts/cognee-graph-models/data_platform_graph.py
docs-bonneagar  infrastructure/scripts/cognee-graph-models/infrastructure_graph.py
docs-agents     infrastructure/scripts/cognee-graph-models/agents_graph.py
docs-ml         infrastructure/scripts/cognee-graph-models/ml_graph.py
docs-teanga     infrastructure/scripts/cognee-graph-models/celtic_language_graph.py
docs-web        infrastructure/scripts/cognee-graph-models/web_graph.py
docs-tuatha     infrastructure/scripts/cognee-graph-models/tuatha_graph.py

Usage
-----
    # Cognify all 7 clusters (run-once-on-fresh-stack)
    uv run python infrastructure/scripts/cognee-ingest-docs.py --all

    # Cognify a single cluster
    uv run python infrastructure/scripts/cognee-ingest-docs.py --cluster docs-data-eng

    # Dry-run (print the plan, do not call the API)
    uv run python infrastructure/scripts/cognee-ingest-docs.py --all --dry-run

    # Cognify in the background (for large corpora)
    uv run python infrastructure/scripts/cognee-ingest-docs.py --all --background

Exit codes
----------
    0   success
    1   cognee stack is not running
    2   invalid cluster name
    3   graph model file not found
    4   cognify API error
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Final

# The 7 typed clusters (canonical shape)
ALL_CLUSTERS: Final[tuple[str, ...]] = (
    "docs-data-eng",
    "docs-bonneagar",
    "docs-agents",
    "docs-ml",
    "docs-teanga",
    "docs-web",
    "docs-tuatha",
)

# Map cluster name → graph_model_file path (relative to repo root)
CLUSTER_TO_GRAPH_MODEL: Final[dict[str, Path]] = {
    "docs-data-eng": Path("infrastructure/scripts/cognee-graph-models/data_platform_graph.py"),
    "docs-bonneagar": Path("infrastructure/scripts/cognee-graph-models/infrastructure_graph.py"),
    "docs-agents": Path("infrastructure/scripts/cognee-graph-models/agents_graph.py"),
    "docs-ml": Path("infrastructure/scripts/cognee-graph-models/ml_graph.py"),
    "docs-teanga": Path("infrastructure/scripts/cognee-graph-models/celtic_language_graph.py"),
    "docs-web": Path("infrastructure/scripts/cognee-graph-models/web_graph.py"),
    "docs-tuatha": Path("infrastructure/scripts/cognee-graph-models/tuatha_graph.py"),
}

# Default Cognee API URL (the in-house cognee stack; Pangolin-routed)
COGNEE_API_URL: Final[str] = "http://localhost:8100"


def validate_clusters(clusters: list[str]) -> int:
    """Validate that all cluster names are canonical. Returns 0 on success, 2 on error."""
    invalid = [c for c in clusters if c not in ALL_CLUSTERS]
    if invalid:
        print(f"ERROR: invalid cluster(s): {invalid}", file=sys.stderr)
        print(f"Valid clusters: {ALL_CLUSTERS}", file=sys.stderr)
        return 2
    return 0


def verify_graph_model_files(repo_root: Path, clusters: list[str]) -> int:
    """Verify all graph model files exist. Returns 0 on success, 3 on error."""
    for cluster in clusters:
        path = repo_root / CLUSTER_TO_GRAPH_MODEL[cluster]
        if not path.exists():
            print(f"ERROR: graph model file missing for {cluster}: {path}", file=sys.stderr)
            return 3
    return 0


def plan_cognify(clusters: list[str], repo_root: Path) -> None:
    """Print the cognify plan (dry-run)."""
    print(f"Plan: cognify {len(clusters)} cluster(s) at {COGNEE_API_URL}")
    for cluster in clusters:
        graph_path = repo_root / CLUSTER_TO_GRAPH_MODEL[cluster]
        print(f"  - {cluster:18s}  graph_model={graph_path}")


def cognify_clusters(clusters: list[str], background: bool) -> int:
    """Call the Cognee cognify API for each cluster. Returns exit code."""
    try:
        import httpx  # type: ignore[import-untyped]
    except ImportError:
        print(
            "ERROR: httpx is required for live cognify. Install with: "
            "`uv add httpx` or use --dry-run for a plan.",
            file=sys.stderr,
        )
        return 4

    for cluster in clusters:
        payload: dict[str, object] = {"datasets": [cluster]}
        if background:
            payload["runInBackground"] = True

        try:
            response = httpx.post(
                f"{COGNEE_API_URL}/api/v1/cognify",
                json=payload,
                timeout=30.0,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            print(f"ERROR: cognify({cluster}) failed: {exc}", file=sys.stderr)
            return 4

        job_id = response.json().get("job_id", "n/a")
        print(f"  {cluster:18s}  job_id={job_id}  background={background}")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Cognify the 7 typed Cognee clusters in one call."
    )
    cluster_group = parser.add_mutually_exclusive_group(required=True)
    cluster_group.add_argument(
        "--all",
        action="store_true",
        help="Cognify all 7 clusters",
    )
    cluster_group.add_argument(
        "--cluster",
        type=str,
        help="Cognify a single cluster (one of: " + ", ".join(ALL_CLUSTERS) + ")",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the plan, do not call the API",
    )
    parser.add_argument(
        "--background",
        action="store_true",
        help="Run cognify in the background (for large corpora)",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Path to the cianfhoghlaim repo root (default: cwd)",
    )

    args = parser.parse_args()
    clusters: list[str] = list(ALL_CLUSTERS) if args.all else [args.cluster]

    # Validate
    if (code := validate_clusters(clusters)) != 0:
        return code
    if (code := verify_graph_model_files(args.repo_root, clusters)) != 0:
        return code

    # Plan
    plan_cognify(clusters, args.repo_root)
    if args.dry_run:
        return 0

    # Execute
    return cognify_clusters(clusters, args.background)


if __name__ == "__main__":
    sys.exit(main())
