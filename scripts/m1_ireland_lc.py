"""M1 entrypoint — Ireland Leaving Cycle pipeline (12 cohorts, EN+GA).

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

Runs the 5-phase pattern for the 12 Ireland LC cohorts:

Phase A: Ingestion (12 PDFs land at canonical snake_case path)
Phase B: Extraction (4-path OCR ensemble + RAGAS voting)
Phase C: Embedding (CocoIndex v1 App per cohort)
Phase D: ibis logging (12 audit rows in ireland_lc_audit DuckLake table)
Phase E: Analytics (notebooks/19_ireland_pipeline_dashboard.py renders
         the 12-row cohort matrix)

Exits 0 iff all 3 asset checks pass:
- ireland_lc_documents_ingested_check (cohort count >= 12)
- ireland_lc_extractions_ragas_check (score >= 0.70)
- ireland_lc_lance_chunks_check (chunk count >= 12_000)
"""

from __future__ import annotations

import logging
import subprocess
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("biiep_v3_m1")


def run(cmd: list[str], timeout: int = 600) -> bool:
    """Run a subprocess and return True iff exit code is 0."""
    logger.info(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        logger.error(f"Command failed (exit {result.returncode}): {result.stderr[-2000:]}")
        return False
    return True


def main() -> int:
    """Run the 5-phase M1 pipeline. Exit 0 iff all 3 asset checks pass."""
    # Phase A: Ingestion
    logger.info("=== M1 Phase A: Ingestion (12 Ireland LC cohorts) ===")
    if not run([
        "uv", "run", "dagster", "asset", "materialize",
        "--select", "ireland_lc_documents_ingested",
        "-m", "orchestration.definitions",
    ]):
        return 1

    # Phase B: Extraction (4-path OCR ensemble + RAGAS voting)
    logger.info("=== M1 Phase B: Extraction (4-path OCR + RAGAS) ===")
    if not run([
        "uv", "run", "dagster", "asset", "materialize",
        "--select", "ireland_lc_extractions",
        "-m", "orchestration.definitions",
    ]):
        return 1

    # Phase C: Embedding (CocoIndex v1 Apps)
    logger.info("=== M1 Phase C: Embedding (CocoIndex v1 Apps) ===")
    if not run([
        "uv", "run", "dagster", "asset", "materialize",
        "--select", "ireland_lc_embeddings",
        "-m", "orchestration.definitions",
    ]):
        return 1

    # Phase D: ibis logging (automatic via asset dependency)
    # Phase E: Analytics (render the marimo notebook)
    logger.info("=== M1 Phase E: Analytics (marimo notebook) ===")
    if not run([
        "uv", "run", "marimo", "run", "notebooks/19_ireland_pipeline_dashboard.py",
        "--headless", "--port=8765",
    ], timeout=120):
        # marimo notebook may fail in headless mode; warn but continue
        logger.warning("marimo notebook may have failed; check the file manually")

    # Asset checks
    logger.info("=== M1 Asset Checks ===")
    if not run([
        "uv", "run", "dagster", "asset", "check",
        "--select", "ireland_lc_documents_ingested_check,ireland_lc_extractions_ragas_check,ireland_lc_lance_chunks_check",
        "-m", "orchestration.definitions",
    ]):
        return 1

    logger.info("M1 complete. All 3 asset checks pass; 12 Ireland LC cohorts (EN+GA) materialised.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
