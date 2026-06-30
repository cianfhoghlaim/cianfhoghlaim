"""Business Dagster Asset Group — Cianfhoghlaim Educational MMO.

6 assets in `group_name="business"` following the standard
raw/structured/quest_pack/embedding/cognify/dashboard pattern.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any

import dagster as dg
import structlog

logger = structlog.get_logger(__name__)


# Partition definitions
bus_levels = dg.StaticPartitionsDefinition(["hl", "ol"])
bus_languages = dg.StaticPartitionsDefinition(["en", "ga"])
bus_partitions = dg.MultiPartitionsDefinition(
    {"level": bus_levels, "language": bus_languages}
)
bus_full_partitions = dg.StaticPartitionsDefinition(["hl_en", "hl_ga", "ol_en", "ol_ga"])


# Asset 1: business_syllabus_raw
@dg.asset(
    group_name="business",
    partitions_def=bus_partitions,
    description="DLT ingestion of NCCA Business syllabus PDFs into DuckLake",
    compute_kind="dlt",
)
def business_syllabus_raw(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    """Ingest the Business PDFs into DuckLake via the DLT source."""
    import dlt

    from cianfhoghlaim.dlt.british_isles.ireland.education.subjects.business import bus_source

    level = context.partition_key.keys_by_dimension["level"]
    language = context.partition_key.keys_by_dimension["language"]

    pipeline = dlt.pipeline(
        pipeline_name=f"business_syllabus_{level}_{language}",
        destination=dlt.destinations.duckdb(
            credentials=os.environ.get("BUS_DUCKDB_PATH", "./data/business.duckdb")
        ),
        dataset_name=f"business_{level}_{language}",
    )
    load_info = pipeline.run(bus_source(language=language, level=level))

    return dg.MaterializeResult(
        metadata={
            "pipeline": pipeline.pipeline_name,
            "dataset_name": pipeline.dataset_name,
            "load_packages": len(load_info.load_packages),
            "level": level,
            "language": language,
        }
    )


# Asset 2: business_syllabus_structured
@dg.asset(
    group_name="business",
    partitions_def=bus_partitions,
    description="BAML ExtractLeavingCertSyllabus per Business PDF",
    compute_kind="baml",
)
def business_syllabus_structured(
    context: dg.AssetExecutionContext,
    business_syllabus_raw: dict[str, Any],
) -> dg.MaterializeResult:
    """Run BAML extraction on each raw PDF row."""
    from cianfhoghlaim.baml_client import b

    level = context.partition_key.keys_by_dimension["level"]
    language = context.partition_key.keys_by_dimension["language"]

    rows = []
    for raw_row in business_syllabus_raw.get("rows", []):
        text = raw_row.get("text", "")
        try:
            result = b.ExtractLeavingCertSyllabus(pdf_text=text)
            rows.append({"sha256": raw_row["sha256"], "level": level, "language": language, "syllabus": result.model_dump()})
        except Exception as e:
            logger.warning(f"BAML extract failed for {raw_row.get('sha256')}: {e}")

    return dg.MaterializeResult(metadata={"rows": rows, "row_count": len(rows)})


# Asset 3: business_quest_pack
@dg.asset(
    group_name="business",
    partitions_def=bus_full_partitions,
    description=f"BAML {baml_qpack} per {title} level",
    compute_kind="baml",
)
def business_quest_pack(
    context: dg.AssetExecutionContext,
    business_syllabus_structured: dict[str, Any],
) -> dg.MaterializeResult:
    """Generate a quest pack for the syllabus."""
    from cianfhoghlaim.baml_client import b

    level_full = context.partition_key
    level = level_full.replace(f"_en", "") if "_" in level_full else level_full

    corpus_dir = Path(os.environ.get(
        "CIANFHOGHLAIM_ROOT",
        str(Path(__file__).resolve().parents[3]
    )) / "cianfhoghlaim" / "leaving_certificate" / "business"

    rows = []
    for struct_row in business_syllabus_structured.get("rows", []):
        try:
            pack = b.GenerateBusinessQuestPack(
                syllabus=struct_row["syllabus"],
                past_papers=[],
                marking_schemes=[],
                level=struct_row["level"],
            )
            rows.append({"level": struct_row["level"], "pack": pack.model_dump()})
        except Exception as e:
            logger.warning(f"Quest pack failed for level {struct_row['level']}: {e}")

    return dg.MaterializeResult(metadata={"packs": rows, "pack_count": len(rows)})


# Asset 4: business_embedding
@dg.asset(
    group_name="business",
    partitions_def=bus_full_partitions,
    description="CocoIndex v1 embedding of Business syllabus into LanceDB",
    compute_kind="cocoindex",
)
def business_embedding(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    """Run CocoIndex to embed the syllabus into LanceDB."""
    try:
        from cianfhoghlaim.cocoindex.business_embedding import business_embedding as coco_flow
        coco_flow.update()
    except Exception as e:
        logger.warning(f"CocoIndex embedding failed: {e}")

    return dg.MaterializeResult(metadata={"subject": "business"})


# Asset 5: business_cognify
@dg.asset(
    group_name="business",
    description=f"Cognee cognify pass for {title} knowledge graph",
    compute_kind="cognee",
)
def business_cognify(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    """Run Cognee cognify on the embedded syllabus."""
    try:
        from cianfhoghlaim.storage.cognify import cognify_subject
        cognify_subject("business")
    except Exception as e:
        logger.warning(f"Cognee cognify failed: {e}")

    return dg.MaterializeResult(metadata={"subject": "business"})


# Asset 6: business_dashboard
@dg.asset(
    group_name="business",
    description=f"Render {title} marimo notebook",
    compute_kind="marimo",
)
def business_dashboard(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    """Execute the Business marimo dashboard notebook."""
    notebook_path = Path(os.environ.get(
        "CIANFHOGHLAIM_ROOT",
        str(Path(__file__).resolve().parents[3])
    )) / "cianfhoghlaim" / "notebooks" / "dashboards" / "education" / "business_full_pipeline.py"

    if notebook_path.exists():
        try:
            subprocess.run(
                ["marimo", "run", str(notebook_path), "--headless"],
                check=False, timeout=300,
            )
        except Exception as e:
            logger.warning(f"Dashboard render failed: {e}")

    return dg.MaterializeResult(metadata={"subject": "business"})
