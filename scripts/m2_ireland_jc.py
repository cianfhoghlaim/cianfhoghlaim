"""M2 entrypoint — Ireland Junior Cycle pipeline (88 cohorts, EN+GA).

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

Runs the 5-phase pattern for the 88 Ireland JC cohorts
(18 subjects × 2 langs + 16 short courses + 36 CBAs):

Phase A: Ingestion (88 PDFs/metadata land at canonical snake_case path)
Phase B: Extraction (4-path OCR ensemble + RAGAS voting)
Phase C: Embedding (CocoIndex v1 App per JC cohort)
Phase D: ibis logging (88 audit rows in ireland_jc_audit DuckLake table)
Phase E: Analytics (notebooks/19_ireland_pipeline_dashboard.py renders
         the 88-row cohort matrix)

Exits 0 iff all 3 asset checks pass:
- ireland_jc_documents_ingested_check (cohort count >= 88)
- ireland_jc_extractions_ragas_check (score >= 0.65)
- ireland_jc_lance_chunks_check (chunk count >= 88_000)
"""

from __future__ import annotations

import logging
import subprocess
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("biiep_v3_m2")


def run(cmd: list[str], timeout: int = 600) -> bool:
    """Run a subprocess and return True iff exit code is 0."""
    logger.info(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        logger.error(f"Command failed (exit {result.returncode}): {result.stderr[-2000:]}")
        return False
    return True


def main() -> int:
    """Run the 5-phase M2 pipeline. Exit 0 iff all 3 asset checks pass."""
    # Phase A: Ingestion
    logger.info("=== M2 Phase A: Ingestion (88 Ireland JC cohorts) ===")
    if not run([
        "uv", "run", "dagster", "asset", "materialize",
        "--select", "ireland_jc_documents_ingested",
        "-m", "orchestration.definitions",
    ]):
        return 1

    # Phase B: Extraction
    logger.info("=== M2 Phase B: Extraction (4-path OCR + RAGAS) ===")
    if not run([
        "uv", "run", "dagster", "asset", "materialize",
        "--select", "ireland_jc_extractions",
        "-m", "orchestration.definitions",
    ]):
        return 1

    # Phase C: Embedding
    logger.info("=== M2 Phase C: Embedding (CocoIndex v1 Apps) ===")
    if not run([
        "uv", "run", "dagster", "asset", "materialize",
        "--select", "ireland_jc_embeddings",
        "-m", "orchestration.definitions",
    ]):
        return 1

    # Phase D: ibis logging (automatic via asset dependency)
    # Phase E: Analytics
    logger.info("=== M2 Phase E: Analytics (marimo notebook) ===")
    if not run([
        "uv", "run", "marimo", "run", "notebooks/19_ireland_pipeline_dashboard.py",
        "--headless", "--port=8765",
    ], timeout=120):
        logger.warning("marimo notebook may have failed; check the file manually")

    # Asset checks
    logger.info("=== M2 Asset Checks ===")
    if not run([
        "uv", "run", "dagster", "asset", "check",
        "--select", "ireland_jc_documents_ingested_check,ireland_jc_extractions_ragas_check,ireland_jc_lance_chunks_check",
        "-m", "orchestration.definitions",
    ]):
        return 1

    logger.info("M2 complete. All 3 asset checks pass; 88 Ireland JC cohorts (18×2 specs + 16 short + 36 CBA) materialised.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
