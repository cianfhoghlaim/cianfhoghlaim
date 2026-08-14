"""Crown Dependencies generic Dagster assets — RE-EXPORT SHIM.

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change,
the 3 Crown Dependencies (Jersey + Guernsey + Isle of Man) have been
**promoted to proper per-jurisdiction directories**. The canonical
Dagster assets for each Crown Dependency are now in:
- `orchestration/defs/2_materials/jersey_education/jersey_assets.py`
- `orchestration/defs/2_materials/guernsey_education/guernsey_assets.py`
- `orchestration/defs/2_materials/isle_of_man_education/isle_of_man_assets.py`

This file is kept as a **re-export shim** for backward compatibility
with the BIEP v3 deferred openspec change
`2026-07-31-biep-v3-crown-dependencies-v1/` and the BIEP v3
orchestration assets that may still import the
`crown_dependencies_*` asset names.

Reference: openspec/changes/2026-07-31-biep-v3-crown-dependencies-v1/
Reference: openspec/changes/2026-08-13-biep-v3-systematic-download-ireland-england-v1/
"""
from __future__ import annotations

import logging
import importlib

logger = logging.getLogger(__name__)

# Re-export the 3 per-jurisdiction Dagster assets via the per-jurisdiction proper files
_jersey_module = importlib.import_module(
    "orchestration.defs.materials.jersey_education.jersey_assets".replace(
        "materials", "2_materials"
    )
)

_guernsey_module = importlib.import_module(
    "orchestration.defs.materials.guernsey_education.guernsey_assets".replace(
        "materials", "2_materials"
    )
)

_iom_module = importlib.import_module(
    "orchestration.defs.materials.isle_of_man_education.isle_of_man_assets".replace(
        "materials", "2_materials"
    )
)


# Backward-compat stubs — the legacy crown_dependencies_* names raise
# NotImplementedError to point users at the per-jurisdiction proper
# assets + the new mise tasks (biep:v3:m8, m9, m10).

def crown_dependencies_documents_ingested():
    raise NotImplementedError(
        "crown_dependencies_documents_ingested is a re-export shim. "
        "Use the per-jurisdiction assets (jersey_documents_ingested, "
        "guernsey_documents_ingested, isle_of_man_documents_ingested) "
        "or the mise tasks (biep:v3:m8, m9, m10) instead."
    )


def crown_dependencies_extractions():
    raise NotImplementedError(
        "crown_dependencies_extractions is a re-export shim. "
        "Use the per-jurisdiction assets instead."
    )


def crown_dependencies_embeddings():
    raise NotImplementedError(
        "crown_dependencies_embeddings is a re-export shim. "
        "Use the per-jurisdiction assets instead."
    )


def crown_dependencies_extractions_ragas_check():
    raise NotImplementedError(
        "crown_dependencies_extractions_ragas_check is a re-export shim."
    )


# Aliases REMOVED 2026-08-13. These re-exported the per-jurisdiction assets
# for backward compatibility, but `dg.load_defs()` auto-discovers the
# ORIGINALS directly from `2_materials/<jurisdiction>_education/`. Having
# both at module scope produced 18 duplicate asset keys, which made
# `Definitions.validate_loadable()` raise and the code location show ZERO
# assets. Import from the owning module instead.

__all__ = [
    "crown_dependencies_documents_ingested",
    "crown_dependencies_extractions",
    "crown_dependencies_embeddings",
    "crown_dependencies_extractions_ragas_check",
]
