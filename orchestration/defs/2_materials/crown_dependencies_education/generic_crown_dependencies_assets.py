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
jersey_documents_ingested = _jersey_module.jersey_documents_ingested
jersey_extractions = _jersey_module.jersey_extractions
jersey_embeddings = _jersey_module.jersey_embeddings
jersey_documents_ingested_check = _jersey_module.jersey_documents_ingested_check
jersey_extractions_ragas_check = _jersey_module.jersey_extractions_ragas_check
jersey_lance_chunks_check = _jersey_module.jersey_lance_chunks_check

_guernsey_module = importlib.import_module(
    "orchestration.defs.materials.guernsey_education.guernsey_assets".replace(
        "materials", "2_materials"
    )
)
guernsey_documents_ingested = _guernsey_module.guernsey_documents_ingested
guernsey_extractions = _guernsey_module.guernsey_extractions
guernsey_embeddings = _guernsey_module.guernsey_embeddings
guernsey_documents_ingested_check = _guernsey_module.guernsey_documents_ingested_check
guernsey_extractions_ragas_check = _guernsey_module.guernsey_extractions_ragas_check
guernsey_lance_chunks_check = _guernsey_module.guernsey_lance_chunks_check

_iom_module = importlib.import_module(
    "orchestration.defs.materials.isle_of_man_education.isle_of_man_assets".replace(
        "materials", "2_materials"
    )
)
isle_of_man_documents_ingested = _iom_module.isle_of_man_documents_ingested
isle_of_man_extractions = _iom_module.isle_of_man_extractions
isle_of_man_embeddings = _iom_module.isle_of_man_embeddings
isle_of_man_documents_ingested_check = _iom_module.isle_of_man_documents_ingested_check
isle_of_man_extractions_ragas_check = _iom_module.isle_of_man_extractions_ragas_check
isle_of_man_lance_chunks_check = _iom_module.isle_of_man_lance_chunks_check


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


__all__ = [
    "crown_dependencies_documents_ingested",
    "crown_dependencies_extractions",
    "crown_dependencies_embeddings",
    "crown_dependencies_extractions_ragas_check",
    # Re-export the per-jurisdiction proper assets for backward compat
    "jersey_documents_ingested", "jersey_extractions", "jersey_embeddings",
    "jersey_documents_ingested_check", "jersey_extractions_ragas_check", "jersey_lance_chunks_check",
    "guernsey_documents_ingested", "guernsey_extractions", "guernsey_embeddings",
    "guernsey_documents_ingested_check", "guernsey_extractions_ragas_check", "guernsey_lance_chunks_check",
    "isle_of_man_documents_ingested", "isle_of_man_extractions", "isle_of_man_embeddings",
    "isle_of_man_documents_ingested_check", "isle_of_man_extractions_ragas_check", "isle_of_man_lance_chunks_check",
]
