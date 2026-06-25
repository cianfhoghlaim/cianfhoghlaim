"""
oideachais.dagster_defs.assets.law.sct — Scotland-law DLT assets.

Phase 3.3 of the lateralise change. 1 Scotland-law DLT source:

  * legislation → legislation.gov.uk Scotland acts
"""
from dagster import MaterializeResult, asset


@asset(
    group_name="law_sct",
    compute_kind="dlt",
    description="legislation.gov.uk Scotland acts (statutory register).",
)
def law_sct_legislation(context) -> MaterializeResult:
    from dlt_sources.domains.law.sct.legislation import sct_legislation_source

    src = sct_legislation_source()
    rows = list(src.resources["acts"])
    return MaterializeResult(
        metadata={"row_count": len(rows), "source": "sct_legislation"}
    )
