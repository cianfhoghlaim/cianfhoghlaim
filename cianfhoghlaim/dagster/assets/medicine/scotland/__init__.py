"""
oideachais.dagster_defs.assets.medicine.sct — Scotland-medicine DLT assets.

Phase 3.3 of the lateralise change. 1 Scotland-medicine DLT source:

  * nhs_scotland → NHS Scotland (national service commissioner)
"""
from dagster import MaterializeResult, asset


@asset(
    group_name="medicine_sct",
    compute_kind="dlt",
    description="NHS Scotland public pages.",
)
def medicine_sct_nhs_scotland(context) -> MaterializeResult:
    from cianfhoghlaim.dlt.british_isles.scotland.medicine.nhs_scotland import (
        nhs_scotland_source,
    )

    src = nhs_scotland_source()
    rows = list(src.resources["pages"])
    return MaterializeResult(
        metadata={"row_count": len(rows), "source": "nhs_scotland"}
    )
