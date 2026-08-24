#!/usr/bin/env python3
"""
Wave 4 namespace consolidation helper.

Per the **2026-08-24-wave-4-ducklake-v1-hardening-v1** openspec
change. This script generates the SQL to migrate the 6 legacy
DuckLake namespaces into the single consolidated
`ducklake_cianfhoghlaim` namespace.

USAGE

    uv run python scripts/wave_4_consolidate_namespaces.py --dry-run
    uv run python scripts/wave_4_consolidate_namespaces.py --apply

The `--apply` flag is intentionally NOT enabled by default — actual
data migration of a production DuckLake is a high-risk operation
that requires:
  - A maintenance window
  - Schema-level backup (Postgres catalog snapshot)
  - S3 versioning enabled on `s3://ducklake-cianfhoghlaim/`
  - A reversible rollback plan (snapshot + RESTORE DATABASE)

The output of this script is a SQL file that the platform team can
review + execute during the maintenance window.

Output: `stedding/sync-reports/wave-4-namespace-consolidation-{date}.sql`
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path("/Users/cianmacandeisigh/dev/cianfhoghlaim")
REPORT_DIR = PROJECT_ROOT / "stedding" / "sync-reports"

# The 6 legacy namespaces + the tables under each.
# Per the Wave 4 master plan, these all migrate into
# `ducklake_cianfhoghlaim`.
LEGACY_NAMESPACES = {
    "ducklake_oideachais": {
        "postgres_schema": "ducklake_oideachais",
        "s3_prefix": "s3://ducklake-oideachais/",
        "tables": [
            "british_isles.education_chunks",
            "british_isles.legal_chunks",
            "british_isles.medical_chunks",
        ],
    },
    "ducklake_educational": {
        "postgres_schema": "ducklake_educational",
        "s3_prefix": "s3://ducklake-educational/",
        "tables": [
            "lc_subjects.mathematics",
            "lc_subjects.chemistry",
            "lc_subjects.gaeilge",
        ],
    },
    "ducklake_crypteolas": {
        "postgres_schema": "ducklake_crypteolas",
        "s3_prefix": "s3://ducklake-crypteolas/",
        "tables": [
            "chain.ethereum_blocks",
            "chain.ethereum_transactions",
        ],
    },
    "ducklake_tertiary": {
        "postgres_schema": "ducklake_tertiary",
        "s3_prefix": "s3://ducklake-tertiary/",
        "tables": [
            "uoq.exam_papers",
            "uog.official_docs",
        ],
    },
    "ducklake_uog": {
        "postgres_schema": "ducklake_uog",
        "s3_prefix": "s3://ducklake-uog/",
        "tables": [
            "personal_archive.assignments",
            "personal_archive.notes",
        ],
    },
    "ducklake_cie": {
        "postgres_schema": "ducklake_cie",
        "s3_prefix": "s3://ducklake-cie/",
        "tables": [
            "official_docs.modules",
            "students_union.events",
        ],
    },
}

CONSOLIDATED_NAMESPACE = "ducklake_cianfhoghlaim"
CONSOLIDATED_S3_PREFIX = "s3://ducklake-cianfhoghlaim/"


def generate_migration_sql() -> str:
    """Generate the SQL migration script for the 6 → 1 namespace consolidation."""
    lines = [
        "-- Wave 4 namespace consolidation migration",
        f"-- Generated: {datetime.utcnow().isoformat()}Z",
        f"-- Consolidated namespace: {CONSOLIDATED_NAMESPACE}",
        f"-- Consolidated S3 prefix: {CONSOLIDATED_S3_PREFIX}",
        "",
        "-- Step 1: Attach the consolidated DuckLake",
        f"ATTACH 'ducklake:postgres://loader:pass@lakehouse-postgres:5433/dlt_data' AS {CONSOLIDATED_NAMESPACE} (DATA_PATH '{CONSOLIDATED_S3_PREFIX}');",
        "",
        "-- Step 2: For each legacy namespace, ATTACH + COPY all tables into the consolidated namespace",
        "",
    ]

    for legacy_ns, info in LEGACY_NAMESPACES.items():
        lines.append(f"-- ─── Migrate {legacy_ns} ───")
        lines.append(f"ATTACH 'ducklake:postgres://loader:pass@lakehouse-postgres:5433/{info['postgres_schema']}' AS {legacy_ns} (DATA_PATH '{info['s3_prefix']}');")
        for table in info["tables"]:
            lines.append(
                f"CREATE TABLE {CONSOLIDATED_NAMESPACE}.{table} AS SELECT * FROM {legacy_ns}.{table};"
            )
        lines.append(f"DETACH {legacy_ns};")
        lines.append("")

    lines.extend([
        "-- Step 3: Apply DuckLake 1.0 optimisations to the high-volume tables",
        "-- (per the SORTED_BY_TABLES + BUCKET_PARTITIONED_TABLES constants)",
        "",
        "ALTER TABLE leabharlann_books.leabharlann_books SET SORTED BY (subject, board, year, language);",
        "ALTER TABLE leabharlann_zotero.leabharlann_zotero SET SORTED BY (subject, board, year, language);",
        "ALTER TABLE leabharlann_takeout.leabharlann_takeout SET SORTED BY (subject, board, year, language);",
        "ALTER TABLE main.weekly_downloads SET PARTITIONED BY (bucket(1000, jurisdiction));",
        "ALTER TABLE main.language_distribution SET PARTITIONED BY (bucket(1000, jurisdiction));",
        "ALTER TABLE media_personal.apple_photos_chunks SET (data_inlining_row_limit = 100);",
        "",
        "-- Step 4: Drop the legacy Postgres schemas",
        "DROP SCHEMA IF EXISTS ducklake_oideachais CASCADE;",
        "DROP SCHEMA IF EXISTS ducklake_educational CASCADE;",
        "DROP SCHEMA IF EXISTS ducklake_crypteolas CASCADE;",
        "DROP SCHEMA IF EXISTS ducklake_tertiary CASCADE;",
        "DROP SCHEMA IF EXISTS ducklake_uog CASCADE;",
        "DROP SCHEMA IF EXISTS ducklake_cie CASCADE;",
    ])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Print the generated SQL to stdout (default)")
    parser.add_argument("--apply", action="store_true",
                        help="Write the generated SQL to stedding/sync-reports/")
    args = parser.parse_args()

    sql = generate_migration_sql()

    if args.apply:
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        out = REPORT_DIR / f"wave-4-namespace-consolidation-{datetime.utcnow().strftime('%Y-%m-%d')}.sql"
        out.write_text(sql)
        print(f"OK: wrote {out}")
        print(f"     {len(sql.splitlines())} lines, {len(sql)} chars")
        print()
        print("REVIEW THE SQL CAREFULLY before running it manually.")
        print("This script intentionally does NOT execute the migration.")
        return 0

    # Default: dry-run to stdout
    print(sql)
    return 0


if __name__ == "__main__":
    sys.exit(main())
