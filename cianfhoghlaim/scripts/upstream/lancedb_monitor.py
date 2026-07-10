"""Firecrawl monitor for LanceDB docs and GitHub releases."""

from __future__ import annotations

from ._common import (
    MonitorTarget,
    PackageMonitorConfig,
    emit_result,
    monitor_package,
)

CONFIG = PackageMonitorConfig(
    package="LANCEDB",
    display_name="LanceDB",
    targets=(
        MonitorTarget(
            url="https://lancedb.com/docs/",
            label="lancedb_docs",
            description=(
                "LanceDB documentation surface for breaking SDK, table, "
                "indexing, Lance format, and deployment changes."
            ),
        ),
        MonitorTarget(
            url="https://github.com/lancedb/lancedb/releases",
            label="lancedb_github_releases",
            description=(
                "LanceDB GitHub releases for versioned migration and "
                "breaking-change announcements."
            ),
        ),
    ),
)


def main() -> int:
    """Run the LanceDB upstream release monitor once."""
    result = monitor_package(CONFIG)
    emit_result(result)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
