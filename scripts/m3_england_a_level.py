"""M3 entrypoint — England A-Level pipeline (147 cohorts, AQA + OCR + Edexcel).

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

Runs the 5-phase pattern for the 147 England A-Level cohorts
(49 subjects × 3 awarding boards: AQA, OCR, Edexcel):

Phase A: Ingestion (147 PDFs land at canonical snake_case path)
Phase B: Extraction (4-path OCR ensemble + RAGAS voting, per board)
Phase C: Embedding (CocoIndex v1 App per (board × subject) pair)
Phase D: ibis logging (147 audit rows in england_a_level_audit DuckLake table)
Phase E: Analytics (notebooks/20_england_pipeline_dashboard.py renders
         the 147-row cohort matrix)

Exits 0 iff all 3 asset checks pass:
- england_a_level_documents_ingested_check (cohort count >= 147)
- england_a_level_extractions_ragas_check (score >= 0.70)
- england_a_level_lance_chunks_check (chunk count >= 147_000)

YEARLY automation (1st September 00:00 UTC) per the BIEP v3 scheduling policy.
"""

from __future__ import annotations

import logging
import subprocess
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("biiep_v3_m3")


def run(cmd: list[str], timeout: int = 600) -> bool:
    """Run a subprocess and return True iff exit code is 0."""
    logger.info(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        logger.error(f"Command failed (exit {result.returncode}): {result.stderr[-2000:]}")
        return False
    return True


def main() -> int:
    """Run the 5-phase M3 pipeline. Exit 0 iff all 3 asset checks pass."""
    # Phase A: Ingestion
    logger.info("=== M3 Phase A: Ingestion (147 England A-Level cohorts) ===")
    if not run([
        "uv", "run", "dagster", "asset", "materialize",
        "--select", "england_documents_ingested",
        "-m", "orchestration.definitions",
    ]):
        return 1

    # Phase B: Extraction
    logger.info("=== M3 Phase B: Extraction (4-path OCR + RAGAS) ===")
    if not run([
        "uv", "run", "dagster", "asset", "materialize",
        "--select", "england_extractions",
        "-m", "orchestration.definitions",
    ]):
        return 1

    # Phase C: Embedding
    logger.info("=== M3 Phase C: Embedding (CocoIndex v1 Apps) ===")
    if not run([
        "uv", "run", "dagster", "asset", "materialize",
        "--select", "england_embeddings",
        "-m", "orchestration.definitions",
    ]):
        return 1

    # Phase D: ibis logging (automatic via asset dependency)
    # Phase E: Analytics
    logger.info("=== M3 Phase E: Analytics (marimo notebook) ===")
    if not run([
        "uv", "run", "marimo", "run", "notebooks/20_england_pipeline_dashboard.py",
        "--headless", "--port=8765",
    ], timeout=120):
        logger.warning("marimo notebook may have failed; check the file manually")

    # Asset checks
    logger.info("=== M3 Asset Checks ===")
    if not run([
        "uv", "run", "dagster", "asset", "check",
        "--select", "england_a_level_documents_ingested_check,england_a_level_extractions_ragas_check,england_a_level_lance_chunks_check",
        "-m", "orchestration.definitions",
    ]):
        return 1

    logger.info("M3 complete. All 3 asset checks pass; 147 England A-Level cohorts (49×3 AQA+OCR+Edexcel) materialised.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
