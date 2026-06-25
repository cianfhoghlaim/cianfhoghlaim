"""
CelticDltSourceComponent — the canonical DLT source Component.

Wraps a single DLT source and registers it as a `dg.asset` with
the appropriate `compute_kind` and `group_name`. This is the
Dagster 1.10 Component that replaces the hand-written
`dlt_asset()` wrapper in `oideachais/dlt_utils/source_factory.py`.

Usage (from a YAML defs file):

    type: oideachais.dagster_defs.components.CelticDltSourceComponent
    attributes:
      source_id: ie.education.ncca
      asset_name: ireland_ncca_curriculum
      group_name: ireland_education
"""
from __future__ import annotations

import os
from typing import Any

import dagster as dg

from sruth.oideachais.dlt_utils.destinations import get_dlt_destination
from sruth.oideachais.dlt_utils.safety import safe_dlt_run, validate_source_kwargs
from sruth.oideachais.dlt_utils.source_factory import get_default_factory


class CelticDltSourceComponent(dg.Component, dg.Model):
    """Wrap a single DLT source as a Dagster asset.

    The component reads `source_id` (an entry in
    `oideachais/sources.yaml`), builds a DLT pipeline, and
    materialises the source into the configured DuckLake
    destination. The component is the new (2026-06) idiomatic
    way to add a DLT-backed Dagster asset.

    Attributes:
        source_id: The source id (e.g. "ie.education.ncca").
        asset_name: The Dagster asset name. Default is the
                    pipeline_name from the factory.
        group_name: The Dagster group_name. Default is
                    "{domain}_{nation}" (per the cross-domain-
                    registry spec).
    """

    source_id: str
    asset_name: str | None = None
    group_name: str | None = None

    def build_defs(self, context: dg.ComponentLoadContext) -> dg.Definitions:
        factory = get_default_factory()
        entry = factory.get(self.source_id)
        pipeline_name = self.asset_name or f"sf_{self.source_id.replace('.', '_')}"
        group_name = self.group_name or f"{entry.domain}_{entry.nation}"
        dataset_name = factory.lance_table(self.source_id).replace(".", "_").replace("-", "_")

        @dg.asset(
            name=pipeline_name,
            group_name=group_name,
            compute_kind="dlt",
            description=entry.name,
        )
        def _dlt_asset(asset_context: dg.AssetExecutionContext) -> dg.MaterializeResult:
            os.environ.setdefault("USE_LOCAL_SCRAPES", "true")
            dlt = __import__("dlt")
            destination = get_dlt_destination()
            pipeline = dlt.pipeline(
                pipeline_name=pipeline_name,
                destination=destination,
                dataset_name=dataset_name,
                dev_mode=False,
            )
            source_obj = factory.source(self.source_id)()
            # Pre-flight dlt 1.0 validation
            try:
                mistakes = validate_source_kwargs(source_obj)
                if mistakes:
                    asset_context.log.warning(
                        f"dlt 1.0 source {self.source_id!r} has mistakes: {mistakes}"
                    )
            except Exception as exc:  # pragma: no cover
                asset_context.log.debug(
                    f"validate_source_kwargs skipped: {exc}"
                )
            load_info = safe_dlt_run(pipeline, source_obj)
            return dg.MaterializeResult(
                metadata={
                    "source_id": self.source_id,
                    "dataset_name": dataset_name,
                    "loads_ids": (
                        str(load_info.loads_ids[0]) if load_info.loads_ids else ""
                    ),
                }
            )

        return dg.Definitions(assets=[_dlt_asset])


__all__ = ["CelticDltSourceComponent"]
