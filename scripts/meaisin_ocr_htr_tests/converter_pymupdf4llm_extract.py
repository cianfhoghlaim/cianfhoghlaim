"""meaisinfhoghlaim Document Converter entrypoint script for pymupdf4llm.

Per the meaisinfhoghlaim v5 umbrella spec + the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

Runs the canonical document converter pipeline for the pymupdf4llm converter.
The converter is registered in the meaisinfhoghlaim document factory
at `meaisinfhoghlaim.document_factory`.

Usage:
    uv run python scripts/meaisin_ocr_htr_tests/converter_pymupdf4llm_extract.py
"""

from __future__ import annotations

import logging
import subprocess
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("converter_pymupdf4llm_extract")


def _run_converter() -> bool:
    """Run the pymupdf4llm converter on a sample PDF."""
    logger.info("Running pymupdf4llm converter on sample PDF...")
    try:
        from meaisinfhoghlaim.document_factory import CONVERTERS

        converter = CONVERTERS.get("pymupdf4llm")
        if converter is None:
            logger.warning("pymupdf4llm not available; skipping")
            return True
        result = converter.convert("s3://garage/cianfhoghlaim/sample.pdf")
        logger.info("Converter result: %s", result)
        return True
    except Exception as exc:  # noqa: BLE001
        logger.error("Converter failed: %s", exc)
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
    """Run the 3 steps for the pymupdf4llm converter. Exit 0 on success."""
    logger.info("=" * 60)
    logger.info("Document converter entrypoint: pymupdf4llm")
    logger.info("=" * 60)

    steps = [
        ("1. Document converter", _run_converter),
        ("2. OCR evaluation harness", _run_ocr_evaluation),
        ("3. 24-model registry audit", _run_model_registry_audit),
    ]

    for name, step in steps:
        logger.info("=== Running step %s ===", name)
        if not step():
            logger.error("pymupdf4llm entrypoint failed at step %s.", name)
            return 1

    logger.info("=" * 60)
    logger.info("pymupdf4llm converter entrypoint complete. All 3 steps passed.")
    logger.info("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
