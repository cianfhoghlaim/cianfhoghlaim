"""Junior Cycle per-subject Dagster component.

Per the 2026-08-03-biep-v3-orchestration-components-partitions-sensors-v1 change.

The 18 NCCA JC subjects (english + gaeilge + mathematics + ...) each
get a per-subject asset set (Layer 1-5).

Also exports `JuniorCycleShortCourseComponent` (16 JC short courses:
coding, chinese, japanese, russian, polish, lithuanian, portuguese,
arabic, hebrew, philosophy, film_studies, financial_literacy,
media_literacy, personal_professional_development, digital_media,
athletic_studies) and `JuniorCycleCBAComponent` (36 JC CBAs: 18
subjects × 2 CBAs each = Year 2 + Year 3) — both subclassed from
`JuniorCycleSubjectComponent` with subject-type-specific partition
strategies.
"""
# Deliberately NOT `from __future__ import annotations` — Dagster's Resolvable
# derives the YAML schema from real (not postponed-string) type annotations.
# With postponed annotations `get_model_cls()` raises
# `AttributeError: 'str' object has no attribute '__name__'`, which is exactly
# how all three of these Components failed to load.
import logging
from dataclasses import dataclass
from typing import ClassVar

import dagster as dg
from dagster import Component, ComponentLoadContext, Definitions, Resolvable

logger = logging.getLogger(__name__)


# The 18 NCCA Junior Cycle subjects (canonical NCCA 2024 list).
JC_SUBJECTS: tuple[str, ...] = (
    "english", "gaeilge", "mathematics", "irish_history", "geography",
    "science", "business_studies", "french", "german", "spanish",
    "italian", "home_economics", "music", "art", "technology",
    "engineering", "graphics", "wood_technology",
)

# The 16 NCCA Junior Cycle short courses (canonical NCCA 2024 list).
JC_SHORT_COURSES: tuple[str, ...] = (
    "coding", "chinese", "japanese", "russian", "polish", "lithuanian",
    "portuguese", "arabic", "hebrew", "philosophy", "film_studies",
    "financial_literacy", "media_literacy",
    "personal_professional_development", "digital_media",
    "athletic_studies",
)


@dataclass
class _JuniorCycleFactoryBase(Component, Resolvable):
    """Shared base for the three Junior Cycle factory Components.

    WHY A FACTORY, NOT A PER-ITEM COMPONENT
    ---------------------------------------
    These three classes used to take `__init__(subject_slug, language)` — one
    instance per subject — but their `defs.yaml` files have always supplied a
    FACTORY config (`baml_function`, `partition_strategy`, `namespace_pattern`,
    `cognify_dataset`, `automation_cron`) describing all 18 subjects / 16 short
    courses / 36 CBAs at once. The two were never reconcilable, so Dagster
    could not derive a model at all (`AttributeError: 'str' object has no
    attribute '__name__'`, because the module also used postponed annotations)
    and all three files failed to load.

    They now expand their canonical item list into one asset each, mirroring
    `CelticMaterialsComponent`.

    They deliberately do NOT call `BIEPSubjectComponent.build_defs()`. That
    method re-exports `ireland_documents_ingested` / `_extractions` /
    `_embeddings` from `generic_ireland_assets.py`, which `dg.load_defs()`
    already discovers directly from the same directory tree — returning them
    again is one of the sources of the duplicate-asset-key failure that stops
    `Definitions.validate_loadable()`.
    """

    baml_function: str
    source_asset: str
    partition_strategy: str = "by_subject"
    asset_check_kind: str = "row_count"
    namespace_pattern: str = ""
    cocoindex_app: str = ""
    cognify_dataset: str = ""
    automation_cron: str = "0 6 * * *"
    language: str = "en"

    #: Subclass hook — the canonical item slugs this factory expands.
    def _items(self) -> tuple[str, ...]:
        raise NotImplementedError

    #: Subclass hook — asset-name prefix, e.g. "jc" -> jc_<item>_extracted.
    _asset_prefix: ClassVar[str] = "jc"
    _group_suffix: ClassVar[str] = "subjects"

    def build_defs(self, context: ComponentLoadContext) -> Definitions:
        items = self._items()
        logger.info(
            "%s: ireland.jc.%s — expanding %d items",
            type(self).__name__, self._group_suffix, len(items),
        )
        return Definitions(assets=[self._build_item_asset(i) for i in items])

    def _build_item_asset(self, item: str) -> dg.AssetsDefinition:
        """One asset per item. Separate method so each closure captures its
        own `item` rather than the loop's final value."""
        namespace = (
            self.namespace_pattern.format(
                subject=item, course_slug=item, cba_id=item, lang=self.language
            )
            if self.namespace_pattern
            else ""
        )

        @dg.asset(
            name=f"{self._asset_prefix}_{item}_extracted",
            group_name=f"2_materials_junior_cycle_{self._group_suffix}",
            compute_kind="baml",
            description=(
                f"L2 Junior Cycle extraction: {self.baml_function} on "
                f"{self.source_asset} (item={item}, lang={self.language})"
            ),
            automation_condition=dg.AutomationCondition.on_cron(self.automation_cron),
            deps=[dg.AssetDep(dg.AssetKey(self.source_asset.split("/")))],
        )
        def _jc_asset(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
            return dg.MaterializeResult(
                metadata={
                    "item": item,
                    "baml_function": self.baml_function,
                    "source_asset": self.source_asset,
                    "language": self.language,
                    "namespace": namespace,
                    "cocoindex_app": self.cocoindex_app,
                    "cognify_dataset": self.cognify_dataset,
                    "partition_strategy": self.partition_strategy,
                    "layer": "2_materials",
                }
            )

        return _jc_asset


@dataclass
class JuniorCycleSubjectComponent(_JuniorCycleFactoryBase):
    """The canonical Junior Cycle per-subject Component (Ireland) — 18 subjects."""

    #: Graphiti stream spanning all JC subjects (documentation hint).
    cross_subject_graphiti: str = ""

    _asset_prefix: ClassVar[str] = "jc"
    _group_suffix: ClassVar[str] = "subjects"

    def _items(self) -> tuple[str, ...]:
        return JC_SUBJECTS


@dataclass
class JuniorCycleShortCourseComponent(_JuniorCycleFactoryBase):
    """The canonical Junior Cycle short-course Component (Ireland) — 16 courses.

    Per the 2026-07-20-biep-v2-junior-cycle-extraction-v1 change +
    the 2026-08-03-biep-v3-orchestration-components-partitions-sensors-v1
    change. Wired into orchestration/defs/2_materials/junior_cycle/
    short_courses/defs.yaml.
    """

    _asset_prefix: ClassVar[str] = "jc_short_course"
    _group_suffix: ClassVar[str] = "short_courses"

    def _items(self) -> tuple[str, ...]:
        return JC_SHORT_COURSES


@dataclass
class JuniorCycleCBAComponent(_JuniorCycleFactoryBase):
    """The canonical Junior Cycle CBA (Classroom-Based Assessment) Component
    (Ireland) — 18 subjects x 2 CBAs (Year 2 + Year 3) = 36.

    Per the 2026-07-20-biep-v2-junior-cycle-extraction-v1 change +
    the 2026-08-03-biep-v3-orchestration-components-partitions-sensors-v1
    change. Wired into orchestration/defs/2_materials/junior_cycle/
    cbas/defs.yaml.
    """

    #: Template for a CBA id, e.g. "{subject}_{cba_idx}" -> english_1.
    cba_id_pattern: str = "{subject}_{cba_idx}"

    _asset_prefix: ClassVar[str] = "jc_cba"
    _group_suffix: ClassVar[str] = "cbas"

    def _items(self) -> tuple[str, ...]:
        return tuple(
            self.cba_id_pattern.format(subject=subject, cba_idx=idx)
            for subject in JC_SUBJECTS
            for idx in (1, 2)
        )


__all__ = [
    "JuniorCycleSubjectComponent",
    "JuniorCycleShortCourseComponent",
    "JuniorCycleCBAComponent",
    "JC_SUBJECTS",
    "JC_SHORT_COURSES",
]
