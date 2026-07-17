"""Daily 8-jurisdiction declarative automation — BIEP v3 P2.

Per the 2026-08-08-biep-v3-production-readiness-v1 change.

Triggers the canonical daily backfill for all 8 BIEP v3 jurisdictions
at midnight UTC. Replaces the dangling 6-hour `ScheduleDefinition`
that targets a non-existent job.
"""
from __future__ import annotations

from dagster import AutomationCondition

# The canonical 8 jurisdictions
EIGHT_JURISDICTIONS = (
    "ireland", "england", "scotland", "wales",
    "northern_ireland", "jersey", "guernsey", "isle_of_man",
)


def make_biiep_v3_daily_automation() -> AutomationCondition:
    """Daily automation for the BIEP v3 ingestion root.

    Triggers at midnight UTC. Eager downstream (extraction → embedding).
    """
    return AutomationCondition.cron("@daily")


def make_per_jurisdiction_daily_automation(jurisdiction: str) -> AutomationCondition:
    """Per-jurisdiction daily automation.

    Triggers at midnight UTC. Eager downstream.
    """
    return AutomationCondition.cron(f"@daily[{jurisdiction}]")


__all__ = ["EIGHT_JURISDICTIONS", "make_biiep_v3_daily_automation", "make_per_jurisdiction_daily_automation"]
