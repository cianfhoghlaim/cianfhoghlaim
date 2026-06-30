"""
oideachais.dagster_defs.assets.medicine.jey — Jersey medicine DLT assets.

Per
https://github.com/cianfhoghlaim/kings_college_galway/issues/19
(closed 2026-06-15) the lateralise change wired this as one of
the 6 crown-dependencies (IOM/JEY/GGY) medicine + law DLT
sources.
"""
from dagster import MaterializeResult, asset


@asset(
    group_name="medicine_jey",
    compute_kind="dlt",
    description=(
        "Government of Jersey — Health & Community Services. "
        "Source: cianfhoghlaim.dlt.british_isles.jersey.medicine.health_community_services."
    ),
)
def medicine_jey_health_community_services(context) -> MaterializeResult:
    from cianfhoghlaim.dlt.british_isles.jersey.medicine.health_community_services import (
        jey_health_community_services_source,
    )

    src = jey_health_community_services_source()
    rows = list(src.resources["pages"])
    return MaterializeResult(
        metadata={"row_count": len(rows), "source": "jey_health_community_services"}
    )
