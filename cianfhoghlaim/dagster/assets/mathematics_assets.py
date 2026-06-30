"""Mathematics Dagster Asset Group — Cianfhoghlaim Educational MMO.

6 assets in `group_name="mathematics"`:
1. math_syllabus_raw — DLT ingestion of the 7 Mathematics PDFs into DuckLake
2. math_syllabus_structured — BAML ExtractSyllabusStructure per PDF
3. math_quest_pack — BAML GenerateMathQuestPack per level
4. math_embedding — CocoIndex v1 embedding into LanceDB
5. math_cognify — Cognee cognify pass (subject knowledge graph)
6. math_dashboard — marimo notebook execution

Pattern follows the existing leabharlann_assets.py + cocoindex_assets.py
in this directory.

Reference:
    openspec/changes/cianfhoghlaim-educational-mmo-v1/proposal.md (D3)
    cianfhoghlaim/baml/qpack_mathematics.baml (the BAML contract)
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any

import dagster as dg
import structlog

logger = structlog.get_logger(__name__)


# ============================================================================
# Partition definitions
# ============================================================================

# 3 levels (Foundation, Ordinary, Higher) × 2 languages (EN, GA)
math_levels = dg.StaticPartitionsDefinition(["hl", "ol", "fl"])
math_languages = dg.StaticPartitionsDefinition(["en", "ga"])
math_partitions = dg.MultiPartitionsDefinition(
    {"level": math_levels, "language": math_languages}
)

# Single-language partitions for assets that don't need a language split
math_full_partitions = dg.StaticPartitionsDefinition(
    ["hl_en", "ol_en", "fl_en", "hl_ga", "ol_ga", "fl_ga"]
)


# ============================================================================
# Asset 1: math_syllabus_raw
# ============================================================================

@dg.asset(
    group_name="mathematics",
    partitions_def=math_partitions,
    description="DLT ingestion of NCCA Mathematics syllabus PDFs into DuckLake",
    compute_kind="dlt",
)
def math_syllabus_raw(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    """Ingest the 7 Mathematics PDFs into DuckLake via the DLT source."""
    import dlt

    from cianfhoghlaim.dlt.subjects.mathematics import math_source

    level = context.partition_key.keys_by_dimension["level"]
    language = context.partition_key.keys_by_dimension["language"]

    pipeline = dlt.pipeline(
        pipeline_name=f"math_syllabus_{level}_{language}",
        destination=dlt.destinations.duckdb(
            credentials=os.environ.get(
                "MATH_DUCKDB_PATH", "./data/mathematics.duckdb"
            )
        ),
        dataset_name=f"mathematics_{level}_{language}",
    )
    load_info = pipeline.run(math_source(language=language, level=level))

    return dg.MaterializeResult(
        metadata={
            "pipeline": pipeline.pipeline_name,
            "dataset_name": pipeline.dataset_name,
            "load_packages": len(load_info.load_packages),
            "level": level,
            "language": language,
        }
    )


# ============================================================================
# Asset 2: math_syllabus_structured
# ============================================================================

@dg.asset(
    group_name="mathematics",
    partitions_def=math_partitions,
    description="BAML ExtractSyllabusStructure per Mathematics PDF (level sections + chapter counts)",
    compute_kind="baml",
)
def math_syllabus_structured(
    context: dg.AssetExecutionContext,
    math_syllabus_raw: dict[str, Any],
) -> dg.MaterializeResult:
    """Extract the per-level structure from each Mathematics syllabus PDF."""
    from cianfhoghlaim.baml_client import b  # type: ignore

    level = context.partition_key.keys_by_dimension["level"]
    language = context.partition_key.keys_by_dimension["language"]

    rows = []
    for raw_row in math_syllabus_raw.get("rows", []):
        text = raw_row.get("text", "")
        structure = b.ExtractSyllabusStructure(text, "Mathematics", language)
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

    return dg.MaterializeResult(
        metadata={
            "rows": rows,
            "row_count": len(rows),
            "level": level,
            "language": language,
        }
    )


# ============================================================================
# Asset 3: math_quest_pack
# ============================================================================

@dg.asset(
    group_name="mathematics",
    partitions_def=math_full_partitions,
    description="BAML GenerateMathQuestPack per Mathematics level (HL/OL/FL × EN/GA)",
    compute_kind="baml",
)
def math_quest_pack(
    context: dg.AssetExecutionContext,
    math_syllabus_structured: dict[str, Any],
) -> dg.MaterializeResult:
    """Generate a formative quest pack for one Mathematics level + language."""
    from cianfhoghlaim.baml_client import b  # type: ignore
    from cianfhoghlaim.dlt.subjects.mathematics.sources import (
        _list_pdfs,
        _pdf_to_text,
    )

    partition_key = context.partition_key  # e.g. "hl_en"
    level, language = partition_key.split("_")

    # Gather the syllabus, past papers, marking schemes
    corpus_dir = (
        Path("/Users/cianmacandeisigh/dev/kings_college_galway")
        / "cianfhoghlaim"
        / "leaving_certificate"
        / "mathematics"
        / language
    )
    if not corpus_dir.exists():
        return dg.MaterializeResult(
            metadata={"error": f"corpus dir not found: {corpus_dir}"}
        )

    syllabus_pdfs = [
        p for p in _list_pdfs(language, level)
        if "syllabus" in p.name.lower() or "SCSEC" in p.name.upper()
    ]
    paper_pdfs = [
        p for p in _list_pdfs(language, level)
        if any(tag in p.name.upper() for tag in ("ALP", "GLP", "BLP"))
    ]

    if not syllabus_pdfs:
        return dg.MaterializeResult(
            metadata={"error": f"no syllabus PDFs found for level={level}, language={language}"}
        )

    syllabus_text = _pdf_to_text(syllabus_pdfs[0])
    syllabus = b.ExtractLeavingCertSyllabus(syllabus_text)
    past_papers = [
        b.ExtractLeavingCertPastPaper(_pdf_to_text(p)) for p in paper_pdfs[:3]
    ]
    marking_schemes = [
        b.ExtractLeavingCertMarkingScheme(_pdf_to_text(p)) for p in paper_pdfs[:3]
    ]

    pack = b.GenerateMathQuestPack(syllabus, past_papers, marking_schemes, level)

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


# ============================================================================
# Asset 4: math_embedding (CocoIndex v1)
# ============================================================================

@dg.asset(
    group_name="mathematics",
    partitions_def=math_full_partitions,
    description="CocoIndex v1 embedding of Mathematics quest packs into LanceDB",
    compute_kind="cocoindex",
)
def math_embedding(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    """Run the cocoindex v1 Mathematics embedding flow via subprocess.

    This is the canonical v1 invocation pattern documented in
    .agents/skills/oideachais-cocoindex-v1/SKILL.md.
    """
    partition_key = context.partition_key
    level, language = partition_key.split("_")

    result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "-m",
            "cocoindex.cli",
            "update",
            "-f",
            "mathematics_embedding",
            "--arg",
            f"level={level}",
            "--arg",
            f"language={language}",
        ],
        capture_output=True,
        text=True,
        cwd=Path(__file__).resolve().parents[3],
    )

    return dg.MaterializeResult(
        metadata={
            "returncode": result.returncode,
            "stdout_lines": result.stdout.count("\n"),
            "stderr_lines": result.stderr.count("\n"),
            "level": level,
            "language": language,
            "lancedb_table": f"oideachais.lc.mathematics.{level}_{language}",
        }
    )


# ============================================================================
# Asset 5: math_cognify (Cognee)
# ============================================================================

@dg.asset(
    group_name="mathematics",
    description="Cognee cognify pass over the Mathematics syllabus corpus",
    compute_kind="cognee",
)
def math_cognify(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    """Run the leabharlann-style cognify pass over the Mathematics corpus."""
    import asyncio

    import cognee

    async def _run_cognify() -> int:
        await cognee.cognify(dataset_name="oideachais_lc_mathematics")
        return 1

    nodes_added = asyncio.run(_run_cognify())
    return dg.MaterializeResult(metadata={"cognee_dataset": "oideachais_lc_mathematics", "nodes_added": nodes_added})


# ============================================================================
# Asset 6: math_dashboard (marimo notebook execution)
# ============================================================================

@dg.asset(
    group_name="mathematics",
    description="Render the Mathematics marimo notebook (teacher view)",
    compute_kind="marimo",
)
def math_dashboard(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    """Execute the Mathematics marimo notebook and export HTML.

    The notebook is the teacher-facing view: all NCCA LOs visible,
    BGE-M3 semantic search over quest packs, quest designer controls.
    """
    nb_path = (
        Path(__file__).resolve().parents[3]
        / "notebooks"
        / "leaving_cert"
        / "mathematics.py"
    )
    if not nb_path.exists():
        return dg.MaterializeResult(
            metadata={"error": f"notebook not found: {nb_path}"}
        )

    export_path = nb_path.with_suffix(".html")
    result = subprocess.run(
        [
            "uv",
            "run",
            "marimo",
            "export",
            "html",
            "--no-include-code",
            str(nb_path),
            "-o",
            str(export_path),
        ],
        capture_output=True,
        text=True,
    )
    return dg.MaterializeResult(
        metadata={
            "notebook": str(nb_path),
            "export": str(export_path),
            "returncode": result.returncode,
        }
    )