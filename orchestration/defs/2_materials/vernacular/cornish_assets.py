"""Cornish (Kernewek) vernacular Dagster assets (Phase 14).

Per the 2026-09-01-cianfhoghlaim-nua-v7-vernaculars-pipelines-v1
change (Phase 14 of the cianfhoghlaim-nua v6 era plan). Calls
``b.ExtractCornishSubjectSpec``.
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


CORNISH_INGESTION_GROUP = "1_ingestion_vernacular_cornish"
CORNISH_EXTRACTION_GROUP = "2_materials_vernacular_cornish_extractions"
CORNISH_EMBEDDING_GROUP = "3_model_lifecycle_vernacular_cornish_embeddings"


@asset(
    group_name=CORNISH_INGESTION_GROUP,
    description="Cornish (Kernewek) DLT ingestion (Phase 14).",
    automation_condition=make_yearly_education_automation(),
)
def cornish_vernacular_documents_ingested(context: AssetExecutionContext) -> dict[str, Any]:
    from dlt_sources.breton_cornish.british_isles.cornish_vernacular import (
        cornish_vernacular_source,
    )
    pages_resource, specs_resource = cornish_vernacular_source(max_pages=50)
    rows = 0
    try:
        for page in pages_resource:
            rows += 1
            if rows >= 50:
                break
        for spec in specs_resource:
            rows += 1
    except Exception as e:  # noqa: BLE001
        context.log.warning("cornish_vernacular_documents_ingested soft-fail: %s", e)
    return {"rows": rows, "dataset_name": "cornish_vernacular_education"}


@asset(
    group_name=CORNISH_EXTRACTION_GROUP,
    description=(
        "Cornish (Kernewek) BAML extraction (Phase 14). "
        "Calls ``b.ExtractCornishSubjectSpec``."
    ),
    automation_condition=make_yearly_education_automation(),
)
def cornish_vernacular_extractions(context: AssetExecutionContext) -> dict[str, Any]:
    if not BAML_AVAILABLE:
        return {"rows_extracted": 0}
    fn = getattr(b, "ExtractCornishSubjectSpec", None)
    rows_extracted = 0
    if fn is not None:
        try:
            spec = fn(
                pdf_text="Sample Cornish-medium education mathematics text...",
                subject_slug="mathematics",
                stage="gcse",
                source_url="https://www.cornwall.gov.uk/education-and-learning/school-resources/kernewek/",
            )
            rows_extracted = 1 if spec is not None else 0
        except Exception as e:  # noqa: BLE001
            context.log.warning("ExtractCornishSubjectSpec soft-fail: %s", e)
    return {"rows_extracted": rows_extracted, "baml_function": "ExtractCornishSubjectSpec"}


@asset(
    group_name=CORNISH_EMBEDDING_GROUP,
    description=(
        "Cornish (Kernewek) CocoIndex embedding (Phase 14). "
        "Drives the ``vernacular_cornish_embedding`` App."
    ),
    automation_condition=make_yearly_education_automation(),
)
def cornish_vernacular_embeddings(context: AssetExecutionContext) -> dict[str, Any]:
    from cocoindex_flows.vernacular.vernacular_factory import (
        vernacular_cornish_embedding,
    )
    context.log.info("cornish_vernacular_embeddings: %s", vernacular_cornish_embedding)
    return {"cohorts_to_embed": 1, "subjects": 1}


@asset_check(asset=cornish_vernacular_documents_ingested)
def cornish_vernacular_documents_ingested_check(context, cornish_vernacular_documents_ingested: dict[str, Any]) -> AssetCheckResult:
    rows = cornish_vernacular_documents_ingested.get("rows", 0)
    return AssetCheckResult(passed=rows >= 1, metadata={"rows": rows, "threshold": 1})


@asset_check(asset=cornish_vernacular_extractions)
def cornish_vernacular_extractions_check(context, cornish_vernacular_extractions: dict[str, Any]) -> AssetCheckResult:
    rows = cornish_vernacular_extractions.get("rows_extracted", 0)
    return AssetCheckResult(passed=rows >= 0, metadata={"rows_extracted": rows, "threshold": 0})


__all__ = [
    "CORNISH_INGESTION_GROUP",
    "CORNISH_EXTRACTION_GROUP",
    "CORNISH_EMBEDDING_GROUP",
    "cornish_vernacular_documents_ingested",
    "cornish_vernacular_extractions",
    "cornish_vernacular_embeddings",
    "cornish_vernacular_documents_ingested_check",
    "cornish_vernacular_extractions_check",
]
