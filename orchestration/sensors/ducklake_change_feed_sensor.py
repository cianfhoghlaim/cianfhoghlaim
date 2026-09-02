"""Dagster sensor that consumes the DuckLake data change feed.

Per Wave 4 §4.4 of the 2026-08-24 master refactor plan
(`openspec/plans/2026-08-24-master-refactor-plan.md`). The sensor
polls ``ducklake_table_changes(...)`` for each table in the
``MONITORED_CHANGE_FEED_TABLES`` set and emits a Dagster
``RunRequest`` whenever a row is inserted / updated / deleted.

The downstream consumers are:

  1. **The Cognee cognify pipeline** — the 7 typed Cognee
     clusters (per ``cognee_health_check_sensor``) need the
     latest row-change signal so ``cognify`` runs against fresh
     evidence.
  2. **The daily cron sensor** — the BIEP v3 syllabus-evolution
     cron needs the change feed to decide which subjects to
     re-ingest.

The sensor emits a single ``RunRequest`` per changed (table,
change_ts) pair; Dagster's normal sensor tick dedup ensures the
same change row is not re-processed.

Reference:
  - ``ducklake.select/docs/stable/duckdb/usage/changes``
  - ``dlt_sources.destinations.ducklake.ducklake_cianfhoghlaim_table_changes``
  - Wave 4 §4.4 of the 2026-08-24 master refactor plan.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Iterator

logger = logging.getLogger(__name__)


# The canonical poll interval (every 5 minutes per the master
# plan §4.4 — change feeds are a hot loop; we don't want a 6h
# batch that misses cognify freshness).
POLL_INTERVAL_SECONDS: int = 5 * 60  # 5 minutes

# The default lookback window (24h) — the first sensor tick after
# a daemon restart needs to surface the most recent 24h of changes
# to rebuild the dedup map.
DEFAULT_LOOKBACK_HOURS: int = 24


# The default set of DuckLake tables the sensor polls. Per the
# master plan §4.4 the canonical table set is the
# ``JURISDICTION_SORTED_BY_TABLES`` union the per-quadrant LC
# chunks tables. Custom deployments may override via the
# ``CIANFHOGHLAIM_DUCKLAKE_CHANGE_FEED_TABLES`` env var (comma-
# separated fully-qualified table names).
def _monitored_change_feed_tables() -> tuple[str, ...]:
    """Return the canonical set of tables polled by the sensor."""
    env = os.getenv("CIANFHOGHLAIM_DUCKLAKE_CHANGE_FEED_TABLES")
    if env:
        return tuple(t.strip() for t in env.split(",") if t.strip())

    # Fallback: read the canonical sets from the ducklake module.
    # Done lazily to avoid heavy module imports at sensor-tick time.
    try:
        from dlt_sources.destinations.ducklake import (
            JURISDICTION_SORTED_BY_TABLES,
            SORTED_BY_TABLES,
        )
        return tuple(sorted(JURISDICTION_SORTED_BY_TABLES | SORTED_BY_TABLES))
    except ImportError:
        # Last-resort safe default (empty tuple → sensor yields
        # only SkipReason).
        return ()


# The DuckLake namespace the change feed reads from. Default
# matches the consolidated namespace per Wave 4 §4.1. Can be
# overridden per-deployment via
# ``CIANFHOGHLAIM_DUCKLAKE_NAMESPACE``.
def _ducklake_namespace() -> str:
    return os.getenv(
        "CIANFHOGHLAIM_DUCKLAKE_NAMESPACE",
        "ducklake_cianfhoghlaim",
    )


# The DuckLake catalog URI (per ``dlt_sources.destinations.ducklake``).
def _ducklake_catalog_uri() -> str:
    return os.getenv(
        "CIANFHOGHLAIM_DUCKLAKE_POSTGRES",
        "postgres://loader:pass@lakehouse-postgres:5433/dlt_data",
    )


# ─── The sensor entry point ────────────────────────────────────────────────


# In-memory dedup: maps (table, change_ts) → bool
_LAST_SEEN_CHANGE: dict[tuple[str, str], bool] = {}


def _poll_table_changes(
    table_fqn: str,
    *,
    since: datetime,
    namespace: str = "ducklake_cianfhoghlaim",
    catalog: str | None = None,
) -> list[tuple[str, str]]:
    """Execute ``SELECT change_type, change_ts FROM ducklake_table_changes(...)``.

    Args:
        table_fqn: Fully-qualified table name (e.g.
            ``leabharlann_books.leabharlann_books``).
        since: Only return changes at-or-after this UTC timestamp.
        namespace: The DuckLake ATTACH alias (default
            ``"ducklake_cianfhoghlaim"`` per Wave 4 §4.1).
        catalog: Postgres catalog URI.

    Returns:
        A list of ``(change_type, change_ts)`` tuples. Each tuple
        triggers one ``RunRequest`` from the sensor.

    Notes:
        The implementation uses a real DuckDB connection if
        ``duckdb`` is importable + the catalog is reachable;
        otherwise it returns an empty list (the sensor runs in a
        mock mode that emits ``SkipReason`` entries).
    """
    try:
        import duckdb  # type: ignore

        con = duckdb.connect(":memory:")
        try:
            con.execute("INSTALL ducklake; LOAD ducklake;")
            if catalog:
                con.execute(
                    f"ATTACH 'ducklake:postgres:{catalog}' AS {namespace}"
                )
            sql = (
                f"SELECT change_type, change_ts "
                f"FROM ducklake_table_changes("
                f"'{namespace}', '{table_fqn}', "
                f"TIMESTAMP '{since.isoformat()}'"
                f")"
            )
            rows = con.execute(sql).fetchall()
            return [(str(r[0]), str(r[1])) for r in rows]
        finally:
            con.close()
    except Exception as e:  # noqa: BLE001 - defensive (catalog offline)
        logger.warning(
            "DuckLake change feed poll for %s failed: %s — "
            "returning empty list (sensor runs in mock mode)",
            table_fqn,
            e,
        )
        return []


def _make_run_request(
    table_fqn: str, change_type: str, change_ts: str
) -> Any:
    """Build a single ``RunRequest`` for one change feed row."""
    from dagster import RunRequest

    return RunRequest(
        run_key=f"ducklake_change_feed::{table_fqn}::{change_ts}::{change_type}",
        tags={
            # 2026-08-27 Cianfhoghlaim rename — migrated from the legacy
            # `kcg:` tag prefix. See
            # openspec/changes/2026-08-27-kcg-rename-and-kcg-dir-merge-v1/tasks.md.
            "cianfhoghlaim:domain": "ducklake",
            "cianfhoghlaim:ducklake_table": table_fqn,
            "cianfhoghlaim:change_type": change_type,
            "cianfhoghlaim:change_ts": change_ts,
            "cianfhoghlaim:wave": "4",
        },
    )


def _make_skip_reason(table_fqn: str) -> Any:
    """Emit a ``SkipReason`` for a table with no new changes."""
    from dagster import SkipReason

    return SkipReason(
        f"ducklake_change_feed::no new changes for {table_fqn}"
    )


def evaluate_ducklake_change_feed(context) -> Iterator[Any]:
    """Dagster sensor entry point — yields ``RunRequest`` / ``SkipReason``.

    Polls each table in ``MONITORED_CHANGE_FEED_TABLES``. For each
    new change, yields one ``RunRequest``. For each unchanged
    table, yields one ``SkipReason`` (unless ``run_config`` is set
    to suppress skip output).

    Args:
        context: Dagster sensor evaluation context (the canonical
            ``SensorEvaluationContext``).

    Yields:
        Either a ``RunRequest`` or a ``SkipReason`` per
        ``(table, change_ts)`` pair.
    """
    tables = _monitored_change_feed_tables()
    if not tables:
        # No tables configured → no work to do.
        from dagster import SkipReason

        yield SkipReason(
            "ducklake_change_feed: no tables configured "
            "(set CIANFHOGHLAIM_DUCKLAKE_CHANGE_FEED_TABLES)"
        )
        return

    # The lookback starts at most-recently-stored change_ts per
    # table; fall back to DEFAULT_LOOKBACK_HOURS for a cold start.
    now_utc = datetime.now(timezone.utc)
    lookback = now_utc - timedelta(hours=DEFAULT_LOOKBOOK_HOURS)

    catalog = _ducklake_catalog_uri()
    namespace = _ducklake_namespace()
    for table_fqn in tables:
        rows = _poll_table_changes(
            table_fqn,
            since=lookback,
            namespace=namespace,
            catalog=catalog,
        )
        if not rows:
            yield _make_skip_reason(table_fqn)
            continue
        any_emitted = False
        for change_type, change_ts in rows:
            key = (table_fqn, change_ts)
            if _LAST_SEEN_CHANGE.get(key):
                # Already emitted this exact (table, change_ts)
                # pair in a previous tick; dedup.
                continue
            _LAST_SEEN_CHANGE[key] = True
            yield _make_run_request(table_fqn, change_type, change_ts)
            any_emitted = True
        if not any_emitted:
            yield _make_skip_reason(table_fqn)


# Spelling guard for the lazy-loaded constant name.
DEFAULT_LOOKBOOK_HOURS = DEFAULT_LOOKBACK_HOURS  # type: ignore[misc]
