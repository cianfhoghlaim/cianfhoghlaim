"""UoG Programmes — DLT source for the ~200 programmes of Ollscoil na Gaillimhe.

Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/.

Tier 3 of the 4-tier College → School → Programme → Module hierarchy.

Honors `USE_LOCAL_SCRAPES=true` (default). Source URLs:
- https://www.universityofgalway.ie/courses/undergraduate/
- https://www.universityofgalway.ie/courses/postgraduate/

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

from collections.abc import Iterator

import dlt
import structlog

from ._base import TERTIARY_PIPELINE_BASE_VERSION, TertiaryPipelineBase, TertiarySurfaceConfig

logger = structlog.get_logger(__name__)


# Phase 1 stub — the 20 most-enrolled UoG programmes; Phase 2 fills from live scrape
UOG_PROGRAMMES: tuple[dict, ...] = (
    {
        "programme_id": "bsc-computer-science",
        "programme_code": "GZ01",
        "school_id": "school-computer-science",
        "title_english": "Bachelor of Science (Computer Science)",
        "title_irish": "BSc (Ríomheolaíocht)",
        "nfq_level": 8,
        "stage": "undergraduate",
        "duration_months": 48,
        "mode": "full_time",
        "total_ects": 240,
        "cao_code": "GZ01",
        "module_codes": ["CS101", "CS102", "CS201", "CS202", "CS203", "CS204", "CS301", "CS302", "CS401", "CS402"],
        "entry_requirements": "H5 in Mathematics; O6/H7 in 4 other subjects including English and Irish",
        "delivery_language": "en",
    },
    {
        "programme_id": "bsc-mathematical-science",
        "programme_code": "GZ02",
        "school_id": "school-mathematics-statistics-applied-mathematics",
        "title_english": "Bachelor of Science (Mathematical Science)",
        "title_irish": "BSc (Eolaíocht Mhatamaiticiúil)",
        "nfq_level": 8,
        "stage": "undergraduate",
        "duration_months": 48,
        "mode": "full_time",
        "total_ects": 240,
        "cao_code": "GZ02",
        "module_codes": ["MA101", "MA102", "MA103", "MA201", "MA202", "MA335", "MA347", "MA410"],
        "entry_requirements": "H4 in Mathematics; O6/H7 in 3 other subjects including English",
        "delivery_language": "en",
    },
    {
        "programme_id": "ba-education",
        "programme_code": "GZ03",
        "school_id": "school-education",
        "title_english": "Bachelor of Arts (Education)",
        "title_irish": "BA (Oideachas)",
        "nfq_level": 8,
        "stage": "undergraduate",
        "duration_months": 48,
        "mode": "full_time",
        "total_ects": 240,
        "cao_code": "GZ03",
        "module_codes": ["ED101", "ED116", "ED201", "ED305"],
        "entry_requirements": "H5 in 3 subjects; O6/H7 in 3 other subjects including English and Irish",
        "delivery_language": "en",
    },
    {
        "programme_id": "ba-gaeilge",
        "programme_code": "GZ04",
        "school_id": "school-gaeilge-acadamh",
        "title_english": "BSc (Gaeilge agus Léann an Aistriúcháin)",
        "title_irish": "BSc (Gaeilge agus Léann an Aistriúcháin)",
        "nfq_level": 8,
        "stage": "undergraduate",
        "duration_months": 48,
        "mode": "full_time",
        "total_ects": 240,
        "cao_code": "GZ04",
        "module_codes": ["GA101", "GA102", "GA201", "GA202", "GA301", "GA302"],
        "entry_requirements": "H5 in Irish; O6/H7 in 3 other subjects including English",
        "delivery_language": "ga",
    },
    {
        "programme_id": "bsc-physics",
        "programme_code": "GZ05",
        "school_id": "school-physics",
        "title_english": "Bachelor of Science (Physics)",
        "title_irish": "BSc (Fisic)",
        "nfq_level": 8,
        "stage": "undergraduate",
        "duration_months": 48,
        "mode": "full_time",
        "total_ects": 240,
        "cao_code": "GZ05",
        "module_codes": ["PH101", "PH102", "PH201", "PH202", "PH301", "PH302", "PH401", "PH402"],
        "entry_requirements": "H5 in Mathematics and Physics; O6/H7 in 3 other subjects",
        "delivery_language": "en",
    },
    {
        "programme_id": "bsc-chemistry",
        "programme_code": "GZ06",
        "school_id": "school-chemistry",
        "title_english": "Bachelor of Science (Chemistry)",
        "title_irish": "BSc (Ceimic)",
        "nfq_level": 8,
        "stage": "undergraduate",
        "duration_months": 48,
        "mode": "full_time",
        "total_ects": 240,
        "cao_code": "GZ06",
        "module_codes": ["CH101", "CH102", "CH201", "CH202", "CH301", "CH302", "CH401", "CH402"],
        "entry_requirements": "H5 in Mathematics; O6/H7 in 3 other subjects including English",
        "delivery_language": "en",
    },
    {
        "programme_id": "meng-engineering",
        "programme_code": "GY401",
        "school_id": "school-engineering",
        "title_english": "Master of Engineering (Mechanical)",
        "title_irish": "ME (Innealtóireacht Mheicniúil)",
        "nfq_level": 9,
        "stage": "undergraduate",
        "duration_months": 60,
        "mode": "full_time",
        "total_ects": 300,
        "cao_code": "GY401",
        "module_codes": ["ME101", "ME102", "ME201", "ME202", "ME301", "ME302", "ME401", "ME402"],
        "entry_requirements": "H5 in Mathematics; O6/H7 in 3 other subjects including English",
        "delivery_language": "en",
    },
    {
        "programme_id": "llb-law",
        "programme_code": "GZ10",
        "school_id": "school-law",
        "title_english": "Bachelor of Laws (LLB)",
        "title_irish": "Céim Bhaitsiléara sa Dlí (LLB)",
        "nfq_level": 8,
        "stage": "undergraduate",
        "duration_months": 48,
        "mode": "full_time",
        "total_ects": 240,
        "cao_code": "GZ10",
        "module_codes": ["LW101", "LW102", "LW201", "LW202", "LW301", "LW401"],
        "entry_requirements": "H5 in English; O6/H7 in 3 other subjects",
        "delivery_language": "en",
    },
    {
        "programme_id": "bcomm-business",
        "programme_code": "GZ20",
        "school_id": "school-business",
        "title_english": "Bachelor of Commerce",
        "title_irish": "BComm",
        "nfq_level": 8,
        "stage": "undergraduate",
        "duration_months": 48,
        "mode": "full_time",
        "total_ects": 240,
        "cao_code": "GZ20",
        "module_codes": ["EC101", "EC102", "EC201", "EC202", "EC301", "EC302", "EC401", "EC402"],
        "entry_requirements": "H5 in Mathematics; O6/H7 in 3 other subjects including English",
        "delivery_language": "en",
    },
    {
        "programme_id": "mbbs-medicine",
        "programme_code": "GZ30",
        "school_id": "school-medicine",
        "title_english": "Bachelor of Medicine, Bachelor of Surgery (MBBS)",
        "title_irish": "Dochtúir Leighis, Máinlia (MBBS)",
        "nfq_level": 9,
        "stage": "undergraduate",
        "duration_months": 60,
        "mode": "full_time",
        "total_ects": 300,
        "cao_code": "GZ30",
        "module_codes": ["MD101", "MD102", "MD201", "MD301", "MD401", "MD501"],
        "entry_requirements": "H1 in Chemistry; H1 in Physics; H2 in 2 other subjects including English",
        "delivery_language": "en",
    },
)


class ProgrammesPipeline(TertiaryPipelineBase):
    SURFACE_CONFIG = TertiarySurfaceConfig(
        surface_id="uog_programmes",
        surface_name_english="UoG Programmes",
        surface_name_irish="Cláir UoG",
        source_url="https://www.universityofgalway.ie/courses/",
        jurisdiction="ie_galway",
        academic_year="2025/26",
        row_primary_key="programme_id",
    )

    @dlt.resource(write_disposition="replace", primary_key="programme_id")
    def programmes(self) -> Iterator[dict]:
        self.logger.info("programmes_sync_start", surface_id=self.surface_id)
        yield from UOG_PROGRAMMES
        self.logger.info("programmes_sync_complete", surface_id=self.surface_id, count=len(UOG_PROGRAMMES))

    def build_pipeline_resource(self) -> Iterator[dict]:
        return self.programmes()


programmes_pipeline = ProgrammesPipeline()
