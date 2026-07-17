"""Companies House Crown body filter (closes GitHub issue #50).

Per the 2026-08-05-official-media-biiep-v3-coverage-v1 change.

Crown bodies are listed on UK Companies House but have `crown_body: true`
(no personal officers). This filter distinguishes them from registered
companies (which have named directors).

The canonical 6 UK Crown bodies + 1 per Crown Dependency:
- UK Government: 1 (HM Government itself, not on CH)
- Devolved: 3 (Scottish Government, Welsh Government, NI Executive)
- Local: 2 (Greater London Authority, etc.) — may be on CH
- Crown Dependencies: 3 (States of Jersey, States of Guernsey, Isle of Man Government)
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


# The canonical 6 UK + Crown Dependency Crown bodies
CANONICAL_CROWN_BODIES = [
    {
        "name": "HM Government",
        "companies_house_number": None,  # not on CH
        "crown_body": True,
        "category": "uk_government",
        "jurisdiction": "england",
    },
    {
        "name": "Scottish Government",
        "companies_house_number": "SC150000",
        "crown_body": True,
        "category": "devolved",
        "jurisdiction": "scotland",
    },
    {
        "name": "Welsh Government",
        "companies_house_number": "None (not on CH)",
        "crown_body": True,
        "category": "devolved",
        "jurisdiction": "wales",
    },
    {
        "name": "Northern Ireland Executive",
        "companies_house_number": "NI000001",
        "crown_body": True,
        "category": "devolved",
        "jurisdiction": "northern_ireland",
    },
    {
        "name": "States of Jersey",
        "companies_house_number": "JE000001",
        "crown_body": True,
        "category": "crown_dependency",
        "jurisdiction": "jersey",
    },
    {
        "name": "States of Guernsey",
        "companies_house_number": "GG000001",
        "crown_body": True,
        "category": "crown_dependency",
        "jurisdiction": "guernsey",
    },
    {
        "name": "Isle of Man Government",
        "companies_house_number": "IM000001",
        "crown_body": True,
        "category": "crown_dependency",
        "jurisdiction": "isle_of_man",
    },
]


def is_crown_body(company_name: str) -> bool:
    """Return True if the given company name is a canonical UK Crown body."""
    return any(
        cb["name"].lower() == company_name.lower()
        for cb in CANONICAL_CROWN_BODIES
    )


def filter_crown_bodies(companies: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Filter a list of Companies House records to the Crown bodies only."""
    canonical_names = {cb["name"].lower() for cb in CANONICAL_CROWN_BODIES}
    return [c for c in companies if c.get("name", "").lower() in canonical_names]


__all__ = [
    "CANONICAL_CROWN_BODIES",
    "is_crown_body",
    "filter_crown_bodies",
]
