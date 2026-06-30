"""
oideachais.dagster_defs.assets.law.iom — Isle of Man law DLT assets.

Per
https://github.com/cianfhoghlaim/kings_college_galway/issues/19
(closed 2026-06-15) the lateralise change wired this as one of
the 6 crown-dependencies (IOM/JEY/GGY) medicine + law DLT
sources.
"""
from dagster import MaterializeResult, asset


@asset(
    group_name="law_iom",
    compute_kind="dlt",
    description=(
        "Isle of Man Statute Books (legislation portal). "
        "Source: cianfhoghlaim.dlt.british_isles.isle_of_man.law.legislation."
    ),
)
def law_iom_legislation(context) -> MaterializeResult:
    from cianfhoghlaim.dlt.british_isles.isle_of_man.law.legislation import (
        iom_legislation_source,
    )

    src = iom_legislation_source()
    rows = list(src.resources["acts"])
    return MaterializeResult(
        metadata={"row_count": len(rows), "source": "iom_legislation"}
    )
