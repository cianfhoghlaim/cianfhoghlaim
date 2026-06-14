"""Legacy shim for `oideachais.data_platform.*` imports.

STATUS (Phase 3.6, 2026-06-13): The `oideachais/data_platform/` subdirectory
that this shim was originally re-exporting from has been removed — the data
platform code now lives at the top level of the `oideachais/` package
(`oideachais/dlt_sources/`, `oideachais/dagster_defs/`, `oideachais/dlt_utils/`,
`oideachais/ocr/`, etc.). Per AGENTS.md rule "Zero Absolute Namespaces in
Data Pipelines", all in-tree code has been migrated to relative imports.

This shim now exists only to emit a clear `DeprecationWarning` and a
helpful `ImportError` for any external consumer that still uses the old
`oideachais.data_platform.*` import path. New code MUST use the new
top-level packages directly.

The shim is exposed as `oideachais.data_platform` via PEP 562 in the
top-level `oideachais/__init__.py`. It registers a `sys.meta_path` finder
so that submodule imports (`from oideachais.data_platform.X import Y`)
also produce a clear migration error rather than a bare
`ModuleNotFoundError`.
"""
from __future__ import annotations

import importlib.abc
import importlib.machinery
import importlib.util
import sys
import warnings


_warned = False


def _warn_once() -> None:
    global _warned
    if _warned:
        return
    _warned = True
    warnings.warn(
        "Importing from `oideachais.data_platform.*` is deprecated and the "
        "legacy `oideachais/data_platform/` subdirectory has been removed. "
        "Update your import to the new top-level package: "
        "`oideachais.dlt_sources`, `oideachais.dlt_utils`, "
        "`oideachais.dagster_defs`, `oideachais.ocr`, etc.",
        DeprecationWarning,
        stacklevel=4,
    )


# Map of legacy `oideachais.data_platform.<X>` → new `oideachais.<X>`.
_LEGACY_TO_NEW = {
    "dlt_sources": "oideachais.dlt_sources",
    "dlt_utils": "oideachais.dlt_utils",
    "dagster_defs": "oideachais.dagster_defs",
    "ocr": "oideachais.ocr",
    "baml_src": "oideachais.baml_src",
    "agents": "oideachais.agents",
    "api": "oideachais.api",
    "subjects": "oideachais.subjects",
    "memory": "oideachais.memory",
    "graph": "oideachais.graph",
    "cognee_integration": "oideachais.cognee_integration",
    "dagster_assets": "oideachais.dagster_assets",
    "cocoindex_flows": "oideachais.cocoindex_flows",
}


class _LegacyDataPlatformFinder(importlib.abc.MetaPathFinder):
    """Intercept imports of `oideachais.data_platform.<X>` and raise a clear error."""

    LEGACY_PREFIX = "oideachais.data_platform."

    def find_spec(self, fullname, path, target=None):
        if not fullname.startswith(self.LEGACY_PREFIX):
            return None
        _warn_once()
        sub = fullname[len(self.LEGACY_PREFIX):]
        # Only intercept the *first* segment (matches `_LEGACY_TO_NEW` keys).
        first = sub.split(".", 1)[0]
        if first in _LEGACY_TO_NEW:
            new_target = _LEGACY_TO_NEW[first]
        else:
            new_target = f"oideachais.{first}"
        # Synthesise a "module not found" spec that points at the new path.
        # Returning `None` would let Python raise a generic
        # `ModuleNotFoundError`; we use a custom exception to make the
        # migration message impossible to miss.
        raise ImportError(
            f"`{fullname}` is deprecated and the legacy "
            f"`oideachais/data_platform/` subdirectory has been removed "
            f"(Phase 3.6, 2026-06-13). Update your import to the new "
            f"top-level package: `{new_target}` (or, for the full path, "
            f"`{new_target}{sub[len(first):]}`)."
        )


# Register the finder once. We register at the FRONT of sys.meta_path so
# it intercepts before the default finders.
if not any(isinstance(f, _LegacyDataPlatformFinder) for f in sys.meta_path):
    _finder = _LegacyDataPlatformFinder()
    sys.meta_path.insert(0, _finder)


def __getattr__(name: str):
    """PEP 562: attribute access on `oideachais.data_platform` is deprecated."""
    _warn_once()
    if name in _LEGACY_TO_NEW:
        new_target = _LEGACY_TO_NEW[name]
        raise ImportError(
            f"`oideachais.data_platform.{name}` is deprecated and the legacy "
            f"`oideachais/data_platform/` subdirectory has been removed "
            f"(Phase 3.6, 2026-06-13). Update your import to the new "
            f"top-level package: `{new_target}`."
        )
    raise AttributeError(
        f"module 'oideachais.data_platform' has no attribute {name!r}. "
        f"This legacy namespace was removed in Phase 3.6. "
        f"Use the new top-level packages instead."
    )


# Make `import oideachais.data_platform` resolve to this module
sys.modules.setdefault("oideachais.data_platform", sys.modules[__name__])
