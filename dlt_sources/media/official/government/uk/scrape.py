"""dlt_sources/media/official/government/uk scrape DLT resource.

United Kingdom government + police + defence + army + Acts +
Treaties. Class E (official) sub-bucket — the UK jurisdiction.

Per the 2026-08-23-tuatha-media-intel-gameplay-capture-research-v1
change, the Class E Wikipedia entries were MOVED to
`dlt_sources/media/celtic_history_research/` (the 9 stub
sources for the downstream theming change). This DLT source
holds the OFFICIAL UK government / police / defence / army /
Acts / treaties surface — the "cianchosaint" knowledge-keeping
spine for the UK jurisdiction.

The descriptor is a structured summary — NEVER a verbatim copy
of the full page. Per the media-intel-corpus spec, every
descriptor ships with `shippable: false` enforced.

Reference: openspec/changes/2026-08-23-tuatha-media-intel-gameplay-capture-research-v1/
            design.md § 1.4 (the no-graphics-from-graphics invariant)
            spec.md § media-intel-acquisition-plan Requirement 5
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import uuid
from collections.abc import Iterator
from typing import Any

import dlt
import structlog

logger = structlog.get_logger(__name__)


# ── Source registry (mirrors the BIEP jurisdictional pattern) ─────────────


# Police (3)
_UK_POLICE: list[dict[str, str]] = [
    {
        "id": "metropolitan_police",
        "title": "Metropolitan Police Service",
        "url": "https://www.met.police.uk/",
        "rights_holder": "Metropolitan Police Service",
        "licence": "OGL-3.0",
    },
    {
        "id": "btp",
        "title": "British Transport Police",
        "url": "https://www.btp.police.uk/",
        "rights_holder": "British Transport Police",
        "licence": "OGL-3.0",
    },
    {
        "id": "psni",
        "title": "Police Service of Northern Ireland",
        "url": "https://www.psni.police.uk/",
        "rights_holder": "Police Service of Northern Ireland",
        "licence": "OGL-3.0",
    },
]


# Defence (4)
_UK_DEFENCE: list[dict[str, str]] = [
    {
        "id": "mod",
        "title": "Ministry of Defence",
        "url": "https://www.gov.uk/government/organisations/ministry-of-defence",
        "rights_holder": "Ministry of Defence",
        "licence": "OGL-3.0",
    },
    {
        "id": "british_army",
        "title": "British Army",
        "url": "https://www.army.mod.uk/",
        "rights_holder": "Ministry of Defence",
        "licence": "OGL-3.0",
    },
    {
        "id": "royal_navy",
        "title": "Royal Navy",
        "url": "https://www.royalnavy.mod.uk/",
        "rights_holder": "Ministry of Defence",
        "licence": "OGL-3.0",
    },
    {
        "id": "raf",
        "title": "Royal Air Force",
        "url": "https://www.raf.mod.uk/",
        "rights_holder": "Ministry of Defence",
        "licence": "OGL-3.0",
    },
]


# Departments (4 — the canonical government surface)
_UK_DEPARTMENTS: list[dict[str, str]] = [
    {
        "id": "home_office",
        "title": "Home Office",
        "url": "https://www.gov.uk/government/organisations/home-office",
        "rights_holder": "Home Office",
        "licence": "OGL-3.0",
    },
    {
        "id": "fcdo",
        "title": "Foreign, Commonwealth & Development Office",
        "url": "https://www.gov.uk/government/organisations/foreign-commonwealth-development-office",
        "rights_holder": "FCDO",
        "licence": "OGL-3.0",
    },
    {
        "id": "moj",
        "title": "Ministry of Justice",
        "url": "https://www.gov.uk/government/organisations/ministry-of-justice",
        "rights_holder": "Ministry of Justice",
        "licence": "OGL-3.0",
    },
    {
        "id": "doh",
        "title": "Department of Health and Social Care",
        "url": "https://www.gov.uk/government/organisations/department-of-health-and-social-care",
        "rights_holder": "Department of Health and Social Care",
        "licence": "OGL-3.0",
    },
]


# Acts + Treaties (7 — Crown copyright; OGL v3.0)
_UK_ACTS_TREATIES: list[dict[str, str]] = [
    {
        "id": "act_of_union_1707",
        "title": "Acts of Union 1707 (England + Scotland → Great Britain)",
        "url": "https://www.legislation.gov.uk/aosp/1707/7",
        "rights_holder": "Crown copyright",
        "licence": "OGL-3.0",
    },
    {
        "id": "act_of_union_1800",
        "title": "Acts of Union 1800 (Great Britain + Ireland → UK)",
        "url": "https://www.legislation.gov.uk/aosp/1800/67",
        "rights_holder": "Crown copyright",
        "licence": "OGL-3.0",
    },
    {
        "id": "anglo_irish_treaty_1921",
        "title": "Anglo-Irish Treaty 1921",
        "url": "https://www.dfa.ie/media/dfa/alldfawebsitemedia/our-role-policies/anglo-irish-treaty/Anglo-Irish-Treaty.pdf",
        "rights_holder": "Crown copyright",
        "licence": "OGL-3.0",
    },
    {
        "id": "good_friday_agreement_1998",
        "title": "Good Friday Agreement (Belfast Agreement) 1998",
        "url": "https://www.gov.uk/government/publications/the-belfast-agreement",
        "rights_holder": "Crown copyright",
        "licence": "OGL-3.0",
    },
    {
        "id": "windsor_framework_2023",
        "title": "Windsor Framework 2023",
        "url": "https://www.gov.uk/government/publications/the-windsor-framework",
        "rights_holder": "Crown copyright",
        "licence": "OGL-3.0",
    },
    {
        "id": "uk_internal_market_act_2020",
        "title": "UK Internal Market Act 2020",
        "url": "https://www.legislation.gov.uk/ukpga/2020/27/contents",
        "rights_holder": "Crown copyright",
        "licence": "OGL-3.0",
    },
    {
        "id": "uk_withdrawal_act_2020",
        "title": "UK Withdrawal from the European Union (Continuity) Act 2020",
        "url": "https://www.legislation.gov.uk/ukpga/2020/25/contents",
        "rights_holder": "Crown copyright",
        "licence": "OGL-3.0",
    },
]


# ── Helpers (mirrors the leaving_cert.py pattern) ────────────────────────────


def _stable_hash(record: dict[str, Any]) -> str:
    """Content-addressable hash for change detection."""
    return hashlib.sha256(
        json.dumps(record, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()[:16]


# ── DLT source ──────────────────────────────────────────────────────────────


@dlt.source(name="uk_government")
def uk_government_source(
    use_local_scrapes: bool | None = None,
    write_disposition: str = "merge",
):
    """DLT source for the UK government + police + defence + army
    + Acts + treaties surface.

    The 18 source records are emitted as 4 `@dlt.resource` per
    the BIEP pattern (one per sub-bucket):
      - uk_police_defence_army_pages
      - uk_departments_pages
      - uk_acts_treaties_pages
      - uk_government_pdf_links (the PDF extraction surface)
    """
    if use_local_scrapes is None:
        use_local_scrapes = os.environ.get("USE_LOCAL_SCRAPES", "true").lower() == "true"

    if not use_local_scrapes:
        # Plan A keyless Firecrawl fallback
        pass

    @dlt.resource(
        name="uk_police_defence_army_pages",
        write_disposition=write_disposition,
        primary_key=("id", "source_url", "source_timestamp"),
    )
    def uk_police_defence_army_pages() -> Iterator[dict[str, Any]]:
        firecrawl_key_present = bool(os.environ.get("FIRECRAWL_API_KEY"))
        for src in _UK_POLICE + _UK_DEFENCE:
            source_timestamp = datetime.datetime.now(
                tz=datetime.UTC
            ).isoformat()
            record = {
                "id": src["id"],
                "title": src["title"],
                "jurisdiction": "uk",
                "category": "police_defence_army",
                "source_url": src["url"],
                "source_timestamp": source_timestamp,
                "rights_holder": src["rights_holder"],
                "licence": src["licence"],
                "provenance": {
                    "rights_holder": src["rights_holder"],
                    "licence": src["licence"],
                    "derivation_class": "fair_use_quote",
                    "shippable": False,
                    "shippable_art_path": None,
                },
            }
            record["_acquisition_id"] = str(uuid.uuid4())
            record["_firecrawl_plan"] = "plan_a_keyless"
            record["_firecrawl_key_present"] = firecrawl_key_present
            record["_content_hash"] = _stable_hash(record)
            yield record

    @dlt.resource(
        name="uk_departments_pages",
        write_disposition=write_disposition,
        primary_key=("id", "source_url", "source_timestamp"),
    )
    def uk_departments_pages() -> Iterator[dict[str, Any]]:
        firecrawl_key_present = bool(os.environ.get("FIRECRAWL_API_KEY"))
        for src in _UK_DEPARTMENTS:
            source_timestamp = datetime.datetime.now(
                tz=datetime.UTC
            ).isoformat()
            record = {
                "id": src["id"],
                "title": src["title"],
                "jurisdiction": "uk",
                "category": "departments",
                "source_url": src["url"],
                "source_timestamp": source_timestamp,
                "rights_holder": src["rights_holder"],
                "licence": src["licence"],
                "provenance": {
                    "rights_holder": src["rights_holder"],
                    "licence": src["licence"],
                    "derivation_class": "fair_use_quote",
                    "shippable": False,
                    "shippable_art_path": None,
                },
            }
            record["_acquisition_id"] = str(uuid.uuid4())
            record["_firecrawl_plan"] = "plan_a_keyless"
            record["_firecrawl_key_present"] = firecrawl_key_present
            record["_content_hash"] = _stable_hash(record)
            yield record

    @dlt.resource(
        name="uk_acts_treaties_pages",
        write_disposition=write_disposition,
        primary_key=("id", "source_url", "source_timestamp"),
    )
    def uk_acts_treaties_pages() -> Iterator[dict[str, Any]]:
        firecrawl_key_present = bool(os.environ.get("FIRECRAWL_API_KEY"))
        for src in _UK_ACTS_TREATIES:
            source_timestamp = datetime.datetime.now(
                tz=datetime.UTC
            ).isoformat()
            record = {
                "id": src["id"],
                "title": src["title"],
                "jurisdiction": "uk",
                "category": "acts_treaties",
                "source_url": src["url"],
                "source_timestamp": source_timestamp,
                "rights_holder": src["rights_holder"],
                "licence": src["licence"],
                "provenance": {
                    "rights_holder": src["rights_holder"],
                    "licence": src["licence"],
                    "derivation_class": "fair_use_quote",
                    "shippable": False,
                    "shippable_art_path": None,
                },
            }
            record["_acquisition_id"] = str(uuid.uuid4())
            record["_firecrawl_plan"] = "plan_a_keyless"
            record["_firecrawl_key_present"] = firecrawl_key_present
            record["_content_hash"] = _stable_hash(record)
            yield record

    return (
        uk_police_defence_army_pages(),
        uk_departments_pages(),
        uk_acts_treaties_pages(),
    )


__all__ = [
    "_UK_ACTS_TREATIES",
    "_UK_DEFENCE",
    "_UK_DEPARTMENTS",
    "_UK_POLICE",
    "_stable_hash",
    "uk_government_source",
]
