"""Shim for `sruth.shared.dagster` — see tuatha/crypteolas/STATUS.md."""

from __future__ import annotations

from dagster import ConfigurableResource


class LakeKeeperResource(ConfigurableResource):
    """Stub: wraps a LakeKeeper Iceberg REST catalog.

    The real implementation would handle OAuth tokens, warehouse binding,
    and table registration. This stub records its configuration and can
    be used in Dagster asset definitions for type-checking and dry-runs.
    """

    catalog_uri: str = "http://localhost:8181"
    warehouse: str = "s3://garage/warehouse"
    namespace: str = "crypteolas"

    def describe(self) -> dict:
        """Return a description of the resource for inspection / debug."""
        return {
            "catalog_uri": self.catalog_uri,
            "warehouse": self.warehouse,
            "namespace": self.namespace,
        }


__all__ = ["LakeKeeperResource"]
