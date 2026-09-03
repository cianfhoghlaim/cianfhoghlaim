"""BIEP v3 scheduling — yearly education content + monthly circulars.

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

This file is a **thin re-export shim** for the canonical
`orchestration.automation.biiep_scheduling` module. It exists for
backward compatibility with the legacy
`biiep_daily_automation.py` callers (the 2026-08-08 production-readiness
change imported the per-jurisdiction daily factories from this module).

**All daily crons have been retired in favour of yearly crons** for
education content (NCCA, SEC, AQA, OCR, Edexcel) and monthly crons
for government circulars. See the canonical module for details.

Reference: openspec/changes/2026-08-13-biep-v3-systematic-download-ireland-england-v1/
openspec/specs/british-isles-education-pipeline-v3/spec.md
"""
from __future__ import annotations

from .biiep_scheduling import (
    EIGHT_JURISDICTIONS,
    MONTHLY_CIRCULARS_CRON,
    NIGHTLY_AUDIT_CRON,
    WEEKLY_SMOKE_TEST_CRON,
    YEARLY_ACADEMIC_CRON,
    make_eager_automation,
    make_england_a_level_yearly_automation,
    make_england_gcse_yearly_automation,
    make_ireland_jc_yearly_automation,
    make_ireland_lc_yearly_automation,
    make_monthly_circulars_automation,
    make_nightly_audit_automation,
    make_weekly_smoke_test_automation,
    make_yearly_education_automation,
)

# -----------------------------------------------------------------------------
# Backward-compat aliases (the legacy daily factories)
# -----------------------------------------------------------------------------
# These are kept so that legacy callers (e.g. `biiep_daily_automation.py`
# references in the 2026-08-08 change) don't break. New code MUST use
# the canonical `make_*_yearly_automation()` factories below.

make_biiep_v3_daily_automation = make_england_a_level_yearly_automation  # alias to yearly
"""Backward-compat alias; new code must use `make_yearly_education_automation`."""

make_per_jurisdiction_daily_automation = make_ireland_lc_yearly_automation  # alias to yearly
"""Backward-compat alias; new code must use the per-milestone yearly factories."""


__all__ = [
    "EIGHT_JURISDICTIONS",
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
    "make_biiep_v3_daily_automation",  # backward-compat alias (now yearly)
    "make_per_jurisdiction_daily_automation",  # backward-compat alias (now yearly)
]
