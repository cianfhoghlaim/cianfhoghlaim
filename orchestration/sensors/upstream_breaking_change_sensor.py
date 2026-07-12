"""Dagster sensor for upstream package breaking changes.

Polls ``md:oideachais_upstream.upstream_monitoring`` every five minutes
for newly detected breaking-change rows written by the four Firecrawl
monitors. Each new row emits a ``RunRequest`` targeting the downstream
upstream-monitoring materialisation surface.
"""

from __future__ import annotations

import dataclasses
import datetime as dt
import json
import os
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

try:
    from dagster import (  # type: ignore[import-not-found]
        AssetKey,
        DefaultSensorStatus,
        RunRequest,
        SensorEvaluationContext,
        SkipReason,
        sensor,
    )

    DAGSTER_AVAILABLE = True
except ImportError:  # pragma: no cover - Dagster is optional in AST-only CI
    AssetKey = None  # type: ignore[assignment]
    DefaultSensorStatus = None  # type: ignore[assignment]
    RunRequest = None  # type: ignore[assignment]
    SensorEvaluationContext = object  # type: ignore[assignment]
    SkipReason = None  # type: ignore[assignment]
    sensor = None  # type: ignore[assignment]
    DAGSTER_AVAILABLE = False


MOTHERDUCK_CONNECTION = os.getenv(
    "UPSTREAM_MONITORING_MOTHERDUCK_CONNECTION",
    "md:oideachais_upstream",
)
UPSTREAM_TABLE = os.getenv(
    "UPSTREAM_MONITORING_TABLE",
    "upstream_monitoring",
)
DOWNSTREAM_ASSET_KEY = ["upstream_monitoring", "breaking_change_materialization"]


@dataclasses.dataclass(frozen=True)
class BreakingChangeRow:
    """Row shape returned by the sensor poll query."""

    package: str
    version: str
    release_notes_url: str
    breaking_changes: tuple[str, ...]
    fetched_at: str
    content_sha256: str

    @property
    def run_key(self) -> str:
        return ":".join(
            [self.package, self.version, self.content_sha256, self.fetched_at]
        )


@dataclasses.dataclass(frozen=True)
class SensorCursor:
    """Cursor state persisted by Dagster between sensor evaluations."""

    last_seen_at: str = "1970-01-01T00:00:00+00:00"

    @classmethod
    def loads(cls, raw: str | None) -> SensorCursor:
        if not raw:
            return cls()
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return cls()
        return cls(last_seen_at=str(payload.get("last_seen_at") or cls().last_seen_at))

    def dumps(self) -> str:
        return json.dumps({"last_seen_at": self.last_seen_at}, sort_keys=True)


def _as_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        try:
            decoded = json.loads(value)
        except json.JSONDecodeError:
            return (value,) if value else ()
        return _as_tuple(decoded)
    if isinstance(value, list | tuple):
        return tuple(str(item) for item in value if str(item).strip())
    return (str(value),)


def _fetch_new_breaking_changes(cursor: SensorCursor) -> list[BreakingChangeRow]:
    """Query MotherDuck for breaking changes newer than the cursor."""
    try:
        import duckdb  # type: ignore[import-not-found]
    except ImportError:
        logger.warning("duckdb_not_available_for_upstream_sensor")
        return []

    try:
        conn = duckdb.connect(MOTHERDUCK_CONNECTION)
    except Exception as exc:  # sensor should skip, not crash Dagster
        logger.warning("motherduck_connect_failed_for_upstream_sensor", error=str(exc))
        return []

    try:
        result = conn.execute(
            f"""
            SELECT
                package,
                version,
                release_notes_url,
                CAST(breaking_changes AS VARCHAR) AS breaking_changes,
                CAST(fetched_at AS VARCHAR) AS fetched_at,
                content_sha256
            FROM {UPSTREAM_TABLE}
            WHERE is_breaking = TRUE
              AND fetched_at > ?::TIMESTAMP
            ORDER BY fetched_at ASC
            LIMIT 50
            """,
            [cursor.last_seen_at],
        ).fetchall()
    except Exception as exc:  # table may not exist on first boot
        logger.warning("upstream_breaking_change_poll_failed", error=str(exc))
        return []
    finally:
        conn.close()

    rows: list[BreakingChangeRow] = []
    for record in result:
        rows.append(
            BreakingChangeRow(
                package=str(record[0]),
                version=str(record[1]),
                release_notes_url=str(record[2]),
                breaking_changes=_as_tuple(record[3]),
                fetched_at=str(record[4]),
                content_sha256=str(record[5]),
            )
        )
    return rows


def _max_fetched_at(rows: list[BreakingChangeRow]) -> str:
    if not rows:
        return SensorCursor().last_seen_at
    parsed: list[dt.datetime] = []
    for row in rows:
        try:
            parsed.append(dt.datetime.fromisoformat(row.fetched_at))
        except ValueError:
            parsed.append(dt.datetime.now(dt.UTC))
    return max(parsed).isoformat()


if DAGSTER_AVAILABLE:

    @sensor(
        name="upstream_breaking_change_sensor",
        minimum_interval_seconds=300,
        default_status=DefaultSensorStatus.RUNNING,
        description=(
            "Poll md:oideachais_upstream.upstream_monitoring for new "
            "breaking changes from motherduck, dlthub, lancedb, and cocoindex."
        ),
    )
    def upstream_breaking_change_sensor(  # type: ignore[no-redef]
        context: SensorEvaluationContext,
    ):
        """Emit one downstream materialisation request per new breaking change."""
        cursor = SensorCursor.loads(context.cursor)
        rows = _fetch_new_breaking_changes(cursor)
        if not rows:
            yield SkipReason("No new upstream breaking changes detected.")
            return

        for row in rows:
            yield RunRequest(
                run_key=row.run_key,
                asset_selection=[AssetKey(DOWNSTREAM_ASSET_KEY)],
                tags={
                    "upstream/package": row.package,
                    "upstream/version": row.version,
                    "upstream/release_notes_url": row.release_notes_url,
                    "upstream/content_sha256": row.content_sha256,
                },
                run_config={
                    "ops": {
                        "upstream_breaking_change_materialization": {
                            "config": dataclasses.asdict(row),
                        }
                    }
                },
            )

        context.update_cursor(SensorCursor(last_seen_at=_max_fetched_at(rows)).dumps())

else:  # pragma: no cover
    upstream_breaking_change_sensor = None


__all__ = [
    "BreakingChangeRow",
    "SensorCursor",
    "upstream_breaking_change_sensor",
]
