"""
spaces/data-engineering/package_analytics/kcg_data_layer/

The KCG-canonical data layer for the data-engineering Space.

E2 of the spaces alignment plan. Replaces the BigQuery source
with the KCG pattern:
- Source: stedding/ingest_queue/pypi/ (the KCG ingest queue)
- Destination: MotherDuck (the canonical lakehouse)
- dbt: dbt-duckdb (the canonical adapter)
- Knowledge graph: Cognee + Graphiti (the canonical memory stack)

The original BigQuery source is preserved at
package_analytics/dlt_sources/bigquery_pipeline.py for backward
compatibility but is no longer the primary path.
"""

from .pypi_source import KcgPypiSource, get_pypi_source
from .motherduck_destination import get_motherduck_destination

__all__ = ["KcgPypiSource", "get_pypi_source", "get_motherduck_destination"]
