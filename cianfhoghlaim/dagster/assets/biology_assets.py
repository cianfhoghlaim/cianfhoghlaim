"""Biology Dagster Asset Group — Cianfhoghlaim Educational MMO.

6 assets in `group_name="biology"` following the standard
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
biol_levels = dg.StaticPartitionsDefinition(["hl", "ol"])
biol_languages = dg.StaticPartitionsDefinition(["en", "ga"])
biol_partitions = dg.MultiPartitionsDefinition(
    {"level": biol_levels, "language": biol_languages}
)
biol_full_partitions = dg.StaticPartitionsDefinition(["hl_en", "hl_ga", "ol_en", "ol_ga"])


# Asset 1: biology_syllabus_raw
@dg.asset(
    group_name="biology",
    partitions_def=biol_partitions,
    description="DLT ingestion of NCCA Biology syllabus PDFs into DuckLake",
    compute_kind="dlt",
)
def biology_syllabus_raw(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    """Ingest the Biology PDFs into DuckLake via the DLT source."""
    import dlt

    from cianfhoghlaim.dlt.british_isles.ireland.education.subjects.biology import biol_source

    level = context.partition_key.keys_by_dimension["level"]
    language = context.partition_key.keys_by_dimension["language"]

    pipeline = dlt.pipeline(
        pipeline_name=f"biology_syllabus_{level}_{language}",
        destination=dlt.destinations.duckdb(
            credentials=os.environ.get("BIOL_DUCKDB_PATH", "./data/biology.duckdb")
        ),
        dataset_name=f"biology_{level}_{language}",
    )
    load_info = pipeline.run(biol_source(language=language, level=level))

    return dg.MaterializeResult(
        metadata={
            "pipeline": pipeline.pipeline_name,
            "dataset_name": pipeline.dataset_name,
            "load_packages": len(load_info.load_packages),
            "level": level,
            "language": language,
        }
    )


# Asset 2: biology_syllabus_structured
@dg.asset(
    group_name="biology",
    partitions_def=biol_partitions,
    description="BAML ExtractLeavingCertSyllabus per Biology PDF",
    compute_kind="baml",
)
def biology_syllabus_structured(
    context: dg.AssetExecutionContext,
    biology_syllabus_raw: dict[str, Any],
) -> dg.MaterializeResult:
    """Run BAML extraction on each raw PDF row."""
    from cianfhoghlaim.baml_client import b

    level = context.partition_key.keys_by_dimension["level"]
    language = context.partition_key.keys_by_dimension["language"]

    rows = []
    for raw_row in biology_syllabus_raw.get("rows", []):
        text = raw_row.get("text", "")
        try:
            result = b.ExtractLeavingCertSyllabus(pdf_text=text)
            rows.append({"sha256": raw_row["sha256"], "level": level, "language": language, "syllabus": result.model_dump()})
        except Exception as e:
            logger.warning(f"BAML extract failed for {raw_row.get('sha256')}: {e}")

    return dg.MaterializeResult(metadata={"rows": rows, "row_count": len(rows)})


# Asset 3: biology_quest_pack
@dg.asset(
    group_name="biology",
    partitions_def=biol_full_partitions,
    description=f"BAML {baml_qpack} per {title} level",
    compute_kind="baml",
)
def biology_quest_pack(
    context: dg.AssetExecutionContext,
    biology_syllabus_structured: dict[str, Any],
) -> dg.MaterializeResult:
    """Generate a quest pack for the syllabus."""
    from cianfhoghlaim.baml_client import b

    level_full = context.partition_key
    level = level_full.replace(f"_en", "") if "_" in level_full else level_full

    corpus_dir = Path(os.environ.get(
        "CIANFHOGHLAIM_ROOT",
        str(Path(__file__).resolve().parents[3]
    )) / "cianfhoghlaim" / "leaving_certificate" / "biology"

    rows = []
    for struct_row in biology_syllabus_structured.get("rows", []):
        try:
            pack = b.GenerateBiologyQuestPack(
                syllabus=struct_row["syllabus"],
                past_papers=[],
                marking_schemes=[],
                level=struct_row["level"],
            )
            rows.append({"level": struct_row["level"], "pack": pack.model_dump()})
        except Exception as e:
            logger.warning(f"Quest pack failed for level {struct_row['level']}: {e}")

    return dg.MaterializeResult(metadata={"packs": rows, "pack_count": len(rows)})


# Asset 4: biology_embedding
@dg.asset(
    group_name="biology",
    partitions_def=biol_full_partitions,
    description="CocoIndex v1 embedding of Biology syllabus into LanceDB",
    compute_kind="cocoindex",
)
def biology_embedding(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    """Run CocoIndex to embed the syllabus into LanceDB."""
    try:
        from cianfhoghlaim.cocoindex.biology_embedding import biology_embedding as coco_flow
        coco_flow.update()
    except Exception as e:
        logger.warning(f"CocoIndex embedding failed: {e}")

    return dg.MaterializeResult(metadata={"subject": "biology"})


# Asset 5: biology_cognify
@dg.asset(
    group_name="biology",
    description=f"Cognee cognify pass for {title} knowledge graph",
    compute_kind="cognee",
)
def biology_cognify(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    """Run Cognee cognify on the embedded syllabus."""
    try:
        from cianfhoghlaim.storage.cognify import cognify_subject
        cognify_subject("biology")
    except Exception as e:
        logger.warning(f"Cognee cognify failed: {e}")

    return dg.MaterializeResult(metadata={"subject": "biology"})


# Asset 6: biology_dashboard
@dg.asset(
    group_name="biology",
    description=f"Render {title} marimo notebook",
    compute_kind="marimo",
)
def biology_dashboard(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    """Execute the Biology marimo dashboard notebook."""
    notebook_path = Path(os.environ.get(
        "CIANFHOGHLAIM_ROOT",
        str(Path(__file__).resolve().parents[3])
    )) / "cianfhoghlaim" / "notebooks" / "dashboards" / "education" / "biology_full_pipeline.py"

    if notebook_path.exists():
        try:
            subprocess.run(
                ["marimo", "run", str(notebook_path), "--headless"],
                check=False, timeout=300,
            )
        except Exception as e:
            logger.warning(f"Dashboard render failed: {e}")

    return dg.MaterializeResult(metadata={"subject": "biology"})
