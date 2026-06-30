"""
oideachais.dagster_defs.assets.law.jey — Jersey law DLT assets.

Per
https://github.com/cianfhoghlaim/kings_college_galway/issues/19
(closed 2026-06-15) the lateralise change wired this as one of
the 6 crown-dependencies (IOM/JEY/GGY) medicine + law DLT
sources.
"""
from dagster import MaterializeResult, asset


@asset(
    group_name="law_jey",
    compute_kind="dlt",
    description=(
        "Jersey Law (Jersey Legal Information Board). "
        "Source: cianfhoghlaim.dlt.british_isles.jersey.law.legislation."
    ),
)
def law_jey_legislation(context) -> MaterializeResult:
    from cianfhoghlaim.dlt.british_isles.jersey.law.legislation import (
        jey_legislation_source,
    )

    src = jey_legislation_source()
    rows = list(src.resources["acts"])
    return MaterializeResult(
        metadata={"row_count": len(rows), "source": "jey_legislation"}
    )
