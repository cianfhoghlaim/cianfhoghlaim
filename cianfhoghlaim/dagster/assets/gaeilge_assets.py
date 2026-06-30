"""gaeilge_dagster_assets — 6 Dagster assets for the Gaeilge subject.

Same pattern as Mathematics + Applied Mathematics.

Reference:
    openspec/changes/cianfhoghlaim-educational-mmo-v1/proposal.md (D3)
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any

import dagster as dg

gael_levels = dg.StaticPartitionsDefinition(["hl", "ol", "fl", "jc"])
gael_languages = dg.StaticPartitionsDefinition(["ga"])  # Gaeilge is in Irish
gael_partitions = dg.MultiPartitionsDefinition(
    {"level": gael_levels, "language": gael_languages}
)

gael_full_partitions = dg.StaticPartitionsDefinition(
    ["hl_ga", "ol_ga", "fl_ga", "jc_ga"]
)


@dg.asset(group_name="gaeilge", partitions_def=gael_partitions, description="DLT ingestion of NCCA Gaeilge PDFs", compute_kind="dlt")
def gael_syllabus_raw(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    import dlt
    from cianfhoghlaim.dlt.subjects.gaeilge import gael_source
    level = context.partition_key.keys_by_dimension["level"]
    language = "ga"
    pipeline = dlt.pipeline(
        pipeline_name=f"gael_syllabus_{level}_{language}",
        destination=dlt.destinations.duckdb(credentials=os.environ.get("GAEL_DUCKDB_PATH", "./data/gaeilge.duckdb")),
        dataset_name=f"gaeilge_{level}_{language}",
    )
    load_info = pipeline.run(gael_source(language=language))
    return dg.MaterializeResult(metadata={"pipeline": pipeline.pipeline_name, "level": level})


@dg.asset(group_name="gaeilge", partitions_def=gael_partitions, description="BAML ExtractSyllabusStructure", compute_kind="baml")
def gael_syllabus_structured(context: dg.AssetExecutionContext, gael_syllabus_raw: dict[str, Any]) -> dg.MaterializeResult:
    from cianfhoghlaim.baml_client import b
    level = context.partition_key.keys_by_dimension["level"]
    language = "ga"
    rows = []
    for raw_row in gael_syllabus_raw.get("rows", []):
        text = raw_row.get("text", "")
        structure = b.ExtractSyllabusStructure(text, "Gaeilge", language)
        rows.append({"sha256": raw_row["sha256"], "filename": raw_row["filename"], "level": level, "language": language, "structure": structure.model_dump()})
    return dg.MaterializeResult(metadata={"rows": rows, "row_count": len(rows)})


@dg.asset(group_name="gaeilge", partitions_def=gael_full_partitions, description="BAML GenerateGaelQuestPack", compute_kind="baml")
def gael_quest_pack(context: dg.AssetExecutionContext, gael_syllabus_structured: dict[str, Any]) -> dg.MaterializeResult:
    from cianfhoghlaim.baml_client import b
    partition_key = context.partition_key
    level, language = partition_key.split("_")
    corpus_dir = Path("/Users/cianmacandeisigh/dev/kings_college_galway") / "cianfhoghlaim" / "leaving_certificate" / "gaeilge"
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
    pack = b.GenerateGaelQuestPack(syllabus, [], [], level)
    return dg.MaterializeResult(metadata={"pack_id": pack.id, "total_items": pack.total_items, "los_covered": pack.los_covered})


@dg.asset(group_name="gaeilge", partitions_def=gael_full_partitions, description="CocoIndex v1 embedding", compute_kind="cocoindex")
def gael_embedding(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    partition_key = context.partition_key
    level, language = partition_key.split("_")
    result = subprocess.run(["uv", "run", "python", "-m", "cocoindex.cli", "update", "-f", "gaeilge_embedding", "--arg", f"level={level}", "--arg", f"language={language}"], capture_output=True, text=True, cwd=Path(__file__).resolve().parents[3])
    return dg.MaterializeResult(metadata={"returncode": result.returncode, "lancedb_table": f"oideachais.lc.gaeilge.{level}_{language}"})


@dg.asset(group_name="gaeilge", description="Cognee cognify pass", compute_kind="cognee")
def gael_cognify(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    import asyncio
    import cognee
    async def _run() -> int:
        await cognee.cognify(dataset_name="oideachais_lc_gaeilge")
        return 1
    nodes_added = asyncio.run(_run())
    return dg.MaterializeResult(metadata={"cognee_dataset": "oideachais_lc_gaeilge"})


@dg.asset(group_name="gaeilge", description="Render Gaeilge marimo notebook", compute_kind="marimo")
def gael_dashboard(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    nb_path = Path(__file__).resolve().parents[3] / "notebooks" / "leaving_cert" / "gaeilge.py"
    if not nb_path.exists():
        return dg.MaterializeResult(metadata={"error": f"notebook not found: {nb_path}"})
    export_path = nb_path.with_suffix(".html")
    result = subprocess.run(["uv", "run", "marimo", "export", "html", "--no-include-code", str(nb_path), "-o", str(export_path)], capture_output=True, text=True)
    return dg.MaterializeResult(metadata={"notebook": str(nb_path), "returncode": result.returncode})