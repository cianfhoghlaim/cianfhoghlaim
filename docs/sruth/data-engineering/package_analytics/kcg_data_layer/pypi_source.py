"""
spaces/data-engineering/package_analytics/kcg_data_layer/pypi_source.py

The KCG-canonical PyPI DLT source.

Reads the 5-7 priority Python packages (duckdb, ibis-framework,
polars, trino, clickhouse-connect) from the local
`stedding/ingest_queue/pypi/` cache (the KCG pattern).

Honors USE_LOCAL_SCRAPES=true (default in compose.yaml) to
read from the local cache. The cache is populated by the
oideachais/dlt_sources/pypi.py source.
"""

from __future__ import annotations

import json
import os
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path

import dlt

_DEFAULT_PACKAGES = ("duckdb", "ibis-framework", "polars", "trino", "clickhouse-connect")
_STEDDING_PATH = Path(os.environ.get("STEDDING_PATH", "/stedding/ingest_queue/pypi"))


@dlt.source(name="kcg_pypi")
def kcg_pypi_source(
    packages: tuple[str, ...] = _DEFAULT_PACKAGES,
    start_date: str | None = None,
    end_date: str | None = None,
) -> Iterator:
    """Yield DLT resources for the KCG PyPI canonical data layer.

    The source reads JSONL files from `stedding/ingest_queue/pypi/`
    and yields one resource per package.

    Args:
        packages: Tuple of PyPI project names to ingest.
        start_date: ISO date (inclusive). None = no lower bound.
        end_date: ISO date (inclusive). None = no upper bound.
    """
    for pkg in packages:
        yield kcg_pypi_package(pkg, start_date=start_date, end_date=end_date)


@dlt.resource(name="downloads", write_disposition="merge", primary_key="id")
def kcg_pypi_package(
    package: str,
    start_date: str | None = None,
    end_date: str | None = None,
) -> Iterator[dict]:
    """Yield download rows for one package from the local cache."""
    cache_path = _STEDDING_PATH / package / "downloads.jsonl"
    if not cache_path.exists():
        dlt.logger.warning(f"No cache for {package} at {cache_path}")
        return
    with open(cache_path) as f:
        for line in f:
            row = json.loads(line)
            if start_date and row.get("date", "") < start_date:
                continue
            if end_date and row.get("date", "") > end_date:
                continue
            row["package"] = package
            row["ingested_at"] = datetime.now(UTC).isoformat()
            row["id"] = f"{package}|{row.get('date', '')}|{row.get('country_code', '')}"
            yield row


def get_pypi_source() -> KcgPypiSource:
    """Return the canonical KCG PyPI source (factory)."""
    return KcgPypiSource()


class KcgPypiSource:
    """Public wrapper for `kcg_pypi_source`. Use in Dagster assets:

    @asset
    def pypi_kcg(kcg_pypi_source: KcgPypiSource = ...):
        return kcg_pypi_source.run()
    """

    def run(self, packages: tuple[str, ...] = _DEFAULT_PACKAGES) -> dict:
        """Execute the KCG PyPI source and return the row counts."""
        pipeline = dlt.pipeline(
            pipeline_name="kcg_pypi",
            destination=get_motherduck_destination(),
            dataset_name="kcg_pypi",
            dev_mode=False,
        )
        info = pipeline.run(kcg_pypi_source(packages=packages))
        return {
            "datasets": [d["name"] for d in info.load_info["datasets"]],
            "first_run": info.first_run,
            "load_ids": info.load_ids,
        }
