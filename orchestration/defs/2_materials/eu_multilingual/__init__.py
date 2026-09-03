"""EU multilingual monitoring + alignment assets (added by 2026-07-15-eu-multilingual-irish-english-v1).

To avoid duplicate asset registration, we do NOT re-export the
@asset objects at package level (Dagster's load_assets_from_modules
discovers them via the submodules already).
"""
import importlib as _il
_il.import_module("orchestration.defs.2_materials.eu_multilingual.english_coverage_monitor")
_il.import_module("orchestration.defs.2_materials.eu_multilingual.irish_coverage_monitor")
_il.import_module("orchestration.defs.2_materials.eu_multilingual.language_alignment_mapper")
__all__: list[str] = []
