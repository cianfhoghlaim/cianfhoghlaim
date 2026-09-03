"""England full-coverage MotherDuck Flight (BIEP v3 Phase 0)."""
from __future__ import annotations

from pathlib import Path

FLIGHT_SQL = Path(__file__).with_suffix(".sql").read_text()


def build_england_full_coverage_flight() -> str:
    return FLIGHT_SQL


__all__ = ["build_england_full_coverage_flight"]
