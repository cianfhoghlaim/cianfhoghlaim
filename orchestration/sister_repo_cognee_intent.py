"""Cognee twin cluster intent files for the 12 sister-scope clusters.

Per the 2026-08-24-dlt-sources-to-multi-repo-scaffold-v1 change
(Phase 2.4 — Cognee twin clusters).

This module is the canonical CREATE-ON-DEPLOY manifest. It is NOT
executed automatically; it is the canonical record of which clusters
must exist in the dev-baile Cognee vault for the sister-scope knowledge
graph cascade to work.

The 12 clusters (6 per sister repo, 2 sister repos):

  ciandlithe_*              cianchosaint_*
  ├── dlt_sources           ├── dlt_sources
  ├── openspec_changes      ├── openspec_changes
  ├── dagster_assets        ├── dagster_assets
  ├── baml_schemas          ├── baml_schemas
  ├── agents                ├── agents
  └── notebooks             └── notebooks

The naming convention follows the 2026-08-15-knowledge-sync-loop-v1
spec: `<repo>_<surface>` where `<repo>` is the lowercase sister repo
slug and `<surface>` matches the existing 6 cianfhoghlaim-scope master
clusters (`dlt_sources` + `openspec_changes` + `dagster_assets` +
`baml_schemas` + `agents` + `notebooks`).

CREATE-ON-DEPLOY COMMANDS
-------------------------
Run from the cianfhoghlaim root with the cognee MCP server active:

    for cluster in \\
        ciandlithe_dlt_sources ciandlithe_openspec_changes \\
        ciandlithe_dagster_assets ciandlithe_baml_schemas \\
        ciandlithe_agents ciandlithe_notebooks \\
        cianchosaint_dlt_sources cianchosaint_openspec_changes \\
        cianchosaint_dagster_assets cianchosaint_baml_schemas \\
        cianchosaint_agents cianchosaint_notebooks; do
        uv run --with cognee python -c \\
          "import asyncio, cognee; asyncio.run(cognee.create_dataset('$cluster'))"
    done

Or via the cognee MCP server (`cognee_create_dataset_json` tool):

    {"name": "ciandlithe_dlt_sources"}
    {"name": "ciandlithe_openspec_changes"}
    ...

(12 calls total — one per cluster. Idempotent.)

PER-TWIN DIFF-SYNC
------------------
The runtime sensor at
`orchestration.defs.2_materials.sister_repo_cognee_sync` reads
SISTER_TWIN_CLUSTERS at module load and emits a
`sister_repo_cognee_sync_job` RunRequest per (master, twin) pair that
has drift. Keep this table + the sensor's inlined list in sync.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TwinCluster:
    """A Cognee twin cluster for a sister repo."""

    repo: str
    surface: str

    @property
    def name(self) -> str:
        return f"{self.repo}_{self.surface}"

    @property
    def description(self) -> str:
        return (
            f"Twin of the cianfhoghlaim-scope `{self.surface}` Cognee "
            f"cluster for the `{self.repo}` sister repo. Diff-synced hourly "
            f"via the `sister_repo_cognee_sync_sensor`."
        )


# The 12 sister-scope Cognee clusters (6 per sister repo, 2 sister repos).
SISTER_TWIN_CLUSTERS: tuple[TwinCluster, ...] = (
    # Ciandlithe (BI civil-litigation)
    TwinCluster(repo="ciandlithe", surface="dlt_sources"),
    TwinCluster(repo="ciandlithe", surface="openspec_changes"),
    TwinCluster(repo="ciandlithe", surface="dagster_assets"),
    TwinCluster(repo="ciandlithe", surface="baml_schemas"),
    TwinCluster(repo="ciandlithe", surface="agents"),
    TwinCluster(repo="ciandlithe", surface="notebooks"),
    # Cianchosaint (BI defence + policing + intelligence oversight)
    TwinCluster(repo="cianchosaint", surface="dlt_sources"),
    TwinCluster(repo="cianchosaint", surface="openspec_changes"),
    TwinCluster(repo="cianchosaint", surface="dagster_assets"),
    TwinCluster(repo="cianchosaint", surface="baml_schemas"),
    TwinCluster(repo="cianchosaint", surface="agents"),
    TwinCluster(repo="cianchosaint", surface="notebooks"),
)


# The 6 master clusters in cianfhoghlaim-scope that the twins mirror.
CIANFHOGHLAIM_MASTER_CLUSTERS: tuple[str, ...] = (
    "dlt_sources",
    "openspec_changes",
    "dagster_assets",
    "baml_schemas",
    "agents",
    "notebooks",
)


def cluster_pairs() -> list[tuple[str, str]]:
    """Return the (master, twin) pairs for the hourly diff-sync sensor."""
    return [
        (master, twin.name)
        for twin in SISTER_TWIN_CLUSTERS
        for master in CIANFHOGHLAIM_MASTER_CLUSTERS
        if master == twin.surface
    ]


__all__ = [
    "TwinCluster",
    "SISTER_TWIN_CLUSTERS",
    "CIANFHOGHLAIM_MASTER_CLUSTERS",
    "cluster_pairs",
]


if __name__ == "__main__":
    print(
        f"Cognee twin cluster intent: {len(SISTER_TWIN_CLUSTERS)} clusters "
        f"({len(set(t.repo for t in SISTER_TWIN_CLUSTERS))} sister repos, "
        f"{len(CIANFHOGHLAIM_MASTER_CLUSTERS)} master surfaces)"
    )
    print()
    print("CREATE-ON-DEPLOY commands:")
    for cluster in SISTER_TWIN_CLUSTERS:
        print(f"  uv run --with cognee python -c \"import cognee; cognee.create_dataset('{cluster.name}')\"")
    print()
    print("Cluster pairs (master -> twin):")
    for master, twin in cluster_pairs():
        print(f"  {master:20s} -> {twin}")
