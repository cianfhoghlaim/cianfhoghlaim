"""
lc_pdf_sync_flight — BIEP v1 daily MotherDuck Flight.

Daily Python job that:
1. Runs `cocoindex update lc_subjects` to re-embed the 6 LC subject
   LanceDB tables.
2. Runs `dagster asset materialize --select '*lc*'` to refresh the
   42 lc5/lc6 Dagster assets.
3. Writes a status row to
   `md:cianfhoghlaim.lc_ops.daily_sync_status`.

Scheduled via `flights/config.yaml` (cron `0 4 * * *` = 04:00 UTC).

Reference: openspec/changes/2026-07-06-british-isles-education-pipeline-v1/
openspec/specs/british-isles-education-pipeline/spec.md
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

logger = logging.getLogger("lc_pdf_sync_flight")

# The 6 BIEP v1 priority LC subjects.
LC_SUBJECTS: tuple[str, ...] = (
    "mathematics",
    "chemistry",
    "geography",
    "gaeilge",
    "english",
    "computer_science",
)

# The 2 CocoIndex subjects that are optional extras in v1
# (gov.ie circulars is the 7th v1 App).
EXTRA_APPS: tuple[str, ...] = ("government_circulars",)


def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def run_cocoindex_update(apps: tuple[str, ...]) -> dict[str, Any]:
    """Run `cocoindex update` for each subject App. Returns a per-app status map."""
    status: dict[str, Any] = {}
    for app in apps:
        app_name = f"{app}_embedding"
        try:
            result = subprocess.run(
                ["uv", "run", "cocoindex", "update", app_name],
                check=False,
                capture_output=True,
                text=True,
                timeout=600,
            )
            status[app_name] = {
                "ok": result.returncode == 0,
                "returncode": result.returncode,
                "stdout_tail": result.stdout[-500:] if result.stdout else "",
                "stderr_tail": result.stderr[-500:] if result.stderr else "",
            }
        except subprocess.TimeoutExpired:
            status[app_name] = {"ok": False, "error": "timeout (10min)"}
        except Exception as e:  # pragma: no cover
            status[app_name] = {"ok": False, "error": str(e)}
    return status


def run_dagster_materialize() -> dict[str, Any]:
    """Run `dagster asset materialize --select '*lc*'` to refresh assets."""
    try:
        result = subprocess.run(
            [
                "uv",
                "run",
                "dagster",
                "asset",
                "materialize",
                "--select",
                "*lc*",
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=1800,  # 30 min
        )
        return {
            "ok": result.returncode == 0,
            "returncode": result.returncode,
            "stdout_tail": result.stdout[-500:] if result.stdout else "",
            "stderr_tail": result.stderr[-500:] if result.stderr else "",
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "timeout (30min)"}
    except Exception as e:  # pragma: no cover
        return {"ok": False, "error": str(e)}


def write_status_row(
    *,
    cocoindex_status: dict[str, Any],
    dagster_status: dict[str, Any],
    flight_name: str = "lc_pdf_sync_flight",
    con: duckdb.DuckDBPyConnection | None = None,
) -> bool:
    """Write the daily sync status row to
    ``md:cianfhoghlaim.lc_ops.daily_sync_status``.

    Creates the table + schema if missing.
    """
    if con is None:
        token = os.environ.get("MOTHERDUCK_TOKEN", "")
        if token:
            # Use a private DuckDB instance to set the token before
            # opening the MotherDuck attach — avoids the SQL-injection
            # risk of an f-string interpolation into ``duckdb.sql``.
            bootstrap = duckdb.connect()
            bootstrap.execute("SET motherduck_token = ?", [token])
            bootstrap.close()
        con = duckdb.connect("md:cianfhoghlaim")

    try:
        con.execute(
            "CREATE SCHEMA IF NOT EXISTS cianfhoghlaim.lc_ops"
        )
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS cianfhoghlaim.lc_ops.daily_sync_status (
                id BIGINT,
                flight_name VARCHAR,
                started_at TIMESTAMP,
                finished_at TIMESTAMP,
                status VARCHAR,
                cocoindex_ok BOOLEAN,
                cocoindex_payload JSON,
                dagster_ok BOOLEAN,
                dagster_payload JSON
            )
            """
        )
    except Exception as e:  # pragma: no cover
        logger.warning("status_table_create_failed: %s", e)

    cocoindex_ok = all(v.get("ok", False) for v in cocoindex_status.values())
    dagster_ok = dagster_status.get("ok", False)
    overall_ok = cocoindex_ok and dagster_ok

    try:
        import json
        con.execute(
            """
            INSERT INTO cianfhoghlaim.lc_ops.daily_sync_status
                (id, flight_name, started_at, finished_at, status,
                 cocoindex_ok, cocoindex_payload, dagster_ok, dagster_payload)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                int(datetime.datetime.now(datetime.timezone.utc).timestamp()),
                flight_name,
                datetime.datetime.now(datetime.timezone.utc),
                datetime.datetime.now(datetime.timezone.utc),
                "ok" if overall_ok else "failed",
                cocoindex_ok,
                json.dumps(cocoindex_status),
                dagster_ok,
                json.dumps(dagster_status),
            ],
        )
        return True
    except Exception as e:  # pragma: no cover
        logger.error("status_row_write_failed: %s", e)
        return False


def main() -> int:
    """Run the daily lc_pdf_sync_flight end-to-end."""
    started_at = _now_iso()
    logger.info("lc_pdf_sync_flight_started at %s", started_at)

    # 1. CocoIndex re-embed (6 subject Apps + government_circulars).
    apps = LC_SUBJECTS + EXTRA_APPS
    cocoindex_status = run_cocoindex_update(apps)
    logger.info("cocoindex_update_complete: %s", cocoindex_status)

    # 2. Dagster asset materialize --select '*lc*'.
    dagster_status = run_dagster_materialize()
    logger.info("dagster_materialize_complete: %s", dagster_status)

    # 3. Write the status row.
    write_status_row(
        cocoindex_status=cocoindex_status, dagster_status=dagster_status
    )

    finished_at = _now_iso()
    logger.info("lc_pdf_sync_flight_finished at %s", finished_at)

    cocoindex_ok = all(v.get("ok", False) for v in cocoindex_status.values())
    dagster_ok = dagster_status.get("ok", False)
    return 0 if (cocoindex_ok and dagster_ok) else 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sys.exit(main())
