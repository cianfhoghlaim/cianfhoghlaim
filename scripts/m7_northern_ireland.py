"""M7 entrypoint — Northern Ireland pipeline (70 cohorts, CCEA).

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

Runs the 5-phase pattern for the 70 Northern Ireland cohorts (35
CCEA subjects × 2 qualification levels × 1 language). Includes the
Gaeltacht overlay (Irish-medium subjects).

YEARLY automation (1st September 00:00 UTC) per the BIEP v3 scheduling.
"""

from __future__ import annotations

import logging
import subprocess
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("biiep_v3_m7")


def run(cmd: list[str], timeout: int = 600) -> bool:
    logger.info(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        logger.error(f"Command failed (exit {result.returncode}): {result.stderr[-2000:]}")
        return False
    return True


def main() -> int:
    """Run the 5-phase M7 pipeline. Exit 0 iff all 3 asset checks pass."""
    # Phase A: Ingestion
    logger.info("=== M7 Phase A: Ingestion (70 Northern Ireland cohorts) ===")
    if not run(
        [
            "uv",
            "run",
            "dagster",
            "asset",
            "materialize",
            "--select",
            "northern_ireland_documents_ingested",
            "-m",
            "orchestration.definitions",
        ]
    ):
        return 1

    # Phase B: Extraction
    logger.info("=== M7 Phase B: Extraction (4-path OCR + RAGAS) ===")
    if not run(
        [
            "uv",
            "run",
            "dagster",
            "asset",
            "materialize",
            "--select",
            "northern_ireland_extractions",
            "-m",
            "orchestration.definitions",
        ]
    ):
        return 1

    # Phase C: Embedding
    logger.info("=== M7 Phase C: Embedding (CocoIndex v1 Apps) ===")
    if not run(
        [
            "uv",
            "run",
            "dagster",
            "asset",
            "materialize",
            "--select",
            "northern_ireland_embeddings",
            "-m",
            "orchestration.definitions",
        ]
    ):
        return 1

    # Asset checks
    logger.info("=== M7 Asset Checks ===")
    if not run(
        [
            "uv",
            "run",
            "dagster",
            "asset",
            "check",
            "--select",
            "northern_ireland_documents_ingested_check,northern_ireland_extractions_ragas_check,northern_ireland_lance_chunks_check",
            "-m",
            "orchestration.definitions",
        ]
    ):
        return 1

    logger.info("M7 complete. All 3 asset checks pass; 70 Northern Ireland cohorts materialised.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
