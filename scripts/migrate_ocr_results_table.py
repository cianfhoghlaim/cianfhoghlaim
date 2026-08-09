"""Migrate the canonical `md:cianfhoghlaim.ocr_results` table (per the 2026-08-10-ocr-vision-activation-v1 openspec change).

The `ocr_results` table is the canonical BIEP v2 4-path ensemble output
sink — one row per path per PDF (4 rows per PDF).

Schema:
    document_id   VARCHAR PRIMARY KEY
    content_hash  VARCHAR NOT NULL
    model_used    VARCHAR NOT NULL    (baml | unstract | qwen3_vl | gemma4)
    confidence    DOUBLE  NOT NULL
    raw_text      TEXT    NOT NULL
    latency_ms    INTEGER NOT NULL
    success       BOOLEAN NOT NULL
    created_at    TIMESTAMP NOT NULL DEFAULT now()

Usage:
    uv run python scripts/migrate_ocr_results_table.py
"""
from __future__ import annotations

import sys


def main() -> int:
    """Create the `cianfhoghlaim.cianfhoghlaim.ocr_results` table if missing."""
    try:
        import duckdb  # type: ignore[import-not-found]
    except ImportError:
        print("ERROR: duckdb not installed", file=sys.stderr)
        return 1

    try:
        con = duckdb.connect("md:cianfhoghlaim")
    except Exception as e:
        print(f"ERROR: cannot connect to md:cianfhoghlaim: {e}", file=sys.stderr)
        return 1

    # MotherDuck has both a database AND a schema named `cianfhoghlaim`
    try:
        con.execute("CREATE SCHEMA IF NOT EXISTS cianfhoghlaim.cianfhoghlaim")
    except Exception:
        pass

    con.execute(
        """
        CREATE TABLE IF NOT EXISTS cianfhoghlaim.cianfhoghlaim.ocr_results (
            document_id   VARCHAR PRIMARY KEY,
            content_hash  VARCHAR NOT NULL,
            model_used    VARCHAR NOT NULL,
            confidence    DOUBLE  NOT NULL,
            raw_text      TEXT    NOT NULL,
            latency_ms    INTEGER NOT NULL,
            success       BOOLEAN NOT NULL,
            created_at    TIMESTAMP NOT NULL DEFAULT now()
        )
        """
    )

    count = con.execute(
        "SELECT COUNT(*) FROM cianfhoghlaim.cianfhoghlaim.ocr_results"
    ).fetchone()[0]
    print(f"OK: cianfhoghlaim.cianfhoghlaim.ocr_results created (existing rows: {count})")
    con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
