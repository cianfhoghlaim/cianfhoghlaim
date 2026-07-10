"""Firecrawl monitor for MotherDuck / DuckLake upstream releases."""

from __future__ import annotations

from ._common import (
    MonitorTarget,
    PackageMonitorConfig,
    emit_result,
    monitor_package,
)

CONFIG = PackageMonitorConfig(
    package="MOTHERDUCK",
    display_name="MotherDuck",
    targets=(
        MonitorTarget(
            url="https://motherduck.com/changelog/",
            label="motherduck_changelog",
            description=(
                "MotherDuck changelog for DuckLake, BYOB, MotherDuck SQL, "
                "Dives, Flights, and breaking migration notes."
            ),
        ),
    ),
)


def main() -> int:
    """Run the MotherDuck upstream release monitor once."""
    result = monitor_package(CONFIG)
    emit_result(result)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
