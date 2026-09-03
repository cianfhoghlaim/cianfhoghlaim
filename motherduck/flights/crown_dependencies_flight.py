"""Crown Dependencies (Jersey/Guernsey/IoM) full-coverage MotherDuck Flight (BIEP v3 Phase 0 + 2026-08-13 update).

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change,
this flight now calls the 3 per-jurisdiction proper entrypoint scripts
(m8 Jersey + m9 Guernsey + m10 Isle of Man) instead of the old
multi-jurisdiction `crown_dependencies_jurisdiction_pipeline()`.
"""
from __future__ import annotations

import logging
import subprocess
from pathlib import Path

logger = logging.getLogger("crown_dependencies_flight")

FLIGHT_SQL = Path(__file__).with_suffix(".sql").read_text()


def _run_per_jurisdiction_entrypoint() -> bool:
    """Run the 3 per-jurisdiction entrypoint scripts in order."""
    for entrypoint in ("m8_jersey", "m9_guernsey", "m10_isle_of_man"):
        try:
            result = subprocess.run(
                ["uv", "run", "python", f"scripts/{entrypoint}.py"],
                capture_output=True,
                text=True,
                timeout=3600,  # 1 hour per jurisdiction
            )
            if result.returncode != 0:
                logger.error(
                    f"{entrypoint} failed (exit {result.returncode}): {result.stderr[-1000:]}"
                )
                return False
        except Exception as exc:  # noqa: BLE001
            logger.error(f"{entrypoint} raised: {exc}")
            return False
    return True


def build_crown_dependencies_flight() -> str:
    """Build the canonical Crown Dependencies full-coverage flight.

    Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1
    change, this flight now calls the 3 per-jurisdiction proper entrypoint
    scripts (m8 Jersey + m9 Guernsey + m10 Isle of Man) instead of the
    old multi-jurisdiction `crown_dependencies_jurisdiction_pipeline()`.
    """
    return FLIGHT_SQL


def main() -> int:
    """Run the canonical Crown Dependencies full-coverage flight. Exit 0 on success."""
    logger.info("Starting Crown Dependencies full-coverage flight (yearly 1st September 00:00 UTC)...")
    if not _run_per_jurisdiction_entrypoint():
        logger.error("Crown Dependencies full-coverage flight failed.")
        return 1
    logger.info("Crown Dependencies full-coverage flight complete.")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())


__all__ = ["build_crown_dependencies_flight"]
