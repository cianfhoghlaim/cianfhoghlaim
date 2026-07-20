"""endpoint_health L2 module — exports the sink + alerts submodules.

To avoid duplicate asset registration, we do NOT re-export the
@asset objects at package level (Dagster's load_assets_from_modules
discovers them via the alerts.py and sink.py submodules already).
"""
import importlib as _il
_il.import_module("orchestration.defs.2_materials.endpoint_health.alerts")
_il.import_module("orchestration.defs.2_materials.endpoint_health.sink")
__all__: list[str] = []
