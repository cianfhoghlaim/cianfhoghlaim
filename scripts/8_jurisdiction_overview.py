#!/usr/bin/env python3
"""8-jurisdiction overview verification.

Reads the BIEP v3 cohort data from local DuckLake + prints a summary
table (per-jurisdiction × per-stage × per-subject count).

Replaces the MotherDuck-backed `notebooks/23_8_jurisdiction_overview.py`
for the local dev deploy.
"""
from __future__ import annotations

import os

import duckdb

# Canonical DuckLake bucket. Must match `destinations_cianfhoghlaim.py` and
# `mise.toml` — the live-seeded catalog uses `ducklake`. This was hardcoded
# to `ducklake-cianfhoghlaim` with no env override until 2026-08-13.
BUCKET: str = os.environ.get("DUCKLAKE_BUCKET", "ducklake")


def get_duckdb_connection() -> duckdb.DuckDBPyConnection:
    """Open a DuckLake connection configured for local Garage."""
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


def main() -> int:
    con = get_duckdb_connection()

    # Read the registry
    print("=" * 70)
    print("BIEP v3 Registry (from DuckLake `education.subjects`)")
    print("=" * 70)
    rows = con.execute(
        "SELECT jurisdiction, COUNT(*) FROM education.subjects GROUP BY jurisdiction ORDER BY jurisdiction"
    ).fetchall()
    total = 0
    for j, n in rows:
        print(f"  {j:<25} {n:>5} subjects")
        total += n
    print(f"  {'TOTAL':<25} {total:>5} subjects")

    # Read the cohort tables from Parquet (per-jurisdiction)
    print()
    print("=" * 70)
    print("BIEP v3 Cohort rows (from DuckLake Parquet files in S3)")
    print("=" * 70)
    cohort_total = 0
    for jurisdiction in [
        "ireland", "england", "scotland", "wales",
        "northern_ireland", "jersey", "guernsey", "isle_of_man",
    ]:
        glob = (
            f"s3://{BUCKET}/cianfhoghlaim/"
            f"{jurisdiction}_education/{jurisdiction}_subjects/*.parquet"
        )
        try:
            cnt = con.execute(
                f"SELECT COUNT(*) FROM read_parquet('{glob}')"
            ).fetchone()[0]
        except duckdb.Error:
            cnt = 0
        cohort_total += cnt
        print(f"  {jurisdiction:<25} {cnt:>5} rows")
    print(f"  {'TOTAL':<25} {cohort_total:>5} rows")

    # Lance datasets
    print()
    print("=" * 70)
    print("Lance datasets (from local file-based Lance)")
    print("=" * 70)
    import sys
    lance_path = "/Users/cianmacandeisigh/dev/kings_college_galway/storage/data/lancedb"
    for d in sorted(os.listdir(lance_path)):
        if d.startswith("cianfhoghlaim_education_") and os.path.isdir(f"{lance_path}/{d}"):
            try:
                import lance
                ds = lance.dataset(f"{lance_path}/{d}")
                print(f"  {d:<55} {ds.count_rows():>5} rows")
            except Exception as e:
                print(f"  {d:<55} ERR {str(e)[:30]}")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())