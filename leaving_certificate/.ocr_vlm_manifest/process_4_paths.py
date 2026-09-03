"""Sample OCR/VLM 4-path ensemble processing — the pipeline runner.

This is the canonical entry point for processing the 148 Ireland LC
PDFs through the 4-path OCR/VLM ensemble. It demonstrates the
pipeline structure; the actual inference calls would invoke:

- Path 1: Docling-serve → text → BAML function (typed Pydantic row)
- Path 2: Docling-serve → Unstract workflow → JSON
- Path 3: qwen3-vl-8b page-level image → JSON
- Path 4: gemma-4-26B-A4B page-level image → JSON
- RAGAS consensus → canonical row → BIEP DuckLake table

Per the 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1
change (Phase 3 - OCR/VLM 4-path ensemble).

In production, this would call:
- meaisinfhoghlaim.ocr.ensemble.ensembled_extractor.EnsembledExtractor
- The BAML extraction functions in:
    baml_src/british_isles/ireland/education/lc_extraction/curriculum_syllabus.baml
    baml_src/british_isles/ireland/education/lc_extraction/exam_paper_layout.baml
    baml_src/british_isles/ireland/education/lc_extraction/marking_scheme.baml
    baml_src/british_isles/ireland/education/lc_extraction/syllabus_diagram.baml
- The MEASAINFHLOGHLAIM OCR ensemble would emit per-PDF:
  - ExtractCurriculumSyllabus → CurriculumSyllabus (typed Pydantic)
  - ExtractExamPaperLayout → ExamPaperLayout
  - ExtractMarkingSchemeGuideline → MarkingSchemeGuideline
  - ExtractSyllabusDiagram → SyllabusDiagram
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# The canonical 4-path ensemble (per the 2026-07-22-biep-v2-ocr-vlm-pipeline-convergence-v1 change)
ENSEMBLE_PATHS = [
    "Path 1: Docling-serve → text → BAML function",
    "Path 2: Docling-serve → Unstract workflow → JSON",
    "Path 3: qwen3-vl-8b page-level image → JSON",
    "Path 4: gemma-4-26B-A4B page-level image → JSON",
    "RAGAS consensus → canonical row → BIEP DuckLake table",
]


def extract_pdf_4_paths(
    pdf_path: Path,
    subject: str,
    language: str,
) -> dict[str, Any]:
    """Run the 4-path OCR/VLM ensemble on a single PDF.

    In production, this:
    1. Reads the PDF bytes
    2. Calls Docling-serve → text → path 1
    3. Calls Docling-serve → Unstract → path 2
    4. Calls qwen3-vl-8b → path 3
    5. Calls gemma-4-26B-A4B → path 4
    6. Calls RAGAS `biiep_extraction_consensus` to vote the canonical row
    7. Emits the canonical row to the BIEP DuckLake table

    Args:
        pdf_path: Path to the official PDF (e.g. curriculumonline.ie syllabus).
        subject: The subject slug (e.g. "physics", "chemistry").
        language: The PDF language ("en" or "ga").

    Returns:
        Dict with the 4-path outputs + the RAGAS consensus.
    """
    # In dev (no GPU), emit a structured stub so the pipeline
    # can still be tested end-to-end. In production, replace each
    # `_stub_*` call with the actual inference call.
    return {
        "pdf_path": str(pdf_path),
        "subject": subject,
        "language": language,
        "path_1_baml": _stub_path_1(pdf_path, subject),
        "path_2_unstract": _stub_path_2(pdf_path),
        "path_3_qwen3_vl": _stub_path_3(pdf_path),
        "path_4_gemma4": _stub_path_4(pdf_path),
        "ragas_consensus": _stub_ragas_consensus(),
        "duration_ms": 0,
    }


def _stub_path_1(pdf_path: Path, subject: str) -> dict[str, Any]:
    """Path 1: Docling-serve → text → BAML function. In production, calls
    meaisinfhoghlaim.ocr.ensemble.ensembled_extractor.EnsembledExtractor
    and emits the typed BAML output (CurriculumSyllabus, ExamPaperLayout,
    MarkingSchemeGuideline, or SyllabusDiagram)."""
    return {
        "stub": True,
        "backend": "Docling-serve → BAML",
        "output_type": "Pydantic row",
        "source_pdf": str(pdf_path),
        "subject": subject,
        "baml_function": f"ExtractCurriculumSyllabus(text, {subject!r})",
    }


def _stub_path_2(pdf_path: Path) -> dict[str, Any]:
    """Path 2: Docling-serve → Unstract workflow. In production, calls
    the Unstract API for structured extraction."""
    return {
        "stub": True,
        "backend": "Docling-serve → Unstract",
        "output_type": "JSON",
        "source_pdf": str(pdf_path),
    }


def _stub_path_3(pdf_path: Path) -> dict[str, Any]:
    """Path 3: qwen3-vl-8b page-level image → JSON. In production,
    routes through the MODEL_REGISTRY qwen3-vl-8b entry."""
    return {
        "stub": True,
        "backend": "qwen3-vl-8b",
        "output_type": "JSON",
        "source_pdf": str(pdf_path),
        "model_registry_key": "local/vision/qwen3-vl-8b",
    }


def _stub_path_4(pdf_path: Path) -> dict[str, Any]:
    """Path 4: gemma-4-26B-A4B page-level image → JSON. In production,
    routes through the MODEL_REGISTRY gemma-4-26B-A4B entry."""
    return {
        "stub": True,
        "backend": "gemma-4-26B-A4B",
        "output_type": "JSON",
        "source_pdf": str(pdf_path),
        "model_registry_key": "local/vision/gemma-4-26B-A4B",
    }


def _stub_ragas_consensus() -> dict[str, Any]:
    """RAGAS consensus voting across the 4 paths. In production, calls
    the RAGAS metric `biiep_extraction_consensus` to vote the canonical row."""
    return {
        "stub": True,
        "metric": "biiep_extraction_consensus",
        "consensus_score": 0.0,
        "winning_path": None,
    }


def process_manifest(
    manifest_path: Path,
    subject: str | None = None,
) -> list[dict[str, Any]]:
    """Process all PDFs (or one subject) per the ingestion manifest.

    Args:
        manifest_path: Path to `ireland_lc_ingestion_manifest.json`.
        subject: If set, only process this subject (e.g. "physics").

    Returns:
        List of extraction results (one per PDF).
    """
    with open(manifest_path) as f:
        manifest = json.load(f)

    results: list[dict[str, Any]] = []
    for subj, data in manifest["subjects"].items():
        if subject and subj != subject:
            continue
        for pdf in data["pdfs"]:
            pdf_path = Path("leaving_certificate") / pdf["path"]
            logger.info(f"Processing {subj}/{pdf['path']}...")
            result = extract_pdf_4_paths(
                pdf_path=pdf_path,
                subject=subj,
                language=pdf["language"],
            )
            results.append(result)

    return results


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)

    # Process physics first (the most recently downloaded)
    subject = sys.argv[1] if len(sys.argv) > 1 else "physics"
    print(f"Processing subject: {subject}")

    manifest_path = Path("leaving_certificate/.ocr_vlm_manifest/ireland_lc_ingestion_manifest.json")
    results = process_manifest(manifest_path, subject=subject)

    # Save the results as a runtime evidence file
    out_path = Path(f"leaving_certificate/.ocr_vlm_manifest/{subject}_extraction_results.json")
    with open(out_path, "w") as f:
        json.dump(
            {
                "subject": subject,
                "results": results,
                "total_processed": len(results),
                "generated_at": "2026-08-13",
            },
            f,
            indent=2,
        )
    print(f"Wrote {out_path} ({len(results)} PDFs)")
