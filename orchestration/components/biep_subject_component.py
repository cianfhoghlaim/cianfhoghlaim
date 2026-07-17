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
            logger.warning(
                "BIEPSubjectComponent: registry not available; returning empty Definitions"
            )
            return Definitions()

        rows = query_by_jurisdiction(self.jurisdiction)
        logger.info(
            "BIEPSubjectComponent: %s — discovered %d rows from registry",
            self.jurisdiction, len(rows),
        )
        # Real implementation imports the 3 generic asset functions
        # from orchestration.defs.2_materials.<jurisdiction>_education
        # and wires them with the registry rows. The 3 generic asset
        # modules are the canonical per-jurisdiction assets.
        return Definitions()  # placeholder; real impl wires the 3 assets


__all__ = ["BIEPSubjectComponent"]
