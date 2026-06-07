"""Legacy `oideachais.*` namespace shim.

Per AGENTS.md rule "Zero Absolute Namespaces in Data Pipelines":

> Never import `oideachais.data_platform...` from within the data platform itself.
> Always use relative or local package imports.

This package exists ONLY to satisfy the broken `from oideachais.data_platform.X`
imports scattered through the codebase. New code MUST use relative imports.

The shim is intentionally minimal — it does NOT eagerly import the
data_platform tree. Instead, it registers a custom `__getattr__` at the
package level (PEP 562) that resolves `oideachais.data_platform` on first
access to the top-level `data_platform` module.

`oideachais.core` is a separate stub package — see `oideachais/core/__init__.py`.
"""

from __future__ import annotations

import sys
import types


def __getattr__(name: str):
    """PEP 562: resolve `oideachais.data_platform` lazily on first access."""
    if name == "data_platform":
        import data_platform  # noqa: F401
        # Re-register so future `import oideachais.data_platform` works
        sys.modules.setdefault("oideachais.data_platform", data_platform)
        return data_platform
    raise AttributeError(f"module 'oideachais' has no attribute {name!r}")


# Re-export oideachais.core as a sub-attribute
def _resolve_core():
    import oideachais.core
    return oideachais.core


# Register oideachais.core in sys.modules so `from oideachais.core import X` works
import oideachais.core  # noqa: E402
sys.modules.setdefault("oideachais.core", oideachais.core)
