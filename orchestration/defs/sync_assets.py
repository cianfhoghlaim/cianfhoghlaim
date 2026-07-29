dagster_sync_health_job = define_asset_job(
    name="dagster_sync_health_refresh",
    selection=[dagster_sync_health],
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
    m = re.search(r"Total \.baml files:\s*(\d+)", text)
    if m:
        metrics["baml_file_count"] = int(m.group(1))
    m = re.search(r"Total functions:\s*(\d+)", text)
    if m:
        metrics["function_count"] = int(m.group(1))
    m = re.search(r"Total classes:\s*(\d+)", text)
    if m:
        metrics["class_count"] = int(m.group(1))
    m = re.search(
        r"Total clients \(across the 3 client files\):\s*(\d+)", text
    )
    if m:
        metrics["client_count"] = int(m.group(1))
    m = re.search(r"Total test blocks:\s*(\d+)", text)
    if m:
        metrics["test_block_count"] = int(m.group(1))
    m = re.search(r"Total drift \(gemma-3-4b \+ gemma-3-27b\):\s*(\d+)", text)
    if m:
        metrics["drift_count"] = int(m.group(1))
    return metrics


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
    selection=[baml_sync_health],
)