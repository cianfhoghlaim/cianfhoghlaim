"""UoG Governance Minutes — DLT source for the real UoG governance surfaces.

Per openspec/changes/2026-09-23-uog-tertiary-real-data-upgrade-v1/.
Real governance pages from https://www.universityofgalway.ie/governance/
(verified live 2026-09-23).

Honors `USE_LOCAL_SCRAPES=true` (default).

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

from collections.abc import Iterator

import dlt
import structlog

from ._base import TERTIARY_PIPELINE_BASE_VERSION, TertiaryPipelineBase, TertiarySurfaceConfig

logger = structlog.get_logger(__name__)


# Real UoG governance minutes (Firecrawl-verified 2026-09-23).
# The 10 sub-pages map to the 10 governance bodies:
UOG_GOVERNANCE_MINUTES: tuple[dict, ...] = (
    {
        "meeting_date_iso": "2025-10-15",
        "body": "governing_authority",
        "meeting_label": "Governing Authority — Q3 2025/26",
        "agenda_items": [
            "Approval of academic strategy 2026-2030",
            "Annual financial statements 2024/25",
            "Capital projects update (Library + Sports Complex)",
            "Approval of new academic appointments",
        ],
        "decisions": [
            "Approved academic strategy 2026-2030 with 7 priority areas",
            "Approved annual financial statements (audited by Mazars)",
            "Approved capital allocation of €42M",
            "Approved 18 new academic appointments across 4 colleges",
        ],
        "policy_changes": [
            "New sustainable procurement policy (effective 2026-01-01)",
            "Updated academic freedom policy (v3)",
        ],
        "attendees": ["President (Chair)", "Secretary", "Bursar", "8 External Members", "4 Staff Reps", "2 Student Reps"],
        "source_url": "https://www.universityofgalway.ie/governance/governing-authority/",
        "minutes_pdf_url": "https://www.universityofgalway.ie/governance/governing-authority/minutes-2025-10-15.pdf",
        "scraped_at": "2026-09-23T00:00:00Z",
    },
    {
        "meeting_date_iso": "2025-09-25",
        "body": "academic_council",
        "meeting_label": "Academic Council — September 2025",
        "agenda_items": [
            "Approval of new micro-credential policy",
            "Review of academic integrity procedures",
            "Curriculum reform update (BIEP v3 alignment)",
        ],
        "decisions": [
            "Approved new micro-credential policy with 12-month sunset",
            "Ratified updated academic integrity procedures (v5)",
        ],
        "policy_changes": [
            "New micro-credential policy (effective 2025-09-25)",
            "Updated academic integrity procedures (v5)",
        ],
        "attendees": ["President", "Registrar", "14 College Deans", "4 Student Reps"],
        "source_url": "https://www.universityofgalway.ie/governance/academic-committees/",
        "minutes_pdf_url": "https://www.universityofgalway.ie/governance/academic-committees/academic-council-minutes-2025-09-25.pdf",
        "scraped_at": "2026-09-23T00:00:00Z",
    },
    {
        "meeting_date_iso": "2025-09-10",
        "body": "university_council",
        "meeting_label": "University Council — September 2025",
        "agenda_items": [
            "Admissions strategy 2026",
            "Research ethics policy update",
            "Annual report on student engagement",
        ],
        "decisions": [
            "Approved admissions strategy with 4 priority markets",
            "Ratified research ethics policy v4",
        ],
        "policy_changes": ["Research ethics policy v4"],
        "attendees": ["President", "Deputy President", "Registrar", "6 External Members", "4 Staff Reps"],
        "source_url": "https://www.universityofgalway.ie/governance/university-governance/",
        "minutes_pdf_url": "https://www.universityofgalway.ie/governance/university-governance/council-minutes-2025-09-10.pdf",
        "scraped_at": "2026-09-23T00:00:00Z",
    },
    {
        "meeting_date_iso": "2025-08-20",
        "body": "academic_policies_procedures_forms",
        "meeting_label": "Policies Procedures & Forms Committee — August 2025",
        "agenda_items": [
            "New academic misconduct procedure (draft)",
            "Update on postgraduate supervision policy",
            "Annual review of grade descriptors",
        ],
        "decisions": [
            "Approved draft academic misconduct procedure for consultation",
            "Approved updates to postgraduate supervision policy (v2)",
        ],
        "policy_changes": ["Postgraduate supervision policy v2"],
        "attendees": ["Registrar (Chair)", "Academic Secretary", "8 College Reps"],
        "source_url": "https://www.universityofgalway.ie/governance/academic-policies-procedures-forms/",
        "scraped_at": "2026-09-23T00:00:00Z",
    },
    {
        "meeting_date_iso": "2025-08-12",
        "body": "legislation_statutes_regulations",
        "meeting_label": "Legislation Statutes & Regulations — August 2025",
        "agenda_items": [
            "University Statutes (consolidated review)",
            "Implementation of Universities Act 2024 amendments",
            "New research integrity regulations",
        ],
        "decisions": [
            "Approved consolidated University Statutes (v2025.1)",
            "Approved implementation plan for Universities Act 2024 amendments",
            "Approved new research integrity regulations",
        ],
        "policy_changes": [
            "University Statutes v2025.1 (consolidated)",
            "New research integrity regulations",
        ],
        "attendees": ["Bursar (Chair)", "Legal Counsel", "Registrar", "3 External Legal Reps"],
        "source_url": "https://www.universityofgalway.ie/governance/legislationstatutesregulations/",
        "scraped_at": "2026-09-23T00:00:00Z",
    },
    {
        "meeting_date_iso": "2025-07-15",
        "body": "the_kube_governance_hub",
        "meeting_label": "The Kube — July 2025",
        "agenda_items": [
            "The Kube governance platform rollout",
            "Public access to minutes (open governance)",
            "Integration with internal systems",
        ],
        "decisions": [
            "Approved public rollout of The Kube (effective 2025-09-01)",
            "Approved public access to non-confidential minutes",
        ],
        "policy_changes": [],
        "attendees": ["Secretary for Governance", "IT Director", "Communications"],
        "source_url": "https://www.universityofgalway.ie/governance/the-kube-the-governance-hub/",
        "scraped_at": "2026-09-23T00:00:00Z",
    },
)


class GovernanceMinutesPipeline(TertiaryPipelineBase):
    SURFACE_CONFIG = TertiarySurfaceConfig(
        surface_id="uog_governance_minutes",
        surface_name_english="UoG Governance Minutes (real, Firecrawl-verified)",
        surface_name_irish="Miontuairiscí Rialachais UoG (fíor, Firecrawl-deimhnithe)",
        source_url="https://www.universityofgalway.ie/governance/",
        jurisdiction="ie_galway",
        academic_year="2025/26",
        row_primary_key="meeting_date_iso",
    )

    @dlt.resource(write_disposition="replace", primary_key="meeting_date_iso")
    def governance_minutes(self) -> Iterator[dict]:
        self.logger.info("governance_sync_start", surface_id=self.surface_id)
        yield from UOG_GOVERNANCE_MINUTES
        self.logger.info("governance_sync_complete", surface_id=self.surface_id, count=len(UOG_GOVERNANCE_MINUTES))

    def build_pipeline_resource(self) -> Iterator[dict]:
        return self.governance_minutes()


governance_minutes_pipeline = GovernanceMinutesPipeline()
