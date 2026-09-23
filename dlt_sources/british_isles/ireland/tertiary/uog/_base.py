"""cianfhoghlaim — TertiaryPipelineBase contract for University of Galway DLT sources.

Per openspec/changes/kcg-university-of-galway-doc-processing-v1/,
Requirement: The TertiaryPipelineBase class — the canonical contract that
all 5 UoG DLT source modules share.

The base class mirrors the cianchosaint `JurisdictionPipelineBase` +
ciandlithe `PoliticalPartyPipelineBase` patterns but is scoped to the
University of Galway domain.

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

TERTIARY_PIPELINE_BASE_VERSION = "0.1.0"

# The 5 canonical UoG public surfaces
_TERTIARY_SURFACES: tuple[str, ...] = (
    "academic_calendar",
    "course_catalog",
    "university_council_minutes",
    "press_releases",
    "research_outputs",
)


@dataclass(frozen=True)
class TertiarySurfaceConfig:
    """The configuration for one UoG public surface."""

    surface_id: str
    surface_name_english: str
    surface_name_irish: str
    source_url: str  # Must be in the OSINT allowlist
    jurisdiction: str = "ie_galway"
    academic_year: str = "2025/26"
    row_primary_key: str = "url"
    extra: dict[str, Any] = field(default_factory=dict)


# The 5 canonical UoG public-surface configs
_TERTIARY_SURFACE_CONFIGS: dict[str, TertiarySurfaceConfig] = {
    "academic_calendar": TertiarySurfaceConfig(
        surface_id="academic_calendar",
        surface_name_english="Academic Calendar",
        surface_name_irish="Féilire Acadúil",
        source_url="https://www.universityofgalway.ie/academic-calendar/",
        jurisdiction="ie_galway",
        academic_year="2025/26",
        row_primary_key="date_iso",
    ),
    "course_catalog": TertiarySurfaceConfig(
        surface_id="course_catalog",
        surface_name_english="Course Catalog (Undergraduate + Postgraduate)",
        surface_name_irish="Catalog Cúrsaí",
        source_url="https://www.universityofgalway.ie/courses/",
        jurisdiction="ie_galway",
        academic_year="2025/26",
        row_primary_key="course_code",
    ),
    "university_council_minutes": TertiarySurfaceConfig(
        surface_id="university_council_minutes",
        surface_name_english="University Council + Academic Council Minutes",
        surface_name_irish="Miontuairiscí an Chomhairle Ollscoile",
        source_url="https://www.universityofgalway.ie/governance/",
        jurisdiction="ie_galway",
        academic_year="2025/26",
        row_primary_key="meeting_date_iso",
    ),
    "press_releases": TertiarySurfaceConfig(
        surface_id="press_releases",
        surface_name_english="Press Releases + News",
        surface_name_irish="Preas-Ráitis + Nuacht",
        source_url="https://www.universityofgalway.ie/news/",
        jurisdiction="ie_galway",
        academic_year="2025/26",
        row_primary_key="url",
    ),
    "research_outputs": TertiarySurfaceConfig(
        surface_id="research_outputs",
        surface_name_english="Research Publications + Theses",
        surface_name_irish="Aschuir Thaighde",
        source_url="https://www.universityofgalway.ie/research/",
        jurisdiction="ie_galway",
        academic_year="2025/26",
        row_primary_key="url",
    ),
}


class TertiaryPipelineBase:
    """The canonical contract every UoG DLT source subclasses.

    Subclasses MUST set:

      - `SURFACE_CONFIG: TertiarySurfaceConfig` — the surface this source
        scrapes (one of the 5 in _TERTIARY_SURFACE_CONFIGS)
      - `@dlt.resource` method `rows()` that yields `dict` rows

    The base class provides:

      - `osint_allowlist_check(source_url)` — verifies the URL is in
        `scripts/osint_allowlist.yaml` (the canonical OSINT allowlist)
      - `local_scrape_path()` — returns the offline scrape path
        (`stedding/ingest_queue/uog/<surface_id>/`)
      - `pipeline_row_key(row)` — returns the natural-key field for
        the row (e.g. `course_code` for course_catalog)
    """

    SURFACE_CONFIG: TertiarySurfaceConfig | None = None

    def __init__(self) -> None:
        if self.SURFACE_CONFIG is None:
            raise ValueError(
                f"{type(self).__name__}.SURFACE_CONFIG must be set to one of "
                f"{list(_TERTIARY_SURFACE_CONFIGS.keys())}"
            )
        self.surface_id = self.SURFACE_CONFIG.surface_id
        self.source_url = self.SURFACE_CONFIG.source_url
        self.jurisdiction = self.SURFACE_CONFIG.jurisdiction
        self.logger = logger.bind(surface_id=self.surface_id)

    def osint_allowlist_check(self, *, source_url: str | None = None) -> bool:
        """Verify the source URL is in the OSINT allowlist.

        The allowlist lives at `scripts/osint_allowlist.yaml`. This
        method is the licence-enforcement surface (per LICENSE.md):
        every DLT source MUST call this before yielding rows.
        """
        url = source_url or self.source_url
        try:
            import yaml
            from pathlib import Path

            allowlist_path = Path(__file__).resolve().parents[2] / "scripts" / "osint_allowlist.yaml"
            if not allowlist_path.exists():
                self.logger.warning("osint_allowlist_file_missing", path=str(allowlist_path))
                return False
            docs = yaml.safe_load_all(allowlist_path.read_text(encoding="utf-8"))
            for doc in docs:
                if doc is None:
                    continue
                if isinstance(doc, list):
                    for entry in doc:
                        if isinstance(entry, dict) and entry.get("url") == url:
                            return True
                elif isinstance(doc, dict):
                    for entry in doc.get("entries", []):
                        if isinstance(entry, dict) and entry.get("url") == url:
                            return True
            return False
        except Exception as e:
            self.logger.error("osint_allowlist_check_failed", error=str(e), url=url)
            return False

    def local_scrape_path(self) -> str:
        """Return the offline scrape path (USE_LOCAL_SCRAPES=true mode)."""
        from pathlib import Path

        repo_root = Path(__file__).resolve().parents[2]
        return str(repo_root / "stedding" / "ingest_queue" / "uog" / self.surface_id)

    def pipeline_row_key(self, row: dict[str, Any]) -> str:
        """Return the natural-key field for a row."""
        pk = self.SURFACE_CONFIG.row_primary_key if self.SURFACE_CONFIG else "url"
        return str(row.get(pk, ""))

    def build_pipeline_resource(self) -> Iterator[dict[str, Any]]:
        """Yield the canonical rows for this surface.

        Subclasses override this. The base class is a no-op (yields nothing)
        so subclasses can't accidentally fall through.
        """
        return iter(())
