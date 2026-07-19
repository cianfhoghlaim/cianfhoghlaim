// BAML Schema for University Deep Extraction
//
// Structured extraction of 4 academic-website artefact types for any
// British Isles university (case study: University of Galway):
//   1. Course descriptors (programme-level)
//   2. Module descriptors (course-level: code, title, ECTS, outcomes, etc.)
//   3. Programme descriptors (degree-level: duration, mode, total ECTS)
//   4. Reading-list items (ISBN-13 / DOI / URL)
//
// This is the *website* side of the pipeline. The *personal-archive*
// side (the user's `leabharlann/ollscoil_na_gaillimhe/` UoG artefacts)
// is handled by `author_archive.baml::ExtractUoGArtifact`. The two are
// joined by the new Cognee cross-archive edge
// `UoGArtifact-MATCHES-CourseDescriptor` (see
// `cianfhoghlaim/cognify/rules/university_cross_archive.py`).
//
// All 4 functions route through the canonical `ExtractEn` LiteLLM
// client (defined in `clients.baml`; the gateway alias `extract-en`
// resolves to gemini-2.5-flash → glm-4.6 → gemini-1.5-flash).
//
// See `openspec/changes/university-of-galway-deep-extraction/` for the
// proposal + tasks + spec deltas that introduced this file.

// =============================================================================
// Enums
// =============================================================================

enum NfqLevel {
  NFQ_6           @description("NFQ Level 6 — Higher Certificate")
  NFQ_7           @description("NFQ Level 7 — Ordinary Bachelor Degree (B.Sc., B.A.)")
  NFQ_8           @description("NFQ Level 8 — Honours Bachelor Degree (B.Sc. Hons, B.A. Hons)")
  NFQ_9           @description("NFQ Level 9 — Masters Degree (M.Sc., M.A., M.Phil.)")
  NFQ_10          @description("NFQ Level 10 — Doctoral Degree (Ph.D., DPhil)")
  UNKNOWN         @description("NFQ level cannot be inferred from the page")
}

enum ProgrammeStage {
  UNDERGRADUATE   @description("Undergraduate (B.Sc., B.A., B.Ed., Higher Diploma, etc.)")
  POSTGRADUATE    @description("Postgraduate taught or research (M.Sc., M.A., Ph.D.)")
  PROFESSIONAL    @description("Professional development / CPD")
  UNKNOWN         @description("Stage cannot be inferred from the page")
}

enum Semester {
  SEMESTER_1      @description("Autumn / Semester 1")
  SEMESTER_2      @description("Spring / Semester 2")
  YEAR_LONG       @description("Full academic year (no semester split)")
  UNKNOWN         @description("Semester cannot be inferred from the page")
}

enum StudyMode {
  FULL_TIME       @description("Full-time study")
  PART_TIME       @description("Part-time study")
  BOTH            @description("Both full-time and part-time options available")
  ONLINE          @description("Online / distance learning only")
  UNKNOWN         @description("Study mode cannot be inferred")
}

enum ReadingFormat {
  ISBN_13         @description("A 13-digit ISBN (e.g. '9780262033848')")
  DOI             @description("A Digital Object Identifier (e.g. '10.1038/nature12373')")
  URL             @description("A free-form URL to the resource (web article, PDF, etc.)")
  INTERNAL_REF    @description("An internal library reference (e.g. 'Library Reserve: HF1234')")
  OTHER           @description("None of the above (no standard identifier visible)")
}

// =============================================================================
// ReadingListItem
// =============================================================================

class ReadingListItem {
  format ReadingFormat @description("The type of identifier the item carries")
  title string @description("The book / paper / resource title")
  authors string[] @description("Ordered list of author / editor names")
  year int? @description("Publication year (4-digit), or null if not visible")
  isbn_13 string? @description("13-digit ISBN, set when format = ISBN_13")
  doi string? @description("Digital Object Identifier (without 'doi:' prefix), set when format = DOI")
  url string? @description("Free-form URL, set when format = URL or DOI")
  library_ref string? @description("Library / shelf reference, set when format = INTERNAL_REF")
  essential bool @description("True if this reading is marked 'essential' or 'core' on the module page")
  confidence float @description("Extraction confidence 0.0-1.0")
  @@stream.done
}

// =============================================================================
// LecturerInfo
// =============================================================================

class LecturerInfo {
  name string @description("Full name, e.g. 'Dr. John McCarthy'")
  email string? @description("University email address if visible, else null")
  school string @description("The lecturer's school / department, e.g. 'School of Computer Science'")
  profile_url string? @description("URL of the lecturer's staff profile page, or null")
  is_coordinator bool @description("True if this lecturer is the module coordinator")
}

// =============================================================================
// CourseDescriptor
// =============================================================================
//
// A *course* in the British Isles university sense is a single unit
// of study with a code, title, ECTS value, and learning outcomes.
// Multiple courses together form a *programme* (see ProgrammeDescriptor).
// At UoG and most Irish universities, a "module" is what this schema
// calls a "course". The class is named `CourseDescriptor` to match
// the academic-catalogue convention ("Course finder", "Course catalogue")
// used on the public-facing websites.

class AssessmentBreakdown {
  exam_weight_percent int? @description("Final-exam weight 0-100, or null if continuous assessment only")
  ca_weight_percent int? @description("Continuous assessment weight 0-100, or null if exam only")
  ca_components string[] @description("Names of CA components (e.g. ['assignment_1', 'midterm_test', 'lab_report']); empty if unknown")
}

class CourseDescriptor {
  course_code string @description("Course code, e.g. 'MA335', 'CT511', 'CT516', 'GA101', 'ED305'")
  course_title string @description("Course / module title, e.g. 'Deep Learning', 'Cryptography'")
  nfq_level NfqLevel @description("NFQ level of the course (NFQ_7 / NFQ_8 / NFQ_9)")
  stage ProgrammeStage @description("Programme stage (UNDERGRADUATE / POSTGRADUATE / PROFESSIONAL)")
  school string @description("School / department, e.g. 'School of Computer Science', 'School of Mathematical and Statistical Sciences'")
  ects int @description("ECTS credit value, 1-30 (5 and 10 are the most common)")
  semester Semester @description("Which semester the course runs in")
  description string @description("2-4 sentence course description, as written on the course page")
  learning_outcomes string[] @description("3-7 learning outcome bullets, each a single sentence")
  assessment AssessmentBreakdown? @description("Assessment breakdown, or null if not visible on the page")
  prerequisite_courses string[] @description("Course codes that are formal prerequisites (e.g. ['CT511', 'MA335']); empty if none")
  lecturers LecturerInfo[] @description("1-5 lecturers for this course, with the coordinator marked `is_coordinator=true`")
  recommended_reading ReadingListItem[] @description("3-10 essential + recommended reading items, in display order")
  programme_codes string[] @description("Programme codes this course belongs to (e.g. ['MSCAI', 'BScCS']); 0-N entries")
  source_url string @description("The canonical URL this descriptor was extracted from")
  scraped_at string @description("ISO-8601 timestamp of the scrape, e.g. '2026-06-29T14:00:00Z'")
  confidence float @description("Overall extraction confidence 0.0-1.0")
  @@stream.done
}

// =============================================================================
// ModuleDescriptor (alias of CourseDescriptor for backward compatibility)
//
// Most British Isles universities call this entity a "module" rather
// than a "course". `ModuleDescriptor` is the same shape as
// `CourseDescriptor` to keep the BAML types flexible; consumers can
// use either name.
// =============================================================================

class ModuleDescriptor {
  module_code string @description("Module / course code, e.g. 'CT516'")
  module_title string @description("Module / course title, e.g. 'Deep Learning'")
  nfq_level NfqLevel @description("NFQ level of the module")
  stage ProgrammeStage @description("Programme stage (UNDERGRADUATE / POSTGRADUATE / PROFESSIONAL)")
  school string @description("School / department")
  ects int @description("ECTS credit value, 1-30")
  semester Semester @description("Which semester the module runs in")
  description string @description("2-4 sentence module description")
  learning_outcomes string[] @description("3-7 learning outcome bullets")
  assessment AssessmentBreakdown? @description("Assessment breakdown, or null if not visible")
  prerequisite_modules string[] @description("Module codes that are formal prerequisites")
  lecturers LecturerInfo[] @description("1-5 lecturers for this module")
  recommended_reading ReadingListItem[] @description("3-10 essential + recommended reading items")
  programme_codes string[] @description("Programme codes this module belongs to")
  source_url string @description("The canonical URL this descriptor was extracted from")
  scraped_at string @description("ISO-8601 timestamp of the scrape")
  confidence float @description("Overall extraction confidence 0.0-1.0")
  @@stream.done
}

// =============================================================================
// ProgrammeDescriptor
// =============================================================================

class ProgrammeDescriptor {
  programme_code string @description("Programme code, e.g. 'MSCAI', 'BScCS', 'HDSD' (Higher Diploma in Software Design)")
  programme_title string @description("Programme / degree title, e.g. 'Master of Science (Artificial Intelligence)'")
  nfq_level NfqLevel @description("NFQ level of the final award (NFQ_9 for M.Sc., NFQ_8 for B.Sc. Hons)")
  stage ProgrammeStage @description("Programme stage")
  school string @description("The lead school / department (programmes can span multiple schools)")
  duration_months int @description("Programme duration in months (12 for 1-year M.Sc., 48 for 4-year B.Sc.)")
  mode StudyMode @description("Study mode (full-time / part-time / both / online)")
  total_ects int @description("Total ECTS to graduate (60 for 1-year M.Sc., 240 for 4-year B.Sc.)")
  module_codes string[] @description("Module codes that make up the programme (6-20 modules); 0-N entries")
  entry_requirements string @description("1-3 sentence entry-requirements summary (e.g. 'B.Sc. Hons in Computer Science or equivalent, 2:1 or higher')")
  source_url string @description("The canonical URL this descriptor was extracted from")
  scraped_at string @description("ISO-8601 timestamp of the scrape")
  confidence float @description("Overall extraction confidence 0.0-1.0")
  @@stream.done
}

// =============================================================================
// Functions
// =============================================================================

function ExtractCourseDescriptor(
  course_page_markdown: string,
  course_url: string
) -> CourseDescriptor {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

function ExtractModuleDescriptor(
  module_page_markdown: string,
  module_url: string
) -> ModuleDescriptor {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

function ExtractProgrammeDescriptor(
  programme_page_markdown: string,
  programme_url: string
) -> ProgrammeDescriptor {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

function ExtractReadingList(
  module_page_markdown: string,
  module_url: string
) -> ReadingListItem[] {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

// =============================================================================
// Tests
// =============================================================================

// test ExtractCourseDescriptorTest {
//   functions [ExtractCourseDescriptor]
//   args {
//     course_page_markdown #"
//       # CT516 — Deep Learning
// 
//       **School:** School of Computer Science
//       **NFQ Level:** 9 (Masters)
//       **ECTS:** 10
//       **Semester:** Semester 1
//       **Academic Year:** 2025-26
// 
//       ## Module Description
//       This module introduces the foundations of deep learning, covering
//       feedforward and convolutional networks, recurrent networks,
//       attention mechanisms, and transformer architectures. Students
//       will implement and train models using PyTorch on a series of
//       coursework assignments and a final project.
// 
//       ## Learning Outcomes
//       On completion of this module, students should be able to:
//       1. Explain the mathematical foundations of gradient descent,
//          backpropagation, and stochastic optimisation.
//       2. Implement feedforward, convolutional, and recurrent neural
//          networks in PyTorch.
//       3. Apply transformer architectures to sequence-modelling tasks.
//       4. Evaluate deep-learning models using appropriate metrics.
//       5. Diagnose and fix common training pathologies (overfitting,
//          underfitting, vanishing gradients, mode collapse).
// 
//       ## Assessment
//       - Continuous assessment: 60% (3 assignments, 20% each)
//       - Final exam: 40%
// 
//       ## Prerequisites
//       CT511 (Software Engineering), MA335 (Mathematical Statistics)
// 
//       ## Lecturers
//       - **Dr. Jane Smith** (Module Coordinator)
//         jane.smith@universityofgalway.ie
//         https://www.universityofgalway.ie/our-research/people/jane-smith
//       - **Dr. Conor O'Brien**
//         conor.obrien@universityofgalway.ie
//         https://www.universityofgalway.ie/our-research/people/conor-obrien
// 
//       ## Recommended Reading
//       - **Essential:** Deep Learning, Ian Goodfellow, Yoshua Bengio,
//         Aaron Courville. MIT Press, 2016. ISBN 9780262033848.
//       - **Essential:** Neural Networks and Deep Learning, Michael
//         Nielsen. Online, 2015. http://neuralnetworksanddeeplearning.com/
//       - **Recommended:** Attention Is All You Need, Vaswani et al.
//         NeurIPS 2017. doi:10.5555/3295222.3295349.
//       - **Reserve:** Library Reserve: 005.1 GOO (Goodfellow)
//     "#
//     course_url "https://www.universityofgalway.ie/programs/ct516-deep-learning.html"
//   }
// }

// test ExtractModuleDescriptorTest {
//   functions [ExtractModuleDescriptor]
//   args {
//     module_page_markdown #"
//       # MA335 — Mathematical Statistics
// 
//       **School:** School of Mathematical and Statistical Sciences
//       **NFQ Level:** 8 (B.Sc. Hons)
//       **ECTS:** 5
//       **Semester:** Semester 2
// 
//       ## Description
//       Probability theory, statistical inference, and applied
//       regression. Covers estimators, hypothesis tests, confidence
//       intervals, and linear models.
// 
//       ## Learning Outcomes
//       1. State and apply the axioms of probability.
//       2. Construct and interpret confidence intervals.
//       3. Perform hypothesis tests at the 0.05 significance level.
//       4. Fit and interpret simple linear regression models.
// 
//       ## Assessment
//       - Exam: 70%
//       - CA: 30% (problem sets)
// 
//       ## Lecturers
//       - **Dr. Mary O'Connell** (Coordinator)
//     "#
//     module_url "https://www.universityofgalway.ie/programs/ma335-mathematical-statistics.html"
//   }
// }

// test ExtractProgrammeDescriptorTest {
//   functions [ExtractProgrammeDescriptor]
//   args {
//     programme_page_markdown #"
//       # Master of Science (Artificial Intelligence) — MSCAI
// 
//       **School:** School of Computer Science
//       **NFQ Level:** 9 (Masters)
//       **Duration:** 12 months (full-time)
//       **Total ECTS:** 90
//       **Mode:** Full-time
// 
//       ## Overview
//       The M.Sc. in AI is a 1-year taught Masters designed for
//       graduates with a B.Sc. in Computer Science (or equivalent)
//       who want to deepen their knowledge of modern AI techniques.
//       The programme is delivered through 8 taught modules (60 ECTS)
//       plus a 30 ECTS research dissertation.
// 
//       ## Modules (Taught)
//       - CT510 — Programming for AI
//       - CT511 — Software Engineering
//       - CT512 — Machine Learning
//       - CT513 — Knowledge Representation
//       - CT514 — Natural Language Processing
//       - CT515 — Computer Vision
//       - CT516 — Deep Learning
//       - CT517 — AI Ethics and Society
// 
//       ## Modules (Dissertation)
//       - CT518 — Research Dissertation (30 ECTS)
// 
//       ## Entry Requirements
//       A B.Sc. Hons in Computer Science (or equivalent) with a
//       2:1 grade or higher. Programming experience required.
//     "#
//     programme_url "https://www.universityofgalway.ie/programs/mscai.html"
//   }
// }

// test ExtractReadingListTest {
//   functions [ExtractReadingList]
//   args {
//     module_page_markdown #"
//       # CT511 — Software Engineering
// 
//       ## Recommended Reading
//       - **Essential:** Clean Architecture, Robert C. Martin.
//         Pearson, 2017. ISBN 9780134494166.
//       - **Essential:** Designing Data-Intensive Applications,
//         Martin Kleppmann. O'Reilly, 2017.
//         ISBN 9781449373320.
//       - **Recommended:** Site Reliability Engineering, Niall
//         Murphy et al. O'Reilly, 2016. ISBN 9781491929124.
//     "#
//     module_url "https://www.universityofgalway.ie/programs/ct511-software-engineering.html"
//   }
// }

// =============================================================================
// Tertiary 18+ stage — 8 universities + 5 TUs + QQI + CAO + SOLAS
// =============================================================================
//
// Added in the `2026-07-15-cianfhoghlaim-university-deep-extraction-v1`
// change. The 5+ classes + 4+ enums + 1+ function below cover the
// **Tertiary 18+ stage** of the K-12 → university pipeline:
//
//   1. `University` — the 8 Republic of Ireland universities (TCD, UCD,
//      UCC, UoG, UL, DCU, Maynooth, RCSI). One row per (institution_id,
//      language). Distinct from the per-university `CourseDescriptor`
//      above (which is a single course/module/programme extracted from a
//      specific page).
//   2. `TU` — the 5 Technological Universities (TUD, MTU, TUS, ATU,
//      SETU). One row per (tu_id, language).
//   3. `QQIAward` — the canonical QQI awards at NFQ 6-10 (Higher
//      Cert, Ordinary Bachelor, Honours Bachelor, Higher Diploma,
//      Masters, Ph.D., etc.). One row per (award_code, language).
//   4. `CAOChoice` — a CAO course choice entry (cao_code, institution
//      id, nfq_level, points_required). One row per (cao_code, year).
//   5. `SOLASCourse` — a SOLAS Further Education course (PLC,
//      apprenticeship, Youthreach). One row per (course_code, etb_slug).
//
// Together with the 4 per-university functions above, the 9 total
// functions + 9 enums + 11 Pydantic classes cover the full Tertiary
// 18+ surface.
//
// All 4 new functions route through the canonical `ExtractEn` LiteLLM
// client (same as the 4 per-university functions above).

// =============================================================================
// Enums (Tertiary 18+)
// =============================================================================

enum UniversityType {
  TRADITIONAL        @description("Traditional (pre-1997) university: TCD, UCD, UCC, UoG, UL, DCU, Maynooth")
  SPECIALIST         @description("Specialist institution: RCSI (Royal College of Surgeons in Ireland)")
  TECHNOLOGICAL      @description("Post-2018 Technological University (TU Dublin, MTU, TUS, ATU, SETU)")
  PRIVATE            @description("Private university (e.g. NCI — National College of Ireland)")
  UNKNOWN            @description("University type cannot be inferred")
}

enum QQILevel {
  NFQ_6              @description("NFQ Level 6 — Higher Certificate (60 ECTS, 1 year)")
  NFQ_7              @description("NFQ Level 7 — Ordinary Bachelor Degree (180 ECTS, 3 years)")
  NFQ_8              @description("NFQ Level 8 — Honours Bachelor Degree / Higher Diploma / Graduate Diploma (240 ECTS, 4 years)")
  NFQ_9              @description("NFQ Level 9 — Masters Degree / Postgraduate Diploma / Postgraduate Certificate (90 ECTS, 1.5 years taught)")
  NFQ_10             @description("NFQ Level 10 — Doctoral Degree (Ph.D., DPhil, professional doctorate)")
  UNKNOWN            @description("NFQ level cannot be inferred")
}

enum CAOField {
  ARTS_HUMANITIES    @description("Arts, Humanities, Celtic Studies, Social Sciences")
  BUSINESS_LAW       @description("Business, Commerce, Law, Economics")
  SCIENCE            @description("Science (Biology, Chemistry, Physics, Mathematical Science)")
  COMPUTING_ENGINEERING @description("Computing, Computer Science, Software Engineering, Electronic Engineering")
  MEDICINE_HEALTH    @description("Medicine, Nursing, Pharmacy, Physiotherapy, Health Sciences")
  EDUCATION          @description("Education, Teaching, Early Childhood Care")
  MUSIC_PERFORMING   @description("Music, Drama, Performing Arts, Film")
  AGRICULTURE_VET    @description("Agriculture, Veterinary Medicine, Food Science")
  UNKNOWN            @description("Field cannot be inferred from the CAO code")
}

enum SOLASPath {
  PLC                @description("Post-Leaving-Cert (PLC) course at one of the 16 ETBs")
  APPRENTICESHIP     @description("Apprenticeship (designated craft or Generation Apprenticeship)")
  YOUTHREACH         @description("Youthreach — early-school-leaver programme (NFQ 3-5)")
  ADULT_LITERACY     @description("Adult Literacy + numeracy programmes")
  VTOS               @description("Vocational Training Opportunities Scheme")
  COMMUNITY_TRAINING @description("Community Training Centres")
  UNKNOWN            @description("SOLAS pathway cannot be inferred")
}

// =============================================================================
// University — the 8 Republic of Ireland universities (registry view)
// =============================================================================

class University {
  institution_id string @description("Kebab-case institution id, e.g. 'ie-university-galway', 'ie-university-trinity'")
  institution_name string @description("Canonical full name, e.g. 'University of Galway', 'Trinity College Dublin'")
  abbreviation string @description("Canonical abbreviation, e.g. 'UoG', 'TCD', 'UCD', 'UCC', 'UL', 'DCU', 'MU', 'RCSI'")
  university_type UniversityType @description("University type (TRADITIONAL / SPECIALIST / TECHNOLOGICAL / PRIVATE)")
  founded int? @description("Year founded (e.g. 1592 for TCD, 1784 for RCSI)")
  home_url string @description("Canonical homepage URL, e.g. 'https://www.universityofgalway.ie'")
  nfq_min int @description("Lowest NFQ level the institution awards (typically 6 for universities, 8 for RCSI)")
  nfq_max int @description("Highest NFQ level the institution awards (always 10 for the Tertiary 18+ bracket)")
  faculty_count int @description("Number of faculties (typical 4-6)")
  faculty_slugs string[] @description("Faculty slugs, e.g. ['arts-humanities', 'science-engineering']")
  language string @description("Primary language of instruction ('en' for all 8 IE universities)")
  source_url string @description("Canonical URL this record was extracted from")
  scraped_at string @description("ISO-8601 timestamp of the scrape")
  confidence float @description("Overall extraction confidence 0.0-1.0")
  @@stream.done
}

// =============================================================================
// TU — the 5 Technological Universities (registry view)
// =============================================================================

class TU {
  tu_id string @description("Kebab-case tu id, e.g. 'ie-tu-dublin', 'ie-tu-atlantic'")
  tu_name string @description("Canonical full name, e.g. 'Technological University Dublin', 'Atlantic Technological University'")
  abbreviation string @description("Canonical abbreviation, e.g. 'TUD', 'MTU', 'TUS', 'ATU', 'SETU'")
  established int @description("Year established (post-2018 mergers: TUD=2019, MTU=2021, TUS=2021, ATU=2022, SETU=2022)")
  home_url string @description("Canonical homepage URL, e.g. 'https://www.tudublin.ie'")
  parent_iots string[] @description("Predecessor Institutes of Technology, e.g. ['DIT', 'ITB', 'ITT'] for TUD")
  campus_slugs string[] @description("Campus slugs, e.g. ['city', 'blanchardstown', 'tallaght'] for TUD")
  campus_count int @description("Number of campuses (typical 3-5)")
  nfq_min int @description("Lowest NFQ level the TU awards (always 6 for the 5 TUs)")
  nfq_max int @description("Highest NFQ level the TU awards (typically 10, occasionally 9 only)")
  language string @description("Primary language of instruction ('en' for all 5 IE TUs)")
  source_url string @description("Canonical URL this record was extracted from")
  scraped_at string @description("ISO-8601 timestamp of the scrape")
  confidence float @description("Overall extraction confidence 0.0-1.0")
  @@stream.done
}

// =============================================================================
// QQIAward — the canonical QQI awards at NFQ 6-10
// =============================================================================

class QQIAward {
  award_code string @description("Canonical award code, e.g. 'NFQ6-HC', 'NFQ8-BA-HONS', 'NFQ9-MASTERS', 'NFQ10-PHD'")
  award_title string @description("Canonical award title, e.g. 'Bachelor Degree (Honours)', 'Masters Degree'")
  qqi_level QQILevel @description("NFQ level of the award (NFQ_6 / NFQ_7 / NFQ_8 / NFQ_9 / NFQ_10)")
  ects int @description("Canonical ECTS value (60 for Higher Cert, 180 for Ord BA, 240 for Hons BA, 90 for Masters, 0 for Ph.D.)")
  duration_months int @description("Typical duration in months (12 for Higher Cert, 48 for Hons BA, 18 for Masters, 48+ for Ph.D.)")
  category string @description("Award category, e.g. 'higher_diploma', 'graduate_diploma', 'postgrad_cert', 'masters', 'doctoral'")
  issuing_body string @description("Always 'QQI' (Quality and Qualifications Ireland)")
  description string @description("1-3 sentence description of the award type")
  source_url string @description("Canonical URL this record was extracted from (typically https://www.qqi.ie)")
  scraped_at string @description("ISO-8601 timestamp of the scrape")
  confidence float @description("Overall extraction confidence 0.0-1.0")
  @@stream.done
}

// =============================================================================
// CAOChoice — a CAO course choice entry (cao_code, points, institution)
// =============================================================================

class CAOChoice {
  cao_code string @description("5-character CAO course code, e.g. 'CK101', 'GY101', 'DC001', 'TR085'")
  year int @description("The year this entry applies to (e.g. 2025)")
  institution_id string @description("The institution id, e.g. 'ie-university-galway' (cross-ref to `University.institution_id`)")
  programme_title string @description("Programme / course title as listed on CAO, e.g. 'Bachelor of Science (Computer Science)'")
  cao_field CAOField @description("Broad CAO field of study (ARTS_HUMANITIES / BUSINESS_LAW / SCIENCE / COMPUTING_ENGINEERING / MEDICINE_HEALTH / etc.)")
  nfq_level QQILevel @description("NFQ level of the final award (NFQ_7 for Ord BA, NFQ_8 for Hons BA, NFQ_9 for Masters)")
  duration_months int @description("Typical duration in months (36 for Ord BA, 48 for Hons BA, 12 for HDip)")
  points_required int? @description("Median CAO points required for an offer (latest available round; null if mature applicant only)")
  mature_applicant_path bool @description("True if the course accepts mature applicants separately (e.g. via the Mature Applicants Office)")
  source_url string @description("Canonical CAO URL, e.g. 'https://www.cao.ie/index.php?page=courses&course=GY101'")
  scraped_at string @description("ISO-8601 timestamp of the scrape")
  confidence float @description("Overall extraction confidence 0.0-1.0")
  @@stream.done
}

// =============================================================================
// SOLASCourse — a SOLAS Further Education course (PLC / apprenticeship / etc.)
// =============================================================================

class SOLASCourse {
  course_code string @description("SOLAS / fetchcourses.ie course code, e.g. 'PLC-DIT-CS-2025'")
  etb_slug string @description("The 16 ETBs slug, e.g. 'cavan-monaghan', 'city-of-dublin', 'galway-roscommon'")
  etb_name string @description("The full ETB name, e.g. 'Galway and Roscommon ETB'")
  course_title string @description("Course title, e.g. 'Post-Leaving-Cert in Software Development'")
  solas_path SOLASPath @description("The SOLAS pathway (PLC / APPRENTICESHIP / YOUTHREACH / etc.)")
  qqi_level QQILevel @description("NFQ level the course leads to (NFQ_5 / NFQ_6 most commonly for PLCs)")
  duration_months int @description("Typical duration in months (8-24 for PLCs, 24-48 for apprenticeships)")
  award_code string? @description("The QQI award code on completion, e.g. 'NFQ6-HC'; null if not QQI-anchored")
  fetchcourses_url string @description("The canonical fetchcourses.ie URL for this course")
  scraped_at string @description("ISO-8601 timestamp of the scrape")
  confidence float @description("Overall extraction confidence 0.0-1.0")
  @@stream.done
}

// =============================================================================
// Functions (Tertiary 18+)
// =============================================================================

function ExtractUniversityInfo(
  page_markdown: string,
  institution_id: string
) -> University {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

function ExtractTuInfo(
  page_markdown: string,
  tu_id: string
) -> TU {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

function ExtractQQIAward(
  page_markdown: string,
  award_code: string
) -> QQIAward {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

function ExtractCAOChoice(
  page_markdown: string,
  cao_code: string
) -> CAOChoice {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

function ExtractSOLASCourse(
  page_markdown: string,
  course_code: string
) -> SOLASCourse {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

// =============================================================================
// Tests (Tertiary 18+)
// =============================================================================

// test ExtractUniversityInfoTest {
//   functions [ExtractUniversityInfo]
//   args {
//     page_markdown #"
//       # University of Galway — About Us
// 
//       The University of Galway (UoG, formerly NUI Galway, founded 1845)
//       is one of the 8 Republic of Ireland universities. We are a leading
//       research-intensive institution with 5 faculties:
// 
//       - Arts, Social Sciences and Celtic Studies
//       - Business, Public Policy and Law
//       - College of Science and Engineering
//       - Medicine, Nursing and Health Sciences
// 
//       We award NFQ Level 6 (Higher Certificate) through NFQ Level 10
//       (Doctoral Degree).
//     "#
//     institution_id "ie-university-galway"
//   }
// }

// test ExtractQQIAwardTest {
//   functions [ExtractQQIAward]
//   args {
//     page_markdown #"
//       # Bachelor Degree (Honours) — NFQ Level 8
// 
//       The Bachelor Degree (Honours) is a 4-year full-time programme
//       at NFQ Level 8, totalling 240 ECTS credits on graduation.
//       It is awarded by QQI and is the standard undergraduate honours
//       degree in Ireland (B.Sc. Hons, B.A. Hons, B.Ed., B.Eng., etc.).
//     "#
//     award_code "NFQ8-BA-HONS"
//   }
// }

// test ExtractCAOChoiceTest {
//   functions [ExtractCAOChoice]
//   args {
//     page_markdown #"
//       # GY101 — Bachelor of Arts (Arts, Social Sciences and Celtic Studies)
// 
//       Institution: University of Galway
//       Duration: 4 years (NFQ Level 8, Honours Bachelor Degree)
//       Field: Arts, Humanities, Social Sciences
// 
//       ## CAO Points
//       Latest round 1: 356 points (median)
// 
//       ## Mature Applicants
//       This course accepts applications from mature applicants (21+ on
//       1 January of the year of entry) via the Mature Applicants Office.
//     "#
//     cao_code "GY101"
//   }
// }
