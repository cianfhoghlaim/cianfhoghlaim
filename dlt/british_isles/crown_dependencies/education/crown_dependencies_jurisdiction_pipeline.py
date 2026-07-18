"""Generic Crown Dependencies pipeline (BIEP v3).

Per the 2026-07-31-biep-v3-crown-dependencies-v1 change +
2026-08-10-biep-v3-preflight-bug-fixes-v1 inheritance refactor.

Handles the 3 Crown Dependencies (Jersey + Guernsey + Isle of Man) via
a single generic factory. The 3 jurisdictions use the English GCSE +
A-Level system (with a small number of additional local qualifications
like French Baccalauréat in Jersey).

Covers:
  - Jersey: 30 subjects × 4 levels (GCSE + A-Level + IB + French Bac) × 2 langs = 240
  - Guernsey: 30 subjects × 4 levels × 2 langs = 240
  - Isle of Man: 30 subjects × 4 levels × 2 langs = 240

= **720 unique qualifications** across the 3 Crown Dependencies.

## KCG patterns used
- ibis (per `.agents/skills/ibis/SKILL.md`) — every query uses
  ``ibis.duckdb.connect()`` (NO raw ``duckdb.connect``).
- dlt (per `.agents/skills/dlt/SKILL.md`) — the canonical destination
  factory at ``dlt.common.destinations_cianfhoghlaim`` is used.
- JurisdictionPipelineBase (per the 2026-08-10 preflight change) —
  inherits shared boilerplate.

Reference: openspec/changes/2026-07-31-biep-v3-crown-dependencies-v1/
"""
from __future__ import annotations

import logging

from dlt.british_isles._cross.jurisdiction_pipeline_base import (
    JurisdictionPipelineBase,
)

logger = logging.getLogger(__name__)

CROWN_DEPENDENCIES: tuple[str, ...] = ("jersey", "guernsey", "isle_of_man")


class CrownDependenciesJurisdictionPipeline(JurisdictionPipelineBase):
    """Crown Dependencies (Jersey / Guernsey / Isle of Man) pipeline (BIEP v3)."""

    STAGE = "gcse"
    VALID_JURISDICTIONS = CROWN_DEPENDENCIES

    def build_pipeline_resource(self):
        """Yield one row per (board, subject, level) cohort from the registry."""
        from dlt.british_isles._cross.registry_api import query_by_jurisdiction

        subjects = query_by_jurisdiction(self.jurisdiction)
        if not subjects:
            raise ValueError(
                f"No subjects found in the registry for "
                f"jurisdiction={self.jurisdiction!r}. "
                "Run seed_registry() first."
            )

        logger.info(
            "crown_dependencies_jurisdiction_pipeline: discovered %d subjects "
            "for %r",
            len(subjects), self.jurisdiction,
        )

        for row in subjects:
            yield self.subject_to_row(row, self.STAGE)


# Pre-built instances for the 3 Crown Dependencies.
crown_jersey_pipeline = CrownDependenciesJurisdictionPipeline("jersey")
crown_guernsey_pipeline = CrownDependenciesJurisdictionPipeline("guernsey")
crown_isle_of_man_pipeline = CrownDependenciesJurisdictionPipeline("isle_of_man")


def crown_dependencies_jurisdiction_pipeline(
    jurisdiction: str,
    dataset_name: str | None = None,
    use_md: bool = True,
):
    """The canonical generic Crown Dependencies DLT pipeline factory.

    Handles the 3 Crown Dependencies (Jersey + Guernsey + Isle of Man)
    via a single factory function. The jurisdiction argument selects
    which registry rows to materialise.
    """
    return CrownDependenciesJurisdictionPipeline(jurisdiction, use_md=use_md)


__all__ = [
    "CrownDependenciesJurisdictionPipeline",
    "crown_dependencies_jurisdiction_pipeline",
    "crown_jersey_pipeline",
    "crown_guernsey_pipeline",
    "crown_isle_of_man_pipeline",
    "CROWN_DEPENDENCIES",
]