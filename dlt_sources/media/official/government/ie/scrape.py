"""dlt_sources/media/official/government/ie scrape DLT resource.

Éire (Ireland) government + Garda + Defence + Oireachtas +
Acts + Treaties. Class E (official) sub-bucket — the IE
jurisdiction.

Reference: openspec/changes/2026-08-23-tuatha-media-intel-gameplay-capture-research-v1/
            design.md § 1.4
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

# ── Source registry ─────────────────────────────────────────────────────────


# Police + Defence (4)
_IE_POLICE_DEFENCE: list[dict[str, str]] = [
    {
        "id": "garda",
        "title": "An Garda Síochána",
        "url": "https://www.garda.ie/",
        "rights_holder": "An Garda Síochána",
        "licence": "PSI",
    },
    {
        "id": "irish_defence_forces",
        "title": "Irish Defence Forces",
        "url": "https://www.military.ie/",
        "rights_holder": "Department of Defence (Ireland)",
        "licence": "PSI",
    },
    {
        "id": "naval_service",
        "title": "Naval Service (Ireland)",
        "url": "https://www.military.ie/en/the-irish-defence-forces/naval-service",
        "rights_holder": "Department of Defence (Ireland)",
        "licence": "PSI",
    },
    {
        "id": "air_corps",
        "title": "Air Corps (Ireland)",
        "url": "https://www.military.ie/en/the-irish-defence-forces/air-corps",
        "rights_holder": "Department of Defence (Ireland)",
        "licence": "PSI",
    },
]


# Departments (5)
_IE_DEPARTMENTS: list[dict[str, str]] = [
    {
        "id": "department_of_defence_ie",
        "title": "Department of Defence (Ireland)",
        "url": "https://www.gov.ie/en/department-of-defence/",
        "rights_holder": "Department of Defence (Ireland)",
        "licence": "PSI",
    },
    {
        "id": "department_of_justice_ie",
        "title": "Department of Justice (Ireland)",
        "url": "https://www.gov.ie/en/department-of-justice/",
        "rights_holder": "Department of Justice (Ireland)",
        "licence": "PSI",
    },
    {
        "id": "department_of_foreign_affairs_ie",
        "title": "Department of Foreign Affairs (Ireland)",
        "url": "https://www.dfa.ie/",
        "rights_holder": "Department of Foreign Affairs (Ireland)",
        "licence": "PSI",
    },
    {
        "id": "oireachtas",
        "title": "Houses of the Oireachtas (Dáil + Seanad)",
        "url": "https://www.oireachtas.ie/",
        "rights_holder": "Houses of the Oireachtas",
        "licence": "PSI",
    },
    {
        "id": "office_of_the_president",
        "title": "Office of the President of Ireland",
        "url": "https://president.ie/",
        "rights_holder": "Office of the President of Ireland",
        "licence": "PSI",
    },
]


# Acts + Treaties (6)
_IE_ACTS_TREATIES: list[dict[str, str]] = [
    {
        "id": "government_of_ireland_act_1920",
        "title": "Government of Ireland Act 1920",
        "url": "https://www.irishstatutebook.ie/eli/1920/act/67/enacted/en/html",
        "rights_holder": "Crown copyright",
        "licence": "OGL-3.0",
    },
    {
        "id": "statute_of_westminster_1931",
        "title": "Statute of Westminster 1931",
        "url": "https://www.irishstatutebook.ie/eli/1931/act/4/enacted/en/html",
        "rights_holder": "Crown copyright",
        "licence": "OGL-3.0",
    },
    {
        "id": "treaty_of_limerick_1691",
        "title": "Treaty of Limerick 1691",
        "url": "https://www.irishstatutebook.ie/eli/1691/act/2/enacted/en/html",
        "rights_holder": "Crown copyright",
        "licence": "OGL-3.0",
    },
    {
        "id": "bunreacht_na_h_eireann_1937",
        "title": "Constitution of Ireland (Bunreacht na hÉireann) 1937",
        "url": "https://www.irishstatutebook.ie/eli/1937/cautored/en/html",
        "rights_holder": "Government of Ireland",
        "licence": "PSI",
    },
    {
        "id": "anglo_irish_treaty_1921",
        "title": "Anglo-Irish Treaty 1921 — Ireland",
        "url": "https://www.dfa.ie/media/dfa/alldfawebsitemedia/our-role-policies/anglo-irish-treaty/Anglo-Irish-Treaty.pdf",
        "rights_holder": "Crown copyright",
        "licence": "OGL-3.0",
    },
    {
        "id": "good_friday_agreement_1998_ie",
        "title": "Good Friday Agreement (Belfast Agreement) 1998 — Ireland",
        "url": "https://www.gov.ie/en/department-of-the-taoiseach/publications/the-belfast-agreement/",
        "rights_holder": "Government of Ireland",
        "licence": "PSI",
    },
]


# ── Helpers (mirrors the leaving_cert.py pattern) ────────────────────────────


def _stable_hash(record: dict[str, Any]) -> str:
    """Content-addressable hash for change detection."""
    return hashlib.sha256(
        json.dumps(record, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()[:16]


# ── DLT source ──────────────────────────────────────────────────────────────


@dlt.source(name="ie_government")
def ie_government_source(
    use_local_scrapes: bool | None = None,
    write_disposition: str = "merge",
):
    """DLT source for the Éire government + Garda + Defence +
    Oireachtas + Acts + Treaties surface.

    The 15 source records are emitted as 3 `@dlt.resource`:
      - ie_police_defence_pages
      - ie_departments_pages
      - ie_acts_treaties_pages
    """
    if use_local_scrapes is None:
        use_local_scrapes = os.environ.get("USE_LOCAL_SCRAPES", "true").lower() == "true"

    if not use_local_scrapes:
        pass  # Plan A keyless Firecrawl fallback

    @dlt.resource(
        name="ie_police_defence_pages",
        write_disposition=write_disposition,
        primary_key=("id", "source_url", "source_timestamp"),
    )
    def ie_police_defence_pages() -> Iterator[dict[str, Any]]:
        firecrawl_key_present = bool(os.environ.get("FIRECRAWL_API_KEY"))
        for src in _IE_POLICE_DEFENCE:
            source_timestamp = datetime.datetime.now(
                tz=datetime.UTC
            ).isoformat()
            record = {
                "id": src["id"],
                "title": src["title"],
                "jurisdiction": "ie",
                "category": "police_defence",
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
        name="ie_departments_pages",
        write_disposition=write_disposition,
        primary_key=("id", "source_url", "source_timestamp"),
    )
    def ie_departments_pages() -> Iterator[dict[str, Any]]:
        firecrawl_key_present = bool(os.environ.get("FIRECRAWL_API_KEY"))
        for src in _IE_DEPARTMENTS:
            source_timestamp = datetime.datetime.now(
                tz=datetime.UTC
            ).isoformat()
            record = {
                "id": src["id"],
                "title": src["title"],
                "jurisdiction": "ie",
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
        name="ie_acts_treaties_pages",
        write_disposition=write_disposition,
        primary_key=("id", "source_url", "source_timestamp"),
    )
    def ie_acts_treaties_pages() -> Iterator[dict[str, Any]]:
        firecrawl_key_present = bool(os.environ.get("FIRECRAWL_API_KEY"))
        for src in _IE_ACTS_TREATIES:
            source_timestamp = datetime.datetime.now(
                tz=datetime.UTC
            ).isoformat()
            record = {
                "id": src["id"],
                "title": src["title"],
                "jurisdiction": "ie",
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
        ie_police_defence_pages(),
        ie_departments_pages(),
        ie_acts_treaties_pages(),
    )


__all__ = [
    "_IE_ACTS_TREATIES",
    "_IE_DEPARTMENTS",
    "_IE_POLICE_DEFENCE",
    "_stable_hash",
    "ie_government_source",
]
