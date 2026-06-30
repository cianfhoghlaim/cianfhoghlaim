"""
oideachais.dagster_defs.assets.medicine.iom — Isle of Man medicine DLT assets.

Per
https://github.com/cianfhoghlaim/kings_college_galway/issues/19
(closed 2026-06-15) the lateralise change wired this as one of
the 6 crown-dependencies (IOM/JEY/GGY) medicine + law DLT
sources.
"""
from dagster import MaterializeResult, asset


@asset(
    group_name="medicine_iom",
    compute_kind="dlt",
    description=(
        "Isle of Man Government — Health & Social Care. "
        "Source: cianfhoghlaim.dlt.british_isles.isle_of_man.medicine.health_social_care."
    ),
)
def medicine_iom_health_social_care(context) -> MaterializeResult:
    from cianfhoghlaim.dlt.british_isles.isle_of_man.medicine.health_social_care import (
        iom_health_social_care_source,
    )

    src = iom_health_social_care_source()
    rows = list(src.resources["pages"])
    return MaterializeResult(
        metadata={"row_count": len(rows), "source": "iom_health_social_care"}
    )
