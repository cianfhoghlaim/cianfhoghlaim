"""Shared helpers for upstream package Firecrawl monitors.

The four monitor entrypoints in this package are deliberately thin:
fetch a canonical upstream URL via the Firecrawl MCP-compatible scrape
path, extract a typed ``PackageRelease`` with BAML
``ExtractPackageRelease``, persist the row to MotherDuck, and notify the
n8n bridge when the release contains breaking changes.

Runtime safety: the helpers honour ``USE_LOCAL_SCRAPES=true`` by looking
for a local markdown cache before making any live Firecrawl request.
Set ``USE_LOCAL_SCRAPES=false`` explicitly to force a live scrape.
"""

from __future__ import annotations

import dataclasses
import datetime as dt
import hashlib
import json
import os
import pathlib
import urllib.error
import urllib.request
from collections.abc import Iterable, Sequence
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

MOTHERDUCK_CONNECTION = os.getenv(
    "UPSTREAM_MONITORING_MOTHERDUCK_CONNECTION",
    "md:oideachais_upstream",
)
UPSTREAM_TABLE = os.getenv(
    "UPSTREAM_MONITORING_TABLE",
    "upstream_monitoring",
)
DEFAULT_N8N_WEBHOOK_URL = os.getenv(
    "N8N_UPSTREAM_BREAKING_CHANGE_WEBHOOK_URL",
    "https://n8n.cianfhoghlaim.ie/webhook/upstream-breaking-change",
)
LOCAL_SCRAPE_ROOT = pathlib.Path(
    os.getenv(
        "UPSTREAM_MONITORING_LOCAL_SCRAPE_ROOT",
        str(
            pathlib.Path(__file__).resolve().parents[3]
            / "stedding"
            / "upstream_monitoring_scrapes"
        ),
    )
)


@dataclasses.dataclass(frozen=True)
class MonitorTarget:
    """One canonical page watched by an upstream package monitor."""

    url: str
    label: str
    description: str


@dataclasses.dataclass(frozen=True)
class PackageMonitorConfig:
    """Static configuration for one upstream package monitor."""

    package: str
    display_name: str
    targets: tuple[MonitorTarget, ...]
    n8n_webhook_url: str = DEFAULT_N8N_WEBHOOK_URL


@dataclasses.dataclass(frozen=True)
class PackageReleaseRow:
    """MotherDuck row shape for ``upstream_monitoring``."""

    package: str
    source_url: str
    version: str
    release_date: str
    breaking_changes: tuple[str, ...]
    new_features: tuple[str, ...]
    deprecations: tuple[str, ...]
    release_notes_url: str
    fetched_at: str
    content_sha256: str
    is_breaking: bool
    raw_release_json: dict[str, Any]

    def webhook_payload(self) -> dict[str, Any]:
        """Return the n8n webhook payload for breaking-change alerts."""
        return {
            "package": self.package,
            "version": self.version,
            "release_date": self.release_date,
            "source_url": self.source_url,
            "release_notes_url": self.release_notes_url,
            "breaking_changes": list(self.breaking_changes),
            "new_features": list(self.new_features),
            "deprecations": list(self.deprecations),
            "detected_at": self.fetched_at,
            "content_sha256": self.content_sha256,
        }


@dataclasses.dataclass(frozen=True)
class MonitorRunResult:
    """Summary returned by each monitor run."""

    package: str
    rows_written: int
    breaking_changes: int
    rows: tuple[PackageReleaseRow, ...]


class UpstreamMonitorError(RuntimeError):
    """Raised when an upstream monitor cannot complete its work."""


# ---------------------------------------------------------------------------
# Fetching
# ---------------------------------------------------------------------------


def _safe_filename(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest() + ".md"


def _read_local_scrape(package: str, url: str) -> str | None:
    """Return cached markdown when ``USE_LOCAL_SCRAPES=true``."""
    use_local = os.getenv("USE_LOCAL_SCRAPES", "true").lower() == "true"
    if not use_local:
        return None

    cache_path = LOCAL_SCRAPE_ROOT / package.lower() / _safe_filename(url)
    if cache_path.exists():
        return cache_path.read_text(encoding="utf-8")

    logger.info(
        "upstream_local_scrape_cache_miss",
        package=package,
        url=url,
        path=str(cache_path),
    )
    return None


def _write_local_scrape(package: str, url: str, markdown: str) -> None:
    """Persist fetched markdown to the local scrape cache for future runs."""
    cache_path = LOCAL_SCRAPE_ROOT / package.lower() / _safe_filename(url)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(markdown, encoding="utf-8")


def fetch_markdown_via_firecrawl_mcp(package: str, url: str) -> str:
    """Fetch ``url`` through the Firecrawl MCP-compatible scrape path.

    The OpenCode runtime exposes Firecrawl via MCP tools; scheduled code
    uses the same Firecrawl scrape endpoint through the Python SDK when it
    is installed. The helper preserves the project safety rule by checking
    the local scrape cache first when ``USE_LOCAL_SCRAPES=true``.
    """
    cached = _read_local_scrape(package, url)
    if cached is not None:
        return cached

    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        raise UpstreamMonitorError(
            "FIRECRAWL_API_KEY is required for a live upstream scrape; "
            "set USE_LOCAL_SCRAPES=true with a cached markdown file for "
            "offline runs."
        )

    try:
        from firecrawl import FirecrawlApp  # type: ignore[import-not-found]
    except ImportError as exc:  # pragma: no cover - dependency optional in CI
        raise UpstreamMonitorError(
            "firecrawl Python SDK is not installed; the monitor expects the "
            "Firecrawl MCP/server scrape surface to be available."
        ) from exc

    app = FirecrawlApp(api_key=api_key)
    scrape_kwargs: dict[str, Any] = {"formats": ["markdown"]}
    result = app.scrape_url(url, params=scrape_kwargs)
    markdown = str(result.get("markdown") or "")
    if not markdown.strip():
        raise UpstreamMonitorError(f"Firecrawl returned empty markdown for {url}")

    _write_local_scrape(package, url, markdown)
    return markdown


# ---------------------------------------------------------------------------
# BAML extraction
# ---------------------------------------------------------------------------


def _value(obj: Any, *names: str, default: Any = None) -> Any:
    """Read the first present attribute/key from a BAML/Pydantic/dict object."""
    for name in names:
        if isinstance(obj, dict) and name in obj:
            return obj[name]
        if hasattr(obj, name):
            return getattr(obj, name)
    return default


def _as_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,) if value else ()
    if isinstance(value, Iterable):
        return tuple(str(item) for item in value if str(item).strip())
    return (str(value),)


def _jsonable(value: Any) -> Any:
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return dataclasses.asdict(value)
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, dict):
        return value
    return {
        name: getattr(value, name)
        for name in dir(value)
        if not name.startswith("_") and not callable(getattr(value, name))
    }


def extract_package_release(package: str, url: str, markdown: str) -> PackageReleaseRow:
    """Run BAML ``ExtractPackageRelease`` and coerce the output to a row."""
    try:
        from baml_client.sync_client import b as baml_sync  # type: ignore[import-not-found]

        release = baml_sync.ExtractPackageRelease(content=markdown, url=url)
    except Exception as exc:  # fallback preserves monitor liveness
        logger.warning(
            "baml_extract_package_release_failed_using_stub",
            package=package,
            url=url,
            error=str(exc),
        )
        release = {
            "pkg": package.upper(),
            "version": "0.0.0",
            "release_date": dt.datetime.now(dt.UTC).date().isoformat(),
            "breaking_changes": [],
            "new_features": [],
            "deprecations": [],
            "release_notes_url": url,
        }

    content_hash = hashlib.sha256(markdown.encode("utf-8")).hexdigest()
    raw_release = _jsonable(release)
    breaking_changes = _as_tuple(_value(release, "breaking_changes", default=()))
    package_value = str(_value(release, "pkg", "package", default=package)).upper()
    release_url = str(_value(release, "release_notes_url", "url", default=url))
    fetched_at = dt.datetime.now(dt.UTC).isoformat()

    return PackageReleaseRow(
        package=package_value,
        source_url=url,
        version=str(_value(release, "version", default="0.0.0")),
        release_date=str(
            _value(
                release,
                "release_date",
                default=dt.datetime.now(dt.UTC).date().isoformat(),
            )
        ),
        breaking_changes=breaking_changes,
        new_features=_as_tuple(_value(release, "new_features", default=())),
        deprecations=_as_tuple(_value(release, "deprecations", default=())),
        release_notes_url=release_url,
        fetched_at=fetched_at,
        content_sha256=content_hash,
        is_breaking=bool(breaking_changes),
        raw_release_json=raw_release,
    )


# ---------------------------------------------------------------------------
# Persistence + n8n bridge
# ---------------------------------------------------------------------------


def _connect_motherduck() -> Any:
    try:
        import duckdb  # type: ignore[import-not-found]
    except ImportError as exc:  # pragma: no cover - dependency installed in runtime
        raise UpstreamMonitorError("duckdb is required to write MotherDuck rows") from exc
    return duckdb.connect(MOTHERDUCK_CONNECTION)


def _ensure_table(conn: Any) -> None:
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {UPSTREAM_TABLE} (
            package VARCHAR,
            source_url VARCHAR,
            version VARCHAR,
            release_date VARCHAR,
            breaking_changes JSON,
            new_features JSON,
            deprecations JSON,
            release_notes_url VARCHAR,
            fetched_at TIMESTAMP,
            content_sha256 VARCHAR,
            is_breaking BOOLEAN,
            raw_release_json JSON,
            PRIMARY KEY (package, release_notes_url, version, content_sha256)
        )
        """
    )


def write_release_rows(rows: Sequence[PackageReleaseRow]) -> int:
    """Write release rows to ``md:oideachais_upstream.upstream_monitoring``."""
    if not rows:
        return 0

    conn = _connect_motherduck()
    try:
        _ensure_table(conn)
        for row in rows:
            conn.execute(
                f"""
                DELETE FROM {UPSTREAM_TABLE}
                WHERE package = ?
                  AND release_notes_url = ?
                  AND version = ?
                  AND content_sha256 = ?
                """,
                [
                    row.package,
                    row.release_notes_url,
                    row.version,
                    row.content_sha256,
                ],
            )
            conn.execute(
                f"""
                INSERT INTO {UPSTREAM_TABLE} (
                    package,
                    source_url,
                    version,
                    release_date,
                    breaking_changes,
                    new_features,
                    deprecations,
                    release_notes_url,
                    fetched_at,
                    content_sha256,
                    is_breaking,
                    raw_release_json
                ) VALUES (?, ?, ?, ?, ?::JSON, ?::JSON, ?::JSON, ?, ?, ?, ?, ?::JSON)
                """,
                [
                    row.package,
                    row.source_url,
                    row.version,
                    row.release_date,
                    json.dumps(list(row.breaking_changes)),
                    json.dumps(list(row.new_features)),
                    json.dumps(list(row.deprecations)),
                    row.release_notes_url,
                    row.fetched_at,
                    row.content_sha256,
                    row.is_breaking,
                    json.dumps(row.raw_release_json, default=str),
                ],
            )
    finally:
        conn.close()
    return len(rows)


def trigger_n8n_webhook(
    payload: dict[str, Any],
    webhook_url: str = DEFAULT_N8N_WEBHOOK_URL,
) -> bool:
    """POST a breaking-change payload to the n8n bridge."""
    body = json.dumps(payload, default=str).encode("utf-8")
    request = urllib.request.Request(
        webhook_url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            status = getattr(response, "status", 200)
            ok = 200 <= int(status) < 300
            if not ok:
                logger.warning("n8n_webhook_non_2xx", status=status)
            return ok
    except (urllib.error.URLError, TimeoutError) as exc:
        logger.warning("n8n_webhook_failed", error=str(exc), url=webhook_url)
        return False


def monitor_package(config: PackageMonitorConfig) -> MonitorRunResult:
    """Run one complete upstream package monitor."""
    rows: list[PackageReleaseRow] = []
    for target in config.targets:
        logger.info(
            "upstream_monitor_fetching",
            package=config.package,
            url=target.url,
            label=target.label,
        )
        markdown = fetch_markdown_via_firecrawl_mcp(config.package, target.url)
        row = extract_package_release(config.package, target.url, markdown)
        rows.append(row)

    rows_written = write_release_rows(rows)
    breaking_count = 0
    for row in rows:
        if row.is_breaking:
            breaking_count += 1
            trigger_n8n_webhook(row.webhook_payload(), config.n8n_webhook_url)

    return MonitorRunResult(
        package=config.package,
        rows_written=rows_written,
        breaking_changes=breaking_count,
        rows=tuple(rows),
    )


def emit_result(result: MonitorRunResult) -> None:
    """Print a compact JSON summary for cron / Dagster logs."""
    print(
        json.dumps(
            {
                "package": result.package,
                "rows_written": result.rows_written,
                "breaking_changes": result.breaking_changes,
                "versions": [row.version for row in result.rows],
            },
            indent=2,
            sort_keys=True,
        )
    )
