"""England cross-board comparator Dagster component.

Per the 2026-08-03-biep-v3-orchestration-components-partitions-sensors-v1 change.

Joins AQA + OCR + Edexcel for the same subject + qualification_level
and surfaces spec differences.
"""
# Deliberately NOT `from __future__ import annotations` — see the identical
# note in biep_subject_component.py (Resolvable + postponed annotations
# crashes on `.__name__` of a string).
import logging
from dagster import Component, ComponentLoadContext, Definitions

from .biep_subject_component import BIEPSubjectComponent

logger = logging.getLogger(__name__)


class EnglandCrossBoardComparatorComponent(BIEPSubjectComponent):
    """The canonical England cross-board comparator Component.

    See the identical note on EnglandBoardSubjectComponent: the single real
    comparators/defs.yaml describes the comparator asset group as a whole,
    not one subject, and never sets subject_slug — so it's optional here.
    The richer descriptive fields are accepted/stored, not yet consumed.
    """

    def __init__(
        self,
        subject_slug: str | None = None,
        qualification_level: str = "gcse",
        baml_function: str | None = None,
        source_assets: list[str] | None = None,
        partition_strategy: str | None = None,
        asset_check_kind: str | None = None,
        namespace_pattern: str | None = None,
        dagster_group_name_prefix: str | None = None,
        join_strategy: str | None = None,
        diff_strategy: str | None = None,
        show_history: bool | None = None,
        years_comparison_window: int | None = None,
        automation_cron: str | None = None,
    ):
        super().__init__(jurisdiction="england")
        self.subject_slug = subject_slug
        self.qualification_level = qualification_level
        self.baml_function = baml_function
        self.source_assets = source_assets
        self.partition_strategy = partition_strategy
        self.asset_check_kind = asset_check_kind
        self.namespace_pattern = namespace_pattern
        self.dagster_group_name_prefix = dagster_group_name_prefix
        self.join_strategy = join_strategy
        self.diff_strategy = diff_strategy
        self.show_history = show_history
        self.years_comparison_window = years_comparison_window
        self.automation_cron = automation_cron

    def build_defs(self, context: ComponentLoadContext) -> Definitions:
        logger.info(
            "EnglandCrossBoardComparatorComponent: england.cross_board.%s.%s",
            self.subject_slug, self.qualification_level,
        )
        # Delegating to super().build_defs() here (the previous behaviour)
        # returned the SAME england_documents_ingested/_extractions/
        # _embeddings asset trio EnglandBoardSubjectComponent already
        # produces — a comparator asset group has no business redeclaring
        # ingestion/extraction assets, and doing so collided on duplicate
        # asset keys once the registry had real data (confirmed live:
        # DagsterInvalidDefinitionError). No real cross-board-diff logic
        # exists yet (the class's own docstring: "Joins AQA + OCR + Edexcel
        # ... and surfaces spec differences" — not implemented anywhere).
        # Returning empty rather than fabricating comparator assets that
        # don't do comparison.
        return Definitions()


__all__ = ["EnglandCrossBoardComparatorComponent"]
