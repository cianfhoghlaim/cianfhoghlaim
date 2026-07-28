"""BIEP v3 scheduling — yearly education content + monthly circulars.

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change +
the user direction (2026-07-28): "all the schedules for these education
official documents should be yearly for exam papers, marking schemes,
syllabus and monthly for more regular types like government circulars."

## Scheduling policy

| Document class | Cadence | Cron | Rationale |
|:--|:--|:--|:--|
| NCCA syllabus (Ireland LC + JC) | **Yearly** | `0 0 1 9 *` | Academic year starts in September; NCCA publishes updated syllabi annually |
| SEC exam papers (Ireland LC) | **Yearly** | `0 0 1 9 *` | SEC publishes exam papers in June + marking schemes in October |
| AQA / OCR / Edexcel GCSE + A-Level specs (England) | **Yearly** | `0 0 1 9 *` | Academic year starts in September; spec changes are annual |
| gov.ie education circulars | **Monthly** | `0 0 1 * *` | Circulars are published irregularly but at high frequency |
| BIEP v3 M0 foundation assets (smoke test, BAML codegen, registry seed) | **Weekly** | `0 6 * * 1` | Smoke tests weekly; codegen runs on BAML file change |
| BIEP v3 RAGAS + audit + RAGAS voting | **Nightly** | `0 0 * * *` | Cheap to run nightly |
| BIEP v3 ChangeDetection.io sensors | **Event-driven** (eager) | n/a | Triggers on NCCA/SEC/AQA/OCR/Edexcel/WJEC/CCEA/JCQ/IoM/Jersey/Guernsey change events |

## Replaces

The legacy 6-hour `biiep_ocr_ensemble_schedule` at
`orchestration/defs/2_materials/ocr_comparison/ensemble_comparison/biiep_ocr_ensemble.py:128`
is retired in favour of the BIEP v3 yearly condition.

The legacy daily crons at:
- `orchestration/defs/1_ingestion/curriculum/ie_ncca_curriculum/`: `0 2 * * *` → **yearly**
- `orchestration/defs/1_ingestion/curriculum/ie_sec_examinations/`: `0 3 * * *` → **yearly**
- `orchestration/defs/1_ingestion/curriculum/lc6_ncca/`: `0 2 * * *` → **yearly**
- `orchestration/defs/1_ingestion/curriculum/lc6_examinations/`: `0 3 * * *` → **yearly**
- `orchestration/defs/1_ingestion/curriculum/lc6/*.yaml` (6 subjects): `0 4 * * *` → **yearly**
- `orchestration/defs/1_ingestion/curriculum/lc5/*.yaml`: `0 5 * * *` → **yearly**
- `orchestration/defs/1_ingestion/curriculum/primary_jc_combined/`: `0 5 * * *` → **yearly**
- `orchestration/defs/1_ingestion/curriculum/junior_cycle/`: `0 4 * * 1` (Mondays) → **yearly**
- `orchestration/defs/1_ingestion/government/circulars/`: `0 * * * *` (hourly) → **monthly**

## Academic year timing

The Irish + English academic year starts in September. The 1st of
September 00:00 UTC is the canonical "yearly tick" for the BIEP
content refresh. For SEC exam papers (published in June) the September
1 trigger is fine — the operator can also re-run the assets manually
after the June exam paper publication.

Reference: openspec/changes/2026-08-13-biep-v3-systematic-download-ireland-england-v1/
openspec/specs/british-isles-education-pipeline-v3/spec.md
"""
from __future__ import annotations

from dagster import AutomationCondition

# -----------------------------------------------------------------------------
# Yearly crons (1st September, 00:00 UTC = start of academic year)
# -----------------------------------------------------------------------------

YEARLY_ACADEMIC_CRON = "0 0 1 9 *"
"""Canonical yearly cron for Ireland + England education content.

September 1st, 00:00 UTC = start of the academic year. NCCA, SEC, AQA,
OCR, and Edexcel publish updated syllabi in the weeks leading up to
this date, and SEC exam papers + marking schemes land in June +
October (covered by manual asset re-runs + ChangeDetection sensors).
"""

# -----------------------------------------------------------------------------
# Monthly crons (1st of each month, 00:00 UTC)
# -----------------------------------------------------------------------------

MONTHLY_CIRCULARS_CRON = "0 0 1 * *"
"""Canonical monthly cron for government circulars (gov.ie + equivalents).

Circulars are published irregularly but at high frequency. A monthly
poll covers the typical cadence (the operator can also re-run the
assets manually between monthly crons if needed).
"""

# -----------------------------------------------------------------------------
# Weekly crons (Monday, 06:00 UTC)
# -----------------------------------------------------------------------------

WEEKLY_SMOKE_TEST_CRON = "0 6 * * 1"
"""Canonical weekly cron for the M0 foundation assets
(lakehouse_smoke_test, baml_codegen_gate, registry_seed_count, lance_namespace_ready).

Monday 06:00 UTC is a low-traffic window; the M0 assets are cheap
and run in < 30 seconds.
"""

# -----------------------------------------------------------------------------
# Nightly crons (00:00 UTC)
# -----------------------------------------------------------------------------

NIGHTLY_AUDIT_CRON = "0 0 * * *"
"""Canonical nightly cron for the BIEP v3 RAGAS + audit + asset checks.

Cheap to run; surfaces stale RAGAS scores, missed ingestion windows,
and 4-path ensemble drift.
"""


# -----------------------------------------------------------------------------
# AutomationCondition factories
# -----------------------------------------------------------------------------


def make_yearly_education_automation() -> AutomationCondition:
    """Yearly automation for Ireland + England education content.

    Triggers on 1st September, 00:00 UTC.
    """
    return AutomationCondition.on_cron(YEARLY_ACADEMIC_CRON, cron_timezone="UTC")


def make_monthly_circulars_automation() -> AutomationCondition:
    """Monthly automation for government circulars (gov.ie + equivalents).

    Triggers on 1st of each month, 00:00 UTC.
    """
    return AutomationCondition.on_cron(MONTHLY_CIRCULARS_CRON, cron_timezone="UTC")


def make_weekly_smoke_test_automation() -> AutomationCondition:
    """Weekly automation for the M0 foundation assets.

    Triggers on Monday, 06:00 UTC.
    """
    return AutomationCondition.on_cron(WEEKLY_SMOKE_TEST_CRON, cron_timezone="UTC")


def make_nightly_audit_automation() -> AutomationCondition:
    """Nightly automation for the BIEP v3 RAGAS + audit + asset checks.

    Triggers at 00:00 UTC.
    """
    return AutomationCondition.on_cron(NIGHTLY_AUDIT_CRON, cron_timezone="UTC")


def make_eager_automation() -> AutomationCondition:
    """Eager automation for event-driven assets (ChangeDetection sensors).

    Triggers immediately on every upstream materialisation.
    """
    return AutomationCondition.eager()


# -----------------------------------------------------------------------------
# Per-milestone yearly factories (for backward-compat with the
# `make_ireland_lc_daily_automation()` naming in
# `orchestration/automation/biiep_daily_automation.py`)
# -----------------------------------------------------------------------------


def make_ireland_lc_yearly_automation() -> AutomationCondition:
    """Yearly automation for the Ireland LC pipeline (M1) — 1st September."""
    return make_yearly_education_automation()


def make_ireland_jc_yearly_automation() -> AutomationCondition:
    """Yearly automation for the Ireland JC pipeline (M2) — 1st September."""
    return make_yearly_education_automation()


def make_england_a_level_yearly_automation() -> AutomationCondition:
    """Yearly automation for the England A-Level pipeline (M3) — 1st September."""
    return make_yearly_education_automation()


def make_england_gcse_yearly_automation() -> AutomationCondition:
    """Yearly automation for the England GCSE pipeline (M4) — 1st September."""
    return make_yearly_education_automation()


__all__ = [
    "YEARLY_ACADEMIC_CRON",
    "MONTHLY_CIRCULARS_CRON",
    "WEEKLY_SMOKE_TEST_CRON",
    "NIGHTLY_AUDIT_CRON",
    "make_yearly_education_automation",
    "make_monthly_circulars_automation",
    "make_weekly_smoke_test_automation",
    "make_nightly_audit_automation",
    "make_eager_automation",
    "make_ireland_lc_yearly_automation",
    "make_ireland_jc_yearly_automation",
    "make_england_a_level_yearly_automation",
    "make_england_gcse_yearly_automation",
]
