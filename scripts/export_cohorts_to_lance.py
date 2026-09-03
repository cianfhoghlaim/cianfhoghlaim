#!/usr/bin/env python3
"""Export BIEP v3 DuckLake cohort rows to local Lance datasets.

Per the 2026-08-13 lakehouse full activation plan (Phase 2.7):

The original `consume_voted_ducklake_to_lance()` function (in
`cocoindex/subjects/education_subject_embedding.py`) reads from
MotherDuck + assumes a `voted_canonical` table. Neither exists in
our local deploy. This script adapts the same idea to our local
DuckLake + writes to a local Lance dataset (file-based, no LanceDB
Viewer needed).

Reads the cohort rows from `{jurisdiction}_education.{jurisdiction}_subjects`
in DuckLake and writes one Lance dataset per jurisdiction + (jurisdiction, stage)
to `storage/data/lancedb/`.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import duckdb
import pyarrow as pa

# Path resolution
REPO_ROOT = Path(__file__).resolve().parents[1]
LANCEDB_PATH = REPO_ROOT / "storage" / "data" / "lancedb"
LANCEDB_PATH.mkdir(parents=True, exist_ok=True)

# Canonical DuckLake bucket. Must match `destinations_cianfhoghlaim.py` and
# `mise.toml` — the live-seeded catalog uses `ducklake`. This was hardcoded to
# `ducklake-cianfhoghlaim` with no env override until 2026-08-13, which is why
# the datasets on disk are stale (last written 2026-07-19).
BUCKET = os.environ.get("DUCKLAKE_BUCKET", "ducklake")


def get_duckdb_connection() -> duckdb.DuckDBPyConnection:
    """Open a DuckLake connection configured for local Garage."""
    import os

    KEY = os.environ["AWS_ACCESS_KEY_ID"]
    SECRET = os.environ["AWS_SECRET_ACCESS_KEY"]
    # Established secret-loading convention (bonneagar/stacks/lakehouse/secrets.env):
    # POSTGRES_PASSWORD is Infisical-first in prod (resolved by the locket
    # sidecar into the container env), .env.dev-fallback in local dev.
    # DUCKLAKE_POSTGRES_PASSWORD is an explicit override some callers use
    # (see dlt_sources/common/destinations_cianfhoghlaim.py); "devpassword"
    # is the last-resort default when neither is set.
    PG_PASSWORD = os.environ.get("DUCKLAKE_POSTGRES_PASSWORD") or os.environ.get(
        "POSTGRES_PASSWORD", "devpassword"
    )

    con = duckdb.connect(":memory:")
    con.execute("INSTALL ducklake; LOAD ducklake;")
    con.execute("INSTALL httpfs; LOAD httpfs;")
    con.execute(
        f"CREATE SECRET gs3 (TYPE S3, PROVIDER config, "
        f"KEY_ID '{KEY}', SECRET '{SECRET}', REGION 'garage', "
        f"ENDPOINT 'localhost:3900', USE_SSL false, URL_STYLE 'path')"
    )
    con.execute(
        "ATTACH 'ducklake:postgres:dbname=ducklake_cianfhoghlaim "
        "host=localhost port=5433 user=lakekeeper "
        f"password={PG_PASSWORD}' "
        f"AS cianfhoghlaim (DATA_PATH 's3://{BUCKET}/cianfhoghlaim/')"
    )
    con.execute("USE cianfhoghlaim;")
    return con


def export_jurisdiction_to_lance(
    con: duckdb.DuckDBPyConnection,
    jurisdiction: str,
) -> dict:
    """Read one jurisdiction's cohort rows from DuckLake (via Parquet) + write to Lance."""
    import lance

    dataset_name = f"cianfhoghlaim_education_{jurisdiction}_subjects"
    dataset_path = LANCEDB_PATH / dataset_name

    t0 = time.time()

    # Read directly from Parquet files in S3 (dlt's DuckLake destination writes
    # these to {bucket}/{namespace}/{dataset}/{table}/). The DuckLake metadata
    # catalog doesn't expose these as tables (they're managed by dlt's staging
    # layer), so we read the Parquet files directly.
    parquet_glob = (
        f"s3://{BUCKET}/cianfhoghlaim/"
        f"{jurisdiction}_education/{jurisdiction}_subjects/*.parquet"
    )
    try:
        rows = con.execute(
            f"SELECT * FROM read_parquet('{parquet_glob}')"
        ).fetchall()
        cols = [d[0] for d in con.description]
    except duckdb.Error as e:
        # Empty jurisdiction (no files)
        if "No files found" in str(e):
            return {
                "jurisdiction": jurisdiction,
                "rows_read": 0,
                "rows_written": 0,
                "dataset": str(dataset_path),
                "duration_s": 0,
                "note": "no Parquet files",
            }
        raise

    rows_read = len(rows)
    if rows_read == 0:
        return {
            "jurisdiction": jurisdiction,
            "rows_read": 0,
            "rows_written": 0,
            "dataset": str(dataset_path),
            "duration_s": 0,
            "note": "0 rows in Parquet files",
        }

    # Convert to PyArrow
    table = pa.Table.from_pylist([dict(zip(cols, row)) for row in rows])

    # Write to Lance (file-based, no server needed)
    lance.write_dataset(
        table,
        uri=str(dataset_path),
        mode="overwrite",
    )

    duration = time.time() - t0
    return {
        "jurisdiction": jurisdiction,
        "rows_read": rows_read,
        "rows_written": rows_read,
        "dataset": str(dataset_path),
        "duration_s": duration,
        "columns": cols,
    }


def main() -> int:
    print("BIEP v3 Lakehouse → LanceDB export")
    print(f"  Output dir: {LANCEDB_PATH}")
    print()

    con = get_duckdb_connection()
    jurisdictions = [
        "ireland", "england", "scotland", "wales",
        "northern_ireland", "jersey", "guernsey", "isle_of_man",
    ]

    total = 0
    for j in jurisdictions:
        result = export_jurisdiction_to_lance(con, j)
        total += result["rows_written"]
        marker = "✓" if result["rows_written"] > 0 else "—"
        print(f"  [{marker}] {j:<25} {result['rows_written']:>5} rows in {result['duration_s']:.1f}s")
        if "error" in result:
            print(f"        error: {result['error']}")

    print()
    print(f"Total: {total} rows across {len(jurisdictions)} jurisdictions")
    print(f"Datasets: {LANCEDB_PATH}")

    # Verify
    print()
    print("Lance datasets created:")
    for d in sorted(LANCEDB_PATH.iterdir()):
        if d.is_dir():
            n_files = sum(1 for _ in d.rglob("*") if _.is_file())
            print(f"  {d.name}: {n_files} files")

    return 0


if __name__ == "__main__":
    sys.exit(main())