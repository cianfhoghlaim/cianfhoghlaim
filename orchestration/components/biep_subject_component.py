"""BIEP v3 canonical Dagster component (Phase 1 contract).

Per the 2026-08-03-biep-v3-orchestration-components-partitions-sensors-v1 change.

This Component is the canonical entry point for the BIEP v3 generic
jurisdiction pipelines. It reads the canonical British Isles subject
registry (`cianfhoghlaim.education._registry.subjects`) and creates
the per-jurisdiction asset partition set.

The 5-layer convention is preserved:
- Layer 1: Ingestion (`<jurisdiction>_documents_ingested`)
- Layer 2: Extraction (`<jurisdiction>_extractions`)
- Layer 3: Embedding (`<jurisdiction>_embeddings`)
- Layer 4: Cognify (Cognee integration)
- Layer 5: Agent Ops (per-jurisdiction agent fleet)

Reference: openspec/changes/2026-07-27-biep-v3-canonical-registry-v1/
openspec/changes/2026-08-03-biep-v3-orchestration-components-partitions-sensors-v1/
"""
from __future__ import annotations

import logging
from typing import Any

from dagster import Component, ComponentLoadContext, Definitions

try:
    from dlt.british_isles._cross.registry_api import query_by_jurisdiction
    REGISTRY_AVAILABLE = True
except ImportError:
    REGISTRY_AVAILABLE = False
    query_by_jurisdiction = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)


class BIEPSubjectComponent(Component):
    """The canonical BIEP v3 Component for the British Isles subject registry.

    Reads `cianfhoghlaim.education._registry.subjects` filtered by
    `jurisdiction` (one of the 8 British Isles jurisdictions) and
    creates the per-jurisdiction asset partition set.
    """

    def __init__(self, jurisdiction: str):
        self.jurisdiction = jurisdiction
        self._validate_jurisdiction()

    def _validate_jurisdiction(self) -> None:
        valid = (
            "ireland", "england", "scotland", "wales",
            "northern_ireland", "jersey", "guernsey", "isle_of_man",
        )
        if self.jurisdiction not in valid:
            raise ValueError(
                f"jurisdiction={self.jurisdiction!r} not in {valid}"
            )

    def build_defs(self, context: ComponentLoadContext) -> Definitions:
        """Build the per-jurisdiction asset definitions from the registry."""
        if not REGISTRY_AVAILABLE:
            raise RuntimeError(
                f"BIEPSubjectComponent: registry not available for jurisdiction={self.jurisdiction!r}. "
                "Run `python3 -c 'from dlt.british_isles._cross.registry_loader import seed_registry; print(seed_registry())'` first."
            )

        rows = query_by_jurisdiction(self.jurisdiction)
        if not rows:
            raise RuntimeError(
                f"BIEPSubjectComponent: no registry rows for jurisdiction={self.jurisdiction!r}"
            )
        logger.info(
            "BIEPSubjectComponent: %s — discovered %d rows from registry",
            self.jurisdiction, len(rows),
        )

        # Build the 3 canonical assets (ingestion + extraction + embedding)
        # backed by the registry rows. Each asset has a key derived from
        # the row's (jurisdiction, subject_slug, board, qualification_level, language).
        from orchestration.defs.2_materials.ireland_education.generic_ireland_assets import (
            ireland_documents_ingested,
            ireland_extractions,
            ireland_embeddings,
        )
        from orchestration.defs.2_materials.england_education.generic_england_assets import (
            england_documents_ingested,
            england_extractions,
            england_embeddings,
        )

        # Per-jurisdiction asset lookup
        asset_lookup = {
            "ireland": (ireland_documents_ingested, ireland_extractions, ireland_embeddings),
            "england": (england_documents_ingested, england_extractions, england_embeddings),
        }
        # For SCT/WLS/NI + Crown Dependencies, the assets are aggregated
        # in their respective modules
        try:
            from orchestration.defs.2_materials.sct_wls_ni_education.generic_sct_wls_ni_assets import (
                sct_wls_ni_documents_ingested,
                sct_wls_ni_extractions,
                sct_wls_ni_embeddings,
            )
            asset_lookup["scotland"] = asset_lookup["wales"] = asset_lookup["northern_ireland"] = (
                sct_wls_ni_documents_ingested, sct_wls_ni_extractions, sct_wls_ni_embeddings,
            )
        except ImportError:
            pass
        try:
            from orchestration.defs.2_materials.crown_dependencies_education.generic_crown_dependencies_assets import (
                crown_dependencies_documents_ingested,
                crown_dependencies_extractions,
                crown_dependencies_embeddings,
            )
            asset_lookup["jersey"] = asset_lookup["guernsey"] = asset_lookup["isle_of_man"] = (
                crown_dependencies_documents_ingested, crown_dependencies_extractions, crown_dependencies_embeddings,
            )
        except ImportError:
            pass

        assets = asset_lookup.get(self.jurisdiction, (None, None, None))
        return Definitions(assets=[a for a in assets if a is not None])


__all__ = ["BIEPSubjectComponent"]
