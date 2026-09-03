"""M6 entrypoint — Wales pipeline (160 cohorts, WJEC).

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

Runs the 5-phase pattern for the 160 Wales cohorts (80 WJEC subjects ×
2 qualification levels × 1 Welsh language).

YEARLY automation (1st September 00:00 UTC) per the BIEP v3 scheduling.
"""

from __future__ import annotations

import logging
import subprocess
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("biiep_v3_m6")


def run(cmd: list[str], timeout: int = 600) -> bool:
    logger.info(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        logger.error(f"Command failed (exit {result.returncode}): {result.stderr[-2000:]}")
        return False
    return True


def main() -> int:
    """Run the 5-phase M6 pipeline. Exit 0 iff all 3 asset checks pass."""
    # Phase A: Ingestion
    logger.info("=== M6 Phase A: Ingestion (160 Wales cohorts) ===")
    if not run([
        "uv", "run", "dagster", "asset", "materialize",
        "--select", "wales_documents_ingested",
        "-m", "orchestration.definitions",
    ]):
        return 1

    # Phase B: Extraction
    logger.info("=== M6 Phase B: Extraction (4-path OCR + RAGAS) ===")
    if not run([
        "uv", "run", "dagster", "asset", "materialize",
        "--select", "wales_extractions",
        "-m", "orchestration.definitions",
    ]):
        return 1

    # Phase C: Embedding
    logger.info("=== M6 Phase C: Embedding (CocoIndex v1 Apps) ===")
    if not run([
        "uv", "run", "dagster", "asset", "materialize",
        "--select", "wales_embeddings",
        "-m", "orchestration.definitions",
    ]):
        return 1

    # Asset checks
    logger.info("=== M6 Asset Checks ===")
    if not run([
        "uv", "run", "dagster", "asset", "check",
        "--select", "wales_documents_ingested_check,wales_extractions_ragas_check,wales_lance_chunks_check",
        "-m", "orchestration.definitions",
    ]):
        return 1

    logger.info("M6 complete. All 3 asset checks pass; 160 Wales cohorts materialised.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
