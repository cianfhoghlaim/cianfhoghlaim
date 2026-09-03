"""
filesystem_monthly_sync_flight — BIEP v3 MotherDuck Flight.

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change
(extended to all British Isles jurisdictions via the
2026-08-13 filesystem + language openspec change).

Monthly Python job that:
1. Runs the filesystem Dagster assets
   (`filesystem_documents_ingested`, `filesystem_extractions`,
   `filesystem_embeddings`) to re-ingest the 11 canonical filesystem
   DLT sources.
2. Writes a status row to
   `md:cianfhoghlaim.education.filesystem._audit.daily_sync_status`.

The flight triggers MONTHLY (1st of each month, 00:00 UTC) per the
BIEP v3 scheduling policy. Filesystem content changes more frequently
than education content (which is yearly), so the monthly cadence
matches the typical filesystem refresh rate.

Reference: openspec/changes/2026-08-13-biep-v3-systematic-download-ireland-england-v1/
"""
from __future__ import annotations

import datetime
import logging
import os
import subprocess
import sys

import duckdb

logger = logging.getLogger("filesystem_monthly_sync_flight")


def run_filesystem_pipeline() -> dict:
    """Run the canonical `dagster asset materialize` for the filesystem assets."""
    result = subprocess.run(
        [
            "uv", "run", "dagster", "asset", "materialize",
            "--select",
            "filesystem_documents_ingested,filesystem_extractions,filesystem_embeddings",
            "-m", "orchestration.definitions",
        ],
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


def write_status(lakehouse_uri: str, status: dict) -> None:
    """Write a status row to the BIEP v3 filesystem daily sync audit table."""
    con = duckdb.connect(lakehouse_uri)
    try:
        con.execute(
            """
            CREATE SCHEMA IF NOT EXISTS cianfhoghlaim.education.filesystem._audit;
            CREATE TABLE IF NOT EXISTS cianfhoghlaim.education.filesystem._audit.daily_sync_status (
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
            INSERT INTO cianfhoghlaim.education.filesystem._audit.daily_sync_status
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                "filesystem_monthly_sync_flight",
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
    """Run the canonical filesystem monthly sync flight. Exit 0 on success."""
    lakehouse_uri = os.environ.get("LAKEHOUSE_DUCKDB", "md:cianfhoghlaim")
    logger.info("Starting filesystem monthly sync flight (cron 1st of each month 00:00 UTC)...")

    pipeline_status = run_filesystem_pipeline()
    if not pipeline_status["ok"]:
        logger.error("filesystem pipeline failed: %s", pipeline_status["stderr_tail"])
        write_status(lakehouse_uri, pipeline_status)
        return 1

    write_status(lakehouse_uri, {"ok": True, "exit_code": 0, "stdout_tail": "all 11 filesystem sources re-ingested + re-embedded", "stderr_tail": ""})
    logger.info("filesystem monthly sync flight complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
