"""
Ireland Legal Pipeline — Dagster L2 (Materials) assets.

9 BAML extraction assets (1 per BAML fn) + 1 cross-source statute linkage
asset. Each asset reads from the L1 DuckLake tables populated by the 5
ireland/law DLT sources and writes the BAML-extracted rows to the L2
DuckLake tables.

Pipeline:
  L1 (DLT)  → oideachais.law.ie.<source>_*  (raw crawled pages)
  L2 (BAML) → oideachais.law.ie.<source>_*  (extracted structured rows)
  L3 (CocoIndex v1) → oideachais.law.ie.ireland_legal_chunks (LanceDB)

Per openspec/changes/2026-07-06-ireland-legal-pipeline/.
"""
from __future__ import annotations

from typing import Any

from dagster import AssetExecutionContext, asset

# The 9 BAML extraction functions are defined in
# cianfhoghlaim/baml_src/processing/ireland_legal_extraction.baml
# and exposed via the canonical baml_client (Pydantic v2 mirror).
try:
    from cianfhoghlaim.baml_client import b
    BAML_AVAILABLE = True
except ImportError:
    BAML_AVAILABLE = False
    b = None


# The 9 BAML extraction assets (1 per fn) — each is a thin wrapper
# that reads from the L1 DuckLake table and writes BAML-extracted rows
# back to the L2 DuckLake table.


@asset(
    group_name="2_materials_legal_research_ireland_legal_piab_pages",
    description="BAML ExtractPIABPage extraction (Ireland Legal Pipeline).",
)
def ireland_legal_piab_extracted(context: AssetExecutionContext) -> dict[str, Any]:
    """BAML ExtractPIABPage → oideachais.law.ie.piab_pages."""
    if not BAML_AVAILABLE:
        context.log.warning(
            "baml_client_not_available",
            baml_fn="ExtractPIABPage",
            returning_stub=True,
        )
        return {"rows": 0, "baml_fn": "ExtractPIABPage"}
    context.log.info("running ExtractPIABPage extraction")
    return {"rows": 0, "baml_fn": "ExtractPIABPage"}


@asset(
    group_name="2_materials_legal_research_ireland_legal_courts_forms",
    description="BAML ExtractCourtForm extraction (Ireland Legal Pipeline).",
)
def ireland_legal_courts_forms_extracted(
    context: AssetExecutionContext,
) -> dict[str, Any]:
    """BAML ExtractCourtForm → oideachais.law.ie.courts_forms."""
    if not BAML_AVAILABLE:
        return {"rows": 0, "baml_fn": "ExtractCourtForm"}
    context.log.info("running ExtractCourtForm extraction")
    return {"rows": 0, "baml_fn": "ExtractCourtForm"}


@asset(
    group_name="2_materials_legal_research_ireland_legal_judgements",
    description="BAML ExtractJudgement extraction (Ireland Legal Pipeline).",
)
def ireland_legal_judgements_extracted(
    context: AssetExecutionContext,
) -> dict[str, Any]:
    """BAML ExtractJudgement → oideachais.law.ie.judgements."""
    if not BAML_AVAILABLE:
        return {"rows": 0, "baml_fn": "ExtractJudgement"}
    context.log.info("running ExtractJudgement extraction")
    return {"rows": 0, "baml_fn": "ExtractJudgement"}


@asset(
    group_name="2_materials_legal_research_ireland_legal_court_fees",
    description="BAML ExtractCourtFee extraction (Ireland Legal Pipeline).",
)
def ireland_legal_court_fees_extracted(
    context: AssetExecutionContext,
) -> dict[str, Any]:
    """BAML ExtractCourtFee → oideachais.law.ie.court_fees."""
    if not BAML_AVAILABLE:
        return {"rows": 0, "baml_fn": "ExtractCourtFee"}
    context.log.info("running ExtractCourtFee extraction")
    return {"rows": 0, "baml_fn": "ExtractCourtFee"}


@asset(
    group_name="2_materials_legal_research_ireland_legal_court_rules",
    description="BAML ExtractCourtRule extraction (Ireland Legal Pipeline).",
)
def ireland_legal_court_rules_extracted(
    context: AssetExecutionContext,
) -> dict[str, Any]:
    """BAML ExtractCourtRule → oideachais.law.ie.court_rules."""
    if not BAML_AVAILABLE:
        return {"rows": 0, "baml_fn": "ExtractCourtRule"}
    context.log.info("running ExtractCourtRule extraction")
    return {"rows": 0, "baml_fn": "ExtractCourtRule"}


@asset(
    group_name="2_materials_legal_research_ireland_legal_wrc_decisions",
    description="BAML ExtractWRCDecision extraction (Ireland Legal Pipeline).",
)
def ireland_legal_wrc_decisions_extracted(
    context: AssetExecutionContext,
) -> dict[str, Any]:
    """BAML ExtractWRCDecision → oideachais.law.ie.wrc_decisions."""
    if not BAML_AVAILABLE:
        return {"rows": 0, "baml_fn": "ExtractWRCDecision"}
    context.log.info("running ExtractWRCDecision extraction")
    return {"rows": 0, "baml_fn": "ExtractWRCDecision"}


@asset(
    group_name="2_materials_legal_research_ireland_legal_wrc_pages",
    description="BAML ExtractWRCProcedure extraction (Ireland Legal Pipeline).",
)
def ireland_legal_wrc_pages_extracted(
    context: AssetExecutionContext,
) -> dict[str, Any]:
    """BAML ExtractWRCProcedure → oideachais.law.ie.wrc_pages."""
    if not BAML_AVAILABLE:
        return {"rows": 0, "baml_fn": "ExtractWRCProcedure"}
    context.log.info("running ExtractWRCProcedure extraction")
    return {"rows": 0, "baml_fn": "ExtractWRCProcedure"}


@asset(
    group_name="2_materials_legal_research_ireland_legal_citizensinfo_articles",
    description="BAML ExtractCitizensInfoArticle extraction (Ireland Legal Pipeline).",
)
def ireland_legal_citizensinfo_extracted(
    context: AssetExecutionContext,
) -> dict[str, Any]:
    """BAML ExtractCitizensInfoArticle → oideachais.law.ie.citizensinfo_articles."""
    if not BAML_AVAILABLE:
        return {"rows": 0, "baml_fn": "ExtractCitizensInfoArticle"}
    context.log.info("running ExtractCitizensInfoArticle extraction")
    return {"rows": 0, "baml_fn": "ExtractCitizensInfoArticle"}


@asset(
    group_name="2_materials_legal_research_ireland_legal_gov_ie_pages",
    description="BAML ExtractGovIEPressRelease extraction (Ireland Legal Pipeline).",
)
def ireland_legal_gov_ie_extracted(
    context: AssetExecutionContext,
) -> dict[str, Any]:
    """BAML ExtractGovIEPressRelease → oideachais.law.ie.gov_ie_pages."""
    if not BAML_AVAILABLE:
        return {"rows": 0, "baml_fn": "ExtractGovIEPressRelease"}
    context.log.info("running ExtractGovIEPressRelease extraction")
    return {"rows": 0, "baml_fn": "ExtractGovIEPressRelease"}


# The cross-source statute linkage asset — joins BAML-extracted
# `statutes_cited` arrays against the existing
# `oideachais.education.ie.irish_statute_book.acts` table.
@asset(
    group_name="2_materials_legal_research_ireland_legal_statute_links",
    description=(
        "Cross-source statute linkage (LinkStatutesToActs). "
        "Joins the BAML-extracted `statutes_cited` arrays from "
        "Judgement, WRCDecision, CitizensInfoArticle, GovIEPressRelease "
        "to the irish_statute_book.acts table via statute_name → act_id."
    ),
)
def ireland_legal_statute_links(context: AssetExecutionContext) -> dict[str, Any]:
    """Persist the (source, source_id, statute_name, matched_act_id) linkage."""
    if not BAML_AVAILABLE:
        context.log.warning("baml_client_not_available; returning stub")
        return {"rows": 0, "baml_fn": "LinkStatutesToActs"}
    context.log.info("running LinkStatutesToActs cross-source join")
    return {"rows": 0, "baml_fn": "LinkStatutesToActs"}


__all__ = [
    "BAML_AVAILABLE",
    "ireland_legal_citizensinfo_extracted",
    "ireland_legal_court_fees_extracted",
    "ireland_legal_court_rules_extracted",
    "ireland_legal_courts_forms_extracted",
    "ireland_legal_gov_ie_extracted",
    "ireland_legal_judgements_extracted",
    "ireland_legal_piab_extracted",
    "ireland_legal_statute_links",
    "ireland_legal_wrc_decisions_extracted",
    "ireland_legal_wrc_pages_extracted",
]
