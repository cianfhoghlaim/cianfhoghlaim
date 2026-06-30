"""
celtic_asset_generation — DLT source factory for Domain 1.

Wires the 8 Celtic-nation education DLT sources (Ireland,
Northern Ireland, England, Scotland, Wales, Isle of Man, Jersey,
Guernsey) plus the 5 Celtic corpus sources (Dúchas, Canuint,
Téarma, Logainm, Universal Dependencies) into a single
DltLoadCollectionComponent. This is the per-domain
implementation of the celtic-asset-generation 5-stage pipeline
described in openspec/specs/celtic-asset-generation/spec.md.

The 5 stages (handled by the 3 KCG Components):
1. BAML extraction          → CelticDltSourceComponent (this file)
2. CocoIndex v1 embedding   → CelticCocoindexV1Component
3. Cognee cognify           → wired in cognify defs (Domain 4)
4. Graphiti temporal memory → wired in cognify defs (Domain 4)
5. LanceDB vector HNSW      → CelticLancedbHnswComponent
"""
from __future__ import annotations

from typing import Iterator

import dlt

from cianfhoghlaim.core.dlt._oideachais_dlt_utils.destinations import get_dlt_destination


# The 8 Celtic-nation education DLT source IDs.
# Sourced from cianfhoghlaim/sources/_oideachais_sources.yaml.
CELTIC_NATION_EDUCATION_SOURCES: list[str] = [
    "ie.education.ncca",
    "ie.education.examinations",
    "ie.education.oide",
    "ie.education.scoilnet",
    "ni.education.ccea",
    "ni.education.deni",
    "ni.education.etini",
    "ni.education.nisra",
    "en.education.dfe",
    "en.education.ofsted",
    "en.education.gias",
    "en.education.aqa",
    "en.education.edexcel",
    "en.education.ocr",
    "sct.education.cfe",
    "sct.education.sqa",
    "sct.education.simd",
    "wls.education.cfw",
    "wls.education.wjec",
    "wls.education.estyn",
    "wls.education.statswales",
    "iom.education.desc",
    "jey.education.govje",
    "ggy.education.govgg",
]


@dlt.source(name="celtic_asset_generation_education")
def celtic_education_source() -> Iterator:
    """Yield one DLT resource per Celtic-nation education source.

    The factory pattern keeps the asset graph in one
    `celtic_asset_generation` group with per-source
    resource-level metadata.
    """
    from cianfhoghlaim.core.dlt._oideachais_dlt_utils.source_factory import (
        get_default_factory,
    )

    factory = get_default_factory()
    for source_id in CELTIC_NATION_EDUCATION_SOURCES:
        yield factory.source(source_id)()


# Single shared DLT pipeline for the entire Component.
celtic_asset_generation_pipeline = dlt.pipeline(
    pipeline_name="celtic_asset_generation",
    destination=get_dlt_destination(),
    dataset_name="celtic_asset_generation",
    dev_mode=False,
)


__all__ = [
    "CELTIC_NATION_EDUCATION_SOURCES",
    "celtic_education_source",
    "celtic_asset_generation_pipeline",
]
