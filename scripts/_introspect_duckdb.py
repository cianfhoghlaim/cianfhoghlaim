"""
scripts/_introspect_duckdb.py

Introspect a DuckDB / DuckLake / MotherDuck database and emit its table
schemas as JSON on stdout.

Why this exists as a Python script rather than the Node.js `duckdb`
package: the Node.js native bindings for `duckdb` are known-unreliable
under bun (see `web/hono-api/src/data/duckdb.ts`'s own comment: "Local
bun dev returns empty arrays; Docker container gets real data"). The
Python `duckdb` package is already a pinned repo dependency
(`pyproject.toml`: `duckdb>=1.5.4,<1.6.0`) and works identically for
local files and MotherDuck ATTACH. `scripts/schema-generate.ts` shells
out to this script instead of importing a native Node module.

Usage:
    uv run python3 scripts/_introspect_duckdb.py --db data/oideachais.duckdb
    uv run python3 scripts/_introspect_duckdb.py --motherduck md:oideachais --token "$MOTHERDUCK_TOKEN"
    uv run python3 scripts/_introspect_duckdb.py --db data/oideachais.duckdb --schema leaving_cert

Output (stdout, JSON):
    {
      "source": "data/oideachais.duckdb",
      "tables": [
        {
          "database": "oideachais",
          "schema": "examinations",
          "table": "all_exam_materials",
          "columns": [
            {"column_name": "...", "column_type": "VARCHAR", "is_nullable": "YES", "comment": null},
            ...
          ]
        },
        ...
      ]
    }

Excludes dlt internal bookkeeping tables (`_dlt_loads`, `_dlt_version`,
`_dlt_pipeline_state`) and the `information_schema`/`pg_catalog`
system schemas by default (use `--include-dlt-tables` / `--include-system-schemas`
to keep them).
"""

from __future__ import annotations

import argparse
import json
import sys

import duckdb

SYSTEM_SCHEMAS = {"information_schema", "pg_catalog"}
DLT_TABLE_PREFIXES = ("_dlt_",)
# dlt writes a transient `<dataset>_staging` schema during load-then-swap.
# Staging tables share table names with their production counterpart
# (e.g. `examinations.all_exam_materials` + `examinations_staging.all_exam_materials`),
# which collides when the caller derives one TS identifier per table name.
# They're also not meant to be read by consumers. Excluded by default.
DLT_STAGING_SCHEMA_SUFFIX = "_staging"


def introspect(
    db_path: str | None,
    motherduck_uri: str | None,
    token: str | None,
    schema_filter: str | None,
    include_dlt_tables: bool,
    include_system_schemas: bool,
    include_staging_schemas: bool = False,
) -> dict:
    if motherduck_uri:
        con = duckdb.connect(":memory:", read_only=False)
        if token:
            con.execute(f"SET motherduck_token='{token}'")
        con.execute(f"ATTACH '{motherduck_uri}' AS md (TYPE motherduck)")
        db_alias = "md"
        source = motherduck_uri
    else:
        if not db_path:
            raise SystemExit("Either --db or --motherduck is required")
        con = duckdb.connect(db_path, read_only=True)
        db_alias = None
        source = db_path

    query = """
        SELECT table_catalog, table_schema, table_name
        FROM information_schema.tables
        ORDER BY table_schema, table_name
    """
    rows = con.execute(query).fetchall()

    tables: list[dict] = []
    for catalog, schema, name in rows:
        if not include_system_schemas and schema in SYSTEM_SCHEMAS:
            continue
        if not include_staging_schemas and schema.endswith(DLT_STAGING_SCHEMA_SUFFIX):
            continue
        if schema_filter and schema != schema_filter:
            continue
        if not include_dlt_tables and name.startswith(DLT_TABLE_PREFIXES):
            continue

        parts = [db_alias, schema, name] if db_alias else [schema, name]
        qualified = ".".join(f'"{p}"' for p in parts)
        try:
            cols = con.execute(f"DESCRIBE {qualified}").fetchall()
        except duckdb.Error as exc:
            # DESCRIBE can fail on views over missing upstream tables etc.
            # Don't let one broken table kill the whole introspection.
            print(f"[warn] DESCRIBE failed for {qualified}: {exc}", file=sys.stderr)
            continue

        columns = []
        for col_name, col_type, null, *_rest in cols:
            columns.append(
                {
                    "column_name": col_name,
                    "column_type": col_type,
                    "is_nullable": "YES" if str(null).upper() in ("YES", "TRUE") else "NO",
                    "comment": None,
                }
            )
        tables.append(
            {
                "database": catalog,
                "schema": schema,
                "table": name,
                "columns": columns,
            }
        )

    con.close()
    return {"source": source, "tables": tables}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", help="Path to a local .duckdb file (read-only)")
    ap.add_argument("--motherduck", help="MotherDuck URI, e.g. md:oideachais")
    ap.add_argument("--token", help="MotherDuck token (else reads MOTHERDUCK_TOKEN env)")
    ap.add_argument("--schema", help="Only include tables in this schema")
    ap.add_argument("--include-dlt-tables", action="store_true")
    ap.add_argument("--include-system-schemas", action="store_true")
    ap.add_argument(
        "--include-staging-schemas",
        action="store_true",
        help="Include dlt's transient <dataset>_staging schemas (excluded by default — "
        "they duplicate production table names and are not meant to be read)",
    )
    args = ap.parse_args()

    import os

    token = args.token or os.environ.get("MOTHERDUCK_TOKEN")

    try:
        result = introspect(
            db_path=args.db,
            motherduck_uri=args.motherduck,
            token=token,
            schema_filter=args.schema,
            include_dlt_tables=args.include_dlt_tables,
            include_system_schemas=args.include_system_schemas,
            include_staging_schemas=args.include_staging_schemas,
        )
    except duckdb.Error as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1

    print(json.dumps(result, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
