"""BIEP v3 milestone gate — verify the active milestone's 3 asset checks pass.

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

Usage:
    mise run biep:v3:gate
    mise run biep:v3:gate --milestone=m1
    mise run biep:v3:gate --milestone=m4

Exits 0 iff all 3 milestone-level asset checks pass:
- <milestone>_documents_ingested_check (cohort count >= N)
- <milestone>_extractions_ragas_check (score >= 0.70)
- <milestone>_lance_chunks_check (chunk count >= N * 1000)

If --milestone is not specified, derives the active milestone from the
BIEP V3 STATE pointer file (defaults to m0 if no state file exists).
"""

from __future__ import annotations

import argparse
import logging
import re
import subprocess
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("biiep_v3_gate")


STATE_FILE = Path(".biiep_v3_state")


MILESTONE_THRESHOLDS = {
    "m0": {"check_count": 4, "min_cohort_count": 0, "min_lance_chunks": 0},
    "m1": {"check_count": 3, "min_cohort_count": 12, "min_lance_chunks": 12_000},
    "m2": {"check_count": 3, "min_cohort_count": 140, "min_lance_chunks": 140_000},
    "m3": {"check_count": 3, "min_cohort_count": 147, "min_lance_chunks": 147_000},
    "m4": {"check_count": 3, "min_cohort_count": 129, "min_lance_chunks": 129_000},
}


def derive_active_milestone() -> str:
    """Derive the active milestone from the state file (default m0)."""
    if not STATE_FILE.exists():
        return "m0"
    return STATE_FILE.read_text().strip() or "m0"


def set_active_milestone(milestone: str) -> None:
    """Mark a milestone as complete in the state file."""
    STATE_FILE.write_text(milestone)


def check_milestone(milestone: str) -> bool:
    """Run the 3 (or 4) asset checks for the given milestone. Return True iff all pass."""
    if milestone not in MILESTONE_THRESHOLDS:
        logger.error(f"Unknown milestone: {milestone}. Valid: {list(MILESTONE_THRESHOLDS)}")
        return False
    if milestone == "m0":
        # M0 has 4 asset checks (no cohort counts)
        logger.info("Running M0 foundation asset checks...")
        result = subprocess.run(
            [
                "uv", "run", "dagster", "asset", "check",
                "--select", "lakehouse_smoke_test_check,baml_codegen_check,registry_seed_check,lance_namespace_check",
                "-m", "orchestration.definitions",
            ],
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode != 0:
            logger.error(f"M0 asset checks failed: {result.stderr[-2000:]}")
            return False
        logger.info("M0 asset checks passed.")
        return True

    # M1–M4: 3 asset checks per milestone
    thresholds = MILESTONE_THRESHOLDS[milestone]
    asset_prefix = {
        "m1": "ireland_lc",
        "m2": "ireland_jc",
        "m3": "england_a_level",
        "m4": "england_gcse",
    }[milestone]
    check_selectors = (
        f"{asset_prefix}_documents_ingested_check,"
        f"{asset_prefix}_extractions_ragas_check,"
        f"{asset_prefix}_lance_chunks_check"
    )
    logger.info(f"Running {milestone.upper()} asset checks for {asset_prefix}... (>= {thresholds['min_cohort_count']} cohorts)")
    result = subprocess.run(
        [
            "uv", "run", "dagster", "asset", "check",
            "--select", check_selectors,
            "-m", "orchestration.definitions",
        ],
        capture_output=True,
        text=True,
        timeout=600,
    )
    if result.returncode != 0:
        logger.error(f"{milestone.upper()} asset checks failed: {result.stderr[-2000:]}")
        return False
    logger.info(f"{milestone.upper()} asset checks passed.")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="BIEP v3 milestone gate")
    parser.add_argument(
        "--milestone",
        choices=[f"m{i}" for i in range(5)] + [f"m{i}" for i in range(1, 5)],
        help="Milestone to gate (default: derive from state file).",
    )
    parser.add_argument(
        "--mark-complete",
        action="store_true",
        help="Mark the milestone as complete in the state file after the gate passes.",
    )
    args = parser.parse_args()

    milestone = args.milestone or derive_active_milestone()
    logger.info(f"BIEP v3 milestone gate — {milestone.upper()}")

    if not check_milestone(milestone):
        logger.error(f"{milestone.upper()} gate FAILED.")
        return 1

    if args.mark_complete:
        set_active_milestone(milestone)
        logger.info(f"{milestone.upper()} marked complete in {STATE_FILE}")

    logger.info(f"{milestone.upper()} gate PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
