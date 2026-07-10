"""Firecrawl monitor for CocoIndex blog and GitHub releases."""

from __future__ import annotations

from ._common import (
    MonitorTarget,
    PackageMonitorConfig,
    emit_result,
    monitor_package,
)

CONFIG = PackageMonitorConfig(
    package="COCOINDEX",
    display_name="CocoIndex",
    targets=(
        MonitorTarget(
            url="https://cocoindex.io/blog/",
            label="cocoindex_blog",
            description=(
                "CocoIndex blog for v1 App, connector, runtime, and live "
                "component changes."
            ),
        ),
        MonitorTarget(
            url="https://github.com/cocoindex-io/cocoindex/releases",
            label="cocoindex_github_releases",
            description=(
                "CocoIndex GitHub releases for API, connector, and "
                "conformance-impacting changes."
            ),
        ),
    ),
)


def main() -> int:
    """Run the CocoIndex upstream release monitor once."""
    result = monitor_package(CONFIG)
    emit_result(result)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
