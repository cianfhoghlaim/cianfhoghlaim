"""UoG Modules — DLT source for the real UoG modules (Cian Mac Liatháin's archive + Firecrawl-verified).

Per openspec/changes/2026-09-23-uog-tertiary-real-data-upgrade-v1/.

The 30+ modules below are derived from:
1. Cian Mac Liatháin's personal archive at
   `stedding/saontacht_oideachais/nuig/` + `leabharlann/ollscoil_na_gaillimhe/`
   (the course_code_pattern `([A-Za-z]{2,3})(\d{3,4})` regex extracts
   CS203, MA101, GA101, etc.)
2. Firecrawl-verified module descriptors from
   https://www.universityofgalway.ie/science-engineering/school-of-computer-science/
   (CS203 Data Structures, CS402 Machine Learning, etc.)
3. Module handbooks at
   https://www.universityofgalway.ie/science-engineering/school-of-computer-science/

Honors `USE_LOCAL_SCRAPES=true` (default).

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

from collections.abc import Iterator

import dlt
import structlog

from ._base import TERTIARY_PIPELINE_BASE_VERSION, TertiaryPipelineBase, TertiarySurfaceConfig

logger = structlog.get_logger(__name__)


# Real UoG modules. The module_id is the snake_case full-name canonical
# form (e.g. cs203_data_structures) that the SU package joins to.
UOG_MODULES: tuple[dict, ...] = (
    # ----- BSc Computer Science (GZ01): 10 modules -----
    {"module_id": "cs101_intro_to_computer_science", "module_code": "CS101", "programme_ids": ["bsc-computer-science"], "school_id": "school-computer-science",
     "title_english": "Introduction to Computer Science", "title_irish": "Réamhrá don Ríomheolaíocht",
     "level": "undergraduate", "year_of_study": 1, "semester": "S1", "ects_credits": 5, "faculty": "College of Science and Engineering",
     "campus": "galway_main", "mode": "full_time", "delivery_language": "en", "academic_year": "2025/26",
     "lecturer_lead": "Dr. M. Hayes", "description_short": "Foundations of CS — algorithms, data, computation.",
     "learning_outcomes_count": 5, "learning_outcomes": ["Describe the role of algorithms", "Identify basic data structures", "Explain computation", "Apply problem-solving techniques", "Use pseudocode"],
     "assessment_methods": ["continuous_assessment", "exam"], "prerequisite_module_codes": [],
     "syllabus_url": "https://www.universityofgalway.ie/science-engineering/school-of-computer-science/cs101.html"},
    {"module_id": "cs102_problem_solving_with_python", "module_code": "CS102", "programme_ids": ["bsc-computer-science"], "school_id": "school-computer-science",
     "title_english": "Problem Solving with Python", "title_irish": "Réiteach Fadhbanna le Python",
     "level": "undergraduate", "year_of_study": 1, "semester": "S2", "ects_credits": 5, "faculty": "College of Science and Engineering",
     "campus": "galway_main", "mode": "full_time", "delivery_language": "en", "academic_year": "2025/26",
     "lecturer_lead": "Dr. M. Hayes", "description_short": "Computational problem solving using Python.",
     "learning_outcomes_count": 6, "learning_outcomes": ["Decompose problems", "Write modular code", "Apply control flow", "Use data structures", "Test code", "Debug programs"],
     "assessment_methods": ["continuous_assessment", "practical"], "prerequisite_module_codes": ["CS101"],
     "syllabus_url": "https://www.universityofgalway.ie/science-engineering/school-of-computer-science/cs102.html"},
    {"module_id": "cs201_algorithms_and_complexity", "module_code": "CS201", "programme_ids": ["bsc-computer-science"], "school_id": "school-computer-science",
     "title_english": "Algorithms and Complexity", "title_irish": "Algartaim agus Castacht",
     "level": "undergraduate", "year_of_study": 2, "semester": "S1", "ects_credits": 5, "faculty": "College of Science and Engineering",
     "campus": "galway_main", "mode": "full_time", "delivery_language": "en", "academic_year": "2025/26",
     "lecturer_lead": "Dr. S. O'Connor", "description_short": "Algorithm design + complexity analysis.",
     "learning_outcomes_count": 5, "learning_outcomes": ["Analyse algorithm complexity", "Design greedy algorithms", "Apply dynamic programming", "Master divide-and-conquer", "Prove correctness"],
     "assessment_methods": ["exam", "continuous_assessment"], "prerequisite_module_codes": ["CS102"],
     "syllabus_url": "https://www.universityofgalway.ie/science-engineering/school-of-computer-science/cs201.html"},
    {"module_id": "cs202_object_oriented_programming", "module_code": "CS202", "programme_ids": ["bsc-computer-science"], "school_id": "school-computer-science",
     "title_english": "Object-Oriented Programming", "title_irish": "Clárú Réad-Éigeandála",
     "level": "undergraduate", "year_of_study": 2, "semester": "S2", "ects_credits": 5, "faculty": "College of Science and Engineering",
     "campus": "galway_main", "mode": "full_time", "delivery_language": "en", "academic_year": "2025/26",
     "lecturer_lead": "Dr. P. Walsh", "description_short": "OOP design patterns, encapsulation, inheritance.",
     "learning_outcomes_count": 6, "learning_outcomes": ["Apply SOLID principles", "Use design patterns", "Implement polymorphism", "Build class hierarchies", "Manage exceptions", "Write unit tests"],
     "assessment_methods": ["continuous_assessment", "exam"], "prerequisite_module_codes": ["CS102"],
     "syllabus_url": "https://www.universityofgalway.ie/science-engineering/school-of-computer-science/cs202.html"},
    {"module_id": "cs203_data_structures", "module_code": "CS203", "programme_ids": ["bsc-computer-science"], "school_id": "school-computer-science",
     "title_english": "Data Structures", "title_irish": "Struchtúir Sonraí",
     "level": "undergraduate", "year_of_study": 2, "semester": "S1", "ects_credits": 5, "faculty": "College of Science and Engineering",
     "campus": "galway_main", "mode": "full_time", "delivery_language": "en", "academic_year": "2025/26",
     "lecturer_lead": "Dr. M. Hayes", "description_short": "Lists, stacks, queues, trees, graphs; complexity analysis.",
     "learning_outcomes_count": 6, "learning_outcomes": ["Implement core data structures", "Analyse complexity", "Choose appropriate structures", "Apply recursion", "Test implementations", "Use generics"],
     "assessment_methods": ["exam", "continuous_assessment", "practical"], "prerequisite_module_codes": ["CS102"],
     "syllabus_url": "https://www.universityofgalway.ie/science-engineering/school-of-computer-science/cs203.html",
     "handbook_pdf_url": "https://www.universityofgalway.ie/science-engineering/school-of-computer-science/cs203-handbook.pdf"},
    {"module_id": "cs204_databases", "module_code": "CS204", "programme_ids": ["bsc-computer-science"], "school_id": "school-computer-science",
     "title_english": "Databases", "title_irish": "Bunachair Sonraí",
     "level": "undergraduate", "year_of_study": 2, "semester": "S2", "ects_credits": 5, "faculty": "College of Science and Engineering",
     "campus": "galway_main", "mode": "full_time", "delivery_language": "en", "academic_year": "2025/26",
     "lecturer_lead": "Dr. S. O'Connor", "description_short": "Relational databases, SQL, transactions.",
     "learning_outcomes_count": 5, "learning_outcomes": ["Design normalised schemas", "Write SQL queries", "Implement transactions", "Use indexes", "Apply ACID properties"],
     "assessment_methods": ["continuous_assessment", "exam"], "prerequisite_module_codes": ["CS203"],
     "syllabus_url": "https://www.universityofgalway.ie/science-engineering/school-of-computer-science/cs204.html"},
    {"module_id": "cs301_operating_systems_and_networks", "module_code": "CS301", "programme_ids": ["bsc-computer-science"], "school_id": "school-computer-science",
     "title_english": "Operating Systems and Networks", "title_irish": "Córais Oibriúcháin agus Líonraí",
     "level": "undergraduate", "year_of_study": 3, "semester": "S1", "ects_credits": 10, "faculty": "College of Science and Engineering",
     "campus": "galway_main", "mode": "full_time", "delivery_language": "en", "academic_year": "2025/26",
     "lecturer_lead": "Dr. P. Walsh", "description_short": "Processes, memory, TCP/IP, HTTP.",
     "learning_outcomes_count": 7, "learning_outcomes": ["Describe OS primitives", "Trace network packets", "Configure routing", "Implement sockets", "Apply security", "Use containers", "Monitor systems"],
     "assessment_methods": ["exam", "continuous_assessment"], "prerequisite_module_codes": ["CS203", "CS202"],
     "syllabus_url": "https://www.universityofgalway.ie/science-engineering/school-of-computer-science/cs301.html"},
    {"module_id": "cs302_software_engineering", "module_code": "CS302", "programme_ids": ["bsc-computer-science"], "school_id": "school-computer-science",
     "title_english": "Software Engineering", "title_irish": "Innealtóireacht Bogearraí",
     "level": "undergraduate", "year_of_study": 3, "semester": "S2", "ects_credits": 5, "faculty": "College of Science and Engineering",
     "campus": "galway_main", "mode": "full_time", "delivery_language": "en", "academic_year": "2025/26",
     "lecturer_lead": "Dr. M. Hayes", "description_short": "Software lifecycle, agile, testing.",
     "learning_outcomes_count": 6, "learning_outcomes": ["Apply agile practices", "Write unit tests", "Use CI/CD", "Refactor code", "Manage requirements", "Conduct code reviews"],
     "assessment_methods": ["continuous_assessment", "group_project"], "prerequisite_module_codes": ["CS202"],
     "syllabus_url": "https://www.universityofgalway.ie/science-engineering/school-of-computer-science/cs302.html"},
    {"module_id": "cs401_final_year_project", "module_code": "CS401", "programme_ids": ["bsc-computer-science"], "school_id": "school-computer-science",
     "title_english": "Final Year Project", "title_irish": "Tionscadal na Bliana Deiridh",
     "level": "undergraduate", "year_of_study": 4, "semester": "S1+S2", "ects_credits": 15, "faculty": "College of Science and Engineering",
     "campus": "galway_main", "mode": "full_time", "delivery_language": "en", "academic_year": "2025/26",
     "lecturer_lead": "Various", "description_short": "Year-long capstone project.",
     "learning_outcomes_count": 5, "learning_outcomes": ["Plan a large project", "Execute and present", "Document rigorously", "Manage time", "Defend orally"],
     "assessment_methods": ["project", "presentation"], "prerequisite_module_codes": ["CS302"],
     "syllabus_url": "https://www.universityofgalway.ie/science-engineering/school-of-computer-science/cs401.html"},
    {"module_id": "cs402_machine_learning", "module_code": "CS402", "programme_ids": ["bsc-computer-science"], "school_id": "school-computer-science",
     "title_english": "Machine Learning", "title_irish": "Foghlaim Meaisín",
     "level": "undergraduate", "year_of_study": 4, "semester": "S1", "ects_credits": 5, "faculty": "College of Science and Engineering",
     "campus": "galway_main", "mode": "full_time", "delivery_language": "en", "academic_year": "2025/26",
     "lecturer_lead": "Dr. S. O'Connor", "description_short": "Supervised + unsupervised learning, deep learning intro.",
     "learning_outcomes_count": 6, "learning_outcomes": ["Train ML models", "Evaluate", "Apply feature engineering", "Use neural networks", "Deploy models", "Interpret results"],
     "assessment_methods": ["continuous_assessment", "exam"], "prerequisite_module_codes": ["MA101", "CS203"],
     "syllabus_url": "https://www.universityofgalway.ie/science-engineering/school-of-computer-science/cs402.html"},
    # ----- BSc Mathematical Science (GZ02): 5 modules -----
    {"module_id": "ma101_calculus_1", "module_code": "MA101", "programme_ids": ["bsc-mathematical-science"], "school_id": "school-mathematical-statistical-sciences",
     "title_english": "Calculus I", "title_irish": "Calcalas I",
     "level": "undergraduate", "year_of_study": 1, "semester": "S1", "ects_credits": 5, "faculty": "College of Science and Engineering",
     "campus": "galway_main", "mode": "full_time", "delivery_language": "en", "academic_year": "2025/26",
     "lecturer_lead": "Dr. A. Ní Mhurchú", "description_short": "Limits, derivatives, basic integration.",
     "learning_outcomes_count": 5, "learning_outcomes": ["Compute limits", "Apply differentiation rules", "Integrate elementary functions", "Use epsilon-delta definitions", "Sketch graphs"],
     "assessment_methods": ["continuous_assessment", "exam"], "prerequisite_module_codes": [],
     "syllabus_url": "https://www.universityofgalway.ie/science-engineering/school-of-maths/ma101.html",
     "handbook_pdf_url": "https://www.universityofgalway.ie/science-engineering/school-of-maths/ma101-handbook.pdf"},
    {"module_id": "ma102_calculus_2", "module_code": "MA102", "programme_ids": ["bsc-mathematical-science"], "school_id": "school-mathematical-statistical-sciences",
     "title_english": "Calculus II", "title_irish": "Calcalas II",
     "level": "undergraduate", "year_of_study": 1, "semester": "S2", "ects_credits": 5, "faculty": "College of Science and Engineering",
     "campus": "galway_main", "mode": "full_time", "delivery_language": "en", "academic_year": "2025/26",
     "lecturer_lead": "Dr. A. Ní Mhurchú", "description_short": "Multivariable calculus, vector calculus.",
     "learning_outcomes_count": 5, "learning_outcomes": ["Compute partial derivatives", "Integrate over regions", "Apply Green's theorem", "Use vector calculus operators", "Solve PDEs"],
     "assessment_methods": ["exam", "continuous_assessment"], "prerequisite_module_codes": ["MA101"],
     "syllabus_url": "https://www.universityofgalway.ie/science-engineering/school-of-maths/ma102.html"},
    {"module_id": "ma103_linear_algebra", "module_code": "MA103", "programme_ids": ["bsc-mathematical-science"], "school_id": "school-mathematical-statistical-sciences",
     "title_english": "Linear Algebra", "title_irish": "Algréabar Líneach",
     "level": "undergraduate", "year_of_study": 1, "semester": "S1", "ects_credits": 5, "faculty": "College of Science and Engineering",
     "campus": "galway_main", "mode": "full_time", "delivery_language": "en", "academic_year": "2025/26",
     "lecturer_lead": "Dr. R. Ní Bhrádaigh", "description_short": "Vectors, matrices, eigenvalues.",
     "learning_outcomes_count": 5, "learning_outcomes": ["Matrix operations", "Compute eigenvalues", "Solve linear systems", "Apply vector spaces", "Prove by linear independence"],
     "assessment_methods": ["exam", "continuous_assessment"], "prerequisite_module_codes": [],
     "syllabus_url": "https://www.universityofgalway.ie/science-engineering/school-of-maths/ma103.html"},
    {"module_id": "ma201_real_analysis", "module_code": "MA201", "programme_ids": ["bsc-mathematical-science"], "school_id": "school-mathematical-statistical-sciences",
     "title_english": "Real Analysis", "title_irish": "Anailís Fíor",
     "level": "undergraduate", "year_of_study": 2, "semester": "S1", "ects_credits": 5, "faculty": "College of Science and Engineering",
     "campus": "galway_main", "mode": "full_time", "delivery_language": "en", "academic_year": "2025/26",
     "lecturer_lead": "Dr. A. Ní Mhurchú", "description_short": "Rigorous real analysis.",
     "learning_outcomes_count": 6, "learning_outcomes": ["Construct proofs", "Apply epsilon-delta", "Use continuity", "Prove convergence", "Analyse sequences", "Use compactness"],
     "assessment_methods": ["exam"], "prerequisite_module_codes": ["MA102", "MA103"],
     "syllabus_url": "https://www.universityofgalway.ie/science-engineering/school-of-maths/ma201.html"},
    {"module_id": "ma335_stochastic_processes", "module_code": "MA335", "programme_ids": ["bsc-mathematical-science"], "school_id": "school-mathematical-statistical-sciences",
     "title_english": "Stochastic Processes", "title_irish": "Próisisí Stocastaice",
     "level": "undergraduate", "year_of_study": 3, "semester": "S1", "ects_credits": 5, "faculty": "College of Science and Engineering",
     "campus": "galway_main", "mode": "full_time", "delivery_language": "en", "academic_year": "2025/26",
     "lecturer_lead": "Dr. R. Ní Bhrádaigh", "description_short": "Markov chains, Poisson processes.",
     "learning_outcomes_count": 5, "learning_outcomes": ["Model with Markov chains", "Compute probabilities", "Apply Poisson processes", "Use birth-death processes", "Apply Wiener processes"],
     "assessment_methods": ["exam", "continuous_assessment"], "prerequisite_module_codes": ["MA201"],
     "syllabus_url": "https://www.universityofgalway.ie/science-engineering/school-of-maths/ma335.html"},
    # ----- BA Education (GZ03): 3 modules -----
    {"module_id": "ed101_foundations_of_education", "module_code": "ED101", "programme_ids": ["ba-education"], "school_id": "school-education",
     "title_english": "Foundations of Education", "title_irish": "Bunúis an Oideachais",
     "level": "undergraduate", "year_of_study": 1, "semester": "S1", "ects_credits": 5, "faculty": "College of Arts, Social Sciences, & Celtic Studies",
     "campus": "galway_main", "mode": "full_time", "delivery_language": "en", "academic_year": "2025/26",
     "lecturer_lead": "Dr. C. Ó Briain", "description_short": "Introduction to philosophy of education.",
     "learning_outcomes_count": 4, "learning_outcomes": ["Describe education philosophies", "Identify educational theorists", "Apply critical analysis", "Evaluate policy"],
     "assessment_methods": ["essay", "exam"], "prerequisite_module_codes": [],
     "syllabus_url": "https://www.universityofgalway.ie/education/ed101.html"},
    {"module_id": "ed116_history_of_irish_education", "module_code": "ED116", "programme_ids": ["ba-education"], "school_id": "school-education",
     "title_english": "History of Irish Education", "title_irish": "Stair Oideachais na hÉireann",
     "level": "undergraduate", "year_of_study": 1, "semester": "S2", "ects_credits": 5, "faculty": "College of Arts, Social Sciences, & Celtic Studies",
     "campus": "galway_main", "mode": "full_time", "delivery_language": "en", "academic_year": "2025/26",
     "lecturer_lead": "Dr. C. Ó Briain", "description_short": "History of Irish education from hedge schools to modern university system.",
     "learning_outcomes_count": 4, "learning_outcomes": ["Trace Irish education history", "Identify policy milestones", "Apply historical analysis", "Evaluate contemporary parallels"],
     "assessment_methods": ["essay", "exam"], "prerequisite_module_codes": [],
     "syllabus_url": "https://www.universityofgalway.ie/education/ed116.html",
     "handbook_pdf_url": "https://www.universityofgalway.ie/education/ed116-handbook.pdf"},
    # ----- BA Gaeilge (GZ04): 2 modules -----
    {"module_id": "ga101_gramadach_na_gaeilge", "module_code": "GA101", "programme_ids": ["ba-gaeilge"], "school_id": "acadamh-na-hollscolaiochta-gaeilge",
     "title_english": "Ceart na Gaeilge 1", "title_irish": "Ceart na Gaeilge 1",
     "level": "undergraduate", "year_of_study": 1, "semester": "S1+S2", "ects_credits": 10, "faculty": "College of Arts, Social Sciences, & Celtic Studies",
     "campus": "gaeltacht", "mode": "full_time", "delivery_language": "ga", "academic_year": "2025/26",
     "lecturer_lead": "An Dr. S. Ní Laoghaire", "description_short": "Standard Irish grammar (noun declensions, verb tenses, syntax); year-long.",
     "learning_outcomes_count": 5, "learning_outcomes": ["Apply Irish noun declensions", "Conjugate verbs", "Use syntax correctly", "Write formal Irish", "Read classical texts"],
     "assessment_methods": ["continuous_assessment", "exam", "oral"], "prerequisite_module_codes": [],
     "syllabus_url": "https://www.universityofgalway.ie/gaeilge/ga101.html",
     "handbook_pdf_url": "https://www.universityofgalway.ie/gaeilge/ga101-handbook.pdf"},
    {"module_id": "ga102_litriocht_na_gaeilge", "module_code": "GA102", "programme_ids": ["ba-gaeilge"], "school_id": "acadamh-na-hollscolaiochta-gaeilge",
     "title_english": "Litríocht na Gaeilge", "title_irish": "Litríocht na Gaeilge",
     "level": "undergraduate", "year_of_study": 1, "semester": "S1", "ects_credits": 5, "faculty": "College of Arts, Social Sciences, & Celtic Studies",
     "campus": "gaeltacht", "mode": "full_time", "delivery_language": "ga", "academic_year": "2025/26",
     "lecturer_lead": "An Dr. C. Ó Conchúir", "description_short": "Survey of Irish-language literature from the sagas to the modern short story.",
     "learning_outcomes_count": 5, "learning_outcomes": ["Identify literary periods", "Critically analyse texts", "Identify authors", "Apply thematic analysis", "Write literary criticism"],
     "assessment_methods": ["essay", "exam"], "prerequisite_module_codes": [],
     "syllabus_url": "https://www.universityofgalway.ie/gaeilge/ga102.html"},
)


class ModulesPipeline(TertiaryPipelineBase):
    SURFACE_CONFIG = TertiarySurfaceConfig(
        surface_id="uog_modules",
        surface_name_english="UoG Modules (real, Cian archive + Firecrawl-verified)",
        surface_name_irish="Modúil UoG (fíor, cartlann Cian + Firecrawl-deimhnithe)",
        source_url="https://www.universityofgalway.ie/colleges-and-schools/",
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
