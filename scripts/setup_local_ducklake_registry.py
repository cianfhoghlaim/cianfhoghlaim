"""Set up local DuckLake for the BIEP v3 registry.

Per the 2026-08-11-biep-v3-lakehouse-population-v1 change (local dev path).

Run once after `km deploy stack lakehouse-bunchloch --action=up`:

    export AWS_ACCESS_KEY_ID=...
    export AWS_SECRET_ACCESS_KEY=...
    export GARAGE_PASSWORD=...
    python3 scripts/setup_local_ducklake_registry.py

This script:
1. Connects to the local Postgres via the lakehouse-bunchloch service.
2. Creates the `ducklake_cianchoghlaim` database (idempotent).
3. ATTACHes a DuckLake catalog backed by that Postgres + Garage S3.
4. Creates the `education.subjects` table.

After running this, set:
    export BIEP_REGISTRY_URI="<ducklake URI>"
    export BIEP_REGISTRY_SCHEMA="education"
    mise run biep:v3:registry:seed
"""
from __future__ import annotations

import os
import sys

import duckdb

PG_HOST: str = os.getenv("PG_HOST", "localhost")
PG_PORT: int = int(os.getenv("PG_PORT", "5433"))
PG_USER: str = os.getenv("PG_USER", "lakekeeper")
PG_PASSWORD: str = os.getenv("PG_PASSWORD", "")
PG_DB: str = os.getenv("PG_DB", "ducklake_cianchoghlaim")
S3_BUCKET: str = os.getenv("S3_BUCKET", "ducklake-cianchoghlaim")
S3_ENDPOINT: str = os.getenv("S3_ENDPOINT", "http://localhost:3900")
S3_REGION: str = os.getenv("S3_REGION", "garage")


def main() -> int:
    if not PG_PASSWORD:
        print("ERROR: PG_PASSWORD env var must be set", file=sys.stderr)
        return 1
    if not os.getenv("AWS_ACCESS_KEY_ID") or not os.getenv("AWS_SECRET_ACCESS_KEY"):
        print(
            "ERROR: AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY must be set",
            file=sys.stderr,
        )
        return 1

    pg_uri = (
        f"dbname={PG_DB} host={PG_HOST} port={PG_PORT} "
        f"user={PG_USER} password={PG_PASSWORD}"
    )
    ducklake_uri = f"ducklake:postgres:{pg_uri}"

    # DuckLake's CREATE SECRET requires the ENDPOINT without `http://` prefix
    # (DuckLake prepends its own scheme). Strip it from the env var.
    endpoint_no_scheme = S3_ENDPOINT.replace("http://", "").replace("https://", "")

    print(f"BIEP v3 local DuckLake setup")
    print(f"  Postgres: {PG_HOST}:{PG_PORT} db={PG_DB} user={PG_USER}")
    print(f"  S3 bucket: {S3_BUCKET} @ {S3_ENDPOINT} (DuckLake endpoint: {endpoint_no_scheme})")
    print()

    con = duckdb.connect(":memory:")
    con.execute("INSTALL ducklake; LOAD ducklake;")
    con.execute("INSTALL httpfs; LOAD httpfs;")

    # Create the S3 secret (note: no http:// prefix in ENDPOINT)
    con.execute(
        f"""
        CREATE OR REPLACE SECRET garage_s3 (
            TYPE S3, PROVIDER config,
            KEY_ID '{os.environ["AWS_ACCESS_KEY_ID"]}',
            SECRET '{os.environ["AWS_SECRET_ACCESS_KEY"]}',
            REGION '{S3_REGION}',
            ENDPOINT '{endpoint_no_scheme}',
            USE_SSL false, URL_STYLE 'path'
        )
        """
    )
    print("OK: S3 secret created")

    # Ensure the target Postgres database exists
    con.execute(
        f"ATTACH 'dbname=lakekeeper host={PG_HOST} port={PG_PORT} "
        f"user={PG_USER} password={PG_PASSWORD}' AS pg_admin_db"
    )
    try:
        rows = con.execute(
            f"SELECT 1 FROM pg_admin_db.pg_database WHERE datname='{PG_DB}'"
        ).fetchall()
        if not rows:
            con.execute(f"CREATE DATABASE pg_admin_db.{PG_DB}")
            print(f"OK: database '{PG_DB}' created")
        else:
            print(f"OK: database '{PG_DB}' already exists")
    except duckdb.Error as e:
        print(f"WARN: could not ensure database: {e}")
    con.execute("DETACH pg_admin_db")

    # Attach DuckLake (the existing catalog might have a different DATA_PATH,
    # so we set OVERRIDE_DATA_PATH=true to re-align it).
    try:
        con.execute(
            f"ATTACH '{ducklake_uri}' AS lakehouse (DATA_PATH 's3://{S3_BUCKET}/')"
        )
    except duckdb.Error:
        con.execute(
            f"ATTACH '{ducklake_uri}' AS lakehouse (DATA_PATH 's3://{S3_BUCKET}/', OVERRIDE_DATA_PATH true)"
        )
    print(f"OK: DuckLake ATTACH'd as 'lakehouse'")

    # Update the stored DATA_PATH in the DuckLake metadata so future
    # connections without OVERRIDE_DATA_PATH still write to the correct bucket.
    try:
        con.execute(
            "UPDATE ducklake_metadata SET value = ? WHERE key = 'data_path'",
            [f"s3://{S3_BUCKET}/"],
        )
        print(f"OK: DuckLake metadata data_path updated to s3://{S3_BUCKET}/")
    except duckdb.Error as e:
        print(f"WARN: could not update data_path: {e}")

    con.execute("USE lakehouse;")
    con.execute("CREATE SCHEMA IF NOT EXISTS education;")
    print("OK: schema 'education' ensured")

    con.execute(
        """
        CREATE TABLE IF NOT EXISTS education.subjects (
            jurisdiction VARCHAR,
            stage VARCHAR,
            subject_slug VARCHAR,
            board VARCHAR,
            qualification_level VARCHAR,
            language VARCHAR,
            display_name_en VARCHAR,
            display_name_local VARCHAR,
            concept VARCHAR,
            source_url VARCHAR,
            ncca_spec_code VARCHAR,
            baml_function VARCHAR,
            source VARCHAR,
            status VARCHAR,
            first_introduced VARCHAR,
            last_verified VARCHAR,
            notes VARCHAR
        )
        """
    )
    print("OK: education.subjects table ensured")

    print()
    print("Next steps:")
    print()
    print("  export BIEP_REGISTRY_URI=" + repr(ducklake_uri))
    print("  export BIEP_REGISTRY_SCHEMA=education")
    print("  export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID")
    print("  export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY")
    print("  export AWS_REGION=" + S3_REGION)
    print("  export AWS_ENDPOINT_URL=" + S3_ENDPOINT)
    print("  mise run biep:v3:registry:seed")
    return 0


if __name__ == "__main__":
    sys.exit(main())