"""
oideachais.dagster_defs.assets.law.en — England-law DLT assets.

Phase 3.3 of the lateralise change. 1 England-law DLT source:

  * legislation → legislation.gov.uk England & Wales acts
"""
from dagster import MaterializeResult, asset


@asset(
    group_name="law_en",
    compute_kind="dlt",
    description="legislation.gov.uk England & Wales acts (statutory register).",
)
def law_en_legislation(context) -> MaterializeResult:
    from cianfhoghlaim.dlt.british_isles.england.law.legislation import en_legislation_source

    src = en_legislation_source()
    rows = list(src.resources["acts"])
    return MaterializeResult(
        metadata={"row_count": len(rows), "source": "en_legislation"}
    )
