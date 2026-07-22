#!/usr/bin/env python3
"""Verify the DuckLake population by reading Parquet files directly."""
import os
import sys

import duckdb

KEY = os.environ["AWS_ACCESS_KEY_ID"]
SECRET = os.environ["AWS_SECRET_ACCESS_KEY"]
ENDPOINT = os.environ["AWS_ENDPOINT_URL"].replace("http://", "")

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
    "password=805c7a4565f7ddf9bea11b6ffbd9a11f536cfe3beaaee7f9' "
    "AS cianfhoghlaim (DATA_PATH 's3://ducklake-cianfhoghlaim/cianfhoghlaim/')"
)
con.execute("USE cianfhoghlaim;")

paths = [
    "s3://ducklake-cianfhoghlaim/cianfhoghlaim/ireland_education/ireland_subjects/*.parquet",
    "s3://ducklake-cianfhoghlaim/cianfhoghlaim/england_education/england_subjects/*.parquet",
    "s3://ducklake-cianfhoghlaim/cianfhoghlaim/scotland_education/scotland_subjects/*.parquet",
    "s3://ducklake-cianfhoghlaim/cianfhoghlaim/wales_education/wales_subjects/*.parquet",
    "s3://ducklake-cianfhoghlaim/cianfhoghlaim/northern_ireland_education/northern_ireland_subjects/*.parquet",
    "s3://ducklake-cianfhoghlaim/cianfhoghlaim/jersey_education/jersey_subjects/*.parquet",
    "s3://ducklake-cianfhoghlaim/cianfhoghlaim/guernsey_education/guernsey_subjects/*.parquet",
    "s3://ducklake-cianfhoghlaim/cianfhoghlaim/isle_of_man_education/isle_of_man_subjects/*.parquet",
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
    "read_parquet('s3://ducklake-cianfhoghlaim/cianfhoghlaim/ireland_education/ireland_subjects/*.parquet') "
    "LIMIT 3"
).fetchall():
    print(f"  {r}")