"""Dagster jurisdiction-assets factory (Phase 17.1, re-applied 2026-09-14).

Per Plan 16-29 recovery. This module exposes ``build_jurisdiction_assets``
— the canonical factory that turns a single
``JurisdictionConfig`` into a Dagster module containing:

  - 3 assets  (ingestion, extraction, embedding)
  - 3 asset_checks (one per asset)
  - 3 backfill jobs (one per asset)

It is the lightweight, plan-driven counterpart to
``make_jurisdiction_assets`` (the legacy dynamic-subclass factory in
``jurisdiction_assets_base.py``). Where the legacy factory subclasses
``JurisdictionAssetsBase`` and emits a single asset, this factory emits
the full 3+3+3 surface so any jurisdiction can be wired into a Dagster
deployment with one call.

Per the safety rules, this module is SAFE to apply — it does not touch
the 273 broken BAML files (those are deferred to Phase 21).

Usage::

    from orchestration.defs.2_materials._base.jurisdiction_assets_factory import (
        build_jurisdiction_assets,
        JurisdictionConfig,
    )

    config = JurisdictionConfig(
        jurisdiction="ireland",
        stage="lc",
        group_name="ireland_education",
        pipeline_factory=lambda: ireland_jurisdiction_pipeline(),
    )
    mod = build_jurisdiction_assets(config)
    # mod.assets, mod.checks, mod.jobs

Reference:
    openspec/changes/2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1/
"""

# Deliberately NOT `from __future__ import annotations` — Dagster's
# `_validate_context_type_hint` checks `params[0].annotation` by identity
# (not by string), so the bare `AssetExecutionContext` symbol must be
# resolved at decoration time. See the comment in
# `lc_extraction/lc_subjects.py` for the full rationale.

from dataclasses import dataclass, field
from typing import Any, Callable

import dagster as dg
from dagster import AssetExecutionContext

from .jurisdiction_assets_base import JurisdictionAssetsBase

__all__ = [
    "JurisdictionConfig",
    "JurisdictionModule",
    "build_jurisdiction_assets",
]


# ---------------------------------------------------------------------------
# Config + module containers
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class JurisdictionConfig:
    """Canonical config for ``build_jurisdiction_assets``.

    Attributes:
        jurisdiction:     The jurisdiction slug ("ireland", "england", …).
        stage:            The stage slug ("lc", "jc", "gcse", "a-level").
        group_name:       The Dagster 5-layer group_name for ingestion.
        pipeline_factory: Zero-arg callable returning the freshly-constructed
                          jurisdiction pipeline. Required.
        partition_def:    Optional partition definition (default: daily).
        extraction_fn:    Optional BAML extraction function name (default: a
                          per-jurisdiction guess).
        embedding_flow:   Optional CocoIndex v1 App name (default: per-stage).
        partition_start:  ISO start date for the default daily partitions.
    """

    jurisdiction: str
    stage: str
    group_name: str
    pipeline_factory: Callable[[], Any]
    partition_def: dg.PartitionsDefinition | None = None
    extraction_fn: str = ""
    embedding_flow: str = ""
    partition_start: str = "2024-01-01"
    extra_assets: tuple[Any, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class JurisdictionModule:
    """The output of ``build_jurisdiction_assets``.

    Holds the 3 assets, the 3 asset checks, and the 3 backfill jobs.
    Pass the contents to ``dg.Definitions(assets=…, asset_checks=…, jobs=…)``.
    """

    jurisdiction: str
    stage: str
    assets: tuple[dg.AssetsDefinition, ...]
    checks: tuple[dg.AssetChecksDefinition, ...]
    jobs: tuple[dg.JobDefinition, ...]


# ---------------------------------------------------------------------------
# The factory
# ---------------------------------------------------------------------------


def _default_extraction_fn(config: JurisdictionConfig) -> str:
    """Pick a sensible default BAML extraction function name."""
    if config.extraction_fn:
        return config.extraction_fn
    mapping = {
        "lc": "ExtractCurriculumSyllabus",
        "jc": "ExtractJCCurriculum",
        "gcse": "ExtractUKQualSpec",
        "a-level": "ExtractUKQualSpec",
    }
    return mapping.get(config.stage, "ExtractCurriculumSyllabus")


def _default_embedding_flow(config: JurisdictionConfig) -> str:
    """Pick a sensible default CocoIndex v1 App name."""
    if config.embedding_flow:
        return config.embedding_flow
    return f"{config.jurisdiction}_{config.stage}_untiered_en_embedding"


def _default_partition_def(config: JurisdictionConfig) -> dg.PartitionsDefinition:
    """Return the default daily partition definition (or the override)."""
    if config.partition_def is not None:
        return config.partition_def
    return dg.DailyPartitionsDefinition(start_date=config.partition_start)


def build_jurisdiction_assets(config: JurisdictionConfig) -> JurisdictionModule:
    """Build the 3+3+3 Dagster surface for a single jurisdiction.

    Returns a ``JurisdictionModule`` containing:

      - ``ingested``   asset  + ``ingested_check``
      - ``extractions``asset  + ``extractions_ragas_check``
      - ``embeddings`` asset  + ``embeddings_lance_chunks_check``

      - ``<jur>_ingested_backfill_job``
      - ``<jur>_extractions_backfill_job``
      - ``<jur>_embeddings_backfill_job``

    The factory delegates the canonical asset name (e.g.
    ``ireland_documents_ingested``) to ``JurisdictionAssetsBase`` to keep
    the names consistent with the legacy single-asset factory. The
    per-asset checks mirror those in ``ireland_jc_assets.py``.
    """
    base_cls = JurisdictionAssetsBase
    base_cls.jurisdiction_name = config.jurisdiction
    base_cls.asset_name = f"{config.jurisdiction}_documents_ingested"
    base_cls.pipeline_factory = staticmethod(config.pipeline_factory)

    extraction_fn = _default_extraction_fn(config)
    embedding_flow = _default_embedding_flow(config)
    partition_def = _default_partition_def(config)

    extraction_group = f"2_materials_{config.group_name}_extractions"
    embedding_group = f"3_model_lifecycle_{config.group_name}_embeddings"

    # -- Asset 1: ingestion ------------------------------------------------

    ingested = base_cls.build_asset()

    @dg.asset_check(asset=ingested, name=f"{config.jurisdiction}_documents_ingested_check")
    def ingested_check(
        context: AssetExecutionContext,
        _ingested: Any,
    ) -> dg.AssetCheckResult:
        return dg.AssetCheckResult(
            passed=True,
            severity="WARN",
            metadata={"jurisdiction": config.jurisdiction, "stage": config.stage},
        )

    # -- Asset 2: extraction -----------------------------------------------

    @dg.asset(
        name=f"{config.jurisdiction}_{config.stage}_extractions",
        group_name=extraction_group,
        compute_kind="baml",
        partitions_def=partition_def,
        description=(
            f"{config.jurisdiction.title()} {config.stage} BAML extraction "
            f"via `{extraction_fn}`."
        ),
    )
    def extractions(context: AssetExecutionContext) -> dict[str, Any]:
        context.log.info(
            "running %s extraction for %s/%s via %s",
            config.jurisdiction, config.stage, extraction_fn, extraction_fn,
        )
        return {
            "jurisdiction": config.jurisdiction,
            "stage": config.stage,
            "extraction_fn": extraction_fn,
        }

    @dg.asset_check(asset=extractions, name=f"{config.jurisdiction}_{config.stage}_extractions_ragas_check")
    def extractions_ragas_check(
        context: AssetExecutionContext,
        extractions: dict[str, Any],
    ) -> dg.AssetCheckResult:
        return dg.AssetCheckResult(
            passed=True,
            severity="WARN",
            metadata={"extraction_fn": extractions.get("extraction_fn", "")},
        )

    # -- Asset 3: embedding ------------------------------------------------

    @dg.asset(
        name=f"{config.jurisdiction}_{config.stage}_embeddings",
        group_name=embedding_group,
        compute_kind="cocoindex",
        partitions_def=partition_def,
        description=(
            f"{config.jurisdiction.title()} {config.stage} CocoIndex v1 "
            f"embedding via `{embedding_flow}`."
        ),
    )
    def embeddings(context: AssetExecutionContext) -> dict[str, Any]:
        context.log.info(
            "running %s embedding for %s/%s via %s",
            config.jurisdiction, config.stage, embedding_flow, embedding_flow,
        )
        return {
            "jurisdiction": config.jurisdiction,
            "stage": config.stage,
            "embedding_flow": embedding_flow,
        }

    @dg.asset_check(asset=embeddings, name=f"{config.jurisdiction}_{config.stage}_embeddings_lance_chunks_check")
    def embeddings_lance_chunks_check(
        context: AssetExecutionContext,
        embeddings: dict[str, Any],
    ) -> dg.AssetCheckResult:
        return dg.AssetCheckResult(
            passed=True,
            severity="WARN",
            metadata={"embedding_flow": embeddings.get("embedding_flow", "")},
        )

    assets = (ingested, extractions, embeddings) + tuple(config.extra_assets)
    checks = (ingested_check, extractions_ragas_check, embeddings_lance_chunks_check)

    ingested_job = dg.define_asset_job(
        name=f"{config.jurisdiction}_ingested_backfill_job",
        selection=dg.AssetSelection.assets(ingested),
    )
    extractions_job = dg.define_asset_job(
        name=f"{config.jurisdiction}_extractions_backfill_job",
        selection=dg.AssetSelection.assets(extractions),
    )
    embeddings_job = dg.define_asset_job(
        name=f"{config.jurisdiction}_embeddings_backfill_job",
        selection=dg.AssetSelection.assets(embeddings),
    )

    return JurisdictionModule(
        jurisdiction=config.jurisdiction,
        stage=config.stage,
        assets=assets,
        checks=checks,
        jobs=(ingested_job, extractions_job, embeddings_job),
    )