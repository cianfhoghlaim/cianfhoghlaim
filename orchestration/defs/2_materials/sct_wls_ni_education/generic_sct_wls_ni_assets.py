"""SCT + WLS + NI generic Dagster assets — RE-EXPORT SHIM.

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change,
the 3 jurisdictions (Scotland + Wales + Northern Ireland) have been
**promoted to proper per-jurisdiction directories**. The canonical
Dagster assets for each jurisdiction are now in:
- `orchestration/defs/2_materials/scotland_education/scotland_assets.py`
- `orchestration/defs/2_materials/wales_education/wales_assets.py`
- `orchestration/defs/2_materials/northern_ireland_education/northern_ireland_assets.py`

This file is kept as a **re-export shim** for backward compatibility
with the BIEP v3 deferred openspec change
`2026-07-30-biep-v3-sct-wls-ni-v1/` and the BIEP v3 orchestration
assets that may still import the `sct_wls_ni_*` asset names.

Because Python doesn't allow numeric segments in module paths, the
canonical home uses a different import path. The 3 per-jurisdiction
Dagster assets are exposed via the BIEP v3 orchestration loaders
(which use a different import strategy — see the per-jurisdiction
asset files directly).

Reference: openspec/changes/2026-07-30-biep-v3-sct-wls-ni-v1/
Reference: openspec/changes/2026-08-13-biep-v3-systematic-download-ireland-england-v1/
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

# The 3 per-jurisdiction assets live in the per-jurisdiction proper
# files. To avoid the Python 2_materials import issue, we re-import
# them via the per-jurisdiction module names.
import importlib

# Re-export the 3 per-jurisdiction Dagster assets via the per-jurisdiction proper files
_scotland_module = importlib.import_module(
    "orchestration.defs.materials.scotland_education.scotland_assets".replace(
        "materials", "2_materials"
    )
)

_wales_module = importlib.import_module(
    "orchestration.defs.materials.wales_education.wales_assets".replace(
        "materials", "2_materials"
    )
)

_ni_module = importlib.import_module(
    "orchestration.defs.materials.northern_ireland_education.northern_ireland_assets".replace(
        "materials", "2_materials"
    )
)


# Backward-compat stubs — the legacy sct_wls_ni_* names raise
# NotImplementedError to point users at the per-jurisdiction proper
# assets + the new mise tasks (biep:v3:m5, m6, m7).

def sct_wls_ni_documents_ingested():
    raise NotImplementedError(
        "sct_wls_ni_documents_ingested is a re-export shim. "
        "Use the per-jurisdiction assets (scotland_documents_ingested, "
        "wales_documents_ingested, northern_ireland_documents_ingested) "
        "or the mise tasks (biep:v3:m5, m6, m7) instead."
    )


def sct_wls_ni_extractions():
    raise NotImplementedError(
        "sct_wls_ni_extractions is a re-export shim. "
        "Use the per-jurisdiction assets instead."
    )


def sct_wls_ni_embeddings():
    raise NotImplementedError(
        "sct_wls_ni_embeddings is a re-export shim. "
        "Use the per-jurisdiction assets instead."
    )


def sct_wls_ni_extractions_ragas_check():
    raise NotImplementedError(
        "sct_wls_ni_extractions_ragas_check is a re-export shim."
    )


# Aliases REMOVED 2026-08-13. These re-exported the per-jurisdiction assets
# for backward compatibility, but `dg.load_defs()` auto-discovers the
# ORIGINALS directly from `2_materials/<jurisdiction>_education/`. Having
# both at module scope produced 18 duplicate asset keys, which made
# `Definitions.validate_loadable()` raise and the code location show ZERO
# assets. Import from the owning module instead.

__all__ = [
    "sct_wls_ni_documents_ingested",
    "sct_wls_ni_extractions",
    "sct_wls_ni_embeddings",
    "sct_wls_ni_extractions_ragas_check",
]
