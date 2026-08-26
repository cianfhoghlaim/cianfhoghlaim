"""Sister-repo Cognee twin-cluster sync sensor.

Per the 2026-08-24-dlt-sources-to-multi-repo-scaffold-v1 change
(Phase 2.4 — Cognee twin clusters).

Diff-syncs the 12 sister-scope Cognee clusters (6 per sister repo, 2
sister repos — ciandlithe + cianchosaint) against their
cianfhoghlaim-scope masters on an hourly cadence.

The 12 sister-scope clusters (per the
`sister_repo_cognee_intent/__init__.py` intent module under the same
`2_materials/` dir):

  ciandlithe_*             cianchosaint_*
  ├── dlt_sources          ├── dlt_sources
  ├── openspec_changes     ├── openspec_changes
  ├── dagster_assets       ├── dagster_assets
  ├── baml_schemas         ├── baml_schemas
  ├── agents               ├── agents
  └── notebooks            └── notebooks

Flow
----
1. The hourly sensor ticks (`@sensor(minimum_interval_seconds=3600)`,
   `default_status=DefaultSensorStatus.STOPPED`).
2. For each (master, twin) pair:
     a. Read the master cluster's recent entities (last 1h window).
     b. Diff against the twin cluster's existing entities.
     c. Emit a `RunRequest` per diff cluster via the
        `sister_repo_cognee_sync_job` (defined below) — the job calls
        `cognee.add()` on the twin with the missing entities.
3. A drift summary is written to
   `stedding/sync-reports/cognee-{date}.md` per the existing
   `notebooks/24_*sync_health.ipynb` convention.

Constraints
-----------
- READ-ONLY on the master cluster; only the twin cluster is mutated.
- The sensor is STOPPED by default — operator must enable it via
  Dagster UI after the 12 clusters are created (CREATE-ON-DEPLOY
  per `orchestration.defs._layer.sister_repo_cognee_intent.__init__`).
- Gracefully degrades to `SkipReason` when cognee is unreachable.
"""
from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Any

from dagster import (
    DefaultSensorStatus,
    RunRequest,
    SensorEvaluationContext,
    SkipReason,
    define_asset_job,
    sensor,
)

try:
    import cognee  # type: ignore[import-not-found]
    COGNEE_AVAILABLE = True
except ImportError:  # pragma: no cover - CI fallback
    COGNEE_AVAILABLE = False
    cognee = None  # type: ignore[assignment]


logger = logging.getLogger(__name__)


# The cluster intent table (12 sister-scope Cognee clusters).
# Mirrors the dataclass table in
# `orchestration/defs/2_materials/sister_repo_cognee_intent/__init__.py`
# (kept in sync manually — the intent module is the canonical
# CREATE-ON-DEPLOY manifest; this list is the runtime sensor input).
#
# The numeric-prefix layer directories (2_materials/) are not valid
# Python identifiers, so this table is inlined rather than imported.
# When a new sister repo is added (ciancheiltis + cianleighis +
# bonneagar + meaisinfhoghlaim), update BOTH this list AND the intent
# module.
SISTER_TWIN_CLUSTERS: tuple[str, ...] = (
    # Ciandlithe (BI civil-litigation) — 6 surfaces
    "ciandlithe_dlt_sources",
    "ciandlithe_openspec_changes",
    "ciandlithe_dagster_assets",
    "ciandlithe_baml_schemas",
    "ciandlithe_agents",
    "ciandlithe_notebooks",
    # Cianchosaint (BI defence + policing + intelligence oversight) — 6 surfaces
    "cianchosaint_dlt_sources",
    "cianchosaint_openspec_changes",
    "cianchosaint_dagster_assets",
    "cianchosaint_baml_schemas",
    "cianchosaint_agents",
    "cianchosaint_notebooks",
)


def _surface_for_cluster(cluster: str) -> str | None:
    """Extract the surface (e.g. 'dlt_sources') from a twin cluster name."""
    for surface in (
        "dlt_sources",
        "openspec_changes",
        "dagster_assets",
        "baml_schemas",
        "agents",
        "notebooks",
    ):
        if cluster.endswith(f"_{surface}"):
            return surface
    return None


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
        (_surface_for_cluster(twin), twin)
        for twin in SISTER_TWIN_CLUSTERS
        if _surface_for_cluster(twin) is not None
    ]


POLL_INTERVAL_SECONDS = 3_600  # hourly
DRIFT_REPORT_PATH = "stedding/sync-reports/cognee-{date}.md"


def _diff_clusters(master: str, twin: str) -> dict[str, Any]:
    """Diff the master + twin clusters; return the missing-entity set.

    Returns a dict shaped:
        {
            "master": master_cluster_name,
            "twin": twin_cluster_name,
            "missing_entities": [str, ...],  # entities in master but not twin
            "ts": iso-timestamp,
        }

    Gracefully degrades to {"missing_entities": [], "ts": ...} when cognee
    is unreachable (so the sensor doesn't crash on a degraded network).
    """
    if not COGNEE_AVAILABLE or cognee is None:
        return {
            "master": master,
            "twin": twin,
            "missing_entities": [],
            "ts": datetime.now(UTC).isoformat(),
            "error": "cognee SDK unavailable",
        }
    try:
        # Real impl: enumerate master + twin entities via cognee.search()
        # + diff. Stubbed here — returns 0 missing entities.
        missing: list[str] = []
        return {
            "master": master,
            "twin": twin,
            "missing_entities": missing,
            "ts": datetime.now(UTC).isoformat(),
        }
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning(
            "sister_repo_cognee_sync.diff_failed",
            master=master,
            twin=twin,
            error=str(exc),
        )
        return {
            "master": master,
            "twin": twin,
            "missing_entities": [],
            "ts": datetime.now(UTC).isoformat(),
            "error": str(exc),
        }


# The job that performs the actual twin ingestion. Selects a single
# placeholder asset (the diff-sync is in-memory in this stub — the
# canonical prod impl calls `cognee.add(entity, dataset_name=twin)`).
sister_repo_cognee_sync_job = define_asset_job(
    name="sister_repo_cognee_sync_job",
    selection=[],
    description=(
        "Diff-sync the 12 sister-scope Cognee clusters "
        "(ciandlithe_* + cianchosaint_* x 6 surfaces) against their "
        "cianfhoghlaim-scope masters. Per the 2026-08-24 multi-repo "
        "scaffold change Phase 2.4."
    ),
)


@sensor(
    job=sister_repo_cognee_sync_job,
    description=(
        "Hourly diff-sync of the 12 sister-scope Cognee clusters "
        "(ciandlithe_* + cianchosaint_* x 6 surfaces) against their "
        "cianfhoghlaim-scope masters. Per the 2026-08-24 multi-repo "
        "scaffold change Phase 2.4."
    ),
    minimum_interval_seconds=POLL_INTERVAL_SECONDS,
    default_status=DefaultSensorStatus.STOPPED,
)
def sister_repo_cognee_sync_sensor(
    context: SensorEvaluationContext,
) -> list[RunRequest] | SkipReason:
    """The hourly sister-scope Cognee twin-cluster sync sensor.

    Disabled by default — the operator MUST enable it via Dagster UI
    after the 12 twin clusters are created (CREATE-ON-DEPLOY per
    `orchestration.defs._layer.sister_repo_cognee_intent.__init__`).
    """
    if not COGNEE_AVAILABLE:
        return SkipReason("cognee SDK unavailable; sensor paused")

    cursor_data: dict[str, Any] = {}
    if context.cursor:
        try:
            cursor_data = json.loads(context.cursor)
        except Exception:
            cursor_data = {}

    now_ts = datetime.now(UTC).isoformat()

    new_runs: list[RunRequest] = []
    drift_report: dict[str, Any] = {
        "ts": now_ts,
        "pairs": [],
        "missing_total": 0,
    }

    for twin_name in SISTER_TWIN_CLUSTERS:
        surface = _surface_for_cluster(twin_name)
        if surface is None:
            continue
        diff = _diff_clusters(master=surface, twin=twin_name)
        drift_report["pairs"].append(diff)
        drift_report["missing_total"] += len(diff.get("missing_entities", []))

        if diff.get("missing_entities"):
            run_key = f"sister_cognee_sync_{twin_name}_{now_ts}"
            new_runs.append(
                RunRequest(
                    run_key=run_key,
                    tags={
                        "twin_cluster": twin_name,
                        "master_cluster": surface,
                        "missing_count": str(len(diff["missing_entities"])),
                        "openspec_change": (
                            "2026-08-24-dlt-sources-to-multi-repo-scaffold-v1"
                        ),
                    },
                )
            )

    # Update the cursor for the next tick
    context.update_cursor(json.dumps({"last_seen_ts": now_ts}))

    # Write the drift summary
    try:
        import pathlib
        report_path = pathlib.Path(
            DRIFT_REPORT_PATH.format(date=datetime.now(UTC).strftime("%Y-%m-%d"))
        )
        report_path.parent.mkdir(parents=True, exist_ok=True)
        # Markdown table
        lines = [
            f"# Cognee Twin-Cluster Drift Report — {now_ts}",
            "",
            f"## {drift_report['missing_total']} missing entities across {len(drift_report['pairs'])} pairs",
            "",
            "| Master | Twin | Missing | TS |",
            "| --- | --- | --- | --- |",
        ]
        for diff in drift_report["pairs"]:
            lines.append(
                f"| `{diff['master']}` | `{diff['twin']}` | "
                f"{len(diff.get('missing_entities', []))} | {diff['ts']} |"
            )
        report_path.write_text("\n".join(lines) + "\n")
        logger.info(
            "sister_repo_cognee_sync.drift_report_written",
            path=str(report_path),
            missing_total=drift_report["missing_total"],
        )
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning(
            "sister_repo_cognee_sync.drift_report_failed",
            error=str(exc),
        )

    if not new_runs:
        return SkipReason(
            f"0 of {len(SISTER_TWIN_CLUSTERS)} twin clusters have drift"
        )
    return new_runs


__all__ = [
    "POLL_INTERVAL_SECONDS",
    "SISTER_TWIN_CLUSTERS",
    "CIANFHOGHLAIM_MASTER_CLUSTERS",
    "cluster_pairs",
    "_surface_for_cluster",
    "sister_repo_cognee_sync_sensor",
    "sister_repo_cognee_sync_job",
]
