"""
Shared Dagster resources and components for sruth pipelines.

This module provides:
- Resources: LakeKeeper, Browser, MotherDuck, PlanetScale, FalkorDB, Cognee, LanceDB
- Factories: Asset factories for common patterns
- Components: YAML-configurable Dagster components
"""

# Resources
from .resources import (
    LakeKeeperResource,
    BrowserResource,
    MotherDuckResource,
    FalkorDBResource,
    CogneeResource,
    LanceDBResource,
    lakekeeper_resource,
    browser_resource,
    motherduck_resource,
    falkordb_resource,
    cognee_resource,
    lancedb_resource,
)

# Factories
from .factories import (
    dlt_asset_factory,
    multi_partition_factory,
    observable_asset,
)

# Components
from .components import (
    DLTAssetComponent,
    IcebergIOComponent,
    BrowserResourceComponent,
    MotherDuckComponent,
    MotherDuckIOComponent,
    PlanetScaleComponent,
    CocoIndexFlowComponent,
    DSPyTransformComponent,
)

# Component loader
from .components.loader import (
    load_components_from_yaml,
    load_components_from_directory,
    get_current_environment,
    load_auto_definitions,
)

__all__ = [
    # Resources
    "LakeKeeperResource",
    "BrowserResource",
    "MotherDuckResource",
    "FalkorDBResource",
    "CogneeResource",
    "LanceDBResource",
    "lakekeeper_resource",
    "browser_resource",
    "motherduck_resource",
    "falkordb_resource",
    "cognee_resource",
    "lancedb_resource",
    # Factories
    "dlt_asset_factory",
    "multi_partition_factory",
    "observable_asset",
    # Components
    "DLTAssetComponent",
    "IcebergIOComponent",
    "BrowserResourceComponent",
    "MotherDuckComponent",
    "MotherDuckIOComponent",
    "PlanetScaleComponent",
    "CocoIndexFlowComponent",
    "DSPyTransformComponent",
    # Component loader
    "load_components_from_yaml",
    "load_components_from_directory",
    "get_current_environment",
    "load_auto_definitions",
]
