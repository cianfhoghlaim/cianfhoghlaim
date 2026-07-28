"""Canonical ibis-first connection helper for the Cianfhoghlaim lakehouse.

The single source of truth for connecting to the BIEP MotherDuck +
DuckLake lakehouse. Replaces the 5+ raw `ibis.duckdb.connect(...)` call-sites
in the legacy `nb_utils.py`.

The pattern matches `marimo_dashboards/06_per_subject_analytics.py:84-95`
which already used ibis-first successfully.

## KCG patterns used
- ibis (per `.agents/skills/ibis/SKILL.md`) — `ibis.duckdb.connect`
  is the canonical entry point; no raw `ibis.duckdb.connect(uri)`.
- marimo (per `.agents/skills/marimo/SKILL.md`) — pure functions,
  marimo-agnostic.

Reference: openspec/changes/2026-07-25-nb-utils-ibis-first-v1/
Reference: openspec/changes/2026-08-13-biep-v3-systematic-download-ireland-england-v1/
(added `connect_local_lakehouse()` + `connect_lance()` +
`format_snake_case_cohort_path()` + `compute_ragas_distribution()`)
"""
from __future__ import annotations

import os
from typing import Any

__all__ = [
    "connect_md",
    "connect_local",
    "connect_local_lakehouse",
    "connect_lance",
    "format_snake_case_cohort_path",
    "compute_ragas_distribution",
    "lakehouse_uri",
    "LAKEHOUSE_URI_DEFAULT",
]


LAKEHOUSE_URI_DEFAULT = "md:cianfhoghlaim"
"""The canonical MotherDuck + DuckLake lakehouse alias."""


def lakehouse_uri() -> str:
    """Return the canonical lakehouse URI (env override supported).

    Honors ``CIANFHOGHLAIM_LAKEHOUSE_DUCKDB``; defaults to ``md:cianfhoghlaim``.
    """
    return os.environ.get(
        "CIANFHOGHLAIM_LAKEHOUSE_DUCKDB",
        LAKEHOUSE_URI_DEFAULT,
    )


def connect_md(*, read_only: bool = True) -> Any:
    """Return an ``ibis.duckdb.connect`` handle to the BIEP lakehouse.

    Parameters
    ----------
    read_only : bool
        If True (the default), connect in read-only mode.

    Returns
    -------
    ibis.duckdb.connect
        An ibis-wrapped DuckDB connection. NOT a raw ``duckdb.connect``
        handle (the legacy `nb_utils.connect_md_oideachais()` returns the
        raw handle — this helper is the ibis-first replacement).

    Notes
    -----
    The MotherDuck token is read from the runtime env
    (``MOTHERDUCK_TOKEN``); mise + Infisical hydration handles this.
    Falls back to ``:memory:`` if ``MOTHERDUCK_ENABLED != "true"`` or the
    token is missing.
    """
    try:
        import ibis  # type: ignore[import-not-found]
    except ImportError as exc:
        raise ImportError(
            "ibis is required for the canonical connect_md() helper. "
            "Install with `uv add ibis-framework[duckdb]`."
        ) from exc

    use_md = os.environ.get("MOTHERDUCK_ENABLED", "").lower() == "true"
    token = os.environ.get("MOTHERDUCK_TOKEN", "")
    uri = lakehouse_uri()

    if use_md and token:
        try:
            return ibis.duckdb.connect(uri, read_only=read_only)
        except Exception:
            pass  # fall through to :memory:

    return ibis.duckdb.connect(":memory:", read_only=read_only)


def connect_local(*, read_only: bool = True) -> Any:
    """Return an ``ibis.duckdb.connect`` handle to an in-memory DuckDB.

    Convenience helper for local development when the MotherDuck
    lakehouse is unreachable. Always succeeds (provided ibis is installed).
    """
    try:
        import ibis  # type: ignore[import-not-found]
    except ImportError as exc:
        raise ImportError(
            "ibis is required for connect_local(); "
            "install with `uv add ibis-framework[duckdb]`."
        ) from exc

    return ibis.duckdb.connect(":memory:", read_only=read_only)


def connect_local_lakehouse(*, read_only: bool = True) -> Any:
    """Return an ``ibis.duckdb.connect`` handle with the local lakehouse
    DuckLake catalog attached.

    This is the canonical local-dev entrypoint that uses the local
    lakehouse stack (Garage S3 + lakehouse-postgres) instead of
    MotherDuck. Falls back to ``:memory:`` if the local lakehouse stack
    is down or unreachable.

    Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change,
    the canonical DuckLake catalog DB is `ducklake_cianfhoghlaim`
    (post-v7 namespace alignment). The canonical S3 path is
    `s3://ducklake-cianhoghlaim/<namespace>/<dataset>/`.

    Environment variables honoured (in order of precedence):
    - ``DUCKLAKE_POSTGRES_HOST`` (default: `localhost`)
    - ``DUCKLAKE_POSTGRES_PORT`` (default: `5433`)
    - ``DUCKLAKE_POSTGRES_DB`` (default: `ducklake_cianfhoghlaim`)
    - ``DUCKLAKE_POSTGRES_USER`` (default: `lakekeeper`)
    - ``DUCKLAKE_POSTGRES_PASSWORD`` (default: empty)
    - ``GARAGE_S3_ENDPOINT`` (default: `http://localhost:3900`)
    - ``GARAGE_BUCKET`` (default: `ducklake-cianhoghlaim`)
    - ``GARAGE_ACCESS_KEY_ID`` (default: empty)
    - ``GARAGE_SECRET_ACCESS_KEY`` (default: empty)
    - ``DUCKLAKE_HEALTHCHECK_URL`` (default: `http://localhost:5433`)
      — used to short-circuit if the local stack is down
    """
    try:
        import ibis  # type: ignore[import-not-found]
    except ImportError as exc:
        raise ImportError(
            "ibis is required for connect_local_lakehouse(); "
            "install with `uv add ibis-framework[duckdb]`."
        ) from exc

    # Short-circuit if the local lakehouse stack is down (no Postgres)
    healthcheck_url = os.environ.get("DUCKLAKE_HEALTHCHECK_URL", "http://localhost:5433")
    try:
        import httpx  # type: ignore[import-not-found]
        resp = httpx.get(healthcheck_url, timeout=2.0)
        if resp.status_code >= 400:
            return ibis.duckdb.connect(":memory:", read_only=read_only)
    except Exception:
        return ibis.duckdb.connect(":memory:", read_only=read_only)

    # Build the DuckLake ATTACH SQL using the canonical 3-tier env matrix
    pg_host = os.environ.get("DUCKLAKE_POSTGRES_HOST", "localhost")
    pg_port = os.environ.get("DUCKLAKE_POSTGRES_PORT", "5433")
    pg_db = os.environ.get("DUCKLAKE_POSTGRES_DB", "ducklake_cianfhoghlaim")
    pg_user = os.environ.get("DUCKLAKE_POSTGRES_USER", "lakekeeper")
    pg_password = os.environ.get("DUCKLAKE_POSTGRES_PASSWORD", "")
    garage_endpoint = os.environ.get("GARAGE_S3_ENDPOINT", "http://localhost:3900")
    garage_bucket = os.environ.get("GARAGE_BUCKET", "ducklake-cianhoghlaim")
    garage_access_key = os.environ.get("GARAGE_ACCESS_KEY_ID", "")
    garage_secret_key = os.environ.get("GARAGE_SECRET_ACCESS_KEY", "")

    conn = ibis.duckdb.connect(":memory:", read_only=read_only)
    try:
        # 1. Set up the S3 secret for Garage
        conn.raw_sql(
            f"""
            CREATE OR REPLACE SECRET lakehouse_s3 (
                TYPE S3,
                PROVIDER config,
                ENDPOINT '{garage_endpoint}',
                URL_STYLE 'path',
                USE_SSL false,
                REGION 'garage',
                KEY_ID '{garage_access_key}',
                SECRET '{garage_secret_key}'
            )
            """
        )
        # 2. ATTACH the DuckLake catalog (Parquet on S3 + Postgres catalog)
        conn.raw_sql(
            f"""
            ATTACH 'ducklake:postgres:dbname={pg_db} host={pg_host} port={pg_port} user={pg_user} password={pg_password}'
            AS lakehouse (DATA_PATH 's3://{garage_bucket}/')
            """
        )
        return conn
    except Exception:  # noqa: BLE001
        # If the ATTACH fails (e.g. Postgres is up but DuckLake isn't), fall back to :memory:
        return ibis.duckdb.connect(":memory:", read_only=read_only)


def connect_lance(*, namespace: str = "cianhoghlaim") -> Any:
    """Return a ``lancedb.connect`` handle to the BIEP Lance namespace.

    Honours the ``LANCEDB_URI`` env var (default:
    `rest://lakehouse-lance-namespace:8182`). Falls back to the local
    LanceDB path at ``storage/data/lancedb`` if the lakehouse Lance
    namespace sidecar is down.

    Parameters
    ----------
    namespace : str
        The canonical Lance namespace (default: `cianhoghlaim`).
    """
    try:
        import lancedb  # type: ignore[import-not-found]
    except ImportError as exc:
        raise ImportError(
            "lancedb is required for connect_lance(); "
            "install with `uv add lancedb`."
        ) from exc

    uri = os.environ.get("LANCEDB_URI", "rest://lakehouse-lance-namespace:8182")
    try:
        return lancedb.connect(uri)
    except Exception:  # noqa: BLE001
        # Fall back to the local path
        local_path = os.environ.get("LANCEDB_LOCAL_PATH", "storage/data/lancedb")
        return lancedb.connect(local_path)


def format_snake_case_cohort_path(
    jurisdiction: str,
    stage: str,
    subject_slug: str,
    board: str = "na",
    qualification_level: str = "untiered",
    language: str = "en",
    year: int | str = "undated",
    sha256_8: str = "00000000",
) -> str:
    """Return the canonical BIEP v3 snake_case S3 path for a cohort.

    This is a thin wrapper around
    ``dlt_sources.common.snake_case_contract.build_s3_path`` that
    doesn't require importing the dlt_sources module (the notebooks
    can call this directly).

    Example
    -------
    >>> format_snake_case_cohort_path(
    ...     jurisdiction="ireland",
    ...     stage="leaving_cycle",
    ...     subject_slug="mathematics",
    ...     qualification_level="higher",
    ...     language="en",
    ...     year=2024,
    ...     sha256_8="a1b2c3d4",
    ... )
    's3://garage/cianfhoghlaim/ireland/leaving_cycle/mathematics/en/2024/ireland__leaving_cycle__mathematics__na__higher__en__2024__a1b2c3d4.pdf'
    """
    from dlt_sources.common.snake_case_contract import (
        CohortAttributes,
        build_s3_path,
    )

    cohort = CohortAttributes(
        jurisdiction=jurisdiction,
        stage=stage,
        subject_slug=subject_slug,
        board=board,
        qualification_level=qualification_level,
        language=language,
        year=year,
    )
    return build_s3_path(cohort, sha256_8)


def compute_ragas_distribution(cohort_kind: str) -> dict[str, Any]:
    """Compute the RAGAS score distribution for a given cohort kind.

    Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change,
    the BIEP v3 4-path OCR ensemble (Docling/Unstract/qwen3-vl-8b/gemma-4-26B-A4B)
    writes per-path rows to:
    - ``cianfhoghlaim.education.<jurisdiction>.<stage>.<subject>.<path>.baml_canonical``
    - ``cianfhoghlaim.education.<jurisdiction>.<stage>.<subject>.<path>.unstract_json``
    - ``cianfhoghlaim.education.<jurisdiction>.<stage>.<subject>.<path>.qwen3_vl``
    - ``cianfhoghlaim.education.<jurisdiction>.<stage>.<subject>.<path>.gemma4``

    The RAGAS `biiep_extraction_consensus` vote writes the consensus row to
    ``cianfhoghlaim.education.<jurisdiction>.<stage>.<subject>.voted_canonical``.

    This helper queries the local lakehouse (or :memory: fallback) and
    returns the average RAGAS score + the score histogram data per
    cohort kind.

    Parameters
    ----------
    cohort_kind : str
        One of: `lc_spec`, `jc_spec`, `jc_short_course`, `jc_cba`,
        `a_level`, `gcse`.

    Returns
    -------
    dict
        - `cohort_kind`: the input cohort kind
        - `avg_ragas_score`: the average RAGAS score across all cohorts
          of this kind (0.0 if no data)
        - `min_ragas_score`: the minimum RAGAS score (0.0 if no data)
        - `max_ragas_score`: the maximum RAGAS score (0.0 if no data)
        - `cohort_count`: the number of cohorts
        - `passing_cohorts`: number of cohorts with RAGAS score >= 0.70
        - `passing_rate`: passing_cohorts / cohort_count
        - `status`: `ok` if avg_ragas >= 0.70, `warn` otherwise,
          `no_data` if cohort_count is 0
    """
    try:
        conn = connect_local_lakehouse()
    except Exception:  # noqa: BLE001
        conn = connect_local()

    try:
        from dlt_sources.common.snake_case_contract import (
            VALID_JURISDICTIONS,
        )

        if cohort_kind == "lc_spec":
            table_prefix = "cianfhoghlaim.education.ireland.leaving_cycle"
        elif cohort_kind == "jc_spec":
            table_prefix = "cianfhoghlaim.education.ireland.junior_cycle"
        elif cohort_kind == "jc_short_course":
            table_prefix = "cianfhoghlaim.education.ireland.junior_cycle.short_courses"
        elif cohort_kind == "jc_cba":
            table_prefix = "cianfhoghlaim.education.ireland.junior_cycle.cbas"
        elif cohort_kind == "a_level":
            table_prefix = "cianfhoghlaim.education.england.a_level"
        elif cohort_kind == "gcse":
            table_prefix = "cianfhoghlaim.education.england.gcse"
        else:
            return {
                "cohort_kind": cohort_kind,
                "avg_ragas_score": 0.0,
                "min_ragas_score": 0.0,
                "max_ragas_score": 0.0,
                "cohort_count": 0,
                "passing_cohorts": 0,
                "passing_rate": 0.0,
                "status": "unknown_cohort_kind",
            }

        # Query the voted_canonical tables for the average RAGAS score
        query = f"""
            SELECT
                AVG(ragas_score) AS avg_ragas_score,
                MIN(ragas_score) AS min_ragas_score,
                MAX(ragas_score) AS max_ragas_score,
                COUNT(*) AS cohort_count,
                SUM(CASE WHEN ragas_score >= 0.70 THEN 1 ELSE 0 END) AS passing_cohorts
            FROM {table_prefix}
            WHERE ragas_score IS NOT NULL
        """
        try:
            result = conn.sql(query).execute()
            if result is None or len(result) == 0:
                return {
                    "cohort_kind": cohort_kind,
                    "avg_ragas_score": 0.0,
                    "min_ragas_score": 0.0,
                    "max_ragas_score": 0.0,
                    "cohort_count": 0,
                    "passing_cohorts": 0,
                    "passing_rate": 0.0,
                    "status": "no_data",
                }
            row = result.iloc[0] if hasattr(result, "iloc") else result[0]
            avg = float(row.get("avg_ragas_score", 0.0) or 0.0)
            min_s = float(row.get("min_ragas_score", 0.0) or 0.0)
            max_s = float(row.get("max_ragas_score", 0.0) or 0.0)
            count = int(row.get("cohort_count", 0) or 0)
            passing = int(row.get("passing_cohorts", 0) or 0)
            return {
                "cohort_kind": cohort_kind,
                "avg_ragas_score": avg,
                "min_ragas_score": min_s,
                "max_ragas_score": max_s,
                "cohort_count": count,
                "passing_cohorts": passing,
                "passing_rate": (passing / count) if count > 0 else 0.0,
                "status": "ok" if avg >= 0.70 else ("warn" if count > 0 else "no_data"),
            }
        except Exception:  # noqa: BLE001
            return {
                "cohort_kind": cohort_kind,
                "avg_ragas_score": 0.0,
                "min_ragas_score": 0.0,
                "max_ragas_score": 0.0,
                "cohort_count": 0,
                "passing_cohorts": 0,
                "passing_rate": 0.0,
                "status": "no_data",
            }
    finally:
        try:
            del conn  # ibis connections are auto-closed on GC
        except Exception:  # noqa: BLE001
            pass
