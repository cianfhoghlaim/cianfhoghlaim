"""
oideachais.dagster_defs.assets.medicine.ggy — Guernsey medicine DLT assets.

Per
https://github.com/cianfhoghlaim/kings_college_galway/issues/19
(closed 2026-06-15) the lateralise change wired this as one of
the 6 crown-dependencies (IOM/JEY/GGY) medicine + law DLT
sources.
"""
from dagster import MaterializeResult, asset


@asset(
    group_name="medicine_ggy",
    compute_kind="dlt",
    description=(
        "States of Guernsey — Health & Social Care. "
        "Source: dlt_sources.ggy.medicine.health_social_care."
    ),
)
def medicine_ggy_health_social_care(context) -> MaterializeResult:
    from dlt_sources.ggy.medicine.health_social_care import (
        ggy_health_social_care_source,
    )

    src = ggy_health_social_care_source()
    rows = list(src.resources["pages"])
    return MaterializeResult(
        metadata={"row_count": len(rows), "source": "ggy_health_social_care"}
    )
