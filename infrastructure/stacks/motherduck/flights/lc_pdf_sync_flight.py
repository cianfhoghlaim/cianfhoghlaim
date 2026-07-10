"""MotherDuck Flight: lc_pdf_sync_flight.

Daily Python job (cron ``0 4 * * *`` = 04:00 UTC) that:

1. Runs ``uv run cocoindex update lc_subjects`` to re-ingest the
   6 LC subjects' PDF corpus (any new PDFs landed in
   ``s3://garage/oideachais/leaving_cert/<subject>/<lang>/<year>/<file>.pdf``
   in the last 24h).
2. Runs ``uv run dagster asset materialize --select '*lc*'`` to
   re-materialise the 6x6+2 = 38 LC assets (6 subjects x 6 stages
   + gov.ie circulars).
3. Writes a status row to
   ``md:oideachais.lc_ops.daily_sync_status`` capturing the
   subprocess exit codes + the full log.

Part of the BIEP v1 flagship Phase 7
(``openspec/changes/2026-07-13-biep-v1-phases-6-7-unblock-v1/``).

The IaC orchestration (Docker Compose stack + cron binding) lives in
the separate ``bonneagar`` repo at ``bonneagar/stacks/motherduck/``.

Reference: openspec/specs/british-isles-education-pipeline/spec.md
            ("Daily MotherDuck Flight for BAML backfill")
"""
from __future__ import annotations

import datetime as _dt
import os
import pathlib
import subprocess
import sys
from typing import Optional

import duckdb


FLIGHT_NAME = "lc_pdf_sync_flight"
STATUS_DB = "md:oideachais"
STATUS_TABLE = "oideachais.lc_ops.daily_sync_status"
REPO_ROOT = pathlib.Path(
    os.environ.get(
        "CIANFHOGHLAIM_ROOT",
        "/Users/cianmacandeisigh/dev/kings_college_galway",
    )
)
COCO_CWD = REPO_ROOT / "cianfhoghlaim"
DAGSTER_CWD = REPO_ROOT / "cianfhoghlaim"


def _now() -> _dt.datetime:
    """UTC now (timezone-aware)."""
    return _dt.datetime.now(_dt.timezone.utc)


def _format_ts(ts: _dt.datetime) -> str:
    """ISO-8601 UTC timestamp string."""
    return ts.astimezone(_dt.timezone.utc).isoformat().replace("+00:00", "Z")


def _run_step(
    name: str,
    cmd: list[str],
    cwd: pathlib.Path,
    log: list[str],
) -> int:
    """Run a subprocess step, capture its exit code + output."""
    log.append(f"{_format_ts(_now())} step:{name} starting cmd={cmd} cwd={cwd}")
    try:
        result = subprocess.run(
            cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=3600,
        )
        log.append(
            f"{_format_ts(_now())} step:{name} exit={result.returncode}"
        )
        if result.stdout:
            log.append(f"{_format_ts(_now())} step:{name} stdout[:1000]={result.stdout[:1000]}")
        if result.stderr:
            log.append(f"{_format_ts(_now())} step:{name} stderr[:1000]={result.stderr[:1000]}")
        return result.returncode
    except subprocess.TimeoutExpired:
        log.append(f"{_format_ts(_now())} step:{name} TIMEOUT after 3600s")
        return 124
    except Exception as exc:
        log.append(f"{_format_ts(_now())} step:{name} EXC={type(exc).__name__}: {exc}")
        return 1


def _ensure_status_table(con: duckdb.DuckDBPyConnection) -> None:
    """Ensure the lc_ops.daily_sync_status table exists."""
    con.execute(
        f"CREATE SCHEMA IF NOT EXISTS oideachais.lc_ops"
    )
    con.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {STATUS_TABLE} (
            flight_name VARCHAR,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            status VARCHAR,
            coco_exit INTEGER,
            dagster_exit INTEGER,
            log VARCHAR
        )
        """
    )


def main() -> None:
    started_at = _now()
    log: list[str] = []

    def _log(msg: str) -> None:
        print(f"[{FLIGHT_NAME}] {msg}", flush=True)
        log.append(f"{_format_ts(_now())} {msg}")

    _log(f"started_at={_format_ts(started_at)} repo_root={REPO_ROOT}")

    # Step 1: cocoindex update lc_subjects
    _log("step1: cocoindex update lc_subjects")
    coco_exit = _run_step(
        "cocoindex_update",
        ["uv", "run", "cocoindex", "update", "lc_subjects"],
        COCO_CWD,
        log,
    )

    # Step 2: dagster materialize
    _log("step2: dagster asset materialize --select '*lc*'")
    dagster_exit = _run_step(
        "dagster_materialize",
        ["uv", "run", "dagster", "asset", "materialize", "--select", "*lc*"],
        DAGSTER_CWD,
        log,
    )

    completed_at = _now()
    overall_status = "ok" if (coco_exit == 0 and dagster_exit == 0) else "failed"
    _log(f"step3: write status row to {STATUS_TABLE} status={overall_status}")

    # Step 3: write status row
    try:
        con = duckdb.connect(STATUS_DB)
        _ensure_status_table(con)
        con.execute(
            f"""
            INSERT INTO {STATUS_TABLE}
                (flight_name, started_at, completed_at, status,
                 coco_exit, dagster_exit, log)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                FLIGHT_NAME,
                started_at,
                completed_at,
                overall_status,
                coco_exit,
                dagster_exit,
                "\n".join(log),
            ],
        )
        con.close()
        _log("done")
    except Exception as exc:
        _log(f"status write failed: {type(exc).__name__}: {exc}")
        # Last-resort: print the log to stdout so the cron daemon captures it
        print("\n".join(log), flush=True)
        sys.exit(2)

    # Exit non-zero if any step failed
    if overall_status != "ok":
        sys.exit(1)


if __name__ == "__main__":
    main()