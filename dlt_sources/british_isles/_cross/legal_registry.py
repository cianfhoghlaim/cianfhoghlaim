"""dlt_sources.british_isles._cross.legal_registry — BACKWARD-COMPAT SHIM.

Per the **2026-09-XX-ciandlithe-initial-carveout-v1** openspec change
(the Phase 3.1 first real carve-out from cianfhoghlaim → ciandlíthe).

The British Isles legal data has been carved out of cianfhoghlaim into
ciandlíthe (the dedicated British-Isles-legal sister repo). The
canonical home is now:

    dlt_sources._cross.legal_registry           # in ciandlíthe
    dlt_sources.law.<jurisdiction>.*            # in ciandlíthe (8 BI jurisdictions)

This module is a **backward-compatibility shim** that re-exports from
the ciandlíthe canonical home and emits a ``DeprecationWarning`` so
existing cianfhoghlaim callers (which import from
``dlt_sources.british_isles._cross.legal_registry``) keep working but
are nudged to migrate to the canonical import path.

## Migration

OLD (cianfhoghlaim, deprecated as of 2026-09-XX):

    from dlt_sources.british_isles._cross.legal_registry import (
        bi_legal_registry_source,
        LegalRegistryJurisdictionPipeline,
        LegalCohortRow,
        BI_LEGAL_SOURCE_DEFAULTS,
    )

NEW (ciandlíthe, canonical):

    from ciandlithe.dlt_sources._cross.legal_registry import (
        bi_legal_registry_source,
        LegalRegistryJurisdictionPipeline,
        LegalCohortRow,
        BI_LEGAL_SOURCE_DEFAULTS,
    )

## Per-PR reciprocal mirror

Per the **2026-08-24-dlt-sources-to-multi-repo-scaffold-v1** parent
change §15 (per-PR reciprocal mirror), changes to the canonical
``dlt_sources._cross.legal_registry`` in ciandlíthe will trigger a
reciprocal PR on cianfhoghlaim that updates this shim.
"""
from __future__ import annotations

import warnings
from typing import Any


# Emit the DeprecationWarning at import time (module-level __getattr__
# would delay it to first attribute access — module-level is louder and
# matches the per-PR mirror's expectation that the shim is dead).
warnings.warn(
    (
        "dlt_sources.british_isles._cross.legal_registry is deprecated as of "
        "2026-09-XX (the 2026-09-XX-ciandlithe-initial-carveout-v1 carve-out). "
        "Use ciandlithe.dlt_sources._cross.legal_registry instead. "
        "This shim will be removed once all cianfhoghlaim callers have migrated "
        "(tracked in the ciandlithe-initial-carveout post-carve-out report)."
    ),
    DeprecationWarning,
    stacklevel=2,
)


# ─── Lazy re-export from ciandlíthe ────────────────────────────────────
#
# We use __getattr__ so the import only fires when an attribute is
# actually accessed. This means the DeprecationWarning fires at
# module-import time (above) AND the ciandlithe import only fires
# when a caller actually accesses one of the re-exported names —
# matching the per-PR mirror's expectation that the shim is a
# thin pass-through.


_LAZY_ATTRS: dict[str, str] = {
    "bi_legal_registry_source": "ciandlithe.dlt_sources._cross.legal_registry.bi_legal_registry_source",
    "LegalRegistryJurisdictionPipeline": "ciandlithe.dlt_sources._cross.legal_registry.LegalRegistryJurisdictionPipeline",
    "LegalCohortRow": "ciandlithe.dlt_sources._cross.legal_registry.LegalCohortRow",
    "BI_LEGAL_SOURCE_DEFAULTS": "ciandlithe.dlt_sources._cross.legal_registry.BI_LEGAL_SOURCE_DEFAULTS",
    "_bi_jurisdiction_law_sources": "ciandlithe.dlt_sources._cross.legal_registry._bi_jurisdiction_law_sources",
}


def __getattr__(name: str) -> Any:
    """Lazy attribute access — delegates to ciandlíthe canonical home."""
    if name in _LAZY_ATTRS:
        import importlib

        module_path, _, attr_name = _LAZY_ATTRS[name].rpartition(".")
        module = importlib.import_module(module_path)
        value = getattr(module, attr_name)
        # Cache on the module so subsequent accesses don't re-import.
        globals()[name] = value
        return value
    raise AttributeError(
        f"module 'dlt_sources.british_isles._cross.legal_registry' has no attribute {name!r} "
        f"(the canonical home is ciandlithe.dlt_sources._cross.legal_registry)"
    )


__all__ = list(_LAZY_ATTRS.keys())