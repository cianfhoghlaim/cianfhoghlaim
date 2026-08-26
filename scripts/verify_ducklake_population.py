#!/usr/bin/env python3
"""Verify the DuckLake population by reading Parquet files directly."""

import os
import sys

import duckdb

KEY = os.environ["AWS_ACCESS_KEY_ID"]
SECRET = os.environ["AWS_SECRET_ACCESS_KEY"]
ENDPOINT = os.environ["AWS_ENDPOINT_URL"].replace("http://", "")
# Established secret-loading convention (bonneagar/stacks/lakehouse/secrets.env):
# POSTGRES_PASSWORD is Infisical-first in prod (resolved by the locket
# sidecar into the container env), .env.dev-fallback in local dev.
# DUCKLAKE_POSTGRES_PASSWORD is an explicit override some callers use
# (see dlt_sources/common/destinations_cianfhoghlaim.py); "devpassword"
# is the last-resort default when neither is set.
PG_PASSWORD = os.environ.get("DUCKLAKE_POSTGRES_PASSWORD") or os.environ.get(
    "POSTGRES_PASSWORD", "devpassword"
)
# Canonical DuckLake bucket. Must match `destinations_cianfhoghlaim.py` and
# `mise.toml` — the live-seeded catalog uses `ducklake`. The nine paths below
# were hardcoded to `ducklake-cianfhoghlaim` with no env override until
# 2026-08-13, so this "verification" script read an empty/absent bucket and
# reported zeros.
BUCKET = os.environ.get("DUCKLAKE_BUCKET", "ducklake")

con = duckdb.connect(":memory:")
con.execute("INSTALL ducklake; LOAD ducklake;")
con.execute("INSTALL httpfs; LOAD httpfs;")
con.execute(
    f"CREATE SECRET gs3 (TYPE S3, PROVIDER config, "
    f"KEY_ID '{KEY}', SECRET '{SECRET}', REGION 'garage', "
    f"ENDPOINT '{ENDPOINT}', USE_SSL false, URL_STYLE 'path')"
)
con.execute(
    "ATTACH 'ducklake:postgres:dbname=ducklake_cianfhoghlaim "
    "host=localhost port=5433 user=lakekeeper "
    f"password={PG_PASSWORD}' "
    f"AS cianfhoghlaim (DATA_PATH 's3://{BUCKET}/cianfhoghlaim/')"
)
con.execute("USE cianfhoghlaim;")

paths = [
    f"s3://{BUCKET}/cianfhoghlaim/{j}_education/{j}_subjects/*.parquet"
    for j in (
        "ireland",
        "england",
        "scotland",
        "wales",
        "northern_ireland",
        "jersey",
        "guernsey",
        "isle_of_man",
    )
]

print("Lakehouse population (Parquet files):")
total = 0
for path in paths:
    cnt = con.execute(f"SELECT COUNT(*) FROM read_parquet('{path}')").fetchone()[0]
    total += cnt
    print(f"  {path.split('/')[-3]:<35} {cnt:>5} rows")
print(f"  {'TOTAL':<35} {total:>5} rows")

print()
print("Sample ireland row:")
for r in con.execute(
    "SELECT jurisdiction, subject, language, source_url FROM "
    f"read_parquet('s3://{BUCKET}/cianfhoghlaim/ireland_education/ireland_subjects/*.parquet') "
    "LIMIT 3"
).fetchall():
    print(f"  {r}")
