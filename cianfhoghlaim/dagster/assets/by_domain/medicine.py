"""
By-domain consolidation: British Isles medicine assets.

The 7 nation-specific medicine assets (england, scotland, wales,
northern_ireland, isle_of_man, jersey, guernsey) have been
consolidated into this single file. Each @asset follows the same
pattern: a dlt pipeline that materialises the healthcare pages
into DuckLake.

Per the v3 consolidation plan (consolidate-cianfhoghlaim-subdirs
Phase B.3). The legacy 7 `medicine/{nation}/__init__.py` files have
backward-compat re-exports via `by_domain/__init__.py` (one-release
transition).
"""
from dagster import MaterializeResult, asset


# === England (3 sources: NHS England, GMC, NICE) ===

@asset(
    group_name="medicine_england",
    compute_kind="dlt",
    description="NHS England public pages.",
)
def medicine_england_nhs_england(context) -> MaterializeResult:
    from cianfhoghlaim.dlt.british_isles.england.medicine.nhs_england import (
        nhs_england_source,
    )
    src = nhs_england_source()
    rows = list(src.resources["pages"])
    return MaterializeResult(
        metadata={"row_count": len(rows), "source": "nhs_england"}
    )


@asset(
    group_name="medicine_england",
    compute_kind="dlt",
    description="General Medical Council (UK register).",
)
def medicine_england_gmc(context) -> MaterializeResult:
    from cianfhoghlaim.dlt.british_isles.england.medicine.gmc import gmc_source
    src = gmc_source()
    rows = list(src.resources["doctors"])
    return MaterializeResult(
        metadata={"row_count": len(rows), "source": "gmc"}
    )


@asset(
    group_name="medicine_england",
    compute_kind="dlt",
    description="National Institute for Health & Care Excellence (NICE).",
)
def medicine_england_nice(context) -> MaterializeResult:
    from cianfhoghlaim.dlt.british_isles.england.medicine.nice import nice_source
    src = nice_source()
    rows = list(src.resources["guidance"])
    return MaterializeResult(
        metadata={"row_count": len(rows), "source": "nice"}
    )


# === Scotland ===

@asset(
    group_name="medicine_scotland",
    compute_kind="dlt",
    description="NHS Scotland public pages.",
)
def medicine_scotland_nhs_scotland(context) -> MaterializeResult:
    from cianfhoghlaim.dlt.british_isles.scotland.medicine.nhs_scotland import (
        nhs_scotland_source,
    )
    src = nhs_scotland_source()
    rows = list(src.resources["pages"])
    return MaterializeResult(
        metadata={"row_count": len(rows), "source": "nhs_scotland"}
    )


# === Wales ===

@asset(
    group_name="medicine_wales",
    compute_kind="dlt",
    description="NHS Wales public pages.",
)
def medicine_wales_nhs_wales(context) -> MaterializeResult:
    from cianfhoghlaim.dlt.british_isles.wales.medicine.nhs_wales import (
        nhs_wales_source,
    )
    src = nhs_wales_source()
    rows = list(src.resources["pages"])
    return MaterializeResult(
        metadata={"row_count": len(rows), "source": "nhs_wales"}
    )


# === Northern Ireland ===

@asset(
    group_name="medicine_northern_ireland",
    compute_kind="dlt",
    description="NIDirect (Northern Ireland Government health services).",
)
def medicine_northern_ireland_nidirect(context) -> MaterializeResult:
    from cianfhoghlaim.dlt.british_isles.northern_ireland.medicine.nidirect import (
        nidirect_source,
    )
    src = nidirect_source()
    rows = list(src.resources["pages"])
    return MaterializeResult(
        metadata={"row_count": len(rows), "source": "nidirect"}
    )


# === Isle of Man ===

@asset(
    group_name="medicine_isle_of_man",
    compute_kind="dlt",
    description=(
        "Isle of Man Government — Health & Social Care. "
        "Source: cianfhoghlaim.dlt.british_isles.isle_of_man.medicine.health_social_care."
    ),
)
def medicine_isle_of_man_health_social_care(context) -> MaterializeResult:
    from cianfhoghlaim.dlt.british_isles.isle_of_man.medicine.health_social_care import (
        iom_health_social_care_source,
    )
    src = iom_health_social_care_source()
    rows = list(src.resources["pages"])
    return MaterializeResult(
        metadata={"row_count": len(rows), "source": "iom_health_social_care"}
    )


# === Jersey ===

@asset(
    group_name="medicine_jersey",
    compute_kind="dlt",
    description=(
        "Jersey Health & Community Services. "
        "Source: cianfhoghlaim.dlt.british_isles.jersey.medicine.health_community_services."
    ),
)
def medicine_jersey_health_community_services(context) -> MaterializeResult:
    from cianfhoghlaim.dlt.british_isles.jersey.medicine.health_community_services import (
        jey_health_community_services_source,
    )
    src = jey_health_community_services_source()
    rows = list(src.resources["pages"])
    return MaterializeResult(
        metadata={"row_count": len(rows), "source": "jersey_health_community_services"}
    )


# === Guernsey ===

@asset(
    group_name="medicine_guernsey",
    compute_kind="dlt",
    description=(
        "States of Guernsey — Health & Social Care. "
        "Source: cianfhoghlaim.dlt.british_isles.guernsey.medicine.health_social_care."
    ),
)
def medicine_guernsey_health_social_care(context) -> MaterializeResult:
    from cianfhoghlaim.dlt.british_isles.guernsey.medicine.health_social_care import (
        ggy_health_social_care_source,
    )
    src = ggy_health_social_care_source()
    rows = list(src.resources["pages"])
    return MaterializeResult(
        metadata={"row_count": len(rows), "source": "ggy_health_social_care"}
    )