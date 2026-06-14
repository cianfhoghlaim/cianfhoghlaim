"""Legacy `oideachais.*` namespace shim.

Per AGENTS.md rule "Zero Absolute Namespaces in Data Pipelines":

> Never import `oideachais.data_platform...` from within the data platform itself.
> Always use relative or local package imports.

This package exists ONLY to provide a clear migration path for external
consumers that still use the old `oideachais.data_platform.*` path. The
data platform code now lives at the top level of the `oideachais/`
package (`dlt_sources/`, `dlt_utils/`, `dagster_defs/`, `ocr/`, etc.) and
all in-tree code has been migrated to relative imports.

This shim is intentionally minimal — it does NOT eagerly import any of
the new top-level packages. It delegates to the inner
`oideachais.oideachais.data_platform` shim (see
`oideachais/oideachais/data_platform/__init__.py`) which emits a
DeprecationWarning and a clear ImportError pointing at the new path.

`oideachais.core` is a separate stub package — see `oideachais/core/__init__.py`.
"""

from __future__ import annotations

import sys


def __getattr__(name: str):
    """PEP 562: resolve `oideachais.data_platform` lazily via the inner shim."""
    if name == "data_platform":
        from oideachais.oideachais import data_platform as _shim
        sys.modules.setdefault("oideachais.data_platform", _shim)
        return _shim
    raise AttributeError(f"module 'oideachais' has no attribute {name!r}")


# Register oideachais.core in sys.modules so `from oideachais.core import X` works
import oideachais.core  # noqa: E402
sys.modules.setdefault("oideachais.core", oideachais.core)
