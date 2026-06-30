"""English Dagster Asset Group — Cianfhoghlaim Educational MMO."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any

import dagster as dg


engl_levels = dg.StaticPartitionsDefinition(["hl", "ol", "jc"])
engl_languages = dg.StaticPartitionsDefinition(["en"])
engl_partitions = dg.MultiPartitionsDefinition(
    {"level": engl_levels, "language": engl_languages}
)
engl_full_partitions = dg.StaticPartitionsDefinition(["hl_en", "ol_en", "jc_en"])


@dg.asset(group_name="english", partitions_def=engl_partitions, description="DLT ingestion of NCCA English PDFs", compute_kind="dlt")
def engl_syllabus_raw(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    import dlt
    from cianfhoghlaim.dlt.subjects.english import engl_source
    level = context.partition_key.keys_by_dimension["level"]
    pipeline = dlt.pipeline(
        pipeline_name=f"engl_syllabus_{level}",
        destination=dlt.destinations.duckdb(credentials=os.environ.get("ENGL_DUCKDB_PATH", "./data/english.duckdb")),
        dataset_name=f"english_{level}",
    )
    load_info = pipeline.run(engl_source())
    return dg.MaterializeResult(metadata={"pipeline": pipeline.pipeline_name, "level": level})


@dg.asset(group_name="english", partitions_def=engl_partitions, description="BAML ExtractSyllabusStructure", compute_kind="baml")
def engl_syllabus_structured(context: dg.AssetExecutionContext, engl_syllabus_raw: dict[str, Any]) -> dg.MaterializeResult:
    from cianfhoghlaim.baml_client import b
    level = context.partition_key.keys_by_dimension["level"]
    rows = []
    for raw_row in engl_syllabus_raw.get("rows", []):
        text = raw_row.get("text", "")
        structure = b.ExtractSyllabusStructure(text, "English", "en")
        rows.append({"sha256": raw_row["sha256"], "level": level, "structure": structure.model_dump()})
    return dg.MaterializeResult(metadata={"rows": rows, "row_count": len(rows)})


@dg.asset(group_name="english", partitions_def=engl_full_partitions, description="BAML GenerateEnglQuestPack", compute_kind="baml")
def engl_quest_pack(context: dg.AssetExecutionContext, engl_syllabus_structured: dict[str, Any]) -> dg.MaterializeResult:
    from cianfhoghlaim.baml_client import b
    level = context.partition_key.replace("_en", "")
    corpus_dir = Path("/Users/cianmacandeisigh/dev/kings_college_galway") / "cianfhoghlaim" / "leaving_certificate" / "english"
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
    pack = b.GenerateEnglQuestPack(syllabus, [], [], level)
    return dg.MaterializeResult(metadata={"pack_id": pack.id, "total_items": pack.total_items, "los_covered": pack.los_covered})


@dg.asset(group_name="english", partitions_def=engl_full_partitions, description="CocoIndex v1 embedding", compute_kind="cocoindex")
def engl_embedding(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    partition_key = context.partition_key
    result = subprocess.run(["uv", "run", "python", "-m", "cocoindex.cli", "update", "-f", "english_embedding", "--arg", f"level={partition_key}"], capture_output=True, text=True, cwd=Path(__file__).resolve().parents[3])
    return dg.MaterializeResult(metadata={"returncode": result.returncode, "lancedb_table": f"oideachais.lc.english.{partition_key}"})


@dg.asset(group_name="english", description="Cognee cognify pass", compute_kind="cognee")
def engl_cognify(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    import asyncio
    import cognee
    async def _run() -> int:
        await cognee.cognify(dataset_name="oideachais_lc_english")
        return 1
    return dg.MaterializeResult(metadata={"cognee_dataset": "oideachais_lc_english"})


@dg.asset(group_name="english", description="Render English marimo notebook", compute_kind="marimo")
def engl_dashboard(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    nb_path = Path(__file__).resolve().parents[3] / "notebooks" / "leaving_cert" / "english.py"
    if not nb_path.exists():
        return dg.MaterializeResult(metadata={"error": f"notebook not found: {nb_path}"})
    export_path = nb_path.with_suffix(".html")
    result = subprocess.run(["uv", "run", "marimo", "export", "html", "--no-include-code", str(nb_path), "-o", str(export_path)], capture_output=True, text=True)
    return dg.MaterializeResult(metadata={"notebook": str(nb_path), "returncode": result.returncode})