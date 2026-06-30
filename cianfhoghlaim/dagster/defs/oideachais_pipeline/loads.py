"""
oideachais_pipeline — DLT source factory for Domain 2.

Wires the 4 Ireland education cycles (early_childhood, primary,
junior_cycle, senior_cycle) + the 4 UK nations (England, Scotland,
Wales, Northern Ireland) + 3 Crown Dependencies (IoM, Jersey, Guernsey)
into a single DltLoadCollectionComponent. This is the per-domain
implementation of the oideachais-pipeline Layer 1 ingestion pattern
(per openspec/specs/oideachais-pipeline/spec.md).

Compared to celtic-asset-generation (Domain 1), this domain focuses
on the 4-stage cycle ingestion (early childhood → senior cycle) with
MultiPartitions by (language, subject).
"""
from __future__ import annotations

from typing import Iterator

import dlt

from cianfhoghlaim.core.dlt._oideachais_dlt_utils.destinations import get_dlt_destination


# The 4 education cycles × 2 languages (en, ga) × the canonical subjects.
# (The 33+ subject list is too long to inline here; the factory pulls
# the canonical subject list from the source_registry at runtime.)
EDUCATION_CYCLES: list[str] = [
    "early_childhood",
    "primary",
    "junior_cycle",
    "senior_cycle",
]

LANGUAGES: list[str] = ["en", "ga"]


@dlt.source(name="oideachais_pipeline_education")
def oideachais_pipeline_source() -> Iterator:
    """Yield one DLT resource per Ireland education cycle.

    The factory pattern keeps the asset graph in one
    `oideachais_pipeline` group with per-cycle resources.
    """
    from cianfhoghlaim.core.dlt._oideachais_dlt_utils.source_factory import (
        get_default_factory,
    )

    factory = get_default_factory()

    # The 4 Ireland education cycles (NCCA / SEC / OIDE / Scoilnet).
    for cycle in EDUCATION_CYCLES:
        source_id = f"ie.education.{cycle}"
        try:
            yield factory.source(source_id)()
        except KeyError:
            # Some cycles may not be present in the source registry
            # during incremental migration; skip gracefully.
            continue


# Single shared DLT pipeline for the entire Component.
oideachais_pipeline_dlt_pipeline = dlt.pipeline(
    pipeline_name="oideachais_pipeline",
    destination=get_dlt_destination(),
    dataset_name="oideachais_pipeline",
    dev_mode=False,
)


__all__ = [
    "EDUCATION_CYCLES",
    "LANGUAGES",
    "oideachais_pipeline_source",
    "oideachais_pipeline_dlt_pipeline",
]
