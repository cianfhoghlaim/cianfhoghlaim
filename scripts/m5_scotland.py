"""M5 entrypoint — Scotland pipeline (150 cohorts, SQA).

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

Runs the 5-phase pattern for the 150 Scotland cohorts (50 SCQF
subjects × 3 qualification levels × 1 language):

Phase A: Ingestion (150 PDFs/metadata land at canonical snake_case path)
Phase B: Extraction (4-path OCR ensemble + RAGAS voting)
Phase C: Embedding (CocoIndex v1 App per (subject, level) cohort)
Phase D: ibis logging (150 audit rows in scotland_audit DuckLake table)
Phase E: Analytics (motherduck/dives/scotland_curriculum_dive.py renders
         the 150-row cohort matrix)

Exits 0 iff all 3 asset checks pass:
- scotland_documents_ingested_check (cohort count >= 150)
- scotland_extractions_ragas_check (score >= 0.70)
- scotland_lance_chunks_check (chunk count >= 150_000)

YEARLY automation (1st September 00:00 UTC) per the BIEP v3 scheduling policy.
"""

from __future__ import annotations

import logging
import subprocess
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("biiep_v3_m5")


def run(cmd: list[str], timeout: int = 600) -> bool:
    """Run a subprocess and return True iff exit code is 0."""
    logger.info(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        logger.error(f"Command failed (exit {result.returncode}): {result.stderr[-2000:]}")
        return False
    return True


def main() -> int:
    """Run the 5-phase M5 pipeline. Exit 0 iff all 3 asset checks pass."""
    # Phase A: Ingestion
    logger.info("=== M5 Phase A: Ingestion (150 Scotland cohorts) ===")
    if not run([
        "uv", "run", "dagster", "asset", "materialize",
        "--select", "scotland_documents_ingested",
        "-m", "orchestration.definitions",
    ]):
        return 1

    # Phase B: Extraction
    logger.info("=== M5 Phase B: Extraction (4-path OCR + RAGAS) ===")
    if not run([
        "uv", "run", "dagster", "asset", "materialize",
        "--select", "scotland_extractions",
        "-m", "orchestration.definitions",
    ]):
        return 1

    # Phase C: Embedding
    logger.info("=== M5 Phase C: Embedding (CocoIndex v1 Apps) ===")
    if not run([
        "uv", "run", "dagster", "asset", "materialize",
        "--select", "scotland_embeddings",
        "-m", "orchestration.definitions",
    ]):
        return 1

    # Phase D: ibis logging (automatic via asset dependency)
    # Phase E: Analytics
    logger.info("=== M5 Phase E: Analytics (MotherDuck Dive) ===")
    logger.info(
        "The MotherDuck Dive `scotland_curriculum_topics` is the canonical "
        "operator surface for this jurisdiction. Run via the MotherDuck UI."
    )

    # Asset checks
    logger.info("=== M5 Asset Checks ===")
    if not run([
        "uv", "run", "dagster", "asset", "check",
        "--select", "scotland_documents_ingested_check,scotland_extractions_ragas_check,scotland_lance_chunks_check",
        "-m", "orchestration.definitions",
    ]):
        return 1

    logger.info("M5 complete. All 3 asset checks pass; 150 Scotland cohorts materialised.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
