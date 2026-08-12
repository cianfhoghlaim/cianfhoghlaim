"""Jurisdiction registry sensor jobs — BIEP v3 wiring.

Per the 2026-08-13-biep-v3-jurisdiction-sensor-jobs-v1 change: this
module defines the 8 `define_asset_job` instances that the 8
jurisdiction registry sensors in `orchestration/sensors/` reference via
their `@sensor(job_name="<jurisdiction>_registry_change_job")`
argument.

Before this module existed, every sensor's emitted `RunRequest` was
silently dropped at Dagster's job-resolution step — the BIEP
critical-path auto-refresh was broken at the wire layer for 8 of 8
jurisdictions. The 8 jobs below wire each sensor to the canonical
`<jurisdiction>_documents_ingested` asset that re-ingests that
jurisdiction's cohorts into DuckLake.

Mirrors the proven pattern from
`orchestration/sensors/garage_pdf_arrival_sensor.py:39-42` (the only
previously-correct jurisdiction wiring, fixed by the
`2026-08-08-lakehouse-extensive-hydration-v1` change).
"""
from __future__ import annotations

from dagster import define_asset_job

# 8 BIEP v3 jurisdictions (NCCA + SQA + CCEA + WJEC + JCQ + IoM + Jersey + Guernsey)
ncca_registry_change_job = define_asset_job(
    name="ncca_registry_change_job",
    selection=["ireland_documents_ingested"],
)

sqa_registry_change_job = define_asset_job(
    name="sqa_registry_change_job",
    selection=["scotland_documents_ingested"],
)

ccea_registry_change_job = define_asset_job(
    name="ccea_registry_change_job",
    selection=["northern_ireland_documents_ingested"],
)

wjec_registry_change_job = define_asset_job(
    name="wjec_registry_change_job",
    selection=["wales_documents_ingested"],
)

jcq_registry_change_job = define_asset_job(
    name="jcq_registry_change_job",
    selection=["england_documents_ingested"],
)

isle_of_man_registry_change_job = define_asset_job(
    name="isle_of_man_registry_change_job",
    selection=["isle_of_man_documents_ingested"],
)

jersey_registry_change_job = define_asset_job(
    name="jersey_registry_change_job",
    selection=["jersey_documents_ingested"],
)

guernsey_registry_change_job = define_asset_job(
    name="guernsey_registry_change_job",
    selection=["guernsey_documents_ingested"],
)


__all__ = [
    "ncca_registry_change_job",
    "sqa_registry_change_job",
    "ccea_registry_change_job",
    "wjec_registry_change_job",
    "jcq_registry_change_job",
    "isle_of_man_registry_change_job",
    "jersey_registry_change_job",
    "guernsey_registry_change_job",
]
