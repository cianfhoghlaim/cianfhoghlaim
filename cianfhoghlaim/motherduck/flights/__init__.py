"""
MotherDuck Flights for the BIEP v1 stack.

Re-exports the daily `lc_pdf_sync_flight` (and any v2 placeholders)
for the MotherDuck Flights runtime.

Scheduled via `flights/config.yaml` (cron `0 4 * * *` = 04:00 UTC).

Reference: openspec/changes/2026-07-06-british-isles-education-pipeline-v1/
openspec/specs/british-isles-education-pipeline/spec.md
"""
from __future__ import annotations

from .lc_pdf_sync_flight import main as lc_pdf_sync_flight_main

__all__ = ["lc_pdf_sync_flight_main"]
