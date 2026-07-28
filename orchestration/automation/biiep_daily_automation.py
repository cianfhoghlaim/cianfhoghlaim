"""Daily 8-jurisdiction declarative automation — BIEP v3 P2.

Per the 2026-08-08-biep-v3-production-readiness-v1 change +
2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

Triggers the canonical daily backfill for all 8 BIEP v3 jurisdictions
at staggered UTC times per the M1 spec:
- Ireland Leaving Cycle: 02:00 UTC
- Ireland Junior Cycle:  02:30 UTC
- England A-Level:        03:00 UTC
- England GCSE:           03:30 UTC
- Scotland:               04:00 UTC
- Wales:                  04:00 UTC
- Northern Ireland:       04:00 UTC
- Crown Dependencies:     04:30 UTC

Replaces the dangling 6-hour `ScheduleDefinition` that targets a
non-existent job.
"""
from __future__ import annotations

from dagster import AutomationCondition

# The canonical 8 jurisdictions
EIGHT_JURISDICTIONS = (
    "ireland", "england", "scotland", "wales",
    "northern_ireland", "jersey", "guernsey", "isle_of_man",
)


# -----------------------------------------------------------------------------
# Per-milestone daily automation cron schedules
# -----------------------------------------------------------------------------

# Format: (milestone, jurisdiction, stage, UTC_hour, UTC_minute)
DAILY_CRON_SCHEDULES = (
    # M1 — Ireland Leaving Cycle (12 cohorts, EN + GA)
    ("m1", "ireland", "leaving_cycle", 2, 0),
    # M2 — Ireland Junior Cycle (140 cohorts, EN + GA)
    ("m2", "ireland", "junior_cycle", 2, 30),
    # M3 — England A-Level (147 cohorts, AQA + OCR + Edexcel)
    ("m3", "england", "a_level", 3, 0),
    # M4 — England GCSE (129 cohorts, AQA + OCR + Edexcel)
    ("m4", "england", "gcse", 3, 30),
    # Reserved for the 4 follow-up jurisdictions (deferred to a different change)
    ("sct_wls_ni", "scotland+waales+ni", "all", 4, 0),
    ("crown", "jersey+guernsey+isle_of_man", "all", 4, 30),
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


def make_ireland_lc_daily_automation() -> AutomationCondition:
    """Daily automation for Ireland LC (M1) — 02:00 UTC."""
    return AutomationCondition.cron("0 2 * * *")


def make_ireland_jc_daily_automation() -> AutomationCondition:
    """Daily automation for Ireland JC (M2) — 02:30 UTC."""
    return AutomationCondition.cron("30 2 * * *")


def make_england_a_level_daily_automation() -> AutomationCondition:
    """Daily automation for England A-Level (M3) — 03:00 UTC."""
    return AutomationCondition.cron("0 3 * * *")


def make_england_gcse_daily_automation() -> AutomationCondition:
    """Daily automation for England GCSE (M4) — 03:30 UTC."""
    return AutomationCondition.cron("30 3 * * *")


__all__ = [
    "EIGHT_JURISDICTIONS",
    "DAILY_CRON_SCHEDULES",
    "make_biiep_v3_daily_automation",
    "make_per_jurisdiction_daily_automation",
    "make_ireland_lc_daily_automation",
    "make_ireland_jc_daily_automation",
    "make_england_a_level_daily_automation",
    "make_england_gcse_daily_automation",
]
