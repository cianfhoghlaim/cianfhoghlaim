"""
oideachais.dagster_defs.assets.law.wls — Wales-law DLT assets.

Phase 3.3 of the lateralise change. 1 Wales-law DLT source:

  * legislation → legislation.gov.uk Wales acts
"""
from dagster import MaterializeResult, asset


@asset(
    group_name="law_wls",
    compute_kind="dlt",
    description="legislation.gov.uk Wales acts.",
)
def law_wls_legislation(context) -> MaterializeResult:
    from dlt_sources.wls.law.legislation import wls_legislation_source

    src = wls_legislation_source()
    rows = list(src.resources["acts"])
    return MaterializeResult(
        metadata={"row_count": len(rows), "source": "wls_legislation"}
    )
