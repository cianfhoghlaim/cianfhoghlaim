"""
oideachais.dagster_defs.assets.medicine.wls — Wales-medicine DLT assets.

Phase 3.3 of the lateralise change. 1 Wales-medicine DLT source:

  * nhs_wales → NHS Wales (national service commissioner)
"""
from dagster import MaterializeResult, asset


@asset(
    group_name="medicine_wls",
    compute_kind="dlt",
    description="NHS Wales public pages.",
)
def medicine_wls_nhs_wales(context) -> MaterializeResult:
    from dlt_sources.domains.medicine.wls.nhs_wales import (
        nhs_wales_source,
    )

    src = nhs_wales_source()
    rows = list(src.resources["pages"])
    return MaterializeResult(
        metadata={"row_count": len(rows), "source": "nhs_wales"}
    )
