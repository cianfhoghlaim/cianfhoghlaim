"""dlt_sources/media/official/government/crown_dependencies scrape DLT resource.

The 3 British Crown Dependencies: Isle of Man + Jersey + Guernsey.
Class E (official) sub-bucket — the Crown Dependencies jurisdiction.

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


_CROWN_DEPS: list[dict[str, str]] = [
    # Isle of Man (4)
    {
        "id": "isle_of_man_government",
        "title": "Isle of Man Government",
        "url": "https://www.gov.im/",
        "rights_holder": "Isle of Man Government",
        "licence": "OGL-3.0",
        "dependency": "isle_of_man",
    },
    {
        "id": "isle_of_man_constabulary",
        "title": "Isle of Man Constabulary",
        "url": "https://www.iompolice.im/",
        "rights_holder": "Isle of Man Constabulary",
        "licence": "OGL-3.0",
        "dependency": "isle_of_man",
    },
    {
        "id": "tynwald",
        "title": "Tynwald (Isle of Man legislature)",
        "url": "https://www.tynwald.org.im/",
        "rights_holder": "Tynwald",
        "licence": "OGL-3.0",
        "dependency": "isle_of_man",
    },
    {
        "id": "isle_of_man_courts",
        "title": "Isle of Man Courts of Justice",
        "url": "https://www.courts.im/",
        "rights_holder": "Isle of Man Courts of Justice",
        "licence": "OGL-3.0",
        "dependency": "isle_of_man",
    },
    # Jersey (2)
    {
        "id": "states_of_jersey",
        "title": "States of Jersey",
        "url": "https://www.gov.je/",
        "rights_holder": "States of Jersey",
        "licence": "OGL-3.0",
        "dependency": "jersey",
    },
    {
        "id": "states_of_jersey_police",
        "title": "States of Jersey Police",
        "url": "https://www.jersey.police.uk/",
        "rights_holder": "States of Jersey Police",
        "licence": "OGL-3.0",
        "dependency": "jersey",
    },
    # Guernsey (2)
    {
        "id": "states_of_guernsey",
        "title": "States of Guernsey",
        "url": "https://www.gov.gg/",
        "rights_holder": "States of Guernsey",
        "licence": "OGL-3.0",
        "dependency": "guernsey",
    },
    {
        "id": "guernsey_police",
        "title": "Bailiwick of Guernsey Police",
        "url": "https://www.guernsey.police.uk/",
        "rights_holder": "Bailiwick of Guernsey Police",
        "licence": "OGL-3.0",
        "dependency": "guernsey",
    },
]


# ── Helpers (mirrors the leaving_cert.py pattern) ────────────────────────────


def _stable_hash(record: dict[str, Any]) -> str:
    """Content-addressable hash for change detection."""
    return hashlib.sha256(
        json.dumps(record, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()[:16]


# ── DLT source ──────────────────────────────────────────────────────────────


@dlt.source(name="crown_dependencies_government")
def crown_dependencies_government_source(
    use_local_scrapes: bool | None = None,
    write_disposition: str = "merge",
):
    """DLT source for the 3 British Crown Dependencies (IoM +
    Jersey + Guernsey) — government + police + courts + legislature.

    The 8 source records are emitted as a single `@dlt.resource`.
    """
    if use_local_scrapes is None:
        use_local_scrapes = os.environ.get("USE_LOCAL_SCRAPES", "true").lower() == "true"

    if not use_local_scrapes:
        pass  # Plan A keyless Firecrawl fallback

    @dlt.resource(
        name="crown_dependencies_pages",
        write_disposition=write_disposition,
        primary_key=("id", "source_url", "source_timestamp"),
    )
    def crown_dependencies_pages() -> Iterator[dict[str, Any]]:
        firecrawl_key_present = bool(os.environ.get("FIRECRAWL_API_KEY"))
        for src in _CROWN_DEPS:
            source_timestamp = datetime.datetime.now(
                tz=datetime.UTC
            ).isoformat()
            record = {
                "id": src["id"],
                "title": src["title"],
                "jurisdiction": "crown_dependencies",
                "dependency": src["dependency"],
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

    return crown_dependencies_pages(),


__all__ = [
    "_CROWN_DEPS",
    "_stable_hash",
    "crown_dependencies_government_source",
]
