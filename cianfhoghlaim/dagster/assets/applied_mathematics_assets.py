"""Applied Mathematics Dagster Asset Group — Cianfhoghlaim Educational MMO.

6 assets in `group_name="applied_mathematics"`. Same pattern as
`mathematics_assets.py` but for APPM (Higher Level only).

Reference:
    openspec/changes/cianfhoghlaim-educational-mmo-v1/proposal.md (D3)
    cianfhoghlaim/baml/qpack_applied_mathematics.baml (the BAML contract)
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any

import dagster as dg
import structlog

logger = structlog.get_logger(__name__)


appm_levels = dg.StaticPartitionsDefinition(["hl"])  # APPM is HL only
appm_languages = dg.StaticPartitionsDefinition(["en", "ga"])
appm_partitions = dg.MultiPartitionsDefinition(
    {"level": appm_levels, "language": appm_languages}
)

appm_full_partitions = dg.StaticPartitionsDefinition(["hl_en", "hl_ga"])


@dg.asset(
    group_name="applied_mathematics",
    partitions_def=appm_partitions,
    description="DLT ingestion of NCCA APPM syllabus PDFs into DuckLake",
    compute_kind="dlt",
)
def appm_syllabus_raw(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    import dlt

    from cianfhoghlaim.dlt.subjects.applied_mathematics import appm_source

    level = context.partition_key.keys_by_dimension["level"]
    language = context.partition_key.keys_by_dimension["language"]

    pipeline = dlt.pipeline(
        pipeline_name=f"appm_syllabus_{level}_{language}",
        destination=dlt.destinations.duckdb(
            credentials=os.environ.get("APPM_DUCKDB_PATH", "./data/applied_mathematics.duckdb")
        ),
        dataset_name=f"applied_mathematics_{level}_{language}",
    )
    load_info = pipeline.run(appm_source(language=language))
    return dg.MaterializeResult(
        metadata={
            "pipeline": pipeline.pipeline_name,
            "dataset_name": pipeline.dataset_name,
            "load_packages": len(load_info.load_packages),
            "level": level,
            "language": language,
        }
    )


@dg.asset(
    group_name="applied_mathematics",
    partitions_def=appm_partitions,
    description="BAML ExtractSyllabusStructure per APPM PDF",
    compute_kind="baml",
)
def appm_syllabus_structured(
    context: dg.AssetExecutionContext,
    appm_syllabus_raw: dict[str, Any],
) -> dg.MaterializeResult:
    from cianfhoghlaim.baml_client import b

    level = context.partition_key.keys_by_dimension["level"]
    language = context.partition_key.keys_by_dimension["language"]

    rows = []
    for raw_row in appm_syllabus_raw.get("rows", []):
        text = raw_row.get("text", "")
        structure = b.ExtractSyllabusStructure(text, "Applied Mathematics", language)
        rows.append(
            {
                "sha256": raw_row["sha256"],
                "filename": raw_row["filename"],
                "level": level,
                "language": language,
                "structure": structure.model_dump(),
                "level_count": len(structure.level_sections),
            }
        )

    return dg.MaterializeResult(metadata={"rows": rows, "row_count": len(rows)})


@dg.asset(
    group_name="applied_mathematics",
    partitions_def=appm_full_partitions,
    description="BAML GenerateAppmQuestPack for APPM HL",
    compute_kind="baml",
)
def appm_quest_pack(
    context: dg.AssetExecutionContext,
    appm_syllabus_structured: dict[str, Any],
) -> dg.MaterializeResult:
    from cianfhoghlaim.baml_client import b
    from cianfhoghlaim.dlt.subjects.applied_mathematics.sources import (
        _list_pdfs,
        _pdf_to_text,
    )

    partition_key = context.partition_key
    level, language = partition_key.split("_")

    corpus_dir = (
        Path("/Users/cianmacandeisigh/dev/kings_college_galway")
        / "cianfhoghlaim"
        / "leaving_certificate"
        / "applied_mathematics"
        / language
    )
    if not corpus_dir.exists():
        return dg.MaterializeResult(metadata={"error": f"corpus dir not found: {corpus_dir}"})

    syllabus_pdfs = [
        p for p in _list_pdfs(language)
        if "specification" in p.name.lower() or "SCSEC" in p.name.upper()
    ]
    paper_pdfs = [
        p for p in _list_pdfs(language)
        if any(tag in p.name.upper() for tag in ("ALP", "GLP"))
    ]

    if not syllabus_pdfs:
        return dg.MaterializeResult(metadata={"error": f"no syllabus PDFs found"})

    syllabus_text = _pdf_to_text(syllabus_pdfs[0])
    syllabus = b.ExtractLeavingCertSyllabus(syllabus_text)
    past_papers = [b.ExtractLeavingCertPastPaper(_pdf_to_text(p)) for p in paper_pdfs[:3]]
    marking_schemes = [b.ExtractLeavingCertMarkingScheme(_pdf_to_text(p)) for p in paper_pdfs[:3]]

    pack = b.GenerateAppmQuestPack(syllabus, past_papers, marking_schemes, level)

    return dg.MaterializeResult(
        metadata={
            "pack": pack.model_dump(),
            "pack_id": pack.id,
            "total_items": pack.total_items,
            "total_marks": pack.total_marks,
            "los_covered": pack.los_covered,
            "level": level,
            "language": language,
        }
    )


@dg.asset(
    group_name="applied_mathematics",
    partitions_def=appm_full_partitions,
    description="CocoIndex v1 embedding of APPM quest packs into LanceDB",
    compute_kind="cocoindex",
)
def appm_embedding(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    partition_key = context.partition_key
    level, language = partition_key.split("_")

    result = subprocess.run(
        [
            "uv", "run", "python", "-m", "cocoindex.cli", "update",
            "-f", "applied_mathematics_embedding",
            "--arg", f"level={level}",
            "--arg", f"language={language}",
        ],
        capture_output=True, text=True,
        cwd=Path(__file__).resolve().parents[3],
    )
    return dg.MaterializeResult(
        metadata={
            "returncode": result.returncode,
            "level": level,
            "language": language,
            "lancedb_table": f"oideachais.lc.applied_mathematics.{level}_{language}",
        }
    )


@dg.asset(
    group_name="applied_mathematics",
    description="Cognee cognify pass over the APPM corpus",
    compute_kind="cognee",
)
def appm_cognify(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    import asyncio
    import cognee

    async def _run() -> int:
        await cognee.cognify(dataset_name="oideachais_lc_applied_mathematics")
        return 1

    nodes_added = asyncio.run(_run())
    return dg.MaterializeResult(metadata={"cognee_dataset": "oideachais_lc_applied_mathematics", "nodes_added": nodes_added})


@dg.asset(
    group_name="applied_mathematics",
    description="Render the APPM marimo notebook (teacher view)",
    compute_kind="marimo",
)
def appm_dashboard(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    nb_path = (
        Path(__file__).resolve().parents[3]
        / "notebooks"
        / "leaving_cert"
        / "applied_mathematics.py"
    )
    if not nb_path.exists():
        return dg.MaterializeResult(metadata={"error": f"notebook not found: {nb_path}"})

    export_path = nb_path.with_suffix(".html")
    result = subprocess.run(
        ["uv", "run", "marimo", "export", "html", "--no-include-code", str(nb_path), "-o", str(export_path)],
        capture_output=True, text=True,
    )
    return dg.MaterializeResult(
        metadata={"notebook": str(nb_path), "export": str(export_path), "returncode": result.returncode}
    )