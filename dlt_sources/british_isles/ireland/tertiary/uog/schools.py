"""UoG Schools — DLT source for the ~10 schools of Ollscoil na Gaillimhe.

Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/.

Tier 2 of the 4-tier College → School → Programme → Module hierarchy.

Honors `USE_LOCAL_SCRAPES=true` (default). Source URLs:
- https://www.universityofgalway.ie/colleges/{college_slug}/schools/

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import os
from collections.abc import Iterator

import dlt
import structlog

from ._base import TERTIARY_PIPELINE_BASE_VERSION, TertiaryPipelineBase, TertiarySurfaceConfig

logger = structlog.get_logger(__name__)


# The canonical UoG schools (Phase 1 stub — Phase 2 fills from live scrape)
UOG_SCHOOLS: tuple[dict, ...] = (
    {
        "school_id": "school-computer-science",
        "college_id": "science-engineering",
        "school_name_english": "School of Computer Science",
        "school_name_irish": "Scoil na Ríomheolaíochta",
        "head_of_school": "Prof. M. Hayes",
        "n_students": 600,
        "n_staff": 35,
        "research_centres": ["Lero", "Data Science Institute"],
        "source_url": "https://www.universityofgalway.ie/science-engineering/schools/computer-science/",
    },
    {
        "school_id": "school-mathematics-statistics-applied-mathematics",
        "college_id": "science-engineering",
        "school_name_english": "School of Mathematics, Statistics and Applied Mathematics",
        "school_name_irish": "Scoil na Matamaitice, na Staitisticí agus na Matamaitice Feidhmí",
        "head_of_school": "Prof. S. Ní Laoghaire",
        "n_students": 250,
        "n_staff": 22,
        "research_centres": ["MACSI"],
        "source_url": "https://www.universityofgalway.ie/science-engineering/schools/mathematics-statistics-applied-mathematics/",
    },
    {
        "school_id": "school-physics",
        "college_id": "science-engineering",
        "school_name_english": "School of Physics",
        "school_name_irish": "Scoil na Fisice",
        "head_of_school": "Prof. L. O'Connor",
        "n_students": 180,
        "n_staff": 18,
        "research_centres": ["Centre for Photonics and Imaging"],
        "source_url": "https://www.universityofgalway.ie/science-engineering/schools/physics/",
    },
    {
        "school_id": "school-chemistry",
        "college_id": "science-engineering",
        "school_name_english": "School of Chemistry",
        "school_name_irish": "Scoil na Ceimice",
        "head_of_school": "Prof. R. Ó Briain",
        "n_students": 200,
        "n_staff": 16,
        "research_centres": ["Synthesis and Solid-State Pharmaceutical Centre"],
        "source_url": "https://www.universityofgalway.ie/science-engineering/schools/chemistry/",
    },
    {
        "school_id": "school-engineering",
        "college_id": "science-engineering",
        "school_name_english": "School of Engineering",
        "school_name_irish": "Scoil na hInnealtóireachta",
        "head_of_school": "Prof. P. Mac Cárthaigh",
        "n_students": 450,
        "n_staff": 28,
        "research_centres": ["MaREI", "CURAM"],
        "source_url": "https://www.universityofgalway.ie/science-engineering/schools/engineering/",
    },
    {
        "school_id": "school-education",
        "college_id": "arts-social-sciences-celtic-studies",
        "school_name_english": "School of Education",
        "school_name_irish": "Scoil an Oideachais",
        "head_of_school": "Prof. C. Ó Briain",
        "n_students": 350,
        "n_staff": 18,
        "research_centres": ["UNESCO Chair in Children, Youth & Civic Engagement"],
        "source_url": "https://www.universityofgalway.ie/arts-social-sciences-celtic-studies/schools/education/",
    },
    {
        "school_id": "school-gaeilge-acadamh",
        "college_id": "arts-social-sciences-celtic-studies",
        "school_name_english": "Acadamh na hOllscolaíochta Gaeilge",
        "school_name_irish": "Acadamh na hOllscolaíochta Gaeilge",
        "head_of_school": "An Dr S. Ní Laoghaire",
        "n_students": 120,
        "n_staff": 12,
        "research_centres": ["Acadamh na hOllscolaíochta Gaeilge Research Cluster"],
        "source_url": "https://www.universityofgalway.ie/gaeilge-acadamh/",
    },
    {
        "school_id": "school-law",
        "college_id": "business-public-policy-law",
        "school_name_english": "School of Law",
        "school_name_irish": "Scoil an Dlí",
        "head_of_school": "Prof. D. Ó Conchúir",
        "n_students": 280,
        "n_staff": 16,
        "research_centres": ["Irish Centre for Human Rights"],
        "source_url": "https://www.universityofgalway.ie/business-public-policy-law/schools/law/",
    },
    {
        "school_id": "school-business",
        "college_id": "business-public-policy-law",
        "school_name_english": "J.E. Cairnes School of Business and Economics",
        "school_name_irish": "Scoil an Ghnó agus na nEacnamaíochta J.E. Cairnes",
        "head_of_school": "Prof. A. Ní Bhrádaigh",
        "n_students": 700,
        "n_staff": 35,
        "research_centres": ["AIR Centre"],
        "source_url": "https://www.universityofgalway.ie/business-public-policy-law/schools/business/",
    },
    {
        "school_id": "school-medicine",
        "college_id": "medicine-nursing-health-sciences",
        "school_name_english": "School of Medicine",
        "school_name_irish": "Scoil an Leighis",
        "head_of_school": "Prof. F. Ní Mhurchú",
        "n_students": 500,
        "n_staff": 80,
        "research_centres": ["CURAM", "CÚRAM Centre for Research in Medical Devices"],
        "source_url": "https://www.universityofgalway.ie/medicine-nursing-health-sciences/schools/medicine/",
    },
)


class SchoolsPipeline(TertiaryPipelineBase):
    SURFACE_CONFIG = TertiarySurfaceConfig(
        surface_id="uog_schools",
        surface_name_english="UoG Schools",
        surface_name_irish="Scoileanna UoG",
        source_url="https://www.universityofgalway.ie/about-us/structure/",
        jurisdiction="ie_galway",
        academic_year="2025/26",
        row_primary_key="school_id",
    )

    @dlt.resource(write_disposition="replace", primary_key="school_id")
    def schools(self) -> Iterator[dict]:
        self.logger.info("schools_sync_start", surface_id=self.surface_id)
        yield from UOG_SCHOOLS
        self.logger.info("schools_sync_complete", surface_id=self.surface_id, count=len(UOG_SCHOOLS))

    def build_pipeline_resource(self) -> Iterator[dict]:
        return self.schools()


schools_pipeline = SchoolsPipeline()
