"""EU multilingual monitoring + alignment assets (added by 2026-07-15-eu-multilingual-irish-english-v1)."""
import importlib as _il
_ecm = _il.import_module("orchestration.defs.2_materials.eu_multilingual.english_coverage_monitor")
_icm = _il.import_module("orchestration.defs.2_materials.eu_multilingual.irish_coverage_monitor")
_lam = _il.import_module("orchestration.defs.2_materials.eu_multilingual.language_alignment_mapper")
english_coverage_monitor = _ecm.english_coverage_monitor
irish_coverage_monitor = _icm.irish_coverage_monitor
language_alignment_mapper = _lam.language_alignment_mapper
__all__ = ["english_coverage_monitor", "irish_coverage_monitor", "language_alignment_mapper"]
