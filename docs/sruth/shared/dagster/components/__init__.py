"""Dagster Components for sruth pipelines.

Provides YAML-configurable components for:
- DLT assets (data loading from APIs/browsers)
- Iceberg I/O managers (Lakekeeper catalog)
- Browser resources (scraping backends)
- MotherDuck resources (cloud data warehouse)
- PlanetScale resources (OLTP PostgreSQL)
- CocoIndex flows (structured extraction with DSPy)

Usage:
    # In defs.yaml
    type: sruth.shared.dagster.components.DLTAssetComponent
    attributes:
      asset_key: ["curriculum", "pages"]
      source_module: "sruth.oideachais.dlt_sources.curriculum_source"
      pipeline_name: "curriculum_pipeline"
"""

from .dlt_component import DLTAssetComponent
from .iceberg_component import IcebergIOComponent
from .browser_component import BrowserResourceComponent
from .motherduck_component import (
    MotherDuckComponent,
    MotherDuckIOComponent,
    PlanetScaleComponent,
)
from .coco_component import (
    CocoIndexFlowComponent,
    DSPyTransformComponent,
)

__all__ = [
    "DLTAssetComponent",
    "IcebergIOComponent",
    "BrowserResourceComponent",
    "MotherDuckComponent",
    "MotherDuckIOComponent",
    "PlanetScaleComponent",
    "CocoIndexFlowComponent",
    "DSPyTransformComponent",
]
