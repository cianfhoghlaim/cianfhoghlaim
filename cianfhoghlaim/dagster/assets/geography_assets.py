"""Geography Dagster Asset Group — Cianfhoghlaim Educational MMO."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any

import dagster as dg


geog_levels = dg.StaticPartitionsDefinition(["hl", "ol", "jc"])
geog_languages = dg.StaticPartitionsDefinition(["en", "ga"])
geog_partitions = dg.MultiPartitionsDefinition(
    {"level": geog_levels, "language": geog_languages}
)
geog_full_partitions = dg.StaticPartitionsDefinition(
    ["hl_en", "ol_en", "hl_ga", "ol_ga", "jc_en"]
)


@dg.asset(group_name="geography", partitions_def=geog_partitions, description="DLT ingestion of NCCA Geography PDFs", compute_kind="dlt")
def geog_syllabus_raw(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    import dlt
    from cianfhoghlaim.dlt.subjects.geography import geog_source
    level = context.partition_key.keys_by_dimension["level"]
    language = context.partition_key.keys_by_dimension["language"]
    pipeline = dlt.pipeline(
        pipeline_name=f"geog_syllabus_{level}_{language}",
        destination=dlt.destinations.duckdb(credentials=os.environ.get("GEOG_DUCKDB_PATH", "./data/geography.duckdb")),
        dataset_name=f"geography_{level}_{language}",
    )
    load_info = pipeline.run(geog_source(language=language))
    return dg.MaterializeResult(metadata={"pipeline": pipeline.pipeline_name, "level": level})


@dg.asset(group_name="geography", partitions_def=geog_partitions, description="BAML ExtractSyllabusStructure", compute_kind="baml")
def geog_syllabus_structured(context: dg.AssetExecutionContext, geog_syllabus_raw: dict[str, Any]) -> dg.MaterializeResult:
    from cianfhoghlaim.baml_client import b
    level = context.partition_key.keys_by_dimension["level"]
    language = context.partition_key.keys_by_dimension["language"]
    rows = []
    for raw_row in geog_syllabus_raw.get("rows", []):
        text = raw_row.get("text", "")
        structure = b.ExtractSyllabusStructure(text, "Geography", language)
        rows.append({"sha256": raw_row["sha256"], "level": level, "language": language, "structure": structure.model_dump()})
    return dg.MaterializeResult(metadata={"rows": rows, "row_count": len(rows)})


@dg.asset(group_name="geography", partitions_def=geog_full_partitions, description="BAML GenerateGeogQuestPack", compute_kind="baml")
def geog_quest_pack(context: dg.AssetExecutionContext, geog_syllabus_structured: dict[str, Any]) -> dg.MaterializeResult:
    from cianfhoghlaim.baml_client import b
    partition_key = context.partition_key
    level, language = partition_key.split("_")
    corpus_dir = Path("/Users/cianmacandeisigh/dev/kings_college_galway") / "cianfhoghlaim" / "leaving_certificate" / "geography" / language
    if not corpus_dir.exists():
        return dg.MaterializeResult(metadata={"error": f"corpus dir not found: {corpus_dir}"})
    syllabus_pdfs = list(corpus_dir.glob("*.pdf"))[:1]
    if not syllabus_pdfs:
        return dg.MaterializeResult(metadata={"error": "no syllabus PDFs found"})
    try:
        import fitz
        doc = fitz.open(str(syllabus_pdfs[0]))
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
    except ImportError:
        return dg.MaterializeResult(metadata={"error": "PyMuPDF not installed"})
    syllabus = b.ExtractLeavingCertSyllabus(text)
    pack = b.GenerateGeogQuestPack(syllabus, [], [], level)
    return dg.MaterializeResult(metadata={"pack_id": pack.id, "total_items": pack.total_items, "los_covered": pack.los_covered})


@dg.asset(group_name="geography", partitions_def=geog_full_partitions, description="CocoIndex v1 embedding", compute_kind="cocoindex")
def geog_embedding(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    partition_key = context.partition_key
    level, language = partition_key.split("_")
    result = subprocess.run(["uv", "run", "python", "-m", "cocoindex.cli", "update", "-f", "geography_embedding", "--arg", f"level={level}", "--arg", f"language={language}"], capture_output=True, text=True, cwd=Path(__file__).resolve().parents[3])
    return dg.MaterializeResult(metadata={"returncode": result.returncode, "lancedb_table": f"oideachais.lc.geography.{level}_{language}"})


@dg.asset(group_name="geography", description="Cognee cognify pass", compute_kind="cognee")
def geog_cognify(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    import asyncio
    import cognee
    async def _run() -> int:
        await cognee.cognify(dataset_name="oideachais_lc_geography")
        return 1
    return dg.MaterializeResult(metadata={"cognee_dataset": "oideachais_lc_geography"})


@dg.asset(group_name="geography", description="Render Geography marimo notebook", compute_kind="marimo")
def geog_dashboard(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    nb_path = Path(__file__).resolve().parents[3] / "notebooks" / "leaving_cert" / "geography.py"
    if not nb_path.exists():
        return dg.MaterializeResult(metadata={"error": f"notebook not found: {nb_path}"})
    export_path = nb_path.with_suffix(".html")
    result = subprocess.run(["uv", "run", "marimo", "export", "html", "--no-include-code", str(nb_path), "-o", str(export_path)], capture_output=True, text=True)
    return dg.MaterializeResult(metadata={"notebook": str(nb_path), "returncode": result.returncode})