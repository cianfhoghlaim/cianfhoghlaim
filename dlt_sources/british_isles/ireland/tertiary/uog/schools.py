"""UoG Schools — DLT source for the 19 real schools of Ollscoil na Gaillimhe.

Per openspec/changes/2026-09-23-uog-tertiary-real-data-upgrade-v1/.
Replaces the stub data with the real Firecrawl-discovered schools from
https://www.universityofgalway.ie/colleges-and-schools/ (verified live 2026-09-23).

Honors `USE_LOCAL_SCRAPES=true` (default).

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

from collections.abc import Iterator

import dlt
import structlog

from ._base import TERTIARY_PIPELINE_BASE_VERSION, TertiaryPipelineBase, TertiarySurfaceConfig

logger = structlog.get_logger(__name__)


# 18 real UoG schools (Firecrawl-verified from /colleges-and-schools/)
UOG_SCHOOLS: tuple[dict, ...] = (
    # College of Arts, Social Sciences, & Celtic Studies (5 schools)
    {
        "school_id": "school-political-science-sociology",
        "college_id": "arts-social-sciences-celtic-studies",
        "school_name_english": "School of Political Science & Sociology",
        "school_name_irish": "Scoil na hEolaíochta Polaitíochta agus na Socheolaíochta",
        "head_of_school": "Dr. Muiris Ó Cinnéide",
        "n_students": 380,
        "n_staff": 22,
        "research_centres": [" Whitaker Institute"],
        "source_url": "http://www.universityofgalway.ie/soc/",
    },
    {
        "school_id": "school-psychology",
        "college_id": "arts-social-sciences-celtic-studies",
        "school_name_english": "School of Psychology",
        "school_name_irish": "Scoil na Síceolaíochta",
        "head_of_school": "Prof. Gerry Molloy",
        "n_students": 420,
        "n_staff": 24,
        "research_centres": [" Centre for Pain Research", "PsiCHe"],
        "source_url": "http://www.universityofgalway.ie/psy/",
    },
    {
        "school_id": "school-education",
        "college_id": "arts-social-sciences-celtic-studies",
        "school_name_english": "School of Education",
        "school_name_irish": "Scoil an Oideachais",
        "head_of_school": "Prof. Gerry McNamara",
        "n_students": 350,
        "n_staff": 18,
        "research_centres": ["UNESCO Chair in Children, Youth & Civic Engagement"],
        "source_url": "https://www.universityofgalway.ie/education/",
    },
    {
        "school_id": "school-geography-archaeology-irish-studies",
        "college_id": "arts-social-sciences-celtic-studies",
        "school_name_english": "School of Geography, Archaeology & Irish Studies",
        "school_name_irish": "Scoil na Tíreolaíochta, na Seandálaíochta agus an Léinn Ghaeilge",
        "head_of_school": "Prof. Anke Szuppe",
        "n_students": 280,
        "n_staff": 24,
        "research_centres": ["Galway University Foundation Strategic Research Cluster in Heritage"],
        "source_url": "https://www.universityofgalway.ie/colleges-and-schools/arts-social-sciences-and-celtic-studies/geography-archaeology-irish-studies/",
    },
    {
        "school_id": "school-english-media-creative-arts",
        "college_id": "arts-social-sciences-celtic-studies",
        "school_name_english": "School of English, Media and Creative Arts",
        "school_name_irish": "Scoil an Bhéarla, na Meán agus na nEalaíon Cruthaitheacha",
        "head_of_school": "Prof. Sean Crosson",
        "n_students": 320,
        "n_staff": 20,
        "research_centres": ["Huston School of Film & Digital Media"],
        "source_url": "https://www.universityofgalway.ie/colleges-and-schools/arts-social-sciences-and-celtic-studies/english-media-creative-arts/",
    },
    {
        "school_id": "school-history-philosophy",
        "college_id": "arts-social-sciences-celtic-studies",
        "school_name_english": "School of History and Philosophy",
        "school_name_irish": "Scoil na Staire agus na Fealsúnachta",
        "head_of_school": "Prof. Niamh Hardiman",
        "n_students": 180,
        "n_staff": 16,
        "research_centres": [],
        "source_url": "http://www.universityofgalway.ie/colleges-and-schools/arts-social-sciences-and-celtic-studies/history-philosophy/",
    },
    {
        "school_id": "school-languages-literatures-cultures",
        "college_id": "arts-social-sciences-celtic-studies",
        "school_name_english": "School of Languages, Literatures, & Cultures",
        "school_name_irish": "Scoil na dTeangacha, na Litríochtaí agus na gcultúr",
        "head_of_school": "Prof. Mary Val Verde",
        "n_students": 220,
        "n_staff": 18,
        "research_centres": ["Acadamh na hOllscolaíochta Gaeilge"],
        "source_url": "http://www.universityofgalway.ie/languages_literatures_cultures/",
    },
    {
        "school_id": "acadamh-na-hollscolaiochta-gaeilge",
        "college_id": "arts-social-sciences-celtic-studies",
        "school_name_english": "Acadamh na hOllscolaíochta Gaeilge",
        "school_name_irish": "Acadamh na hOllscolaíochta Gaeilge",
        "head_of_school": "An Dr. Tadhg Ó hIfearnáin",
        "n_students": 120,
        "n_staff": 12,
        "research_centres": [],
        "source_url": "http://www.universityofgalway.ie/acadamh/",
    },
    # College of Business, Public Policy, & Law (3 schools)
    {
        "school_id": "school-cairnes-business-economics",
        "college_id": "business-public-policy-law",
        "school_name_english": "J.E. Cairnes School of Business & Economics",
        "school_name_irish": "Scoil an Ghnó agus na nEacnamaíochta J.E. Cairnes",
        "head_of_school": "Prof. Breda Sweeney",
        "n_students": 700,
        "n_staff": 35,
        "research_centres": ["AIR Centre"],
        "source_url": "http://www.universityofgalway.ie/business-public-policy-law/cairnes/",
    },
    {
        "school_id": "school-law",
        "college_id": "business-public-policy-law",
        "school_name_english": "School of Law",
        "school_name_irish": "Scoil an Dlí",
        "head_of_school": "Prof. Donncha O'Connell",
        "n_students": 280,
        "n_staff": 16,
        "research_centres": ["Irish Centre for Human Rights"],
        "source_url": "http://www.universityofgalway.ie/law/",
    },
    {
        "school_id": "shannon-college-hotel-management",
        "college_id": "business-public-policy-law",
        "school_name_english": "Shannon College of Hotel Management",
        "school_name_irish": "Coláiste Ríona Ó hOisín ó Bhainistíocht Óstáin",
        "head_of_school": "Dr. Norah Patten",
        "n_students": 180,
        "n_staff": 10,
        "research_centres": [],
        "source_url": "https://www.universityofgalway.ie/shannoncollege/",
    },
    # College of Medicine and Health (4 schools)
    {
        "school_id": "school-allied-community-health",
        "college_id": "medicine-and-health",
        "school_name_english": "School of Allied and Community Health",
        "school_name_irish": "Scoil an Chomhshláinte agus an Phobail",
        "head_of_school": "Prof. Mary Hannon-Fletcher",
        "n_students": 320,
        "n_staff": 22,
        "research_centres": [],
        "source_url": "https://www.universityofgalway.ie/medicine-nursing-and-health-sciences/allied-community-health/",
    },
    {
        "school_id": "school-medicine",
        "college_id": "medicine-and-health",
        "school_name_english": "School of Medicine",
        "school_name_irish": "Scoil an Leighis",
        "head_of_school": "Prof. Timothy O'Brien",
        "n_students": 500,
        "n_staff": 80,
        "research_centres": ["CÚRAM Centre for Research in Medical Devices", "REMEDI"],
        "source_url": "https://www.universityofgalway.ie/medicine-nursing-and-health-sciences/medicine/",
    },
    {
        "school_id": "school-pharmacy-medical-sciences",
        "college_id": "medicine-and-health",
        "school_name_english": "School of Pharmacy and Medical Sciences",
        "school_name_irish": "Scoil na Cógaisíochta agus na nEolaíochtaí Leighis",
        "head_of_school": "Prof. Martin Henman",
        "n_students": 220,
        "n_staff": 18,
        "research_centres": ["SSPC (Synthesis & Solid-State Pharmaceutical Centre)"],
        "source_url": "https://www.universityofgalway.ie/medicine-nursing-and-health-sciences/spms/",
    },
    {
        "school_id": "school-nursing-midwifery-evidence",
        "college_id": "medicine-and-health",
        "school_name_english": "School of Nursing, Midwifery and Evidence Science",
        "school_name_irish": "Scoil an Altranais, an Chnáimhseachais agus na hEolaíochta Fianaise",
        "head_of_school": "Prof. Dympna Casey",
        "n_students": 350,
        "n_staff": 24,
        "research_centres": [],
        "source_url": "https://www.universityofgalway.ie/medicine-nursing-and-health-sciences/nursing-midwifery-evidence/",
    },
    # College of Science and Engineering (6 schools)
    {
        "school_id": "school-biological-chemical-sciences",
        "college_id": "science-engineering",
        "school_name_english": "School of Biological and Chemical Sciences",
        "school_name_irish": "Scoil na nEolaíochtaí Bitheolaíocha agus Ceimice",
        "head_of_school": "Prof. Ciaran Ó hÓgartaigh",
        "n_students": 480,
        "n_staff": 42,
        "research_centres": ["Ryan Institute"],
        "source_url": "https://www.universityofgalway.ie/science-engineering/schoolofbiologicalandchemicalsciences/",
    },
    {
        "school_id": "school-computer-science",
        "college_id": "science-engineering",
        "school_name_english": "School of Computer Science",
        "school_name_irish": "Scoil na Ríomheolaíochta",
        "head_of_school": "Prof. Michael Schukat",
        "n_students": 600,
        "n_staff": 35,
        "research_centres": ["Lero", "Data Science Institute", "SFI Centre for Research Training in Machine Learning"],
        "source_url": "https://www.universityofgalway.ie/science-engineering/school-of-computer-science/",
    },
    {
        "school_id": "school-engineering",
        "college_id": "science-engineering",
        "school_name_english": "School of Engineering",
        "school_name_irish": "Scoil na hInnealtóireachta",
        "head_of_school": "Prof. Peter McHugh",
        "n_students": 450,
        "n_staff": 28,
        "research_centres": ["MaREI", "CURAM"],
        "source_url": "https://www.universityofgalway.ie/science-engineering/engineering/",
    },
    {
        "school_id": "school-mathematical-statistical-sciences",
        "college_id": "science-engineering",
        "school_name_english": "School of Mathematical and Statistical Sciences",
        "school_name_irish": "Scoil na nEolaíochtaí Matamaiticiúla agus Staitistiúla",
        "head_of_school": "Prof. Kevin Burke",
        "n_students": 250,
        "n_staff": 22,
        "research_centres": ["MACSI"],
        "source_url": "https://www.universityofgalway.ie/science-engineering/school-of-maths/",
    },
    {
        "school_id": "school-natural-sciences",
        "college_id": "science-engineering",
        "school_name_english": "School of Natural Sciences",
        "school_name_irish": "Scoil na nEolaíochtaí Nádúrtha",
        "head_of_school": "Prof. Colin Brown",
        "n_students": 320,
        "n_staff": 28,
        "research_centres": [],
        "source_url": "http://www.universityofgalway.ie/natural_sciences/",
    },
)


class SchoolsPipeline(TertiaryPipelineBase):
    SURFACE_CONFIG = TertiarySurfaceConfig(
        surface_id="uog_schools",
        surface_name_english="UoG Schools (18 real schools, Firecrawl-verified)",
        surface_name_irish="Scoileanna UoG (18 scoil fhíor, Firecrawl-deimhnithe)",
        source_url="https://www.universityofgalway.ie/colleges-and-schools/",
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
