"""
oideachais.dagster_defs.assets.law.ggy — Guernsey law DLT assets.

Per
https://github.com/cianfhoghlaim/kings_college_galway/issues/19
(closed 2026-06-15) the lateralise change wired this as one of
the 6 crown-dependencies (IOM/JEY/GGY) medicine + law DLT
sources.
"""
from dagster import MaterializeResult, asset


@asset(
    group_name="law_ggy",
    compute_kind="dlt",
    description=(
        "Laws of Guernsey (Royal Court legal resources). "
        "Source: dlt_sources.domains.law.ggy.legislation."
    ),
)
def law_ggy_legislation(context) -> MaterializeResult:
    from dlt_sources.domains.law.ggy.legislation import (
        ggy_legislation_source,
    )

    src = ggy_legislation_source()
    rows = list(src.resources["acts"])
    return MaterializeResult(
        metadata={"row_count": len(rows), "source": "ggy_legislation"}
    )
