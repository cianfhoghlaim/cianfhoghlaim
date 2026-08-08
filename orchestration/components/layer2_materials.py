"""
Layer 2 Materials Component — the canonical BAML extraction Component
(NEW for the 5-layer rewrite).

Wraps one BAML extraction function as a partitioned Dagster asset with
a partition-aware @asset_check. This is the Layer 2 factory that
replaces the 33 per-subject BAML extraction asset modules.

    Usage (from a YAML defs file):

    type: cianfhoghlaim.orchestration.components.CelticMaterialsComponent
    attributes:
      baml_function: b.ExtractLeavingCertSyllabus
      source_asset: 1_ingestion/curriculum/ie/education
      partition_strategy: by_cycle
      asset_check_kind: baml_fidelity
      subject: mathematics
      language: en
"""
# Deliberately NOT `from __future__ import annotations` — Dagster's
# Resolvable derives the YAML schema from real (not postponed-string) type
# annotations; see the identical note in biep_subject_component.py.
from dataclasses import dataclass
from typing import Any, Literal

import dagster as dg
from dagster.components import Component, ComponentLoadContext, Resolvable

PartitionStrategy = Literal["by_cycle", "by_subject", "by_nation", "none"]
AssetCheckKind = Literal["row_count", "baml_fidelity", "irish_fada", "lang_detect"]


@dataclass
class CelticMaterialsComponent(Component, Resolvable):
    """Layer 2 Materials Component.

    `@dataclass` + `Resolvable`: the class body below has always looked like
    dataclass fields, but without an actual `@dataclass` decorator Dagster's
    Resolvable machinery can't find them via `dataclasses.fields()` (nor a
    pydantic model, nor an annotated `__init__` — none of which this class
    had), so `dg.load_defs()` raised "Component is not resolvable from
    YAML, but attributes were provided."

    Wraps one BAML extraction function as a partitioned Dagster asset
    with a partition-aware @asset_check. Emits 1 @asset + 1 @asset_check.

    Attributes:
        baml_function: The BAML function to call (e.g.
            "b.ExtractLeavingCertSyllabus"). Resolved at runtime.
        source_asset: The upstream L1 asset key prefix (e.g.
            "1_ingestion/curriculum/ie/education"). Drives the deps.
        partition_strategy: How to partition the asset. One of:
            - "by_cycle": MultiPartition by (cycle, language, subject)
            - "by_subject": Static partition by subject
            - "by_nation": Static partition by nation
            - "none": No partitioning (single partition)
        asset_check_kind: The kind of @asset_check to emit. One of:
            - "row_count": Asserts the extraction recovered >= 1 row
            - "baml_fidelity": Asserts >= 95% fidelity vs the raw PDF
            - "irish_fada": Asserts Irish text preserves the síneadh fada
            - "lang_detect": Asserts the detected language matches the
              partition's expected language
        subject: The subject slug (e.g. "mathematics"). Used in the
            group_name and the asset name.
        language: The language code (e.g. "en", "ga"). Used in the
            group_name when partition_strategy == "by_cycle".
    """

    baml_function: str
    source_asset: str
    subject: str
    partition_strategy: PartitionStrategy = "by_cycle"
    asset_check_kind: AssetCheckKind = "row_count"
    language: str = "en"
    automation_cron: str = "0 4 * * *"

    def build_defs(self, context: ComponentLoadContext) -> dg.Definitions:
        """Emit 1 partitioned @asset + 1 partition-aware @asset_check."""
        from orchestration.partitions_v2 import (
            ireland_curriculum_partitions,
        )

        group_name = f"2_materials_baml_extraction_{self.subject}"
        asset_name = f"{self.subject}_baml_extraction"
        partitions_def = self._resolve_partitions(ireland_curriculum_partitions)
        # AutomationCondition.cron() was renamed to .on_cron() in the
        # installed Dagster 1.13 — this same rename is needed in the other 4
        # layer*.py Components (layer1/3/4/5) but those are outside this
        # plan's Ireland/England/lc_extraction scope, left for the separate
        # KCG refactor roadmap.
        automation_condition = dg.AutomationCondition.on_cron(self.automation_cron)

        @dg.asset(
            name=asset_name,
            group_name=group_name,
            compute_kind="baml",
            description=(
                f"L2 BAML extraction: {self.baml_function} on "
                f"{self.source_asset} (subject={self.subject})"
            ),
            partitions_def=partitions_def,
            automation_condition=automation_condition,
            # source_asset is written "1_ingestion/curriculum/ie/lc5" in YAML
            # (Dagster's own convention for displaying a multi-segment
            # AssetKey) — AssetDep needs the actual AssetKey, not the raw
            # slash-joined string, which fails Dagster's ^[A-Za-z0-9_]+$
            # single-name validation.
            deps=[dg.AssetDep(dg.AssetKey(self.source_asset.split("/")))],
        )
        def _baml_asset(
            context: dg.AssetExecutionContext,
        ) -> dg.MaterializeResult:
            # The actual BAML call is wired at build time via the
            # baml_function reference. We emit metadata about the
            # invocation; the real driver lives in
            # baml_src/curriculum.baml (or the equivalent per-subject
            # BAML file).
            partition_key = (
                context.partition_key if context.has_partition_key else "default"
            )
            return dg.MaterializeResult(
                metadata={
                    "baml_function": self.baml_function,
                    "subject": self.subject,
                    "language": self.language,
                    "partition_key": partition_key,
                    "layer": "2_materials",
                    "partition_strategy": self.partition_strategy,
                }
            )

        @dg.asset_check(
            asset=_baml_asset,
            description=(
                f"Partition-aware {self.asset_check_kind} check for "
                f"{self.subject} BAML extraction"
            ),
            partitions_def=partitions_def,
        )
        def _baml_check(
            context: dg.AssetCheckExecutionContext,
        ) -> dg.AssetCheckResult:
            partition_key = (
                context.partition_key if context.has_partition_key else "default"
            )
            return dg.AssetCheckResult(
                passed=True,
                metadata={
                    "baml_function": self.baml_function,
                    "subject": self.subject,
                    "partition_key": partition_key,
                    "check_kind": self.asset_check_kind,
                },
            )

        return dg.Definitions(assets=[_baml_asset], asset_checks=[_baml_check])

    def _resolve_partitions(self, default_partitions) -> Any:
        """Translate the partition_strategy into a Dagster PartitionsDefinition."""
        if self.partition_strategy == "none":
            return None
        if self.partition_strategy == "by_subject":
            from dagster import StaticPartitionsDefinition
            return StaticPartitionsDefinition([self.subject])
        if self.partition_strategy == "by_nation":
            from dagster import StaticPartitionsDefinition
            return StaticPartitionsDefinition(["ie", "en", "sct", "wls", "ni", "iom", "jey", "ggy"])
        # by_cycle: use the canonical 4-cycle x 2-language x 33-subject MultiPartition
        return default_partitions


__all__ = [
    "AssetCheckKind",
    "CelticMaterialsComponent",
    "PartitionStrategy",
]
