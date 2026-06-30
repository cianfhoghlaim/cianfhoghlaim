"""
oideachais.dagster_defs.assets.medicine.ni — Northern Ireland-medicine DLT assets.

Phase 3.3 of the lateralise change. 1 NI-medicine DLT source:

  * nidirect → nidirect (NI government health pages)
"""
from dagster import MaterializeResult, asset


@asset(
    group_name="medicine_ni",
    compute_kind="dlt",
    description="nidirect (NI government) health pages.",
)
def medicine_ni_nidirect(context) -> MaterializeResult:
    from dlt_sources.ni.medicine.nidirect import (
        nidirect_medicine_source,
    )

    src = nidirect_medicine_source()
    rows = list(src.resources["pages"])
    return MaterializeResult(
        metadata={"row_count": len(rows), "source": "nidirect"}
    )
