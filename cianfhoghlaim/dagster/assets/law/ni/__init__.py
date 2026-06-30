"""
oideachais.dagster_defs.assets.law.ni — Northern Ireland-law DLT assets.

Phase 3.3 of the lateralise change. 1 NI-law DLT source:

  * legislation → legislation.gov.uk Northern Ireland acts
"""
from dagster import MaterializeResult, asset


@asset(
    group_name="law_ni",
    compute_kind="dlt",
    description="legislation.gov.uk Northern Ireland acts.",
)
def law_ni_legislation(context) -> MaterializeResult:
    from dlt_sources.ni.law.legislation import ni_legislation_source

    src = ni_legislation_source()
    rows = list(src.resources["acts"])
    return MaterializeResult(
        metadata={"row_count": len(rows), "source": "ni_legislation"}
    )
