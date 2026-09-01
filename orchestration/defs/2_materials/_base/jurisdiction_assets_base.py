"""Dagster `JurisdictionAssetsBase` — the per-jurisdiction assets base.

This module provides the canonical shared logic for the 10 per-
jurisdiction Dagster asset wrappers. Today each jurisdiction
(`ireland`, `england`, `scotland`, `wales`, `ni`, `sct_wls_ni`,
`isle_of_man`, `jersey`, `guernsey`, `crown_dependencies`) has its
own ~378-LOC asset file:

    orchestration/defs/2_materials/{jurisdiction}_education/generic_<jur>_assets.py

Each file repeats the same logic:
- Run the jurisdiction pipeline via .run()
- Materialize a `<jur>_documents_ingested` asset
- Log to Langfuse v3 + RAGAS

Per the `centralized-model-registry` + `dagster-5-layer-component-architecture`
specs, the per-jurisdiction files become thin subclasses of
``JurisdictionAssetsBase``. Net reduction per jurisdiction: ~378 → ~50 LOC.
The full rollout saves ~3,300 LOC across 10 files (from ~3,800 to ~500).

Reference:
    openspec/changes/2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1/
"""

import logging
import os
from dataclasses import dataclass
from typing import Any, Type

import dagster as dg

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# The base class — abstract, must be subclassed.
# ---------------------------------------------------------------------------


class JurisdictionAssetsBase:
    """Base class for per-jurisdiction Dagster assets.

    Subclasses MUST set:
        - ``jurisdiction_name: str`` (e.g. ``"ireland"``)
        - ``pipeline_factory: Callable[[], Any]`` — a function that
          returns the freshly-constructed jurisdiction pipeline
          (e.g. ``ireland_jurisdiction_pipeline`` from
          ``dlt_sources.education.ireland.british_isles.education.ireland_jurisdiction_pipeline``).
        - ``asset_name: str`` (default: ``f"{jurisdiction_name}_documents_ingested"``)

    Subclasses MAY override:
        - ``partition_defs`` (default: daily partitions)
        - ``group_name`` (default: the jurisdiction name)
    """

    jurisdiction_name: str = ""
    pipeline_factory: Any = None
    asset_name: str = ""

    @classmethod
    def build_asset(cls) -> dg.AssetsDefinition:
        """Build the canonical `<jur>_documents_ingested` Dagster asset."""
        if not cls.jurisdiction_name:
            raise ValueError(
                "JurisdictionAssetsBase subclasses must set "
                "`jurisdiction_name`."
            )
        if cls.pipeline_factory is None:
            raise ValueError(
                "JurisdictionAssetsBase subclasses must set "
                "`pipeline_factory`."
            )
        asset_name = cls.asset_name or f"{cls.jurisdiction_name}_documents_ingested"
        group_name = getattr(cls, "group_name", cls.jurisdiction_name)

        @dg.asset(
            name=asset_name,
            group_name=group_name,
            compute_kind="dlt",
            partitions_def=getattr(
                cls,
                "partition_defs",
                dg.DailyPartitionsDefinition(start_date="2024-01-01"),
            ),
        )
        def _asset(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
            pipeline = cls.pipeline_factory()
            result = pipeline.run()
            n_rows = _count_rows(result)
            context.add_output_metadata(
                {
                    "jurisdiction": cls.jurisdiction_name,
                    "rows_ingested": n_rows,
                    "metadata": {
                        "dataset_name": getattr(
                            pipeline, "dataset_name", cls.jurisdiction_name,
                        ),
                        "stage": getattr(pipeline, "stage", "education"),
                    },
                }
            )
            return dg.MaterializeResult(
                metadata={
                    "rows_ingested": dg.MetadataValue.int(n_rows),
                }
            )

        return _asset


def _count_rows(pipeline_result: Any) -> int:
    """Count rows ingested (best-effort)."""
    try:
        if hasattr(pipeline_result, "load_packages"):
            pkgs = pipeline_result.load_packages
            if pkgs and hasattr(pkgs[0], "jobs"):
                return sum(
                    j.completed and len(j.table_metrics) for j in pkgs[0].jobs
                )
    except Exception:
        pass
    return 0


# ---------------------------------------------------------------------------
# Reference subclass — Ireland (the canonical BIEP v3 implementation).
# ---------------------------------------------------------------------------


@dataclass
class IrelandAssetsConfig:
    """Ireland-specific config — used by JurisdictionAssetsBase subclass."""

    jurisdiction_name: str = "ireland"
    asset_name: str = "ireland_documents_ingested"


class IrelandAssets(JurisdictionAssetsBase):
    """Ireland-jurisdiction Dagster assets (the reference)."""

    jurisdiction_name = "ireland"
    asset_name = "ireland_documents_ingested"
    group_name = "ireland_education"

    @staticmethod
    def pipeline_factory():
        """Return the freshly-constructed Ireland jurisdiction pipeline."""
        from dlt_sources.education.ireland.british_isles.education.ireland_jurisdiction_pipeline import (
            ireland_jurisdiction_pipeline,
        )
        return ireland_jurisdiction_pipeline()


# ---------------------------------------------------------------------------
# Generic factory for any other jurisdiction.
# ---------------------------------------------------------------------------


def make_jurisdiction_assets(
    jurisdiction_name: str,
    pipeline_factory: Any,
    asset_name: str | None = None,
    group_name: str | None = None,
) -> type:
    """Dynamically build a subclass for any jurisdiction.

    Example::

        england_assets_cls = make_jurisdiction_assets(
            jurisdiction_name="england",
            pipeline_factory=lambda: england_jurisdiction_pipeline(),
        )
        england_assets = england_assets_cls.build_asset()

    This is the recommended pattern for the 10 per-jurisdiction
    asset files in
    ``orchestration/defs/2_materials/{jurisdiction}_education/generic_<jur>_assets.py``.
    """
    asset_name = asset_name or f"{jurisdiction_name}_documents_ingested"
    group_name = group_name or f"{jurisdiction_name}_education"

    class _JurisdictionAssets(JurisdictionAssetsBase):
        pass

    _JurisdictionAssets.jurisdiction_name = jurisdiction_name
    _JurisdictionAssets.pipeline_factory = staticmethod(pipeline_factory)
    _JurisdictionAssets.asset_name = asset_name
    _JurisdictionAssets.group_name = group_name
    _JurisdictionAssets.__name__ = f"{jurisdiction_name.capitalize()}Assets"
    _JurisdictionAssets.__qualname__ = _JurisdictionAssets.__name__
    return _JurisdictionAssets


# ---------------------------------------------------------------------------
# The 10 per-jurisdiction subclasses (built dynamically).
# ---------------------------------------------------------------------------


def _build_all_jurisdiction_assets() -> list[dg.AssetsDefinition]:
    """Construct one Dagster asset per jurisdiction.

    Used by Dagster's `Definitions` resolver. The 10 jurisdictions
    are: ireland, england, scotland, wales, ni, sct_wls_ni,
    isle_of_man, jersey, guernsey, crown_dependencies.
    """
    out: list[dg.AssetsDefinition] = []
    for jurisdiction in (
        "ireland", "england", "scotland", "wales", "ni",
        "sct_wls_ni", "isle_of_man", "jersey", "guernsey",
        "crown_dependencies",
    ):
        try:
            # Dynamic import — the jurisdiction pipeline module
            # may not be available in dev environments.
            mod_path = (
                f"dlt_sources.british_isles.{jurisdiction}"
                f".education.{jurisdiction}_jurisdiction_pipeline"
            )
            if jurisdiction == "ireland":
                cls = IrelandAssets
            else:
                # Build a dynamic subclass
                factory = _late_import_factory(jurisdiction, mod_path)
                cls = make_jurisdiction_assets(
                    jurisdiction_name=jurisdiction,
                    pipeline_factory=factory,
                )
            out.append(cls.build_asset())
        except Exception as e:
            logger.debug(
                f"Skipping {jurisdiction} (pipeline not available): {e}"
            )
            continue
    return out


def _late_import_factory(jurisdiction: str, module_path: str):
    """Return a factory callable that lazy-imports the jurisdiction pipeline."""
    def _factory():
        import importlib
        mod = importlib.import_module(module_path)
        # Convention: the pipeline is exposed as a top-level
        # `<jur>_jurisdiction_pipeline` symbol.
        attr = f"{jurisdiction}_jurisdiction_pipeline"
        return getattr(mod, attr)

    return _factory


# Convenience: the canonical asset list
def all_jurisdiction_assets() -> list[dg.AssetsDefinition]:
    """All 10 jurisdiction assets (for the Dagster Definitions object)."""
    return _build_all_jurisdiction_assets()


__all__ = [
    "JurisdictionAssetsBase",
    "IrelandAssets",
    "IrelandAssetsConfig",
    "all_jurisdiction_assets",
    "make_jurisdiction_assets",
]
