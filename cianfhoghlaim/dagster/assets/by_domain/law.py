"""
By-domain consolidation: British Isles law assets.

The 7 nation-specific law assets (england, scotland, wales,
northern_ireland, isle_of_man, jersey, guernsey) have been
consolidated into this single file. Each @asset follows the same
pattern: a dlt pipeline that materialises the legislation rows
into DuckLake.

Per the v3 consolidation plan (consolidate-cianfhoghlaim-subdirs
Phase B.2). The legacy 7 `law/{nation}/__init__.py` files have
backward-compat re-exports via `by_domain/__init__.py` (one-release
transition).
"""
from dagster import MaterializeResult, asset


# === England & Wales ===

@asset(
    group_name="law_england",
    compute_kind="dlt",
    description="legislation.gov.uk England & Wales acts (statutory register).",
)
def law_england_legislation(context) -> MaterializeResult:
    from cianfhoghlaim.dlt.british_isles.england.law.legislation import en_legislation_source

    src = en_legislation_source()
    rows = list(src.resources["acts"])
    return MaterializeResult(
        metadata={"row_count": len(rows), "source": "england_legislation"}
    )


# === Scotland ===

@asset(
    group_name="law_scotland",
    compute_kind="dlt",
    description="legislation.gov.uk Scotland acts (statutory register).",
)
def law_scotland_legislation(context) -> MaterializeResult:
    from cianfhoghlaim.dlt.british_isles.scotland.law.legislation import sct_legislation_source

    src = sct_legislation_source()
    rows = list(src.resources["acts"])
    return MaterializeResult(
        metadata={"row_count": len(rows), "source": "scotland_legislation"}
    )


# === Wales ===

@asset(
    group_name="law_wales",
    compute_kind="dlt",
    description="legislation.gov.uk Wales acts.",
)
def law_wales_legislation(context) -> MaterializeResult:
    from cianfhoghlaim.dlt.british_isles.wales.law.legislation import wls_legislation_source

    src = wls_legislation_source()
    rows = list(src.resources["acts"])
    return MaterializeResult(
        metadata={"row_count": len(rows), "source": "wales_legislation"}
    )


# === Northern Ireland ===

@asset(
    group_name="law_northern_ireland",
    compute_kind="dlt",
    description="legislation.gov.uk Northern Ireland acts.",
)
def law_northern_ireland_legislation(context) -> MaterializeResult:
    from cianfhoghlaim.dlt.british_isles.northern_ireland.law.legislation import ni_legislation_source

    src = ni_legislation_source()
    rows = list(src.resources["acts"])
    return MaterializeResult(
        metadata={"row_count": len(rows), "source": "northern_ireland_legislation"}
    )


# === Isle of Man ===

@asset(
    group_name="law_isle_of_man",
    compute_kind="dlt",
    description=(
        "Isle of Man Statute Books (legislation portal). "
        "Source: cianfhoghlaim.dlt.british_isles.isle_of_man.law.legislation."
    ),
)
def law_isle_of_man_legislation(context) -> MaterializeResult:
    from cianfhoghlaim.dlt.british_isles.isle_of_man.law.legislation import iom_legislation_source

    src = iom_legislation_source()
    rows = list(src.resources["acts"])
    return MaterializeResult(
        metadata={"row_count": len(rows), "source": "isle_of_man_legislation"}
    )


# === Jersey ===

@asset(
    group_name="law_jersey",
    compute_kind="dlt",
    description=(
        "Jersey Law (Jersey Legal Information Board). "
        "Source: cianfhoghlaim.dlt.british_isles.jersey.law.legislation."
    ),
)
def law_jersey_legislation(context) -> MaterializeResult:
    from cianfhoghlaim.dlt.british_isles.jersey.law.legislation import jey_legislation_source

    src = jey_legislation_source()
    rows = list(src.resources["acts"])
    return MaterializeResult(
        metadata={"row_count": len(rows), "source": "jersey_legislation"}
    )


# === Guernsey ===

@asset(
    group_name="law_guernsey",
    compute_kind="dlt",
    description=(
        "Laws of Guernsey (Royal Court legal resources). "
        "Source: cianfhoghlaim.dlt.british_isles.guernsey.law.legislation."
    ),
)
def law_guernsey_legislation(context) -> MaterializeResult:
    from cianfhoghlaim.dlt.british_isles.guernsey.law.legislation import ggy_legislation_source

    src = ggy_legislation_source()
    rows = list(src.resources["acts"])
    return MaterializeResult(
        metadata={"row_count": len(rows), "source": "guernsey_legislation"}
    )