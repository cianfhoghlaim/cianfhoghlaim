"""SCT+WLS+NI full-coverage MotherDuck Flight (BIEP v3 Phase 0 + 2026-08-13 update).

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change,
this flight now calls the 3 per-jurisdiction proper entrypoint scripts
(m5 Scotland + m6 Wales + m7 Northern Ireland) instead of the old
multi-jurisdiction `sct_wls_ni_jurisdiction_pipeline()`.
"""
from __future__ import annotations

import logging
import subprocess
from pathlib import Path

logger = logging.getLogger("sct_wls_ni_flight")

FLIGHT_SQL = Path(__file__).with_suffix(".sql").read_text()


def _run_per_jurisdiction_entrypoint() -> bool:
    """Run the 3 per-jurisdiction entrypoint scripts in order."""
    for entrypoint in ("m5_scotland", "m6_wales", "m7_northern_ireland"):
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


def build_sct_wls_ni_flight() -> str:
    """Build the canonical SCT+WLS+NI full-coverage flight.

    Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1
    change, this flight now calls the 3 per-jurisdiction proper entrypoint
    scripts (m5 Scotland + m6 Wales + m7 Northern Ireland) instead of
    the old multi-jurisdiction `sct_wls_ni_jurisdiction_pipeline()`.
    """
    return FLIGHT_SQL


def main() -> int:
    """Run the canonical SCT+WLS+NI full-coverage flight. Exit 0 on success."""
    logger.info("Starting SCT+WLS+NI full-coverage flight (yearly 1st September 00:00 UTC)...")
    if not _run_per_jurisdiction_entrypoint():
        logger.error("SCT+WLS+NI full-coverage flight failed.")
        return 1
    logger.info("SCT+WLS+NI full-coverage flight complete.")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())


__all__ = ["build_sct_wls_ni_flight"]
