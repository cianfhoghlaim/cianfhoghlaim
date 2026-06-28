"""Multi-engine asset exporters for game development.

Supports export to:
- Godot 4 (.tres, .tscn, .material)
- Unity (.prefab, .asset, .mat)
- Unreal Engine (.uasset, .umap)
- Babylon.js (ES modules, .babylon)
"""

from .babylon_exporter import BabylonExporter
from .base_exporter import (
    BaseExporter,
    ExportConfig,
    ExportResult,
    MeshFormat,
    TargetEngine,
    TextureFormat,
)
from .godot_exporter import GodotExporter
from .unity_exporter import UnityExporter
from .unreal_exporter import UnrealExporter

__all__ = [
    "BabylonExporter",
    # Base classes
    "BaseExporter",
    "ExportConfig",
    "ExportResult",
    # Engine exporters
    "GodotExporter",
    "MeshFormat",
    "TargetEngine",
    "TextureFormat",
    "UnityExporter",
    "UnrealExporter",
]


def get_exporter(engine: TargetEngine, config: ExportConfig) -> BaseExporter:
    """Factory function to get the appropriate exporter for a target engine.

    Args:
        engine: Target game engine
        config: Export configuration

    Returns:
        Configured exporter instance

    Raises:
        ValueError: If engine is not supported
    """
    exporters = {
        TargetEngine.GODOT: GodotExporter,
        TargetEngine.UNITY: UnityExporter,
        TargetEngine.UNREAL: UnrealExporter,
        TargetEngine.BABYLON: BabylonExporter,
    }

    exporter_class = exporters.get(engine)
    if exporter_class is None:
        raise ValueError(f"Unsupported engine: {engine}")

    return exporter_class(config)
