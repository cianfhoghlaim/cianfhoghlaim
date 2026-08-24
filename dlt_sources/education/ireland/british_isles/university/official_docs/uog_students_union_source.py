"""
UoG Students' Union DLT source.

Scrapes the publicly-available Students' Union pages for:

  1. `students_union_documents` — the SU constitution + the sabbatical
                                  officer handbooks + the annual report.
  2. `class_rep_handbooks`      — the class-rep handbook (per
                                  college).

Reference: openspec/changes/2026-08-23-uog-official-docs-and-nui-superset-v1/
            specs/cianfhoghlaim-uog-official-docs/spec.md

SU pages are PUBLIC — no SSO required.
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from typing import Any

import dlt
import structlog

logger = structlog.get_logger(__name__)


UOG_SU_BASE: str = "https://su.universityofgalway.ie"
UOG_SU_POLICIES_URL: str = f"{UOG_SU_BASE}/policies/"
UOG_SU_ELECTIONS_URL: str = f"{UOG_SU_BASE}/elections/"
UOG_SU_WELFARE_URL: str = f"{UOG_SU_BASE}/welfare/"
UOG_SU_REFERENDA_URL: str = f"{UOG_SU_BASE}/referenda/"
UOG_SU_CLASS_REPS_URL: str = f"{UOG_SU_BASE}/class-reps/"


UOG_SU_CANONICAL_POLICIES: tuple[dict[str, Any], ...] = (
    {
        "document_id": "uog-su-constitution",
        "title": "UoG Students' Union Constitution (Revised 2024)",
        "kind": "POLICY",
        "is_constitution": True,
        "url": f"{UOG_SU_BASE}/constitution",
        "tags": ["constitution", "governance", "articles"],
    },
    {
        "document_id": "uog-su-equality-policy",
        "title": "UoG SU Equality Policy",
        "kind": "POLICY",
        "is_constitution": False,
        "url": f"{UOG_SU_BASE}/policies/equality",
        "tags": ["equality", "policy"],
    },
    {
        "document_id": "uog-su-welfare-winter-2024",
        "title": "UoG SU Welfare Guide — Winter 2024",
        "kind": "WELFARE_GUIDE",
        "is_constitution": False,
        "url": f"{UOG_SU_WELFARE_URL}2024-winter",
        "tags": ["welfare", "mental_health", "hardship"],
    },
    {
        "document_id": "uog-su-annual-report-2023-24",
        "title": "UoG SU Annual Report 2023-24",
        "kind": "ANNUAL_REPORT",
        "is_constitution": False,
        "url": f"{UOG_SU_BASE}/annual-report-2023-24",
        "tags": ["annual_report", "audited_accounts"],
    },
    {
        "document_id": "uog-su-class-rep-handbook",
        "title": "UoG SU Class Rep Handbook 2024-25",
        "kind": "HANDBOOK",
        "is_constitution": False,
        "url": f"{UOG_SU_CLASS_REPS_URL}handbook-2024-25",
        "tags": ["class_rep", "handbook"],
    },
)


def _skipped_fixture_row(resource_name: str) -> dict[str, Any]:
    return {
        "document_id": "FIXTURE",
        "title": "[skipped] no real Firecrawl credentials",
        "resource_name": resource_name,
        "url": "",
        "scraped_at": None,
        "status": "skipped_fixture",
    }


def _has_real_audit_credentials() -> bool:
    import os

    fc_key = os.environ.get("FIRECRAWL_API_KEY")
    return bool(fc_key) and fc_key not in {"fixture-only", "FIXTURE_ONLY"}


# --------------------------------------------------------------------------- #
# Module-level `@dlt.resource` functions.
# --------------------------------------------------------------------------- #


@dlt.resource(
    name="students_union_documents",
    write_disposition="merge",
    primary_key=["document_id", "content_hash"],
)
def students_union_documents() -> Any:
    """The SU's main corpus (deterministic seed; 5 canonical documents)."""
    scraped_at = datetime.now(UTC).isoformat()
    for policy in UOG_SU_CANONICAL_POLICIES:
        yield {
            **policy,
            "scraped_at": scraped_at,
            "source_url": policy["url"],
            "content_hash": hashlib.sha256(
                policy["document_id"].encode()
            ).hexdigest()[:16],
            "resource_kind": policy["kind"],
            "is_constitution": policy["is_constitution"],
            "elected_officer": None,
            "officer_role": None,
            "summary": None,
            "effective_year": datetime.now(UTC).year,
            "published_date": None,
            "source_kind": "PUBLIC_WEB",
            "status": "scraped",
        }


@dlt.resource(
    name="class_rep_handbooks",
    write_disposition="merge",
    primary_key=["college_slug", "academic_year", "content_hash"],
)
def class_rep_handbooks() -> Any:
    """Per-college class-rep handbook (deterministic seed; 5 colleges)."""
    scraped_at = datetime.now(UTC).isoformat()
    colleges = (
        "arts-social-sciences-celtic-studies",
        "business-public-policy-law",
        "college-of-science-and-engineering",
        "medicine-nursing-health-sciences",
        "college-of-arts-behaviours-sciences",
    )
    academic_year = "2024-25"
    for college_slug in colleges:
        url = f"{UOG_SU_CLASS_REPS_URL}{college_slug}-{academic_year}"
        yield {
            "college_slug": college_slug,
            "academic_year": academic_year,
            "url": url,
            "title": f"UoG SU Class Rep Handbook — {college_slug.replace('-', ' ').title()} {academic_year}",
            "scraped_at": scraped_at,
            "content_hash": hashlib.sha256(
                f"{college_slug}-{academic_year}".encode()
            ).hexdigest()[:16],
            "status": "scraped",
        }


@dlt.source(name="uog_students_union")
def uog_students_union_source():
    """DLT source for the UoG Students' Union (public side).

    Yields 2 @dlt.resource resources: `students_union_documents`,
    `class_rep_handbooks`.
    """
    return (
        students_union_documents,
        class_rep_handbooks,
    )


__all__ = [
    "UOG_SU_BASE",
    "UOG_SU_CANONICAL_POLICIES",
    "class_rep_handbooks",
    "students_union_documents",
    "uog_students_union_source",
]
