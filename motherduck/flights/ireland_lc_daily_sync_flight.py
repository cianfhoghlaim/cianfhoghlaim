"""
ireland_lc_daily_sync_flight — BIEP v3 daily MotherDuck Flight.

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

Daily Python job that:
1. Runs `mise run biep:v3:m1` to re-extract the 12 Ireland LC cohorts
   (6 subjects × 2 languages).
2. Runs the 6 per-subject CocoIndex v1 Apps to re-embed the
   `cianhoghlaim.ireland.leaving_cycle.<subject>.<level>_<lang>_chunks`
   LanceDB tables.
3. Writes a status row to
   `md:cianfhoghlaim.education.ireland._audit.daily_sync_status`.

Scheduled via `flights/config.yaml` (cron `0 2 * * *` = 02:00 UTC).

Reference: openspec/changes/2026-08-13-biep-v3-systematic-download-ireland-england-v1/
openspec/specs/british-isles-education-pipeline-v3/spec.md
"""
from __future__ import annotations

import datetime
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import duckdb

logger = logging.getLogger("ireland_lc_daily_sync_flight")


def run_m1_pipeline() -> dict[str, Any]:
    """Run the M1 Ireland LC pipeline via `mise run biep:v3:m1`."""
    result = subprocess.run(
        ["mise", "run", "biep:v3:m1"],
        capture_output=True,
        text=True,
        timeout=1800,  # 30 minutes
    )
    return {
        "exit_code": result.returncode,
        "stdout_tail": result.stdout[-2000:],
        "stderr_tail": result.stderr[-2000:],
        "ok": result.returncode == 0,
    }


def replicate_ireland_lc_to_lance() -> dict[str, Any]:
    """Replicate the 12 cohort tables (6 subjects × 2 languages) to LanceDB.

    Reads from the cianfhoghlaim.education.ireland.leaving_cycle.<subject>
    DuckLake tables and writes to the per-cohort LanceDB tables.
    """
    # Use the canonical scripts/export_cohorts_to_lance.py helper
    script_path = Path("scripts/export_cohorts_to_lance.py")
    if not script_path.exists():
        logger.warning("scripts/export_cohorts_to_lance.py not found")
        return {"ok": False, "error": "missing script"}
    result = subprocess.run(
        ["python3", str(script_path), "--jurisdiction", "ireland", "--stage", "leaving_cycle"],
        capture_output=True,
        text=True,
        timeout=1800,
    )
    return {
        "exit_code": result.returncode,
        "stdout_tail": result.stdout[-2000:],
        "stderr_tail": result.stderr[-2000:],
        "ok": result.returncode == 0,
    }


def write_status(lakehouse_uri: str, status: dict[str, Any]) -> None:
    """Write a status row to the BIEP v3 daily sync audit table."""
    con = duckdb.connect(lakehouse_uri)
    try:
        con.execute(
            """
            CREATE SCHEMA IF NOT EXISTS cianfhoghlaim.education.ireland._audit;
            CREATE TABLE IF NOT EXISTS cianfhoghlaim.education.ireland._audit.daily_sync_status (
                flight_name VARCHAR,
                sync_at TIMESTAMP,
                exit_code INT,
                ok BOOLEAN,
                stdout_tail VARCHAR,
                stderr_tail VARCHAR
            );
            """
        )
        con.execute(
            """
            INSERT INTO cianfhoghlaim.education.ireland._audit.daily_sync_status
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                "ireland_lc_daily_sync_flight",
                datetime.datetime.now(datetime.UTC),
                status.get("exit_code", -1),
                status.get("ok", False),
                status.get("stdout_tail", ""),
                status.get("stderr_tail", ""),
            ],
        )
    finally:
        con.close()


def main() -> int:
    """Run the canonical Ireland LC daily sync flight. Exit 0 on success."""
    lakehouse_uri = os.environ.get("LAKEHOUSE_DUCKDB", "md:cianfhoghlaim")
    logger.info("Starting Ireland LC daily sync flight (cron 02:00 UTC)...")

    # Step 1: run the M1 pipeline
    pipeline_status = run_m1_pipeline()
    if not pipeline_status["ok"]:
        logger.error("M1 pipeline failed: %s", pipeline_status["stderr_tail"])
        write_status(lakehouse_uri, pipeline_status)
        return 1

    # Step 2: replicate to LanceDB
    lance_status = replicate_ireland_lc_to_lance()
    if not lance_status["ok"]:
        logger.error("LanceDB replication failed: %s", lance_status["stderr_tail"])
        write_status(lakehouse_uri, lance_status)
        return 1

    # Step 3: write status
    write_status(lakehouse_uri, {"ok": True, "exit_code": 0, "stdout_tail": "all 12 cohorts re-extracted + re-embedded", "stderr_tail": ""})
    logger.info("Ireland LC daily sync flight complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
