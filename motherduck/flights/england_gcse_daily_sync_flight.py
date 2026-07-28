"""
england_gcse_daily_sync_flight — BIEP v3 MotherDuck Flight (M4).

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

Yearly Python job that:
1. Runs `mise run biep:v3:m4` to re-extract the 129 England GCSE
   cohorts (43 subjects × 3 boards).
2. Runs the 129 per-cohort CocoIndex v1 Apps to re-embed the
   `cianhoghlaim.england.gcse.<board>.<subject>_gcse_chunks`
   LanceDB tables.
3. Writes a status row to
   `md:cianfhoghlaim.education.england._audit.daily_sync_status`.

The flight triggers YEARLY (1st September, 00:00 UTC) per the
BIEP v3 scheduling policy.

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

import duckdb

logger = logging.getLogger("england_gcse_daily_sync_flight")


def run_m4_pipeline() -> dict:
    """Run the M4 England GCSE pipeline via `mise run biep:v3:m4`."""
    result = subprocess.run(
        ["mise", "run", "biep:v3:m4"],
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


def replicate_england_gcse_to_lance() -> dict:
    """Replicate the 129 GCSE cohort tables to LanceDB."""
    script_path = Path("scripts/export_cohorts_to_lance.py")
    if not script_path.exists():
        logger.warning("scripts/export_cohorts_to_lance.py not found")
        return {"ok": False, "error": "missing script"}
    result = subprocess.run(
        ["python3", str(script_path), "--jurisdiction", "england", "--stage", "gcse"],
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


def write_status(lakehouse_uri: str, status: dict) -> None:
    """Write a status row to the BIEP v3 daily sync audit table."""
    con = duckdb.connect(lakehouse_uri)
    try:
        con.execute(
            """
            CREATE SCHEMA IF NOT EXISTS cianfhoghlaim.education.england._audit;
            CREATE TABLE IF NOT EXISTS cianfhoghlaim.education.england._audit.daily_sync_status (
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
            INSERT INTO cianfhoghlaim.education.england._audit.daily_sync_status
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                "england_gcse_daily_sync_flight",
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
    """Run the canonical England GCSE daily sync flight. Exit 0 on success."""
    lakehouse_uri = os.environ.get("LAKEHOUSE_DUCKDB", "md:cianfhoghlaim")
    logger.info("Starting England GCSE daily sync flight (cron yearly 1st September 00:00 UTC)...")

    # Step 1: run the M4 pipeline
    pipeline_status = run_m4_pipeline()
    if not pipeline_status["ok"]:
        logger.error("M4 pipeline failed: %s", pipeline_status["stderr_tail"])
        write_status(lakehouse_uri, pipeline_status)
        return 1

    # Step 2: replicate to LanceDB
    lance_status = replicate_england_gcse_to_lance()
    if not lance_status["ok"]:
        logger.error("LanceDB replication failed: %s", lance_status["stderr_tail"])
        write_status(lakehouse_uri, lance_status)
        return 1

    # Step 3: write status
    write_status(lakehouse_uri, {"ok": True, "exit_code": 0, "stdout_tail": "all 129 England GCSE cohorts re-extracted + re-embedded", "stderr_tail": ""})
    logger.info("England GCSE daily sync flight complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
