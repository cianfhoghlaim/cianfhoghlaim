"""Firecrawl monitor for dltHub / dlt upstream releases."""

from __future__ import annotations

from ._common import (
    MonitorTarget,
    PackageMonitorConfig,
    emit_result,
    monitor_package,
)

CONFIG = PackageMonitorConfig(
    package="DLTHUB",
    display_name="dltHub / dlt",
    targets=(
        MonitorTarget(
            url="https://github.com/dlt-hub/dlt/releases",
            label="dlt_github_releases",
            description=(
                "dlt GitHub releases for source API changes, CLI changes, "
                "destination changes, and migration notes."
            ),
        ),
    ),
)


def main() -> int:
    """Run the dltHub upstream release monitor once."""
    result = monitor_package(CONFIG)
    emit_result(result)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
