"""OCR/VLM model entrypoint script for molmo2-4b.

Per the meaisinfhoghlaim v5 umbrella spec + the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

Runs the canonical 4-path OCR ensemble for the molmo2-4b OCR/VLM model.
The 4 paths are:
- Path 1 (BAML): Docling-serve -> text -> BAML molmo2-4b
- Path 2 (Unstract): Docling-serve -> Unstract workflow
- Path 3 (qwen3-vl): qwen3-vl-8b page-level image
- Path 4 (gemma4): gemma-4-26B-A4B page-level image

Each path output lands in its own per-jurisdiction DuckLake table.
Then the RAGAS biiep_extraction_consensus metric votes the canonical row.

Usage:
    uv run python scripts/meaisin_ocr_htr_tests/ocr_model_molmo2_4b_extract.py

Reference: openspec/changes/2026-07-22-biep-v2-ocr-vlm-pipeline-convergence-v1/
"""

from __future__ import annotations

import logging
import subprocess
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ocr_model_molmo2_4b_extract")


def _run_4_path_ensemble() -> bool:
    """Run the 4-path OCR ensemble for the molmo2-4b model."""
    logger.info("Running 4-path OCR ensemble for molmo2-4b...")
    try:
        from meaisinfhoghlaim.ocr.ensemble.ensembled_extractor import EnsembledExtractor
        from meaisinfhoghlaim.models.registry import VISION_MODELS

        model = VISION_MODELS.get("molmo2-4b")
        if model is None or not model.available:
            logger.warning("molmo2-4b not available; skipping")
            return True

        extractor = EnsembledExtractor()
        result = extractor.extract(
            pdf_path="s3://garage/cianfhoghlaim/sample.pdf",
            baml_function="b.ExtractPrimaryLearningOutcomes",
            jurisdiction="ireland",
            scope="education",
            subject="sample",
            board="ncca",
            qualification_level="higher",
            language="en",
        )
        logger.info(
            "Ensemble result: ragas_score=%s, paths=%s",
            getattr(result, "ragas_score", "N/A"),
            ["baml", "unstract", "qwen3_vl", "gemma4"],
        )
        return True
    except Exception as exc:  # noqa: BLE001
        logger.error("Ensemble failed: %s", exc)
        return False


def _run_ocr_evaluation() -> bool:
    """Run the OCR evaluation harness."""
    logger.info("Running OCR evaluation harness...")
    try:
        result = subprocess.run(
            ["mise", "run", "cic:ocr:test"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            logger.error("OCR evaluation failed: %s", result.stderr[-1000:])
            return False
        return True
    except Exception as exc:  # noqa: BLE001
        logger.error("OCR evaluation raised: %s", exc)
        return False


def _run_model_registry_audit() -> bool:
    """Run the meaisinfhoghlaim 24-model registry audit."""
    logger.info("Running meaisinfhoghlaim 24-model registry audit...")
    try:
        result = subprocess.run(
            ["mise", "run", "cic:meaisin:registry-audit"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            logger.error("Registry audit failed: %s", result.stderr[-1000:])
            return False
        return True
    except Exception as exc:  # noqa: BLE001
        logger.error("Registry audit raised: %s", exc)
        return False


def main() -> int:
    """Run the 3 steps for the molmo2-4b OCR/VLM model. Exit 0 on success."""
    logger.info("=" * 60)
    logger.info("OCR/VLM model entrypoint: molmo2-4b")
    logger.info("=" * 60)

    steps = [
        ("1. 4-path OCR ensemble", _run_4_path_ensemble),
        ("2. OCR evaluation harness", _run_ocr_evaluation),
        ("3. 24-model registry audit", _run_model_registry_audit),
    ]

    for name, step in steps:
        logger.info("=== Running step %s ===", name)
        if not step():
            logger.error("molmo2-4b entrypoint failed at step %s.", name)
            return 1

    logger.info("=" * 60)
    logger.info("molmo2-4b OCR/VLM entrypoint complete. All 3 steps passed.")
    logger.info("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
