"""England per-board per-subject Dagster component.

Per the 2026-08-03-biep-v3-orchestration-components-partitions-sensors-v1 change.
"""
# Deliberately NOT `from __future__ import annotations` — see the identical
# note in biep_subject_component.py (Resolvable + postponed annotations
# crashes on `.__name__` of a string).
import logging
from dagster import Component, ComponentLoadContext, Definitions

from .biep_subject_component import BIEPSubjectComponent

logger = logging.getLogger(__name__)


class EnglandBoardSubjectComponent(BIEPSubjectComponent):
    """The canonical England per-board (AQA / OCR / Edexcel) per-subject Component.

    The 3 real defs.yaml files this loads today (aqa/edexcel/ocr) describe a
    whole board, not one subject — per-subject fan-out happens inside
    build_defs() via the registry query, not via a subject_slug the YAML
    never actually sets — so subject_slug/qualification_level are optional
    here, and the richer BIEP-v2-era descriptive fields the YAML carries
    (baml_function, source_asset, partition_strategy, asset_check_kind,
    namespace_pattern, cocoindex_app, cognify_dataset, automation_cron,
    dagster_group_name_prefix) are accepted and stored for forward
    compatibility but not yet consumed by build_defs() — deliberately not
    over-engineered per-board asset specialization in this pass; see the
    KCG local-lakehouse plan's Phase 6 for where that's picked up.
    """

    def __init__(
        self,
        exam_board: str,
        subject_slug: str | None = None,
        qualification_level: str = "gcse",
        baml_function: str | None = None,
        source_asset: str | None = None,
        source_assets: list[str] | None = None,
        partition_strategy: str | None = None,
        asset_check_kind: str | None = None,
        namespace_pattern: str | None = None,
        cocoindex_app: str | None = None,
        cognify_dataset: str | None = None,
        automation_cron: str | None = None,
        dagster_group_name_prefix: str | None = None,
    ):
        super().__init__(jurisdiction="england")
        self.exam_board = exam_board
        self.subject_slug = subject_slug
        self.qualification_level = qualification_level
        self.baml_function = baml_function
        self.source_asset = source_asset
        self.source_assets = source_assets
        self.partition_strategy = partition_strategy
        self.asset_check_kind = asset_check_kind
        self.namespace_pattern = namespace_pattern
        self.cocoindex_app = cocoindex_app
        self.cognify_dataset = cognify_dataset
        self.automation_cron = automation_cron
        self.dagster_group_name_prefix = dagster_group_name_prefix

    def build_defs(self, context: ComponentLoadContext) -> Definitions:
        if self.exam_board not in ("aqa", "ocr", "edexcel"):
            raise ValueError(f"Unknown exam board: {self.exam_board!r}")
        logger.info(
            "EnglandBoardSubjectComponent: england.%s.%s.%s",
            self.exam_board, self.qualification_level, self.subject_slug,
        )
        # BIEPSubjectComponent.build_defs() returns the same
        # england_documents_ingested/_extractions/_embeddings functions
        # that dg.load_defs()'s own file-based auto-discovery ALSO picks
        # up directly from generic_england_assets.py sitting in this same
        # directory tree (confirmed live via the component-tree printout:
        # "generic_england_assets.py (loaded)" appears as its own sibling
        # entry alongside aqa/edexcel/ocr/comparators). Returning them
        # again here double-registers the identical asset keys — confirmed
        # live via DagsterInvalidDefinitionError: "Duplicate asset key:
        # AssetKey(['england_documents_ingested'])" — regardless of how
        # many of the 3 board instances do it, since even ONE collides
        # with the file-based auto-discovery copy. Ireland's equivalent
        # subtree doesn't hit this because it has no competing
        # Component-level declaration of the same functions. Returning
        # empty here, relying entirely on the auto-discovered copy.
        return Definitions()


__all__ = ["EnglandBoardSubjectComponent"]
