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
# Deliberately NOT `from __future__ import annotations`: Dagster's Resolvable
# derives each Component's YAML schema from `inspect.signature(__init__)`
# without resolving forward references, so postponed-evaluation string
# annotations (e.g. "str" instead of the type str) crash deep inside
# dagster.components.resolved.base with `AttributeError: 'str' object has
# no attribute '__name__'`. Python 3.13 supports `X | Y` union syntax
# natively, so this file doesn't need the future import anyway.
import logging
from typing import Any

from dagster import Component, ComponentLoadContext, Definitions, Resolvable

try:
    from dlt_sources.british_isles._cross.registry_api import query_by_jurisdiction
    REGISTRY_AVAILABLE = True
except ImportError:
    REGISTRY_AVAILABLE = False
    query_by_jurisdiction = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)


class BIEPSubjectComponent(Component, Resolvable):
    """The canonical BIEP v3 Component for the British Isles subject registry.

    Reads `cianfhoghlaim.education._registry.subjects` filtered by
    `jurisdiction` (one of the 8 British Isles jurisdictions) and
    creates the per-jurisdiction asset partition set.

    Subclasses `Resolvable` (in addition to `Component`) so `dg.load_defs()`
    can instantiate this — and EnglandBoardSubjectComponent /
    EnglandCrossBoardComparatorComponent, which inherit resolvability through
    this base — from a YAML `type:` + `attributes:` block. Component alone
    does not provide YAML resolution in Dagster 1.13; every field must come
    from a fully type-annotated `__init__` (already true here), a dataclass,
    a pydantic model, or a `@record`.
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
        #
        # `2_materials` is not a valid Python identifier (the tokenizer reads
        # `2_` as an incomplete numeric literal), so these must be dynamic
        # imports via importlib — same workaround orchestration/definitions.py
        # already uses for the same digit-prefixed layer directory. The
        # literal `from orchestration.defs.2_materials...` form previously
        # here was a dormant SyntaxError: nothing imported this module before
        # it was wired into orchestration/components/__init__.py.
        import importlib

        _ireland_mod = importlib.import_module(
            "orchestration.defs.2_materials.ireland_education.generic_ireland_assets"
        )
        _england_mod = importlib.import_module(
            "orchestration.defs.2_materials.england_education.generic_england_assets"
        )

        # Per-jurisdiction asset lookup
        asset_lookup = {
            "ireland": (
                _ireland_mod.ireland_documents_ingested,
                _ireland_mod.ireland_extractions,
                _ireland_mod.ireland_embeddings,
            ),
            "england": (
                _england_mod.england_documents_ingested,
                _england_mod.england_extractions,
                _england_mod.england_embeddings,
            ),
        }
        # For SCT/WLS/NI + Crown Dependencies, the assets are aggregated
        # in their respective modules
        try:
            _sct_wls_ni_mod = importlib.import_module(
                "orchestration.defs.2_materials.sct_wls_ni_education.generic_sct_wls_ni_assets"
            )
            asset_lookup["scotland"] = asset_lookup["wales"] = asset_lookup["northern_ireland"] = (
                _sct_wls_ni_mod.sct_wls_ni_documents_ingested,
                _sct_wls_ni_mod.sct_wls_ni_extractions,
                _sct_wls_ni_mod.sct_wls_ni_embeddings,
            )
        except ImportError:
            pass
        try:
            _crown_dep_mod = importlib.import_module(
                "orchestration.defs.2_materials.crown_dependencies_education.generic_crown_dependencies_assets"
            )
            asset_lookup["jersey"] = asset_lookup["guernsey"] = asset_lookup["isle_of_man"] = (
                _crown_dep_mod.crown_dependencies_documents_ingested,
                _crown_dep_mod.crown_dependencies_extractions,
                _crown_dep_mod.crown_dependencies_embeddings,
            )
        except ImportError:
            pass

        assets = asset_lookup.get(self.jurisdiction, (None, None, None))
        return Definitions(assets=[a for a in assets if a is not None])


__all__ = ["BIEPSubjectComponent"]
