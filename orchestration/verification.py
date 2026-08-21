"""Store-backed verification helpers for Dagster asset checks.

THE RULE THIS EXISTS TO ENFORCE
-------------------------------
**An asset check queries the destination. It never asserts against the
upstream asset's return value.**

The repo's defining failure mode was a closed loop: an asset returned a
hardcoded number, its paired check asserted against that same number and
passed, and the documentation then cited the passing check as evidence. Live
examples this module replaces:

  * `generic_england_assets.py` returned `{"rows_a_level": 147}` regardless of
    what dlt actually loaded, and `england_a_level_documents_ingested_check`
    asserted `rows_a_level >= 147`.
  * `england_extractions` set `ragas_scores[slug] = 0.85  # placeholder` and
    the RAGAS check averaged those placeholders against a 0.70 threshold.
  * `generic_ireland_assets.py` shipped the comment "In a real implementation,
    we would query LanceDB for the actual count ... For now, we use the
    expected count."

UNVERIFIABLE IS NOT PASSING
---------------------------
Every helper here returns `None` when the store cannot be reached or the table
does not exist, and every caller must treat `None` as a FAILED check with the
reason attached. A check that cannot see the data has not verified anything;
reporting success in that case is the bug, not a convenience.
"""

from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


def _connect() -> Any | None:
    """Open a read connection to whichever destination is actually in use.

    Mirrors `dlt_sources.common.destinations_cianfhoghlaim.get_dlt_destination`'s
    tier decision so a check reads the same store the pipeline wrote to:
    DuckLake (Garage S3 + Postgres catalog) when it is reachable, else the
    local DuckDB file. Returns `None` if neither can be opened.
    """
    import duckdb

    namespace = os.environ.get("CIANFHOGHLAIM_NAMESPACE", "cianfhoghlaim")
    use_ducklake = os.environ.get("USE_DUCKLAKE", "true").lower() == "true"

    if use_ducklake:
        try:
            from dlt_sources.common.destinations_cianfhoghlaim import (
                _verify_ducklake_connectivity,
            )

            env = os.environ.get("DLT_ENVIRONMENT", "local").lower()
            if _verify_ducklake_connectivity(env):
                con = duckdb.connect(":memory:")
                con.execute("INSTALL ducklake; LOAD ducklake;")
                con.execute("INSTALL httpfs; LOAD httpfs;")
                key = os.environ.get("AWS_ACCESS_KEY_ID", "")
                secret = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
                endpoint = os.environ.get(
                    "AWS_ENDPOINT_URL", "http://localhost:3900"
                ).replace("http://", "").replace("https://", "")
                con.execute(
                    f"CREATE SECRET verify_s3 (TYPE S3, PROVIDER config, "
                    f"KEY_ID '{key}', SECRET '{secret}', REGION 'garage', "
                    f"ENDPOINT '{endpoint}', USE_SSL false, URL_STYLE 'path')"
                )
                pg_host = os.environ.get("DUCKLAKE_POSTGRES_HOST", "localhost")
                pg_port = os.environ.get("DUCKLAKE_POSTGRES_PORT", "5433")
                pg_db = os.environ.get(
                    "DUCKLAKE_POSTGRES_DB", f"ducklake_{namespace}"
                )
                pg_user = os.environ.get("DUCKLAKE_POSTGRES_USER") or os.environ.get(
                    "POSTGRES_USER", "lakekeeper"
                )
                # Credentials come from PGUSER/PGPASSWORD rather than the
                # connection string — see the note in mise.toml about the
                # password echoing back via `SHOW DATABASES`.
                os.environ.setdefault("PGUSER", pg_user)
                bucket = os.environ.get("DUCKLAKE_BUCKET", "ducklake")
                con.execute(
                    f"ATTACH 'ducklake:postgres:dbname={pg_db} host={pg_host} "
                    f"port={pg_port} user={pg_user}' AS {namespace} "
                    f"(DATA_PATH 's3://{bucket}/{namespace}/', READ_ONLY)"
                )
                return con
        except Exception as exc:  # noqa: BLE001
            logger.warning("verification_ducklake_connect_failed: %s", exc)

    # DuckDB fallback — the same path `get_duckdb_fallback_destination` writes.
    path = f"./data/{namespace}.duckdb"
    if not os.path.exists(path):
        logger.warning("verification_duckdb_missing path=%s", path)
        return None
    try:
        return duckdb.connect(path, read_only=True)
    except Exception as exc:  # noqa: BLE001
        logger.warning("verification_duckdb_connect_failed: %s", exc)
        return None


def count_rows(table: str, where: str | None = None) -> int | None:
    """Return the real row count for `table`, or `None` if unverifiable.

    `table` is `schema.table` (e.g. `"education.subjects"`). When the
    connection is DuckLake, the ATTACH alias (the namespace) is prepended
    automatically, since DuckLake tables are addressed as
    `<namespace>.<schema>.<table>`.

    `None` means the store was unreachable or the table does not exist — the
    caller MUST fail the check in that case rather than assume zero or pass.
    """
    con = _connect()
    if con is None:
        return None
    namespace = os.environ.get("CIANFHOGHLAIM_NAMESPACE", "cianfhoghlaim")
    if table.count(".") == 1:
        # Try the namespace-qualified form first; fall back to the bare form
        # for the plain-DuckDB tier, where there is no catalog alias.
        candidates = [f"{namespace}.{table}", table]
    else:
        candidates = [table]
    try:
        last_exc: Exception | None = None
        for candidate in candidates:
            try:
                sql = f"SELECT count(*) FROM {candidate}"  # noqa: S608
                if where:
                    sql += f" WHERE {where}"
                row = con.execute(sql).fetchone()
                return int(row[0]) if row else 0
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
        logger.warning(
            "verification_count_failed table=%s tried=%s err=%s",
            table, candidates, last_exc,
        )
        return None
    finally:
        try:
            con.close()
        except Exception:  # noqa: BLE001, S110
            pass


def count_lance_rows(dataset_name: str) -> int | None:
    """Return the real row count of a local Lance dataset, or `None`.

    Reads `storage/data/lancedb/<dataset_name>.lance` — the path
    `scripts/export_cohorts_to_lance.py` writes.
    """
    import pathlib

    root = pathlib.Path(
        os.environ.get("LANCEDB_PATH", "storage/data/lancedb")
    )
    path = root / f"{dataset_name}.lance"
    if not path.exists():
        # Also accept the un-suffixed directory form.
        path = root / dataset_name
        if not path.exists():
            logger.warning("verification_lance_missing path=%s", path)
            return None
    # NOTE: the `lance` module (pylance) is NOT installed in this venv — only
    # `lancedb` is. `scripts/export_cohorts_to_lance.py` does a bare
    # `import lance`, so it cannot run here either; that is a real missing
    # dependency, not a bug in this helper. Try `lance` first, then fall back
    # to reading the dataset through `lancedb`, which is present.
    try:
        import lance

        return int(lance.dataset(str(path)).count_rows())
    except ImportError:
        pass
    except Exception as exc:  # noqa: BLE001
        logger.warning("verification_lance_failed path=%s err=%s", path, exc)
        return None

    try:
        import lancedb

        db = lancedb.connect(str(path.parent))
        return int(db.open_table(path.name.removesuffix(".lance")).count_rows())
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "verification_lance_failed path=%s err=%s (neither `lance` nor "
            "`lancedb` could read it; `lance`/pylance is not installed)",
            path, exc,
        )
        return None


def unverifiable(reason: str, **extra: Any) -> dict[str, Any]:
    """Standard metadata payload for a check that could not reach the store."""
    payload: dict[str, Any] = {
        "verified": False,
        "reason": reason,
        "rule": (
            "an asset check must query the destination; it may not assert "
            "against the upstream asset's return value"
        ),
    }
    payload.update(extra)
    return payload


__all__ = ["count_lance_rows", "count_rows", "unverifiable"]
