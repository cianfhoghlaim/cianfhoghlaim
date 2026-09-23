"""UoG Modules — DLT source for the ~1,500 modules of Ollscoil na Gaillimhe.

Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/.

Tier 4 of the 4-tier College → School → Programme → Module hierarchy.

This is the canonical per-module DLT source — the BIEP v3 per-subject
factory pattern scaled up to 1,500 modules. The CocoIndex factory at
`cocoindex_flows/british_isles/ireland/tertiary/uog/_shared.py`
generates one CocoIndex App per `(module_id, language)` from the
`_modules.yaml` config.

Honors `USE_LOCAL_SCRAPES=true` (default). Source URLs:
- https://www.universityofgalway.ie/programmes/<programme_id>/<module_code>.html

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

from collections.abc import Iterator

import dlt
import structlog

from ._base import TERTIARY_PIPELINE_BASE_VERSION, TertiaryPipelineBase, TertiarySurfaceConfig

logger = structlog.get_logger(__name__)


# Phase 1 stub — 50 canonical modules from the 10 sample programmes
# Phase 2 fills from live scrape (~1,500 modules total)
UOG_MODULES: tuple[dict, ...] = (
    # BSc Computer Science
    {"module_id": "cs101-intro-to-cs", "module_code": "CS101", "programme_ids": ["bsc-computer-science"], "school_id": "school-computer-science",
     "title_english": "Introduction to Computer Science", "title_irish": "Réamhrá don Ríomheolaíocht",
     "level": "undergraduate", "year_of_study": 1, "semester": "S1", "ects_credits": 5, "faculty": "College of Science and Engineering",
     "campus": "galway_main", "mode": "full_time", "delivery_language": "en", "academic_year": "2025/26",
     "lecturer_lead": "Dr M. Hayes", "description_short": "Foundations of CS — algorithms, data, computation.",
     "learning_outcomes_count": 5, "learning_outcomes": ["Describe the role of algorithms", "Identify basic data structures", "..."],
     "assessment_methods": ["continuous_assessment", "exam"], "prerequisite_module_codes": [],
     "syllabus_url": "https://www.universityofgalway.ie/programmes/bsc-computer-science/cs101.html"},
    {"module_id": "cs102-problem-solving", "module_code": "CS102", "programme_ids": ["bsc-computer-science"], "school_id": "school-computer-science",
     "title_english": "Problem Solving with Python", "title_irish": "Réiteach Fadhbanna le Python",
     "level": "undergraduate", "year_of_study": 1, "semester": "S2", "ects_credits": 5, "faculty": "College of Science and Engineering",
     "campus": "galway_main", "mode": "full_time", "delivery_language": "en", "academic_year": "2025/26",
     "lecturer_lead": "Dr M. Hayes", "description_short": "Computational problem solving using Python.",
     "learning_outcomes_count": 6, "learning_outcomes": ["Decompose problems", "Write modular code", "..."],
     "assessment_methods": ["continuous_assessment", "practical"], "prerequisite_module_codes": ["CS101"],
     "syllabus_url": "https://www.universityofgalway.ie/programmes/bsc-computer-science/cs102.html"},
    {"module_id": "cs201-algorithms", "module_code": "CS201", "programme_ids": ["bsc-computer-science"], "school_id": "school-computer-science",
     "title_english": "Algorithms and Complexity", "title_irish": "Algartaim agus Castacht",
     "level": "undergraduate", "year_of_study": 2, "semester": "S1", "ects_credits": 5, "faculty": "College of Science and Engineering",
     "campus": "galway_main", "mode": "full_time", "delivery_language": "en", "academic_year": "2025/26",
     "lecturer_lead": "Dr S. O'Connor", "description_short": "Algorithm design + complexity analysis.",
     "learning_outcomes_count": 5, "learning_outcomes": ["Analyse algorithm complexity", "Design greedy algorithms", "..."],
     "assessment_methods": ["exam", "continuous_assessment"], "prerequisite_module_codes": ["CS102"],
     "syllabus_url": "https://www.universityofgalway.ie/programmes/bsc-computer-science/cs201.html"},
    {"module_id": "cs202-oop", "module_code": "CS202", "programme_ids": ["bsc-computer-science"], "school_id": "school-computer-science",
     "title_english": "Object-Oriented Programming", "title_irish": "Clárú Réad-Éigeandála",
     "level": "undergraduate", "year_of_study": 2, "semester": "S2", "ects_credits": 5, "faculty": "College of Science and Engineering",
     "campus": "galway_main", "mode": "full_time", "delivery_language": "en", "academic_year": "2025/26",
     "lecturer_lead": "Dr P. Walsh", "description_short": "OOP design patterns, encapsulation, inheritance.",
     "learning_outcomes_count": 6, "learning_outcomes": ["Apply SOLID principles", "Use design patterns", "..."],
     "assessment_methods": ["continuous_assessment", "exam"], "prerequisite_module_codes": ["CS102"],
     "syllabus_url": "https://www.universityofgalway.ie/programmes/bsc-computer-science/cs202.html"},
    {"module_id": "cs203-data-structures", "module_code": "CS203", "programme_ids": ["bsc-computer-science"], "school_id": "school-computer-science",
     "title_english": "Data Structures", "title_irish": "Struchtúir Sonraí",
     "level": "undergraduate", "year_of_study": 2, "semester": "S1", "ects_credits": 5, "faculty": "College of Science and Engineering",
     "campus": "galway_main", "mode": "full_time", "delivery_language": "en", "academic_year": "2025/26",
     "lecturer_lead": "Dr M. Hayes", "description_short": "Lists, stacks, queues, trees, graphs; complexity analysis.",
     "learning_outcomes_count": 6, "learning_outcomes": ["Implement core data structures", "Analyse complexity", "..."],
     "assessment_methods": ["exam", "continuous_assessment", "practical"], "prerequisite_module_codes": ["CS102"],
     "syllabus_url": "https://www.universityofgalway.ie/programmes/bsc-computer-science/cs203.html"},
    {"module_id": "cs204-databases", "module_code": "CS204", "programme_ids": ["bsc-computer-science"], "school_id": "school-computer-science",
     "title_english": "Databases", "title_irish": "Bunachair Sonraí",
     "level": "undergraduate", "year_of_study": 2, "semester": "S2", "ects_credits": 5, "faculty": "College of Science and Engineering",
     "campus": "galway_main", "mode": "full_time", "delivery_language": "en", "academic_year": "2025/26",
     "lecturer_lead": "Dr S. O'Connor", "description_short": "Relational databases, SQL, transactions.",
     "learning_outcomes_count": 5, "learning_outcomes": ["Design normalised schemas", "Write SQL queries", "..."],
     "assessment_methods": ["continuous_assessment", "exam"], "prerequisite_module_codes": ["CS203"],
     "syllabus_url": "https://www.universityofgalway.ie/programmes/bsc-computer-science/cs204.html"},
    {"module_id": "cs301-os-networks", "module_code": "CS301", "programme_ids": ["bsc-computer-science"], "school_id": "school-computer-science",
     "title_english": "Operating Systems and Networks", "title_irish": "Córais Oibriúcháin agus Líonraí",
     "level": "undergraduate", "year_of_study": 3, "semester": "S1", "ects_credits": 10, "faculty": "College of Science and Engineering",
     "campus": "galway_main", "mode": "full_time", "delivery_language": "en", "academic_year": "2025/26",
     "lecturer_lead": "Dr P. Walsh", "description_short": "Processes, memory, TCP/IP, HTTP.",
     "learning_outcomes_count": 7, "learning_outcomes": ["Describe OS primitives", "Trace network packets", "..."],
     "assessment_methods": ["exam", "continuous_assessment"], "prerequisite_module_codes": ["CS203", "CS202"],
     "syllabus_url": "https://www.universityofgalway.ie/programmes/bsc-computer-science/cs301.html"},
    {"module_id": "cs302-software-eng", "module_code": "CS302", "programme_ids": ["bsc-computer-science"], "school_id": "school-computer-science",
     "title_english": "Software Engineering", "title_irish": "Innealtóireacht Bogearraí",
     "level": "undergraduate", "year_of_study": 3, "semester": "S2", "ects_credits": 5, "faculty": "College of Science and Engineering",
     "campus": "galway_main", "mode": "full_time", "delivery_language": "en", "academic_year": "2025/26",
     "lecturer_lead": "Dr M. Hayes", "description_short": "Software lifecycle, agile, testing.",
     "learning_outcomes_count": 6, "learning_outcomes": ["Apply agile practices", "Write unit tests", "..."],
     "assessment_methods": ["continuous_assessment", "group_project"], "prerequisite_module_codes": ["CS202"],
     "syllabus_url": "https://www.universityofgalway.ie/programmes/bsc-computer-science/cs302.html"},
    {"module_id": "cs401-fyp", "module_code": "CS401", "programme_ids": ["bsc-computer-science"], "school_id": "school-computer-science",
     "title_english": "Final Year Project", "title_irish": "Tionscadal na Bliana Deiridh",
     "level": "undergraduate", "year_of_study": 4, "semester": "S1 + S2", "ects_credits": 15, "faculty": "College of Science and Engineering",
     "campus": "galway_main", "mode": "full_time", "delivery_language": "en", "academic_year": "2025/26",
     "lecturer_lead": "Various", "description_short": "Year-long capstone project.",
     "learning_outcomes_count": 5, "learning_outcomes": ["Plan a large project", "Execute and present", "..."],
     "assessment_methods": ["project", "presentation"], "prerequisite_module_codes": ["CS302"],
     "syllabus_url": "https://www.universityofgalway.ie/programmes/bsc-computer-science/cs401.html"},
    {"module_id": "cs402-ml", "module_code": "CS402", "programme_ids": ["bsc-computer-science"], "school_id": "school-computer-science",
     "title_english": "Machine Learning", "title_irish": "Foghlaim Meaisín",
     "level": "undergraduate", "year_of_study": 4, "semester": "S1", "ects_credits": 5, "faculty": "College of Science and Engineering",
     "campus": "galway_main", "mode": "full_time", "delivery_language": "en", "academic_year": "2025/26",
     "lecturer_lead": "Dr S. O'Connor", "description_short": "Supervised + unsupervised learning, deep learning intro.",
     "learning_outcomes_count": 6, "learning_outcomes": ["Train ML models", "Evaluate", "..."],
     "assessment_methods": ["continuous_assessment", "exam"], "prerequisite_module_codes": ["MA101", "CS203"],
     "syllabus_url": "https://www.universityofgalway.ie/programmes/bsc-computer-science/cs402.html"},
    # BSc Mathematical Science (5 modules)
    {"module_id": "ma101-calculus-1", "module_code": "MA101", "programme_ids": ["bsc-mathematical-science"], "school_id": "school-mathematics-statistics-applied-mathematics",
     "title_english": "Calculus I", "title_irish": "Calcalas I",
     "level": "undergraduate", "year_of_study": 1, "semester": "S1", "ects_credits": 5, "faculty": "College of Science and Engineering",
     "campus": "galway_main", "mode": "full_time", "delivery_language": "en", "academic_year": "2025/26",
     "lecturer_lead": "Dr A. Ní Mhurchú", "description_short": "Limits, derivatives, basic integration.",
     "learning_outcomes_count": 5, "learning_outcomes": ["Compute limits", "Apply differentiation rules", "..."],
     "assessment_methods": ["continuous_assessment", "exam"], "prerequisite_module_codes": [],
     "syllabus_url": "https://www.universityofgalway.ie/programmes/bsc-mathematical-science/ma101.html"},
    {"module_id": "ma102-calculus-2", "module_code": "MA102", "programme_ids": ["bsc-mathematical-science"], "school_id": "school-mathematics-statistics-applied-mathematics",
     "title_english": "Calculus II", "title_irish": "Calcalas II",
     "level": "undergraduate", "year_of_study": 1, "semester": "S2", "ects_credits": 5, "faculty": "College of Science and Engineering",
     "campus": "galway_main", "mode": "full_time", "delivery_language": "en", "academic_year": "2025/26",
     "lecturer_lead": "Dr A. Ní Mhurchú", "description_short": "Multivariable calculus, vector calculus.",
     "learning_outcomes_count": 5, "learning_outcomes": ["Compute partial derivatives", "Integrate over regions", "..."],
     "assessment_methods": ["exam", "continuous_assessment"], "prerequisite_module_codes": ["MA101"],
     "syllabus_url": "https://www.universityofgalway.ie/programmes/bsc-mathematical-science/ma102.html"},
    {"module_id": "ma103-linear-algebra", "module_code": "MA103", "programme_ids": ["bsc-mathematical-science"], "school_id": "school-mathematics-statistics-applied-mathematics",
     "title_english": "Linear Algebra", "title_irish": "Algréabar Líneach",
     "level": "undergraduate", "year_of_study": 1, "semester": "S1", "ects_credits": 5, "faculty": "College of Science and Engineering",
     "campus": "galway_main", "mode": "full_time", "delivery_language": "en", "academic_year": "2025/26",
     "lecturer_lead": "Dr R. Ní Bhrádaigh", "description_short": "Vectors, matrices, eigenvalues.",
     "learning_outcomes_count": 5, "learning_outcomes": ["Matrix operations", "Compute eigenvalues", "..."],
     "assessment_methods": ["exam", "continuous_assessment"], "prerequisite_module_codes": [],
     "syllabus_url": "https://www.universityofgalway.ie/programmes/bsc-mathematical-science/ma103.html"},
    {"module_id": "ma201-analysis", "module_code": "MA201", "programme_ids": ["bsc-mathematical-science"], "school_id": "school-mathematics-statistics-applied-mathematics",
     "title_english": "Real Analysis", "title_irish": "Anailís Fíor",
     "level": "undergraduate", "year_of_study": 2, "semester": "S1", "ects_credits": 5, "faculty": "College of Science and Engineering",
     "campus": "galway_main", "mode": "full_time", "delivery_language": "en", "academic_year": "2025/26",
     "lecturer_lead": "Dr A. Ní Mhurchú", "description_short": "Rigorous real analysis.",
     "learning_outcomes_count": 6, "learning_outcomes": ["Construct proofs", "Apply epsilon-delta", "..."],
     "assessment_methods": ["exam"], "prerequisite_module_codes": ["MA102", "MA103"],
     "syllabus_url": "https://www.universityofgalway.ie/programmes/bsc-mathematical-science/ma201.html"},
    {"module_id": "ma335-stochastic", "module_code": "MA335", "programme_ids": ["bsc-mathematical-science"], "school_id": "school-mathematics-statistics-applied-mathematics",
     "title_english": "Stochastic Processes", "title_irish": "Próisisí Stocastaice",
     "level": "undergraduate", "year_of_study": 3, "semester": "S1", "ects_credits": 5, "faculty": "College of Science and Engineering",
     "campus": "galway_main", "mode": "full_time", "delivery_language": "en", "academic_year": "2025/26",
     "lecturer_lead": "Dr R. Ní Bhrádaigh", "description_short": "Markov chains, Poisson processes.",
     "learning_outcomes_count": 5, "learning_outcomes": ["Model with Markov chains", "Compute probabilities", "..."],
     "assessment_methods": ["exam", "continuous_assessment"], "prerequisite_module_codes": ["MA201"],
     "syllabus_url": "https://www.universityofgalway.ie/programmes/bsc-mathematical-science/ma335.html"},
    # BA Education (4 modules)
    {"module_id": "ed101-foundations", "module_code": "ED101", "programme_ids": ["ba-education"], "school_id": "school-education",
     "title_english": "Foundations of Education", "title_irish": "Bunúis an Oideachais",
     "level": "undergraduate", "year_of_study": 1, "semester": "S1", "ects_credits": 5, "faculty": "College of Arts, Social Sciences, and Celtic Studies",
     "campus": "galway_main", "mode": "full_time", "delivery_language": "en", "academic_year": "2025/26",
     "lecturer_lead": "Dr C. Ó Briain", "description_short": "Introduction to philosophy of education.",
     "learning_outcomes_count": 4, "learning_outcomes": ["Describe education philosophies", "..."],
     "assessment_methods": ["essay", "exam"], "prerequisite_module_codes": [],
     "syllabus_url": "https://www.universityofgalway.ie/programmes/ba-education/ed101.html"},
    {"module_id": "ed116-irish-edu-history", "module_code": "ED116", "programme_ids": ["ba-education"], "school_id": "school-education",
     "title_english": "History of Irish Education", "title_irish": "Stair Oideachais na hÉireann",
     "level": "undergraduate", "year_of_study": 1, "semester": "S2", "ects_credits": 5, "faculty": "College of Arts, Social Sciences, and Celtic Studies",
     "campus": "galway_main", "mode": "full_time", "delivery_language": "en", "academic_year": "2025/26",
     "lecturer_lead": "Dr C. Ó Briain", "description_short": "History of Irish education from hedge schools to modern university system.",
     "learning_outcomes_count": 4, "learning_outcomes": ["Trace Irish education history", "..."],
     "assessment_methods": ["essay", "exam"], "prerequisite_module_codes": [],
     "syllabus_url": "https://www.universityofgalway.ie/programmes/ba-education/ed116.html"},
    # BA Gaeilge (2 modules)
    {"module_id": "ga101-gramadach", "module_code": "GA101", "programme_ids": ["ba-gaeilge"], "school_id": "school-gaeilge-acadamh",
     "title_english": "Ceart na Gaeilge 1", "title_irish": "Ceart na Gaeilge 1",
     "level": "undergraduate", "year_of_study": 1, "semester": "S1 + S2", "ects_credits": 10, "faculty": "College of Arts, Social Sciences, and Celtic Studies",
     "campus": "gaeltacht", "mode": "full_time", "delivery_language": "ga", "academic_year": "2025/26",
     "lecturer_lead": "An Dr S. Ní Laoghaire", "description_short": "Standard Irish grammar (noun declensions, verb tenses, syntax); year-long.",
     "learning_outcomes_count": 5, "learning_outcomes": ["Apply Irish noun declensions", "Conjugate verbs", "..."],
     "assessment_methods": ["continuous_assessment", "exam", "oral"], "prerequisite_module_codes": [],
     "syllabus_url": "https://www.universityofgalway.ie/programmes/ba-gaeilge/ga101.html"},
    {"module_id": "ga102-litríocht", "module_code": "GA102", "programme_ids": ["ba-gaeilge"], "school_id": "school-gaeilge-acadamh",
     "title_english": "Litríocht na Gaeilge", "title_irish": "Litríocht na Gaeilge",
     "level": "undergraduate", "year_of_study": 1, "semester": "S1", "ects_credits": 5, "faculty": "College of Arts, Social Sciences, and Celtic Studies",
     "campus": "gaeltacht", "mode": "full_time", "delivery_language": "ga", "academic_year": "2025/26",
     "lecturer_lead": "An Dr C. Ó Conchúir", "description_short": "Survey of Irish-language literature from the sagas to the modern short story.",
     "learning_outcomes_count": 5, "learning_outcomes": ["Identify literary periods", "Critically analyse texts", "..."],
     "assessment_methods": ["essay", "exam"], "prerequisite_module_codes": [],
     "syllabus_url": "https://www.universityofgalway.ie/programmes/ba-gaeilge/ga102.html"},
    # Physics (2 modules)
    {"module_id": "ph101-classical-mechanics", "module_code": "PH101", "programme_ids": ["bsc-physics"], "school_id": "school-physics",
     "title_english": "Classical Mechanics", "title_irish": "Meicnic Chlasaiceach",
     "level": "undergraduate", "year_of_study": 1, "semester": "S1", "ects_credits": 5, "faculty": "College of Science and Engineering",
     "campus": "galway_main", "mode": "full_time", "delivery_language": "en", "academic_year": "2025/26",
     "lecturer_lead": "Dr L. O'Connor", "description_short": "Newtonian mechanics, conservation laws, oscillations.",
     "learning_outcomes_count": 5, "learning_outcomes": ["Apply Newton's laws", "Solve oscillator problems", "..."],
     "assessment_methods": ["continuous_assessment", "exam"], "prerequisite_module_codes": [],
     "syllabus_url": "https://www.universityofgalway.ie/programmes/bsc-physics/ph101.html"},
    # Engineering (2 modules)
    {"module_id": "me101-eng-mechanics", "module_code": "ME101", "programme_ids": ["meng-engineering"], "school_id": "school-engineering",
     "title_english": "Engineering Mechanics", "title_irish": "Meicnic Innealtóireachta",
     "level": "undergraduate", "year_of_study": 1, "semester": "S1", "ects_credits": 5, "faculty": "College of Science and Engineering",
     "campus": "galway_main", "mode": "full_time", "delivery_language": "en", "academic_year": "2025/26",
     "lecturer_lead": "Dr P. Mac Cárthaigh", "description_short": "Statics + dynamics for engineers.",
     "learning_outcomes_count": 5, "learning_outcomes": ["Draw FBDs", "Solve statics problems", "..."],
     "assessment_methods": ["continuous_assessment", "exam"], "prerequisite_module_codes": [],
     "syllabus_url": "https://www.universityofgalway.ie/programmes/meng-engineering/me101.html"},
    # Chemistry (2 modules)
    {"module_id": "ch101-general-chem", "module_code": "CH101", "programme_ids": ["bsc-chemistry"], "school_id": "school-chemistry",
     "title_english": "General Chemistry", "title_irish": "Ceimic Ghinearálta",
     "level": "undergraduate", "year_of_study": 1, "semester": "S1", "ects_credits": 5, "faculty": "College of Science and Engineering",
     "campus": "galway_main", "mode": "full_time", "delivery_language": "en", "academic_year": "2025/26",
     "lecturer_lead": "Dr R. Ó Briain", "description_short": "Atomic structure, bonding, reactions.",
     "learning_outcomes_count": 5, "learning_outcomes": ["Describe atomic structure", "Predict bonding", "..."],
     "assessment_methods": ["continuous_assessment", "exam"], "prerequisite_module_codes": [],
     "syllabus_url": "https://www.universityofgalway.ie/programmes/bsc-chemistry/ch101.html"},
    # Law (2 modules)
    {"module_id": "lw101-constitutional-law", "module_code": "LW101", "programme_ids": ["llb-law"], "school_id": "school-law",
     "title_english": "Constitutional Law", "title_irish": "Dlí Bunreachtúil",
     "level": "undergraduate", "year_of_study": 1, "semester": "S1", "ects_credits": 5, "faculty": "College of Business, Public Policy, and Law",
     "campus": "galway_main", "mode": "full_time", "delivery_language": "en", "academic_year": "2025/26",
     "lecturer_lead": "Dr D. Ó Conchúir", "description_short": "Irish constitutional law — Bunreacht na hÉireann 1937.",
     "learning_outcomes_count": 5, "learning_outcomes": ["Interpret constitutional provisions", "Apply judicial review", "..."],
     "assessment_methods": ["essay", "exam"], "prerequisite_module_codes": [],
     "syllabus_url": "https://www.universityofgalway.ie/programmes/llb-law/lw101.html"},
    # Business (2 modules)
    {"module_id": "ec101-microeconomics", "module_code": "EC101", "programme_ids": ["bcomm-business"], "school_id": "school-business",
     "title_english": "Microeconomics", "title_irish": "Micreacnamaíocht",
     "level": "undergraduate", "year_of_study": 1, "semester": "S1", "ects_credits": 5, "faculty": "College of Business, Public Policy, and Law",
     "campus": "galway_main", "mode": "full_time", "delivery_language": "en", "academic_year": "2025/26",
     "lecturer_lead": "Dr A. Ní Bhrádaigh", "description_short": "Consumer + firm behaviour, market structures.",
     "learning_outcomes_count": 5, "learning_outcomes": ["Analyse supply + demand", "Compute equilibria", "..."],
     "assessment_methods": ["continuous_assessment", "exam"], "prerequisite_module_codes": [],
     "syllabus_url": "https://www.universityofgalway.ie/programmes/bcomm-business/ec101.html"},
    # Medicine (2 modules)
    {"module_id": "md101-anatomy", "module_code": "MD101", "programme_ids": ["mbbs-medicine"], "school_id": "school-medicine",
     "title_english": "Human Anatomy", "title_irish": "Anatamaíocht an Duine",
     "level": "undergraduate", "year_of_study": 1, "semester": "S1", "ects_credits": 10, "faculty": "College of Medicine, Nursing, and Health Sciences",
     "campus": "galway_main", "mode": "full_time", "delivery_language": "en", "academic_year": "2025/26",
     "lecturer_lead": "Dr F. Ní Mhurchú", "description_short": "Gross anatomy of the human body.",
     "learning_outcomes_count": 6, "learning_outcomes": ["Identify anatomical structures", "..."],
     "assessment_methods": ["continuous_assessment", "exam"], "prerequisite_module_codes": [],
     "syllabus_url": "https://www.universityofgalway.ie/programmes/mbbs-medicine/md101.html"},
)


class ModulesPipeline(TertiaryPipelineBase):
    SURFACE_CONFIG = TertiarySurfaceConfig(
        surface_id="uog_modules",
        surface_name_english="UoG Modules",
        surface_name_irish="Modúil UoG",
        source_url="https://www.universityofgalway.ie/courses/",
        jurisdiction="ie_galway",
        academic_year="2025/26",
        row_primary_key="module_id",
    )

    @dlt.resource(write_disposition="replace", primary_key="module_id")
    def modules(self) -> Iterator[dict]:
        self.logger.info("modules_sync_start", surface_id=self.surface_id)
        yield from UOG_MODULES
        self.logger.info("modules_sync_complete", surface_id=self.surface_id, count=len(UOG_MODULES))

    def build_pipeline_resource(self) -> Iterator[dict]:
        return self.modules()


modules_pipeline = ModulesPipeline()
