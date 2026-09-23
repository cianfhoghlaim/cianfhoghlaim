"""cianfhoghlaim — DLT source for the UoG University Council + Academic Council Minutes.

Per openspec/changes/kcg-university-of-galway-doc-processing-v1/,
Case Study: Governance Minutes.

The UoG governance minutes are the canonical public record of
University Council + Academic Council + Údarás na hOllscoile
(Governing Authority) meetings. Published at:

    https://www.universityofgalway.ie/governance/

This DLT source scrapes the governance pages and emits one
`GovernanceMinute` row per meeting.

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import os
from collections.abc import Iterator

import dlt
import structlog

from ._base import TERTIARY_PIPELINE_BASE_VERSION, TertiaryPipelineBase, TertiarySurfaceConfig

logger = structlog.get_logger(__name__)


class GovernanceMinutesPipeline(TertiaryPipelineBase):
    """DLT pipeline for the UoG University Council + Academic Council minutes."""

    SURFACE_CONFIG = TertiarySurfaceConfig(
        surface_id="university_council_minutes",
        surface_name_english="University Council + Academic Council Minutes",
        surface_name_irish="Miontuairiscí an Chomhairle Ollscoile",
        source_url="https://www.universityofgalway.ie/governance/",
        jurisdiction="ie_galway",
        academic_year="2025/26",
        row_primary_key="meeting_date_iso",
    )

    @dlt.resource(write_disposition="replace", primary_key="meeting_date_iso")
    def minutes(self) -> Iterator[dict]:
        """Yield one GovernanceMinute per council meeting."""
        self.logger.info("governance_minutes_sync_start", surface_id=self.surface_id)

        if os.environ.get("USE_LOCAL_SCRAPES", "").lower() == "true":
            yield from self._yield_local_scrape_rows()
        else:
            yield from self._yield_live_scrape_rows()

        self.logger.info("governance_minutes_sync_complete", surface_id=self.surface_id)

    def _yield_live_scrape_rows(self) -> Iterator[dict]:
        """Live HTTP scrape — stub with canonical sample."""
        yield from _CANONICAL_SAMPLE_MINUTES

    def _yield_local_scrape_rows(self) -> Iterator[dict]:
        """Read from `stedding/ingest_queue/uog/university_council_minutes/*.json`."""
        import json
        from pathlib import Path

        local_path = Path(self.local_scrape_path())
        if not local_path.exists():
            self.logger.info("local_scrape_path_empty", path=str(local_path))
            return

        for json_file in sorted(local_path.glob("*.json")):
            yield from json.loads(json_file.read_text(encoding="utf-8"))

    def build_pipeline_resource(self) -> Iterator[dict]:
        return self.minutes()


# Canonical sample (stub for testing — replace with live scrape)
_CANONICAL_SAMPLE_MINUTES: list[dict] = [
    {
        "meeting_date_iso": "2025-09-12",
        "committee_name": "Academic Council",
        "committee_name_irish": "Comhairle Acadúil",
        "session_number": "2025/26/01",
        "chair_name": "Professor D. Fitzgerald",
        "attendees_count": 24,
        "quorum_met": True,
        "decisions_count": 8,
        "decisions_summary": (
            "Approved new BSc in Sustainability (stage 1 entry 2026/27); "
            "approved revised regulations for the BA (Hons) in Education; "
            "approved Q4 academic quality report."
        ),
        "action_items_count": 5,
        "source_url": "https://www.universityofgalway.ie/governance/academic-council/",
    },
    {
        "meeting_date_iso": "2025-10-10",
        "committee_name": "University Council",
        "committee_name_irish": "Comhairle na hOllscoile",
        "session_number": "2025/26/02",
        "chair_name": "Dr J. O'Connell",
        "attendees_count": 18,
        "quorum_met": True,
        "decisions_count": 6,
        "decisions_summary": (
            "Approved 2026/27 draft budget; "
            "approved revised strategic plan midpoint; "
            "approved appointment of 3 new professorial chairs."
        ),
        "action_items_count": 7,
        "source_url": "https://www.universityofgalway.ie/governance/university-council/",
    },
    {
        "meeting_date_iso": "2025-11-14",
        "committee_name": "Údarás na hOllscoile (Governing Authority)",
        "committee_name_irish": "Údarás na hOllscoile",
        "session_number": "2025/26/01",
        "chair_name": "An Dr E. Ní Cheallaigh",
        "attendees_count": 22,
        "quorum_met": True,
        "decisions_count": 4,
        "decisions_summary": (
            "Approved Athlone campus partnership extension; "
            "approved University of Galway Sustainability Strategy 2030."
        ),
        "action_items_count": 3,
        "source_url": "https://www.universityofgalway.ie/governance/udarás/",
    },
]


governance_minutes_pipeline = GovernanceMinutesPipeline()
