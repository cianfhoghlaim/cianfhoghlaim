"""`oideachais` top-level package.

The data platform code lives at the top level of this package
(`dlt_sources/`, `dlt_utils/`, `dagster_defs/`, `ocr/`, etc.). Per
AGENTS.md rule "Zero Absolute Namespaces in Data Pipelines", new code
MUST import from these top-level sub-packages directly (or use
relative imports when inside the package).

A legacy compatibility shim is provided at
`cianfhoghlaim/cianfhoghlaim/data_platform/__init__.py` for any external
consumers that still use the old `cianfhoghlaim.data_platform.*` path.
We pre-register that shim in `sys.modules` AND as a module attribute
here so that BOTH `import cianfhoghlaim.data_platform` and
`cianfhoghlaim.data_platform.X` attribute access continue to work
without a `data_platform/` subdirectory in the root.
"""

from __future__ import annotations

import importlib
import sys as _sys


# Pre-register the legacy `cianfhoghlaim.data_platform` shim in BOTH
# `sys.modules` (so `import cianfhoghlaim.data_platform` works) AND as a
# module attribute (so `cianfhoghlaim.data_platform` attribute access works).
# This is intentionally lightweight: we only load the shim module itself,
# NOT its target modules — those are loaded lazily via the shim's PEP 562
# `__getattr__` to avoid breaking on transitive import failures.
def _register_legacy_data_platform_shim() -> None:
    if "cianfhoghlaim.data_platform" in _sys.modules:
        globals()["data_platform"] = _sys.modules["cianfhoghlaim.data_platform"]
        return
    try:
        _shim = importlib.import_module("cianfhoghlaim.cianfhoghlaim.data_platform")
    except ImportError as e:  # pragma: no cover
        import warnings
        warnings.warn(f"oideachais: legacy shim unavailable: {e}", ImportWarning, stacklevel=2)
        return
    _sys.modules["cianfhoghlaim.data_platform"] = _shim
    globals()["data_platform"] = _shim


_register_legacy_data_platform_shim()


# Lazy proxy for the `core` sub-package
def __getattr__(name: str):  # PEP 562
    if name == "core":
        from oideachais import core as _core
        globals()["core"] = _core
        _sys.modules.setdefault("cianfhoghlaim.core", _core)
        return _core
    raise AttributeError(f"module 'cianfhoghlaim' has no attribute {name!r}")


__all__ = [
    "agents",
    "api",
    "baml_src",
    "cognee_integration",
    "core",
    "dagster_defs",
    "data_platform",  # legacy shim
    "dlt_sources",
    "dlt_utils",
    "graph",
    "memory",
    "notebooks",
    "ocr",
    "subjects",
]
