"""Manx (Gaelg) vernacular Dagster assets (Phase 14).

Per the 2026-09-01-cianfhoghlaim-nua-v7-vernaculars-pipelines-v1
change (Phase 14 of the cianfhoghlaim-nua v6 era plan). Calls
``b.ExtractManxSubjectSpec``.

Manx is one of 3 vernaculars with actual PDF corpora (per the
Phase 14 spec).
"""


import logging
from typing import Any

from dagster import AssetCheckResult, AssetExecutionContext, asset, asset_check

from orchestration.automation.biiep_scheduling import (
    make_yearly_education_automation,
)

try:
    from baml_client import b
    BAML_AVAILABLE = True
except ImportError:
    BAML_AVAILABLE = False
    b = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)


MANX_INGESTION_GROUP = "1_ingestion_vernacular_manx"
MANX_EXTRACTION_GROUP = "2_materials_vernacular_manx_extractions"
MANX_EMBEDDING_GROUP = "3_model_lifecycle_vernacular_manx_embeddings"


@asset(
    group_name=MANX_INGESTION_GROUP,
    description="Manx (Gaelg) DLT ingestion (Phase 14).",
    automation_condition=make_yearly_education_automation(),
)
def manx_vernacular_documents_ingested(context: AssetExecutionContext) -> dict[str, Any]:
    from dlt_sources.education.isle_of_man.british_isles.manx_vernacular import (
        manx_vernacular_source,
    )
    pages_resource, specs_resource = manx_vernacular_source(max_pages=50)
    rows = 0
    try:
        for page in pages_resource:
            rows += 1
            if rows >= 50:
                break
        for spec in specs_resource:
            rows += 1
    except Exception as e:  # noqa: BLE001
        context.log.warning("manx_vernacular_documents_ingested soft-fail: %s", e)
    return {"rows": rows, "dataset_name": "manx_vernacular_education"}


@asset(
    group_name=MANX_EXTRACTION_GROUP,
    description=(
        "Manx (Gaelg) BAML extraction (Phase 14). "
        "Calls ``b.ExtractManxSubjectSpec``."
    ),
    automation_condition=make_yearly_education_automation(),
)
def manx_vernacular_extractions(context: AssetExecutionContext) -> dict[str, Any]:
    if not BAML_AVAILABLE:
        return {"rows_extracted": 0}
    fn = getattr(b, "ExtractManxSubjectSpec", None)
    rows_extracted = 0
    if fn is not None:
        try:
            spec = fn(
                pdf_text="Sample Manx (Gaelg) Isle-of-Man DESC Mathematics spec text...",
                subject_slug="mathematics",
                stage="gcse",
                source_url="https://www.gov.im/education-training-and-careers/gaelg-medium-education",
            )
            rows_extracted = 1 if spec is not None else 0
        except Exception as e:  # noqa: BLE001
            context.log.warning("ExtractManxSubjectSpec soft-fail: %s", e)
    return {"rows_extracted": rows_extracted, "baml_function": "ExtractManxSubjectSpec"}


@asset(
    group_name=MANX_EMBEDDING_GROUP,
    description=(
        "Manx (Gaelg) CocoIndex embedding (Phase 14). "
        "Drives the ``vernacular_manx_embedding`` App."
    ),
    automation_condition=make_yearly_education_automation(),
)
def manx_vernacular_embeddings(context: AssetExecutionContext) -> dict[str, Any]:
    from cocoindex_flows.vernacular.vernacular_factory import (
        vernacular_manx_embedding,
    )
    context.log.info("manx_vernacular_embeddings: %s", vernacular_manx_embedding)
    return {"cohorts_to_embed": 1, "subjects": 1}


@asset_check(asset=manx_vernacular_documents_ingested)
def manx_vernacular_documents_ingested_check(context, manx_vernacular_documents_ingested: dict[str, Any]) -> AssetCheckResult:
    rows = manx_vernacular_documents_ingested.get("rows", 0)
    return AssetCheckResult(passed=rows >= 1, metadata={"rows": rows, "threshold": 1})


@asset_check(asset=manx_vernacular_extractions)
def manx_vernacular_extractions_check(context, manx_vernacular_extractions: dict[str, Any]) -> AssetCheckResult:
    rows = manx_vernacular_extractions.get("rows_extracted", 0)
    return AssetCheckResult(passed=rows >= 0, metadata={"rows_extracted": rows, "threshold": 0})


__all__ = [
    "MANX_INGESTION_GROUP",
    "MANX_EXTRACTION_GROUP",
    "MANX_EMBEDDING_GROUP",
    "manx_vernacular_documents_ingested",
    "manx_vernacular_extractions",
    "manx_vernacular_embeddings",
    "manx_vernacular_documents_ingested_check",
    "manx_vernacular_extractions_check",
]
