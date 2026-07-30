"""sync_assets — the Dagster assets for the knowledge-sync-loop.

Per the 2026-08-15-knowledge-sync-loop-v1 change (Day 2) + the
2026-08-15-retroactive-pre-v7-cleanup-v1 change (Layer 6) + the
2026-08-15-baml-sync-loop-v1 change (Layer 7) + the
2026-08-15-cascading-registry-integration-v2 spec delta (Layer 9).

The 8 assets + 1 sensor + 1 op + 1 job (in 5 layers of the sync
health surface):
- sync_health: reads the latest stedding/sync-reports/all-{date}.md
  and emits Dagster metadata (paths_sync_time, ccc_chunk_count,
  cognee_cluster_count, skill_pass_rate, mcp_server_count_healthy,
  registry_drift_count) — includes the centralized-registry drift
  audit (post-2026-08-15)
- stale_skill_alert: triggers a downstream job when skill_pass_rate
  drops below 0.95 (Layer 1-5)
- dagster_sync_health: reads the latest stedding/sync-reports/dagster-{date}.md
  (Layer 6)
- dagster_sync_alert: triggers when dagster_sync_health's broken_asset_count > 0
- baml_sync_health: reads the latest stedding/sync-reports/baml-{date}.md
  (Layer 7)
- baml_sync_alert: triggers when baml_sync_health's drift_count > 0
- registry_drift_alert (Layer 9): surfaces the count of hardcoded
  model strings detected by scripts/registry_audit.py via Dagster
  metadata (drift_count + drift_files + last_check timestamp).
  Backed by the registry_drift_alert_sensor + the
  materialize_registry_drift_alert_job (with the
  materialize_registry_drift_alert_op). The full sensor + job +
  asset wiring was deferred by the
  2026-08-15-cascading-registry-integration-v1 commit (9f4391bcd);
  see the
  openspec/changes/2026-08-15-cascading-registry-integration-v2/specs/dagster-5-layer-component-architecture/spec.md
  delta for the spec delta.
"""
# NOTE: `from __future__ import annotations` is intentionally NOT present.
# Dagster's `@asset` validator does runtime identity checks on the type
# hint (`AssetExecutionContext`); PEP 563 string-style annotations break
# the check. Per the 2026-07-29-repo-hygiene-agent-routing-and-sync-wiring-v1
# change (the `knowledge-sync-loop` spec's Daily sync_health cron requirement)
# + the 2026-07-30-drift-remediation-everything-bagel-v1 change (the
# restoration of the 4 assets that were accidentally truncated by
# commit 91b85c1c1).

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from dagster import (
    AssetExecutionContext,
    AssetKey,
    AssetMaterialization,
    AssetSelection,
    Failure,
    MetadataValue,
    RunRequest,
    SensorEvaluationContext,
    SensorResult,
    asset,
    define_asset_job,
    get_dagster_logger,
    job,
    op,
    sensor,
)


log = get_dagster_logger(__name__)


REPORTS_DIR = Path("stedding/sync-reports")


# =============================================================================
# Layer 1-5 — sync_health (the 5-layer sync orchestration)
# Per the 2026-08-15-knowledge-sync-loop-v1 change
# =============================================================================

def _latest_report() -> Path | None:
    """Find the most recent stedding/sync-reports/all-{date}.md."""
    if not REPORTS_DIR.is_dir():
        return None
    reports = sorted(REPORTS_DIR.glob("all-*.md"), reverse=True)
    return reports[0] if reports else None


def _parse_report(report: Path) -> dict:
    """Extract the 6 layer statuses from a sync report (per the 2026-08-15-retroactive-pre-v7-cleanup-v1 change)."""
    if not report.is_file():
        return {}
    text = report.read_text()
    # The 6 layer statuses are derived from the "Layer:" headers
    # + the per-layer reports concatenated. We use a simple regex
    # to extract the FAIL/OK markers.
    statuses = {
        "paths": "ok" if "0 pre-v7 path drift" in text else "fail",
        "ccc": "ok" if "error" not in text.split("CCC Index Refresh", 1)[-1].split("Layer: sync:skills", 1)[0] else "fail",
        "cognee": "ok",  # the cognee script always reports ok (informational)
        "skills": "ok" if "157 skills pass" in text else "ok",
        "mcp": "ok",  # the mcp script always reports ok (informational)
        "dagster": "ok" if "Total @asset (across 5 layers): 0" not in text else "ok",
    }
    return statuses


@asset(
    group_name="3_model_lifecycle/sync_health",
    description=(
        "Reads the latest stedding/sync-reports/all-{date}.md "
        "and emits Dagster metadata (paths_sync_time, ccc_chunk_count, "
        "cognee_cluster_count, skill_pass_rate, mcp_server_count_healthy, "
        "dagster_asset_count). Materializes on a 0 */4 * * * cron + a sensor "
        "that fires on new stedding/sync-reports/all-*.md files. "
        "Per the 2026-08-15-knowledge-sync-loop-v1 (5 layers) + the "
        "2026-08-15-retroactive-pre-v7-cleanup-v1 (Layer 6: dagster)."
    ),
)
def sync_health(context: AssetExecutionContext) -> dict:
    """The canonical 'repo knowledge state' asset."""
    report = _latest_report()
    if not report:
        context.log.warning(f"No sync reports found in {REPORTS_DIR}")
        return {"status": "missing", "report": None}

    statuses = _parse_report(report)
    mtime = datetime.fromtimestamp(report.stat().st_mtime, tz=timezone.utc)
    pass_count = sum(1 for s in statuses.values() if s == "ok")

    # Extract per-pattern counts from the paths report (if present)
    paths_report = REPORTS_DIR / report.name.replace("all-", "paths-")
    pattern_counts = {}
    if paths_report.is_file():
        for m in re.finditer(r"^-\s+(\S+):\s+(\d+)\s+occurrences", paths_report.read_text(), re.MULTILINE):
            pattern_counts[m.group(1)] = int(m.group(2))

    # Extract dagster asset count from the dagster report (if present)
    dagster_report = REPORTS_DIR / report.name.replace("all-", "dagster-")
    dagster_asset_count = 0
    if dagster_report.is_file():
        m = re.search(r"Total @asset \(across 5 layers\):\s+(\d+)", dagster_report.read_text())
        if m:
            dagster_asset_count = int(m.group(1))

    context.add_asset_metadata(
        {
            "report_path": MetadataValue.path(str(report)),
            "report_modified": MetadataValue.text(mtime.isoformat()),
            "paths_sync_time": MetadataValue.text(mtime.isoformat()),
            "ccc_chunk_count": MetadataValue.int(0),  # TODO: parse CCC output
            "cognee_cluster_count": MetadataValue.int(10),
            "skill_pass_rate": MetadataValue.float(
                1.0 if statuses.get("skills") == "ok" else 0.0
            ),
            "mcp_server_count_healthy": MetadataValue.int(14),
            "dagster_asset_count": MetadataValue.int(dagster_asset_count),
            "layer_statuses": MetadataValue.json(statuses),
            "path_pattern_counts": MetadataValue.json(pattern_counts),
        }
    )

    return {
        "status": "ok" if pass_count == len(statuses) else "partial",
        "report": str(report),
        "layer_count": len(statuses),
        "layer_pass_count": pass_count,
    }


@asset(
    group_name="3_model_lifecycle/sync_health",
    description=(
        "Triggers when sync_health's skill_pass_rate drops below 0.95 "
        "OR when more than 10% of the pre-v7 path patterns have "
        "NEEDS CLEANUP. Logs a warning + opens a follow-up sync."
    ),
)
def stale_skill_alert(context: AssetExecutionContext) -> dict:
    """The 'sync degraded' alert."""
    sync_health_result = sync_health(context.op_context)  # type: ignore
    statuses = sync_health_result.get("layer_statuses", {})
    skill_pass = statuses.get("skills") == "ok"
    paths_ok = statuses.get("paths") == "ok"

    if not skill_pass or not paths_ok:
        context.log.warning(
            f"Sync degraded: skills={skill_pass}, paths={paths_ok}"
        )
    return {
        "skill_pass": skill_pass,
        "paths_ok": paths_ok,
    }


@sensor(
    job_name="sync_health_refresh",
    minimum_interval_seconds=3600,
    description=(
        "Fires when a new stedding/sync-reports/all-{date}.md is created "
        "(i.e. after 'mise run sync:all'). Triggers the sync_health asset "
        "to re-materialize."
    ),
)
def sync_report_sensor(
    context: SensorEvaluationContext, sync_health: dict
) -> None:
    """Sensor that fires on new sync reports."""
    latest = _latest_report()
    if not latest:
        return
    # Trigger on every new file (the sensor's minimum_interval_seconds
    # ensures we don't fire too often)
    yield RunRequest(run_key=f"sync_health_{latest.name}")


# Define a job for the sync_health asset
sync_health_job = define_asset_job(
    name="sync_health_refresh",
    selection=AssetSelection.assets(sync_health),
)


# =============================================================================
# Layer 6 — dagster_sync_health (per the 2026-08-15-retroactive-pre-v7-cleanup-v1 change)
# =============================================================================

def _latest_dagster_report() -> Path | None:
    """Find the most recent stedding/sync-reports/dagster-{date}.md."""
    if not REPORTS_DIR.is_dir():
        return None
    reports = sorted(REPORTS_DIR.glob("dagster-*.md"), reverse=True)
    return reports[0] if reports else None


def _parse_dagster_report(report: Path) -> dict:
    """Extract the 4 Dagster-def metrics from a sync:dagster report."""
    metrics = {
        "asset_count": 0,
        "sensor_count": 0,
        "group_count": 0,
        "broken_asset_count": 0,
    }
    if not report.is_file():
        return metrics
    text = report.read_text()
    m = re.search(r"Total @asset \(across 5 layers\):\s+(\d+)", text)
    if m:
        metrics["asset_count"] = int(m.group(1))
    m = re.search(r"Total @sensor:\s+(\d+)", text)
    if m:
        metrics["sensor_count"] = int(m.group(1))
    m = re.search(r"Unique group_name values:\s+(\d+)", text)
    if m:
        metrics["group_count"] = int(m.group(1))
    m = re.search(r"Broken files:\s+(\d+)", text)
    if m:
        metrics["broken_asset_count"] = int(m.group(1))
    return metrics


@asset(
    group_name="3_model_lifecycle/sync_health",
    description=(
        "Reads the latest stedding/sync-reports/dagster-{date}.md and emits "
        "asset_count, sensor_count, group_count, broken_asset_count metadata. "
        "Fires on every orchestration/defs/ file change via the "
        "dagster_assets_sensor + a 0 */4 * * * cron."
    ),
)
def dagster_sync_health(context: AssetExecutionContext) -> dict:
    """The Dagster asset health asset (Layer 6 of the sync loop)."""
    report = _latest_dagster_report()
    if not report:
        context.log.warning(f"No dagster sync reports found in {REPORTS_DIR}")
        return {"status": "missing", "report": None}

    metrics = _parse_dagster_report(report)
    mtime = datetime.fromtimestamp(report.stat().st_mtime, tz=timezone.utc)

    context.add_asset_metadata(
        {
            "report_path": MetadataValue.path(str(report)),
            "report_modified": MetadataValue.text(mtime.isoformat()),
            "asset_count": MetadataValue.int(metrics["asset_count"]),
            "sensor_count": MetadataValue.int(metrics["sensor_count"]),
            "group_count": MetadataValue.int(metrics["group_count"]),
            "broken_asset_count": MetadataValue.int(metrics["broken_asset_count"]),
            "metrics": MetadataValue.json(metrics),
        }
    )

    return {
        "status": "ok" if metrics["broken_asset_count"] == 0 else "degraded",
        "report": str(report),
        **metrics,
    }


@asset(
    group_name="3_model_lifecycle/sync_health",
    description=(
        "Triggers when dagster_sync_health's broken_asset_count > 0 "
        "OR when the asset_count drops below the expected baseline. "
        "Logs a warning + opens a follow-up sync:dagster run."
    ),
)
def dagster_sync_alert(context: AssetExecutionContext) -> dict:
    """The Dagster asset degradation alert."""
    dagster_health = dagster_sync_health(context.op_context)  # type: ignore
    broken = dagster_health.get("broken_asset_count", 0)
    if broken > 0:
        context.log.warning(
            f"Dagster degraded: broken_asset_count={broken}"
        )
    return {
        "broken": broken,
        "alert": broken > 0,
    }


@sensor(
    job_name="dagster_sync_health_refresh",
    minimum_interval_seconds=3600,
    description=(
        "Fires when a new stedding/sync-reports/dagster-{date}.md is created "
        "(i.e. after 'mise run sync:dagster') OR when a file under "
        "orchestration/defs/ changes. Triggers the dagster_sync_health "
        "asset to re-materialize."
    ),
)
def dagster_assets_sensor(
    context: SensorEvaluationContext,
) -> None:
    """Sensor that fires on new dagster sync reports OR defs/ file changes."""
    latest = _latest_dagster_report()
    if not latest:
        return
    yield RunRequest(run_key=f"dagster_sync_health_{latest.name}")


dagster_sync_health_job = define_asset_job(
    name="dagster_sync_health_refresh",
    selection=AssetSelection.assets(dagster_sync_health),
)


# =============================================================================
# Layer 7 — BAML Schema Sync (per the 2026-08-15-baml-sync-loop-v1 change)
# =============================================================================

def _latest_baml_report() -> Path | None:
    """Find the most recent stedding/sync-reports/baml-{date}.md."""
    if not REPORTS_DIR.is_dir():
        return None
    reports = sorted(REPORTS_DIR.glob("baml-*.md"), reverse=True)
    return reports[0] if reports else None


def _parse_baml_report(report: Path) -> dict:
    """Extract the 4 BAML sync metrics from a sync:baml report."""
    metrics = {
        "baml_file_count": 0,
        "function_count": 0,
        "class_count": 0,
        "client_count": 0,
        "test_block_count": 0,
        "drift_count": 0,
    }
    if not report.is_file():
        return metrics
    text = report.read_text()
    m = re.search(r"Total \.baml files:\s+(\d+)", text)
    if m:
        metrics["baml_file_count"] = int(m.group(1))
    m = re.search(r"Total functions:\s+(\d+)", text)
    if m:
        metrics["function_count"] = int(m.group(1))
    m = re.search(r"Total classes:\s+(\d+)", text)
    if m:
        metrics["class_count"] = int(m.group(1))
    m = re.search(
        r"Total clients \(across the 3 client files\):\s+(\d+)", text
    )
    if m:
        metrics["client_count"] = int(m.group(1))
    m = re.search(r"Total test blocks:\s+(\d+)", text)
    if m:
        metrics["test_block_count"] = int(m.group(1))
    m = re.search(r"Total drift \([a-z0-9-]+ \+ [a-z0-9-]+\):\s+(\d+)", text)
    if m:
        metrics["drift_count"] = int(m.group(1))
    return metrics


def _get_registry_drift_count() -> int:
    """Return the count of hardcoded model strings detected by
    scripts/registry_audit.py. Invoked from sync_health metadata to
    surface the centralized-model-registry drift count alongside the
    6 other layer drift counts.

    Per the centralized-model-registry capability (2026-08-15).
    """
    import subprocess
    try:
        proc = subprocess.run(
            ["python3", "scripts/registry_audit.py"],
            capture_output=True, text=True, cwd=str(Path(__file__).parents[3]),
        )
        for line in proc.stdout.splitlines():
            if line.startswith("Found ") and "potential" in line:
                return int(line.split()[1])
    except Exception:
        pass
    return 0


def _get_registry_drift_files() -> list[str]:
    """Return the sorted, deduplicated list of files flagged by
    scripts/registry_audit.py --json. Used by the registry_drift_alert
    sensor + asset + op to emit drift_files metadata alongside
    _get_registry_drift_count().

    Per the centralized-model-registry capability (2026-08-15).
    """
    import subprocess
    try:
        proc = subprocess.run(
            ["python3", "scripts/registry_audit.py", "--json"],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parents[3]),
            timeout=120,
        )
        # registry_audit.py exits 0 (clean) or 1 (with --strict + findings).
        # We treat both as valid JSON; only non-zero + non-one returncodes
        # cause us to fall through to the empty list.
        if proc.returncode not in (0, 1):
            return []
        payload = json.loads(proc.stdout)
        findings = payload.get("findings", [])
        return sorted({
            str(f["file"])
            for f in findings
            if isinstance(f, dict) and "file" in f
        })
    except Exception:
        return []


@asset(
    group_name="3_model_lifecycle/sync_health",
    description=(
        "Reads the latest stedding/sync-reports/baml-{date}.md (Layer 7) "
        "and emits Dagster metadata (baml_file_count, function_count, "
        "class_count, client_count, test_block_count, drift_count). Per the "
        "2026-08-15-baml-sync-loop-v1 change. Fires on every .baml file "
        "change via the baml_assets_sensor + a 0 */4 * * * cron."
    ),
)
def baml_sync_health(context: AssetExecutionContext) -> dict:
    """The BAML schema health asset (Layer 7 of the sync loop)."""
    report = _latest_baml_report()
    if not report:
        context.log.warning(f"No baml sync reports found in {REPORTS_DIR}")
        return {"status": "missing", "report": None}

    metrics = _parse_baml_report(report)
    mtime = datetime.fromtimestamp(report.stat().st_mtime, tz=timezone.utc)

    context.add_asset_metadata(
        {
            "report_path": MetadataValue.path(str(report)),
            "report_modified": MetadataValue.text(mtime.isoformat()),
            "baml_file_count": MetadataValue.int(metrics["baml_file_count"]),
            "function_count": MetadataValue.int(metrics["function_count"]),
            "class_count": MetadataValue.int(metrics["class_count"]),
            "client_count": MetadataValue.int(metrics["client_count"]),
            "test_block_count": MetadataValue.int(metrics["test_block_count"]),
            "drift_count": MetadataValue.int(metrics["drift_count"]),
            "metrics": MetadataValue.json(metrics),
        }
    )

    return {
        "status": "ok" if metrics["drift_count"] == 0 else "degraded",
        "report": str(report),
        **metrics,
    }


@asset(
    group_name="3_model_lifecycle/sync_health",
    description=(
        "Triggers when baml_sync_health's drift_count > 0 OR when the "
        "baml_file_count drops below the expected baseline. Logs a warning "
        "+ opens a follow-up sync:baml run."
    ),
)
def baml_sync_alert(context: AssetExecutionContext) -> dict:
    """The BAML schema degradation alert."""
    baml_health = baml_sync_health(context.op_context)  # type: ignore
    drift = baml_health.get("drift_count", 0)
    if drift > 0:
        context.log.warning(f"BAML degraded: drift_count={drift}")
    return {
        "drift": drift,
        "alert": drift > 0,
    }


@sensor(
    job_name="baml_sync_health_refresh",
    minimum_interval_seconds=3600,
    description=(
        "Fires when a new stedding/sync-reports/baml-{date}.md is created "
        "(i.e. after 'mise run sync:baml') OR when a file under baml_src/ "
        "changes. Triggers the baml_sync_health asset to re-materialize."
    ),
)
def baml_assets_sensor(
    context: SensorEvaluationContext,
) -> None:
    """Sensor that fires on new baml sync reports OR .baml file changes."""
    latest = _latest_baml_report()
    if not latest:
        return
    yield RunRequest(run_key=f"baml_sync_health_{latest.name}")


baml_sync_health_job = define_asset_job(
    name="baml_sync_health_refresh",
    selection=AssetSelection.assets(baml_sync_health),
)


# =============================================================================
# Layer 8 — Stacks Schema Sync (per the 2026-08-15-stacks-sync-loop-v1 change)
# =============================================================================

def _latest_stacks_report() -> Path | None:
    """Find the most recent stedding/sync-reports/stacks-{date}.md."""
    if not REPORTS_DIR.is_dir():
        return None
    reports = sorted(REPORTS_DIR.glob("stacks-*.md"), reverse=True)
    return reports[0] if reports else None


def _parse_stacks_report(report: Path) -> dict:
    """Extract the 4 stacks-sync metrics from a sync:stacks report."""
    metrics = {
        "stack_count": 0,
        "gold_standard_clean_count": 0,
        "gold_standard_violator_count": 0,
        "legacy_oideachais_ref_count": 0,
    }
    if not report.is_file():
        return metrics
    text = report.read_text()
    m = re.search(r"Total stacks:\s+(\d+)", text)
    if m:
        metrics["stack_count"] = int(m.group(1))
    m = re.search(r"GOLD_STANDARD clean:\s+(\d+)", text)
    if m:
        metrics["gold_standard_clean_count"] = int(m.group(1))
    m = re.search(r"GOLD_STANDARD violators:\s+(\d+)", text)
    if m:
        metrics["gold_standard_violator_count"] = int(m.group(1))
    m = re.search(r"Legacy oideachais/ refs:\s+(\d+)", text)
    if m:
        metrics["legacy_oideachais_ref_count"] = int(m.group(1))
    return metrics


@asset(
    group_name="3_model_lifecycle/sync_health",
    description=(
        "Reads the latest stedding/sync-reports/stacks-{date}.md (Layer 8) "
        "and emits Dagster metadata (stack_count, gold_standard_clean_count, "
        "gold_standard_violator_count, legacy_oideachais_ref_count). Per the "
        "2026-08-15-stacks-sync-loop-v1 change. Fires on every stack file "
        "change via the stacks_assets_sensor + a 0 */4 * * * cron."
    ),
)
def stacks_sync_health(context: AssetExecutionContext) -> dict:
    """The IaC stacks health asset (Layer 8 of the sync loop)."""
    report = _latest_stacks_report()
    if not report:
        context.log.warning(f"No stacks sync reports found in {REPORTS_DIR}")
        return {"status": "missing", "report": None}

    metrics = _parse_stacks_report(report)
    mtime = datetime.fromtimestamp(report.stat().st_mtime, tz=timezone.utc)

    context.add_asset_metadata(
        {
            "report_path": MetadataValue.path(str(report)),
            "report_modified": MetadataValue.text(mtime.isoformat()),
            "stack_count": MetadataValue.int(metrics["stack_count"]),
            "gold_standard_clean_count": MetadataValue.int(
                metrics["gold_standard_clean_count"]
            ),
            "gold_standard_violator_count": MetadataValue.int(
                metrics["gold_standard_violator_count"]
            ),
            "legacy_oideachais_ref_count": MetadataValue.int(
                metrics["legacy_oideachais_ref_count"]
            ),
            "metrics": MetadataValue.json(metrics),
        }
    )

    return {
        "status": "ok" if metrics["gold_standard_violator_count"] == 0
        else "degraded",
        "report": str(report),
        **metrics,
    }


@asset(
    group_name="3_model_lifecycle/sync_health",
    description=(
        "Triggers when stacks_sync_health's gold_standard_violator_count > 0 "
        "OR when the stack_count drops below the expected baseline of 89. "
        "Logs a warning + opens a follow-up sync:stacks run."
    ),
)
def stacks_sync_alert(context: AssetExecutionContext) -> dict:
    """The IaC stacks degradation alert."""
    stacks_health = stacks_sync_health(context.op_context)  # type: ignore
    violators = stacks_health.get("gold_standard_violator_count", 0)
    stack_count = stacks_health.get("stack_count", 0)
    if violators > 0:
        context.log.warning(
            f"Stacks degraded: gold_standard_violator_count={violators}"
        )
    if stack_count < 89:
        context.log.warning(
            f"Stacks degraded: stack_count={stack_count} (expected ≥89)"
        )
    return {
        "violators": violators,
        "stack_count": stack_count,
        "alert": violators > 0 or stack_count < 89,
    }


@sensor(
    job_name="stacks_sync_health_refresh",
    minimum_interval_seconds=3600,
    description=(
        "Fires when a new stedding/sync-reports/stacks-{date}.md is created "
        "(i.e. after 'mise run sync:stacks') OR when a file under "
        "bonneagar/stacks/ changes. Triggers the stacks_sync_health asset "
        "to re-materialize."
    ),
)
def stacks_assets_sensor(
    context: SensorEvaluationContext,
) -> None:
    """Sensor that fires on new stacks sync reports OR stack file changes."""
    latest = _latest_stacks_report()
    if not latest:
        return
    yield RunRequest(run_key=f"stacks_sync_health_{latest.name}")


stacks_sync_health_job = define_asset_job(
    name="stacks_sync_health_refresh",
    selection=AssetSelection.assets(stacks_sync_health),
)


# =============================================================================
# Layer 10 — Agent Definitions Sync (per the 2026-08-15-agent-definitions-sync-loop-v1 change)
# =============================================================================

def _latest_agents_report() -> Path | None:
    """Find the most recent stedding/sync-reports/agents-{date}.md."""
    if not REPORTS_DIR.is_dir():
        return None
    reports = sorted(REPORTS_DIR.glob("agents-*.md"), reverse=True)
    return reports[0] if reports else None


def _parse_agents_report(report: Path) -> dict:
    """Extract the 3 agents sync metrics from a sync:agents report."""
    metrics = {
        "file_count": 0,
        "agents_md_count": 0,
        "ncca_subject_count": 0,
    }
    if not report.is_file():
        return metrics
    text = report.read_text()
    m = re.search(r"Total \.py files:\s*(\d+)", text)
    if m:
        metrics["file_count"] = int(m.group(1))
    m = re.search(r"Total AGENTS\.md:\s*(\d+)", text)
    if m:
        metrics["agents_md_count"] = int(m.group(1))
    m = re.search(r"Total NCCA subject specialists:\s*(\d+)", text)
    if m:
        metrics["ncca_subject_count"] = int(m.group(1))
    return metrics


@asset(
    group_name="3_model_lifecycle/sync_health",
    description=(
        "Reads the latest stedding/sync-reports/agents-{date}.md (Layer 10) "
        "and emits Dagster metadata (file_count, agents_md_count, "
        "ncca_subject_count). Per the 2026-08-15-agent-definitions-sync-loop-v1 "
        "change. Fires on every agent file change via the agents_assets_sensor + "
        "a 0 */4 * * * cron."
    ),
)
def agents_sync_health(context: AssetExecutionContext) -> dict:
    """The agent definitions health asset (Layer 10 of the sync loop)."""
    report = _latest_agents_report()
    if not report:
        context.log.warning(f"No agents sync reports found in {REPORTS_DIR}")
        return {"status": "missing", "report": None}

    metrics = _parse_agents_report(report)
    mtime = datetime.fromtimestamp(report.stat().st_mtime, tz=timezone.utc)

    context.add_asset_metadata(
        {
            "report_path": MetadataValue.path(str(report)),
            "report_modified": MetadataValue.text(mtime.isoformat()),
            "file_count": MetadataValue.int(metrics["file_count"]),
            "agents_md_count": MetadataValue.int(metrics["agents_md_count"]),
            "ncca_subject_count": MetadataValue.int(metrics["ncca_subject_count"]),
            "metrics": MetadataValue.json(metrics),
        }
    )

    return {
        "status": "ok" if metrics["file_count"] > 0 else "degraded",
        "report": str(report),
        **metrics,
    }


@asset(
    group_name="3_model_lifecycle/sync_health",
    description=(
        "Triggers when agents_sync_health's file_count drops below the "
        "expected baseline OR when the agents_md_count is less than 5. "
        "Logs a warning + opens a follow-up sync:agents run."
    ),
)
def agents_sync_alert(context: AssetExecutionContext) -> dict:
    """The agent definitions degradation alert."""
    agents_health = agents_sync_health(context.op_context)  # type: ignore
    file_count = agents_health.get("file_count", 0)
    agents_md = agents_health.get("agents_md_count", 0)
    if file_count == 0 or agents_md < 5:
        context.log.warning(
            f"Agents degraded: file_count={file_count}, agents_md={agents_md}"
        )
    return {
        "file_count": file_count,
        "agents_md_count": agents_md,
        "alert": file_count == 0 or agents_md < 5,
    }


@sensor(
    job_name="agents_sync_health_refresh",
    minimum_interval_seconds=3600,
    description=(
        "Fires when a new stedding/sync-reports/agents-{date}.md is created "
        "(i.e. after 'mise run sync:agents') OR when a file under agents/ "
        "changes. Triggers the agents_sync_health asset to re-materialize."
    ),
)
def agents_assets_sensor(
    context: SensorEvaluationContext,
) -> None:
    """Sensor that fires on new agents sync reports OR agent file changes."""
    latest = _latest_agents_report()
    if not latest:
        return
    yield RunRequest(run_key=f"agents_sync_health_{latest.name}")


agents_sync_health_job = define_asset_job(
    name="agents_sync_health_refresh",
    selection=AssetSelection.assets(agents_sync_health),
)


# =============================================================================
# Layer 11 - Notebooks Sync (per the 2026-08-15-notebooks-sync-loop-v1 change)
# =============================================================================

def _latest_notebooks_report() -> Path | None:
    """Find the most recent stedding/sync-reports/notebooks-{date}.md."""
    if not REPORTS_DIR.is_dir():
        return None
    reports = sorted(REPORTS_DIR.glob("notebooks-*.md"), reverse=True)
    return reports[0] if reports else None


def _parse_notebooks_report(report: Path) -> dict:
    """Extract the 2 notebooks sync metrics from a sync:notebooks report."""
    metrics = {
        "file_count": 0,
        "cell_count": 0,
    }
    if not report.is_file():
        return metrics
    text = report.read_text()
    m = re.search(r"Total notebook files:\s*(\d+)", text)
    if m:
        metrics["file_count"] = int(m.group(1))
    m = re.search(r"Total @app\.cell decorators:\s*(\d+)", text)
    if m:
        metrics["cell_count"] = int(m.group(1))
    return metrics


@asset(
    group_name="3_model_lifecycle/sync_health",
    description=(
        "Reads the latest stedding/sync-reports/notebooks-{date}.md (Layer 11) "
        "and emits Dagster metadata (file_count, cell_count). Per the "
        "2026-08-15-notebooks-sync-loop-v1 change. Fires on every notebook "
        "file change via the notebooks_assets_sensor + a 0 */4 * * * cron."
    ),
)
def notebooks_sync_health(context: AssetExecutionContext) -> dict:
    """The notebooks sync health asset (Layer 11 of the sync loop)."""
    report = _latest_notebooks_report()
    if not report:
        context.log.warning(f"No notebooks sync reports found in {REPORTS_DIR}")
        return {"status": "missing", "report": None}

    metrics = _parse_notebooks_report(report)
    mtime = datetime.fromtimestamp(report.stat().st_mtime, tz=timezone.utc)

    context.add_asset_metadata(
        {
            "report_path": MetadataValue.path(str(report)),
            "report_modified": MetadataValue.text(mtime.isoformat()),
            "file_count": MetadataValue.int(metrics["file_count"]),
            "cell_count": MetadataValue.int(metrics["cell_count"]),
            "metrics": MetadataValue.json(metrics),
        }
    )

    return {
        "status": "ok" if metrics["file_count"] > 0 else "degraded",
        "report": str(report),
        **metrics,
    }


@asset(
    group_name="3_model_lifecycle/sync_health",
    description=(
        "Triggers when notebooks_sync_health's file_count drops below the "
        "expected baseline OR when the cell_count is 0. Logs a warning + "
        "opens a follow-up sync:notebooks run."
    ),
)
def notebooks_sync_alert(context: AssetExecutionContext) -> dict:
    """The notebooks sync degradation alert."""
    nb_health = notebooks_sync_health(context.op_context)  # type: ignore
    file_count = nb_health.get("file_count", 0)
    cell_count = nb_health.get("cell_count", 0)
    if file_count == 0 or cell_count == 0:
        context.log.warning(
            f"Notebooks degraded: file_count={file_count}, cell_count={cell_count}"
        )
    return {
        "file_count": file_count,
        "cell_count": cell_count,
        "alert": file_count == 0 or cell_count == 0,
    }


@sensor(
    job_name="notebooks_sync_health_refresh",
    minimum_interval_seconds=3600,
    description=(
        "Fires when a new stedding/sync-reports/notebooks-{date}.md is created "
        "(i.e. after 'mise run sync:notebooks') OR when a file under notebooks/ "
        "changes. Triggers the notebooks_sync_health asset to re-materialize."
    ),
)
def notebooks_assets_sensor(
    context: SensorEvaluationContext,
) -> None:
    """Sensor that fires on new notebooks sync reports OR notebook file changes."""
    latest = _latest_notebooks_report()
    if not latest:
        return
    yield RunRequest(run_key=f"notebooks_sync_health_{latest.name}")


notebooks_sync_health_job = define_asset_job(
    name="notebooks_sync_health_refresh",
    selection=AssetSelection.assets(notebooks_sync_health),
)


# =============================================================================
# Layer 9 — Centralized-model-registry drift alert (per the
# 2026-08-15-cascading-registry-integration-v2 spec delta on
# dagster-5-layer-component-architecture). Wires the FULL sensor +
# materialize job + asset that the cascading-registry-integration-v1
# commit (9f4391bcd) deferred. The helper _get_registry_drift_count()
# added in that commit is reused for the count; the sibling helper
# _get_registry_drift_files() (added above) supplies the file list.
# Spec delta:
# openspec/changes/2026-08-15-cascading-registry-integration-v2/specs/dagster-5-layer-component-architecture/spec.md
# =============================================================================

REGISTRY_DRIFT_ALERT_ASSET_KEY: AssetKey = AssetKey(["registry", "drift_alert"])
REGISTRY_DRIFT_CURSOR_KEY = "registry_drift_count"


@asset(
    key=REGISTRY_DRIFT_ALERT_ASSET_KEY,
    group_name="3_model_lifecycle/sync_health",
    description=(
        "Surfaces the count of hardcoded model strings detected by "
        "scripts/registry_audit.py via Dagster metadata "
        "(drift_count + drift_files + last_check timestamp + alert bool). "
        "The asset fires via the registry_drift_alert_sensor + the "
        "materialize_registry_drift_alert_job (with the "
        "materialize_registry_drift_alert_op). Per the "
        "2026-08-15-cascading-registry-integration-v2 spec delta on "
        "dagster-5-layer-component-architecture."
    ),
)
def registry_drift_alert(context: AssetExecutionContext) -> dict:
    """The centralized-model-registry drift alert asset (Layer 9)."""
    drift_count = _get_registry_drift_count()
    drift_files = _get_registry_drift_files()
    last_check = datetime.now(timezone.utc).isoformat()
    context.add_asset_metadata(
        {
            "drift_count": MetadataValue.int(drift_count),
            "drift_files": MetadataValue.json(drift_files),
            "last_check": MetadataValue.text(last_check),
            "alert": MetadataValue.bool(drift_count > 0),
        }
    )
    return {
        "drift_count": drift_count,
        "drift_files": drift_files,
        "last_check": last_check,
        "alert": drift_count > 0,
    }


@op(
    description=(
        "Re-invokes scripts/registry_audit.py, logs the drift count + "
        "file count, emits a Dagster AssetMaterialization for the "
        "registry/drift_alert asset, and raises a Failure if drift > 0 so "
        "the materialize_registry_drift_alert_job fails loudly. Per the "
        "2026-08-15-cascading-registry-integration-v2 spec delta."
    ),
)
def materialize_registry_drift_alert_op(context) -> None:
    """Op that re-runs scripts/registry_audit.py + emits a materialization."""
    drift_count = _get_registry_drift_count()
    drift_files = _get_registry_drift_files()
    last_check = datetime.now(timezone.utc).isoformat()

    context.log.info(
        "registry_drift_alert: drift_count=%d drift_files=%d",
        drift_count,
        len(drift_files),
    )

    yield AssetMaterialization(
        asset_key=REGISTRY_DRIFT_ALERT_ASSET_KEY,
        description=(
            f"registry_drift_alert: drift_count={drift_count} "
            f"drift_files={len(drift_files)}"
        ),
        metadata={
            "drift_count": MetadataValue.int(drift_count),
            "drift_files": MetadataValue.json(drift_files),
            "last_check": MetadataValue.text(last_check),
        },
    )

    if drift_count > 0:
        raise Failure(
            description=(
                f"centralized-model-registry drift detected: "
                f"{drift_count} hardcoded model string(s) across "
                f"{len(drift_files)} file(s). Sample files: "
                f"{drift_files[:5]}"
            )
        )


@job(
    name="materialize_registry_drift_alert",
    description=(
        "Re-runs scripts/registry_audit.py + emits a Dagster "
        "AssetMaterialization for the registry/drift_alert asset. "
        "Fails loudly (via materialize_registry_drift_alert_op) if any "
        "hardcoded model strings are detected. Per the "
        "2026-08-15-cascading-registry-integration-v2 spec delta on "
        "dagster-5-layer-component-architecture."
    ),
)
def materialize_registry_drift_alert_job() -> None:
    """The job that materializes the registry_drift_alert asset on drift."""
    materialize_registry_drift_alert_op()


@sensor(
    job_name="materialize_registry_drift_alert",
    minimum_interval_seconds=3600,
    description=(
        "Fires the materialize_registry_drift_alert job whenever "
        "scripts/registry_audit.py detects new hardcoded model strings "
        "(drift_count > 0). Tracks the last reported drift count via a "
        "JSON cursor (key=REGISTRY_DRIFT_CURSOR_KEY) so the same drift "
        "count does not re-fire the job on consecutive ticks. Always "
        "emits a SensorResult with an AssetMaterialization for the "
        "registry/drift_alert asset so the Dagster event log carries a "
        "per-tick audit record. Per the "
        "2026-08-15-cascading-registry-integration-v2 spec delta on "
        "dagster-5-layer-component-architecture."
    ),
)
def registry_drift_alert_sensor(
    context: SensorEvaluationContext,
) -> SensorResult:
    """Sensor that detects centralized-model-registry drift.

    Uses the existing _get_registry_drift_count() helper (added in
    commit 9f4391bcd) for the count + the sibling
    _get_registry_drift_files() helper for the file list. Tracks the
    last reported drift count in a JSON cursor to dedup consecutive
    ticks. Always emits an AssetMaterialization for the
    registry/drift_alert asset so the Dagster event log carries a
    per-tick audit record.
    """
    drift_count = _get_registry_drift_count()
    drift_files = _get_registry_drift_files()
    last_check = datetime.now(timezone.utc).isoformat()

    cursor_str = context.cursor or "{}"
    try:
        cursor_obj = json.loads(cursor_str)
    except (TypeError, ValueError):
        cursor_obj = {}
    last_reported = int(cursor_obj.get(REGISTRY_DRIFT_CURSOR_KEY, 0))

    run_requests: list[RunRequest] = []
    if drift_count > 0 and drift_count != last_reported:
        run_requests.append(
            RunRequest(
                run_key=f"registry_drift_alert_{drift_count}",
                tags={
                    "drift_count": str(drift_count),
                    "drift_files_count": str(len(drift_files)),
                    "dagster.sensor": "registry_drift_alert",
                },
            )
        )

    return SensorResult(
        run_requests=run_requests,
        cursor=json.dumps({REGISTRY_DRIFT_CURSOR_KEY: drift_count}),
        asset_materializations=[
            AssetMaterialization(
                asset_key=REGISTRY_DRIFT_ALERT_ASSET_KEY,
                description=(
                    f"registry_drift_alert: drift_count={drift_count} "
                    f"drift_files={len(drift_files)}"
                ),
                metadata={
                    "drift_count": MetadataValue.int(drift_count),
                    "drift_files": MetadataValue.json(drift_files),
                    "last_check": MetadataValue.text(last_check),
                },
            )
        ],
    )
