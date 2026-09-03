"""M10 entrypoint — Isle of Man pipeline (120 cohorts).

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

Runs the 5-phase pattern for the 120 Isle of Man cohorts (30 subjects
× 4 qualification levels: GCSE + A-Level + IB + Local). Includes the
unique Manx Gaelic GCSE.

YEARLY automation (1st September 00:00 UTC) per the BIEP v3 scheduling.
"""

from __future__ import annotations

import logging
import subprocess
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("biiep_v3_m10")


def run(cmd: list[str], timeout: int = 600) -> bool:
    logger.info(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        logger.error(f"Command failed (exit {result.returncode}): {result.stderr[-2000:]}")
        return False
    return True


def main() -> int:
    """Run the 5-phase M10 pipeline. Exit 0 iff all 3 asset checks pass."""
    # Phase A: Ingestion
    logger.info("=== M10 Phase A: Ingestion (120 Isle of Man cohorts) ===")
    if not run([
        "uv", "run", "dagster", "asset", "materialize",
        "--select", "isle_of_man_documents_ingested",
        "-m", "orchestration.definitions",
    ]):
        return 1

    # Phase B: Extraction
    logger.info("=== M10 Phase B: Extraction (4-path OCR + RAGAS) ===")
    if not run([
        "uv", "run", "dagster", "asset", "materialize",
        "--select", "isle_of_man_extractions",
        "-m", "orchestration.definitions",
    ]):
        return 1

    # Phase C: Embedding
    logger.info("=== M10 Phase C: Embedding (CocoIndex v1 Apps) ===")
    if not run([
        "uv", "run", "dagster", "asset", "materialize",
        "--select", "isle_of_man_embeddings",
        "-m", "orchestration.definitions",
    ]):
        return 1

    # Asset checks
    logger.info("=== M10 Asset Checks ===")
    if not run([
        "uv", "run", "dagster", "asset", "check",
        "--select", "isle_of_man_documents_ingested_check,isle_of_man_extractions_ragas_check,isle_of_man_lance_chunks_check",
        "-m", "orchestration.definitions",
    ]):
        return 1

    logger.info("M10 complete. All 3 asset checks pass; 120 Isle of Man cohorts materialised.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
