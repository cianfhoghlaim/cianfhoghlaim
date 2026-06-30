#!/usr/bin/env python3
"""Create missing subject asset files in dagster/assets/ following the english_assets.py template.

Subjects: biology, business, french, technology, ukrainian.
The 6-asset pattern: raw, structured, quest_pack, embedding, cognify, dashboard.
"""
from __future__ import annotations
from pathlib import Path

# Subject name mapping: (subject_key, baml_qpack_function, baml_extract_function, partition_levels)
SUBJECTS = {
    "biology": {
        "title": "Biology",
        "code": "biol",
        "baml_qpack": "GenerateBiologyQuestPack",
        "baml_extract": "ExtractLeavingCertSyllabus",
        "levels": ["hl", "ol"],
        "langs": ["en", "ga"],
    },
    "business": {
        "title": "Business",
        "code": "bus",
        "baml_qpack": "GenerateBusinessQuestPack",
        "baml_extract": "ExtractLeavingCertSyllabus",
        "levels": ["hl", "ol"],
        "langs": ["en", "ga"],
    },
    "french": {
        "title": "French",
        "code": "fren",
        "baml_qpack": "GenerateFrenchQuestPack",
        "baml_extract": "ExtractLeavingCertSyllabus",
        "levels": ["hl", "ol"],
        "langs": ["en", "fr", "ga"],
    },
    "technology": {
        "title": "Technology",
        "code": "tech",
        "baml_qpack": "GenerateTechnologyQuestPack",
        "baml_extract": "ExtractLeavingCertSyllabus",
        "levels": ["hl", "ol"],
        "langs": ["en", "ga"],
    },
    "ukrainian": {
        "title": "Ukrainian",
        "code": "ukr",
        "baml_qpack": "GenerateUkrainianQuestPack",
        "baml_extract": "ExtractLeavingCertSyllabus",
        "levels": ["hl", "ol"],
        "langs": ["en", "uk", "ga"],
    },
}


def generate_assets_file(subject: str, info: dict) -> str:
    """Generate a 6-asset pattern file for the given subject."""
    title = info["title"]
    code = info["code"]
    levels = info["levels"]
    langs = info["langs"]
    baml_qpack = info["baml_qpack"]
    baml_extract = info["baml_extract"]

    partitions_list = ", ".join(f'"{lv}_{ln}"' for lv in levels for ln in langs)
    levels_list = ", ".join(f'"{lv}"' for lv in levels)
    langs_list = ", ".join(f'"{ln}"' for ln in langs)

    return f'''"""{title} Dagster Asset Group — Cianfhoghlaim Educational MMO.

6 assets in `group_name="{subject}"` following the standard
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
{code}_levels = dg.StaticPartitionsDefinition([{levels_list}])
{code}_languages = dg.StaticPartitionsDefinition([{langs_list}])
{code}_partitions = dg.MultiPartitionsDefinition(
    {{"level": {code}_levels, "language": {code}_languages}}
)
{code}_full_partitions = dg.StaticPartitionsDefinition([{partitions_list}])


# Asset 1: {subject}_syllabus_raw
@dg.asset(
    group_name="{subject}",
    partitions_def={code}_partitions,
    description="DLT ingestion of NCCA {title} syllabus PDFs into DuckLake",
    compute_kind="dlt",
)
def {subject}_syllabus_raw(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    """Ingest the {title} PDFs into DuckLake via the DLT source."""
    import dlt

    from cianfhoghlaim.dlt.british_isles.ireland.education.subjects.{subject} import {code}_source

    level = context.partition_key.keys_by_dimension["level"]
    language = context.partition_key.keys_by_dimension["language"]

    pipeline = dlt.pipeline(
        pipeline_name=f"{subject}_syllabus_{{level}}_{{language}}",
        destination=dlt.destinations.duckdb(
            credentials=os.environ.get("{code.upper()}_DUCKDB_PATH", "./data/{subject}.duckdb")
        ),
        dataset_name=f"{subject}_{{level}}_{{language}}",
    )
    load_info = pipeline.run({code}_source(language=language, level=level))

    return dg.MaterializeResult(
        metadata={{
            "pipeline": pipeline.pipeline_name,
            "dataset_name": pipeline.dataset_name,
            "load_packages": len(load_info.load_packages),
            "level": level,
            "language": language,
        }}
    )


# Asset 2: {subject}_syllabus_structured
@dg.asset(
    group_name="{subject}",
    partitions_def={code}_partitions,
    description="BAML ExtractLeavingCertSyllabus per {title} PDF",
    compute_kind="baml",
)
def {subject}_syllabus_structured(
    context: dg.AssetExecutionContext,
    {subject}_syllabus_raw: dict[str, Any],
) -> dg.MaterializeResult:
    """Run BAML extraction on each raw PDF row."""
    from cianfhoghlaim.baml_client import b

    level = context.partition_key.keys_by_dimension["level"]
    language = context.partition_key.keys_by_dimension["language"]

    rows = []
    for raw_row in {subject}_syllabus_raw.get("rows", []):
        text = raw_row.get("text", "")
        try:
            result = b.{baml_extract}(pdf_text=text)
            rows.append({{"sha256": raw_row["sha256"], "level": level, "language": language, "syllabus": result.model_dump()}})
        except Exception as e:
            logger.warning(f"BAML extract failed for {{raw_row.get('sha256')}}: {{e}}")

    return dg.MaterializeResult(metadata={{"rows": rows, "row_count": len(rows)}})


# Asset 3: {subject}_quest_pack
@dg.asset(
    group_name="{subject}",
    partitions_def={code}_full_partitions,
    description=f"BAML {{baml_qpack}} per {{title}} level",
    compute_kind="baml",
)
def {subject}_quest_pack(
    context: dg.AssetExecutionContext,
    {subject}_syllabus_structured: dict[str, Any],
) -> dg.MaterializeResult:
    """Generate a quest pack for the syllabus."""
    from cianfhoghlaim.baml_client import b

    level_full = context.partition_key
    level = level_full.replace(f"_{langs[0]}", "") if "_" in level_full else level_full

    corpus_dir = Path(os.environ.get(
        "CIANFHOGHLAIM_ROOT",
        str(Path(__file__).resolve().parents[3]
    )) / "cianfhoghlaim" / "leaving_certificate" / "{subject}"

    rows = []
    for struct_row in {subject}_syllabus_structured.get("rows", []):
        try:
            pack = b.{baml_qpack}(
                syllabus=struct_row["syllabus"],
                past_papers=[],
                marking_schemes=[],
                level=struct_row["level"],
            )
            rows.append({{"level": struct_row["level"], "pack": pack.model_dump()}})
        except Exception as e:
            logger.warning(f"Quest pack failed for level {{struct_row['level']}}: {{e}}")

    return dg.MaterializeResult(metadata={{"packs": rows, "pack_count": len(rows)}})


# Asset 4: {subject}_embedding
@dg.asset(
    group_name="{subject}",
    partitions_def={code}_full_partitions,
    description="CocoIndex v1 embedding of {title} syllabus into LanceDB",
    compute_kind="cocoindex",
)
def {subject}_embedding(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    """Run CocoIndex to embed the syllabus into LanceDB."""
    try:
        from cianfhoghlaim.cocoindex.{subject}_embedding import {subject}_embedding as coco_flow
        coco_flow.update()
    except Exception as e:
        logger.warning(f"CocoIndex embedding failed: {{e}}")

    return dg.MaterializeResult(metadata={{"subject": "{subject}"}})


# Asset 5: {subject}_cognify
@dg.asset(
    group_name="{subject}",
    description=f"Cognee cognify pass for {{title}} knowledge graph",
    compute_kind="cognee",
)
def {subject}_cognify(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    """Run Cognee cognify on the embedded syllabus."""
    try:
        from cianfhoghlaim.storage.cognify import cognify_subject
        cognify_subject("{subject}")
    except Exception as e:
        logger.warning(f"Cognee cognify failed: {{e}}")

    return dg.MaterializeResult(metadata={{"subject": "{subject}"}})


# Asset 6: {subject}_dashboard
@dg.asset(
    group_name="{subject}",
    description=f"Render {{title}} marimo notebook",
    compute_kind="marimo",
)
def {subject}_dashboard(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    """Execute the {title} marimo dashboard notebook."""
    notebook_path = Path(os.environ.get(
        "CIANFHOGHLAIM_ROOT",
        str(Path(__file__).resolve().parents[3])
    )) / "cianfhoghlaim" / "notebooks" / "dashboards" / "education" / "{subject}_full_pipeline.py"

    if notebook_path.exists():
        try:
            subprocess.run(
                ["marimo", "run", str(notebook_path), "--headless"],
                check=False, timeout=300,
            )
        except Exception as e:
            logger.warning(f"Dashboard render failed: {{e}}")

    return dg.MaterializeResult(metadata={{"subject": "{subject}"}})
'''


def main() -> None:
    root = Path("/Users/cianmacandeisigh/dev/kings_college_galway/cianfhoghlaim/dagster/assets")
    for subject, info in SUBJECTS.items():
        path = root / f"{subject}_assets.py"
        if path.exists():
            print(f"[SKIP] {path.name} (exists)")
            continue
        content = generate_assets_file(subject, info)
        path.write_text(content)
        print(f"[OK] {path.name} ({len(content)} chars)")


if __name__ == "__main__":
    main()