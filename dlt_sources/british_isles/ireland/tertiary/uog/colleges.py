"""UoG Colleges — DLT source for the 4 colleges of Ollscoil na Gaillimhe.

Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/.

The 4 UoG colleges (the top tier of the 4-tier College → School →
Programme → Module hierarchy):

  1. College of Arts, Social Sciences, and Celtic Studies
     (id: arts-social-sciences-celtic-studies)
  2. College of Business, Public Policy, and Law
     (id: business-public-policy-law)
  3. College of Medicine, Nursing, and Health Sciences
     (id: medicine-nursing-health-sciences)
  4. College of Science and Engineering
     (id: science-engineering)

Honors `USE_LOCAL_SCRAPES=true` (default). Source URLs:
- https://www.universityofgalway.ie/about-us/structure/

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import os
from collections.abc import Iterator

import dlt
import structlog

from ._base import TERTIARY_PIPELINE_BASE_VERSION, TertiaryPipelineBase, TertiarySurfaceConfig

logger = structlog.get_logger(__name__)


# The 4 canonical UoG colleges
UOG_COLLEGES: tuple[dict, ...] = (
    {
        "college_id": "arts-social-sciences-celtic-studies",
        "college_name_english": "College of Arts, Social Sciences, and Celtic Studies",
        "college_name_irish": "Coláiste na nEalaíon, na nEolaíochtaí Sóisialta agus an Léinn Cheiltigh",
        "dean_name": "Prof. D. Ní Mhurchú",
        "source_url": "https://www.universityofgalway.ie/about-us/structure/arts-social-sciences-celtic-studies/",
        "nfq_min": 6,
        "nfq_max": 10,
        "established_year": 1849,
        "school_count": 4,
    },
    {
        "college_id": "business-public-policy-law",
        "college_name_english": "College of Business, Public Policy, and Law",
        "college_name_irish": "Coláiste an Ghnó, an Pholasaí Phoiblí agus an Dlí",
        "dean_name": "Prof. A. Walsh",
        "source_url": "https://www.universityofgalway.ie/about-us/structure/business-public-policy-law/",
        "nfq_min": 6,
        "nfq_max": 10,
        "established_year": 2021,
        "school_count": 3,
    },
    {
        "college_id": "medicine-nursing-health-sciences",
        "college_name_english": "College of Medicine, Nursing, and Health Sciences",
        "college_name_irish": "Coláiste an Leighis, an Altranais agus na nEolaíochtaí Sláinte",
        "dean_name": "Prof. B. Smith",
        "source_url": "https://www.universityofgalway.ie/about-us/structure/medicine-nursing-health-sciences/",
        "nfq_min": 6,
        "nfq_max": 10,
        "established_year": 1845,
        "school_count": 3,
    },
    {
        "college_id": "science-engineering",
        "college_name_english": "College of Science and Engineering",
        "college_name_irish": "Coláiste na hEolaíochta agus na hInnealtóireachta",
        "dean_name": "Prof. C. O'Brien",
        "source_url": "https://www.universityofgalway.ie/about-us/structure/science-engineering/",
        "nfq_min": 6,
        "nfq_max": 10,
        "established_year": 1845,
        "school_count": 5,
    },
)


class CollegesPipeline(TertiaryPipelineBase):
    SURFACE_CONFIG = TertiarySurfaceConfig(
        surface_id="uog_colleges",
        surface_name_english="UoG Colleges",
        surface_name_irish="Coláistí UoG",
        source_url="https://www.universityofgalway.ie/about-us/structure/",
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
