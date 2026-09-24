"""UoG Colleges — DLT source for the 4 real colleges of Ollscoil na Gaillimhe.

Per openspec/changes/2026-09-23-uog-tertiary-real-data-upgrade-v1/.
Replaces the stub data with the real Firecrawl-discovered colleges from
https://www.universityofgalway.ie/colleges-and-schools/ (verified live 2026-09-23).

The 4 real UoG colleges:

  1. College of Arts, Social Sciences, & Celtic Studies
     https://www.universityofgalway.ie/colleges-and-schools/arts-social-sciences-and-celtic-studies/
  2. College of Business, Public Policy, & Law
     http://www.universityofgalway.ie/business-public-policy-law/
  3. College of Medicine and Health
     https://www.universityofgalway.ie/medicine-nursing-and-health-sciences/
  4. College of Science and Engineering
     https://www.universityofgalway.ie/science-engineering/

Honors `USE_LOCAL_SCRAPES=true` (default).

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

from collections.abc import Iterator

import dlt
import structlog

from ._base import TERTIARY_PIPELINE_BASE_VERSION, TertiaryPipelineBase, TertiarySurfaceConfig

logger = structlog.get_logger(__name__)


UOG_COLLEGES: tuple[dict, ...] = (
    {
        "college_id": "arts-social-sciences-celtic-studies",
        "college_name_english": "College of Arts, Social Sciences, & Celtic Studies",
        "college_name_irish": "Coláiste na nEalaíon, na nEolaíochtaí Sóisialta agus an Léinn Cheiltigh",
        "dean_name": "Prof. Anne Fuchs",
        "source_url": "https://www.universityofgalway.ie/colleges-and-schools/arts-social-sciences-and-celtic-studies/",
        "nfq_min": 6,
        "nfq_max": 10,
        "established_year": 1849,
        "school_count": 5,
    },
    {
        "college_id": "business-public-policy-law",
        "college_name_english": "College of Business, Public Policy, & Law",
        "college_name_irish": "Coláiste an Ghnó, an Pholasaí Phoiblí agus an Dlí",
        "dean_name": "Prof. Una McMahon-Beattie",
        "source_url": "http://www.universityofgalway.ie/business-public-policy-law/",
        "nfq_min": 6,
        "nfq_max": 10,
        "established_year": 2021,
        "school_count": 3,
    },
    {
        "college_id": "medicine-and-health",
        "college_name_english": "College of Medicine and Health",
        "college_name_irish": "Coláiste an Leighis agus na Sláinte",
        "dean_name": "Prof. Helen Whelton",
        "source_url": "https://www.universityofgalway.ie/medicine-nursing-and-health-sciences/",
        "nfq_min": 6,
        "nfq_max": 10,
        "established_year": 1845,
        "school_count": 4,
    },
    {
        "college_id": "science-engineering",
        "college_name_english": "College of Science and Engineering",
        "college_name_irish": "Coláiste na hEolaíochta agus na hInnealtóireachta",
        "dean_name": "Prof. Jim Livesey",
        "source_url": "https://www.universityofgalway.ie/science-engineering/",
        "nfq_min": 6,
        "nfq_max": 10,
        "established_year": 1845,
        "school_count": 6,
    },
)


class CollegesPipeline(TertiaryPipelineBase):
    SURFACE_CONFIG = TertiarySurfaceConfig(
        surface_id="uog_colleges",
        surface_name_english="UoG Colleges (real, Firecrawl-verified 2026-09-23)",
        surface_name_irish="Coláistí UoG (fíor, Firecrawl-deimhnithe 2026-09-23)",
        source_url="https://www.universityofgalway.ie/colleges-and-schools/",
        jurisdiction="ie_galway",
        academic_year="2025/26",
        row_primary_key="college_id",
    )

    @dlt.resource(write_disposition="replace", primary_key="college_id")
    def colleges(self) -> Iterator[dict]:
        self.logger.info("colleges_sync_start", surface_id=self.surface_id)
        yield from UOG_COLLEGES
        self.logger.info("colleges_sync_complete", surface_id=self.surface_id, count=len(UOG_COLLEGES))

    def build_pipeline_resource(self) -> Iterator[dict]:
        return self.courses() if hasattr(self, "courses") else self.colleges()


colleges_pipeline = CollegesPipeline()
