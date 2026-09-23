// BAML Schema for Tertiary Deep Extraction (4-tier)
//
// Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/.
//
// Structured extraction of 4 academic-website artefact types for any
// British Isles university (case study: University of Galway / Ollscoil
// na Gaillimhe):
//   1. College (top tier — UoG has 4)
//   2. School (within a college — UoG has ~10)
//   3. Programme (degree — UoG has ~200)
//   4. Module (course within a programme — UoG has ~1,500)
//
// Plus the per-module deep-extraction functions:
//   - ModuleHandbook (PDF extraction)
//   - ReadingList (extracted from PDFs)
//   - PastPaper (extracted from regexam.nuigalway.ie)
//
// This file supersedes the prior `CourseDescriptor` / `ModuleDescriptor` /
// `ProgrammeDescriptor` triple (per the schema consolidation in
// 2026-09-23-consolidate-uog-tertiary-pipeline-v1). The KCG
// `CourseOutline` class (16 fields) maps 1-to-1 onto the new `Module`
// class; we ADD 4 new fields (learning_outcomes[], reading_list[],
// past_paper_urls[], handbook_pdf_url?) which are exactly the
// "more in-depth module-specific materials" the user asked for.
//
// All 6 functions route through the canonical `ExtractEn` LiteLLM
// client (defined in `clients.baml`; the gateway alias `extract-en`
// resolves to gemini-2.5-flash → glm-4.6 → gemini-1.5-flash).

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
  MICRO_CREDENTIAL @description("Short-form credential (<10 ECTS)")
  UNKNOWN         @description("Stage cannot be inferred from the page")
}

enum Semester {
  SEMESTER_1      @description("Autumn / Semester 1 (S1)")
  SEMESTER_2      @description("Spring / Semester 2 (S2)")
  YEAR_LONG       @description("Full academic year (S1 + S2 or year-long)")
  SUMMER          @description("Summer period")
  UNKNOWN         @description("Semester cannot be inferred from the page")
}

enum StudyMode {
  FULL_TIME       @description("Full-time study")
  PART_TIME       @description("Part-time study")
  BOTH            @description("Both full-time and part-time options available")
  ONLINE          @description("Online / distance learning only")
  BLENDED         @description("Blended (mix of in-person + online)")
  UNKNOWN         @description("Study mode cannot be inferred")
}

enum ReadingFormat {
  ISBN_13         @description("A 13-digit ISBN (e.g. '9780262033848')")
  DOI             @description("A Digital Object Identifier (e.g. '10.1038/nature12373')")
  URL             @description("A free-form URL to the resource (web article, PDF, etc.)")
  INTERNAL_REF    @description("An internal library reference (e.g. 'Library Reserve: HF1234')")
  OTHER           @description("None of the above (no standard identifier visible)")
}

enum DeliveryLanguage {
  EN              @description("English-medium instruction")
  GA              @description("Irish (Gaeilge)-medium instruction")
  BI              @description("Bilingual EN/GA instruction")
  UNKNOWN         @description("Delivery language cannot be inferred")
}

enum Campus {
  GALWAY_MAIN     @description("Galway (main campus)")
  GAELTACHT       @description("Gaeltacht na Gaillimhe / Cheathrú Rua")
  SHANNON         @description("Shannon College of Hotel Management")
  ONLINE          @description("Online / distance")
  OTHER           @description("Other UoG campus")
}

// =============================================================================
// Tier 1: College
// =============================================================================

class College {
  college_id string @description("Canonical kebab-case slug, e.g. 'science-engineering'")
  college_name_english string @description("Full English name, e.g. 'College of Science and Engineering'")
  college_name_irish string? @description("Full Irish name, e.g. 'Coláiste na hEolaíochta agus na hInnealtóireachta'")
  dean_name string? @description("Name of the current Dean, e.g. 'Prof. M. O'Brien'")
  source_url string @description("Canonical URL of the college's overview page")
  nfq_min int @description("Lowest NFQ level the college awards degrees at (e.g. 6 for Higher Certificate)")
  nfq_max int @description("Highest NFQ level the college awards degrees at (e.g. 10 for PhD)")
  established_year int? @description("Year the college was founded, e.g. 1845 for UoG")
  school_count int? @description("Number of schools within the college, e.g. 4 for College of Science and Engineering")
  scraped_at string @description("ISO-8601 timestamp of the scrape")
  confidence float @description("Overall extraction confidence 0.0-1.0")
}

// =============================================================================
// Tier 2: School
// =============================================================================

class School {
  school_id string @description("Canonical kebab-case slug, e.g. 'school-computer-science'")
  college_id string @description("FK → College.college_id")
  school_name_english string @description("Full English name, e.g. 'School of Computer Science'")
  school_name_irish string? @description("Full Irish name, e.g. 'Scoil na Ríomheolaíochta'")
  head_of_school string? @description("Name of the current Head of School")
  n_students int? @description("Approximate undergraduate + postgraduate headcount")
  n_staff int? @description("Approximate academic staff count")
  research_centres string[] @description("Research centres affiliated with the school, e.g. ['Lero', 'Data Science Institute']")
  source_url string @description("Canonical URL of the school's overview page")
  scraped_at string @description("ISO-8601 timestamp of the scrape")
  confidence float @description("Overall extraction confidence 0.0-1.0")
}

// =============================================================================
// Tier 3: Programme
// =============================================================================

class Programme {
  programme_id string @description("Canonical kebab-case slug, e.g. 'bsc-computer-science'")
  programme_code string @description("Programme code (CAO or internal), e.g. 'GZ01' for BSc CS")
  school_id string @description("FK → School.school_id")
  title_english string @description("Full programme title, e.g. 'Bachelor of Science (Computer Science)'")
  title_irish string? @description("Full programme title in Irish")
  nfq_level NfqLevel @description("NFQ level of the final award (NFQ_8 for BSc Hons, NFQ_9 for MSc)")
  stage ProgrammeStage @description("Programme stage (UNDERGRADUATE / POSTGRADUATE / etc.)")
  duration_months int @description("Programme duration in months (12 for 1-year MSc, 48 for 4-year BSc)")
  mode StudyMode @description("Study mode (full-time / part-time / both / online / blended)")
  total_ects int @description("Total ECTS to graduate (60 for 1-year MSc, 240 for 4-year BSc)")
  cao_code string? @description("CAO code for undergraduate entry, e.g. 'GZ01' (null for postgraduate)")
  module_codes string[] @description("Module codes that make up the programme (6-20 modules); 0-N entries")
  entry_requirements string @description("1-3 sentence entry-requirements summary")
  delivery_language DeliveryLanguage @description("Primary delivery language")
  source_url string @description("Canonical URL of the programme's overview page")
  scraped_at string @description("ISO-8601 timestamp of the scrape")
  confidence float @description("Overall extraction confidence 0.0-1.0")
}

// =============================================================================
// Tier 4: Module
// =============================================================================
//
// The Module class consolidates the KCG `CourseOutline` (16 fields) +
// the legacy cianfhoghlaim `CourseDescriptor`/`ModuleDescriptor`
// (~14 fields) + 4 new in-depth fields. This is the canonical module
// schema across the BIEP v3 tertiary pipeline.

class AssessmentBreakdown {
  exam_weight_percent int? @description("Final-exam weight 0-100, or null if continuous assessment only")
  ca_weight_percent int? @description("Continuous assessment weight 0-100, or null if exam only")
  ca_components string[] @description("Names of CA components (e.g. ['assignment_1', 'midterm_test']); empty if unknown")
}

class LecturerInfo {
  name string @description("Full name, e.g. 'Dr. John McCarthy'")
  email string? @description("University email address if visible, else null")
  school string @description("The lecturer's school / department")
  profile_url string? @description("URL of the lecturer's staff profile page, or null")
  is_coordinator bool @description("True if this lecturer is the module coordinator")
}

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

class Module {
  // Identity
  module_id string @description("Canonical kebab-case slug, e.g. 'cs203-data-structures'")
  module_code string @description("User-visible module code, e.g. 'CS203'")
  programme_ids string[] @description("FK → Programme.programme_id (many-to-many); modules can belong to multiple programmes")
  school_id string @description("FK → School.school_id")

  // Titles
  title_english string @description("Full module title in English, e.g. 'Data Structures'")
  title_irish string? @description("Full module title in Irish, e.g. 'Struchtúir Sonraí'")

  // Classification (from KCG CourseOutline)
  level ProgrammeStage @description("Stage (UNDERGRADUATE / POSTGRADUATE / PROFESSIONAL / MICRO_CREDENTIAL)")
  year_of_study int? @description("Year of study within the programme (1-4 for BSc; null if not visible)")
  semester Semester @description("Which semester the module runs in")
  ects_credits int @description("ECTS credit value, 1-30 (5 and 10 are the most common)")
  faculty string? @description("Legacy field — mapped from College.college_name_english for BIEP join compatibility")
  campus Campus @description("Which campus the module is delivered at")
  mode StudyMode @description("Study mode (full-time / part-time / blended / online)")
  delivery_language DeliveryLanguage @description("Delivery language (EN / GA / BI)")
  academic_year string @description("Academic year, e.g. '2025/26'")

  // People
  lecturer_lead string? @description("Lead lecturer name (the coordinator)")

  // Content (from KCG CourseOutline + new in-depth fields)
  description_short string @description("2-4 sentence module description")
  learning_outcomes_count int @description("Number of learning outcomes (3-10)")
  learning_outcomes string[] @description("The actual learning outcome bullets, each a single sentence")
  assessment_methods string[] @description("List of assessment types, e.g. ['exam', 'continuous_assessment', 'practical']")
  assessment AssessmentBreakdown? @description("Detailed assessment breakdown, or null if not visible")
  prerequisite_module_codes string[] @description("Formal prerequisite module codes (e.g. ['CS102']); empty if none")

  // Deep extraction sources (NEW in this change)
  syllabus_url string? @description("URL of the syllabus page on universityofgalway.ie (public)")
  handbook_pdf_url string? @description("URL of the per-module PDF handbook (e.g. https://www.universityofgalway.ie/programmes/bsc-computer-science/cs203.pdf)")
  reading_list ReadingListItem[] @description("3-10 reading-list items extracted from the handbook PDF")
  past_paper_urls string[] @description("Links to past exam papers for this module on regexam.nuigalway.ie (authenticated; per-user credential vault)")

  // Provenance
  source_url string @description("Canonical URL this descriptor was extracted from")
  scraped_at string @description("ISO-8601 timestamp of the scrape")
  confidence float @description("Overall extraction confidence 0.0-1.0")
  @@stream.done
}

// =============================================================================
// Per-module deep extraction classes
// =============================================================================

class ModuleHandbookSection {
  section_title string @description("Heading from the handbook, e.g. 'Aims & Objectives'")
  section_body string @description("Full markdown body of the section")
  confidence float @description("Extraction confidence 0.0-1.0")
}

class ModuleHandbook {
  module_code string @description("FK → Module.module_code")
  pdf_url string @description("URL of the source PDF")
  sections ModuleHandbookSection[] @description("The 6-12 canonical handbook sections, in document order")
  total_pages int @description("Number of pages in the source PDF")
  scraped_at string @description("ISO-8601 timestamp of the scrape")
  confidence float @description("Overall extraction confidence 0.0-1.0")
}

class PastPaper {
  paper_id string @description("Canonical paper ID, e.g. 'CS203-2024-P1'")
  module_code string @description("FK → Module.module_code")
  year int @description("Examination year, e.g. 2024")
  paper_number int @description("Paper number (1, 2, or 3 for some modules)")
  pdf_url string @description("Direct URL to the past paper PDF on regexam.nuigalway.ie")
  has_marking_scheme bool @description("True if a marking scheme PDF is also available")
  marking_scheme_url string? @description("URL to the marking scheme PDF (if has_marking_scheme = true)")
  scraped_at string @description("ISO-8601 timestamp of the scrape")
}

// =============================================================================
// Functions
// =============================================================================

function ExtractCollege(college_page_markdown: string, college_url: string) -> College {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting University of Galway college metadata
    from the college's overview page.

    Extract: college_id (kebab-case slug), college_name_english + irish,
    dean_name, nfq_min + nfq_max, established_year, school_count.

    {{ ctx.output_format }}
    {{ input }}
  "#
}

function ExtractSchool(school_page_markdown: string, school_url: string) -> School {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting University of Galway school metadata
    from the school's overview page.

    Extract: school_id (kebab-case slug), college_id (FK),
    school_name_english + irish, head_of_school, n_students + n_staff,
    research_centres (array).

    {{ ctx.output_format }}
    {{ input }}
  "#
}

function ExtractProgramme(programme_page_markdown: string, programme_url: string) -> Programme {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting University of Galway programme metadata.

    Extract: programme_id (kebab-case slug), programme_code + cao_code,
    school_id (FK), title_english + irish, nfq_level, stage,
    duration_months, mode, total_ects, module_codes, entry_requirements,
    delivery_language.

    {{ ctx.output_format }}
    {{ input }}
  "#
}

function ExtractModule(module_page_markdown: string, module_url: string) -> Module {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting University of Galway module metadata.

    Extract: module_id (kebab-case slug), module_code, programme_ids[] + school_id,
    title_english + irish, level, year_of_study, semester, ects_credits,
    campus, mode, delivery_language, academic_year, lecturer_lead,
    description_short, learning_outcomes[] (the actual outcome text),
    assessment_methods[], assessment (AssessmentBreakdown),
    prerequisite_module_codes[], syllabus_url, handbook_pdf_url.

    University module pages follow a common template. The module_code is
    the canonical identifier.

    {{ ctx.output_format }}
    {{ input }}
  "#
}

function ExtractModuleHandbook(module_handbook_pdf_markdown: string, module_code: string) -> ModuleHandbook {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting the canonical 6-12 sections from a
    University of Galway module handbook PDF.

    For module {{ module_code }}, extract each section as
    {section_title, section_body}. Typical sections include:
    'Aims & Objectives', 'Learning Outcomes', 'Content',
    'Assessment', 'Reading List', 'Timetable', 'Contact'.

    {{ ctx.output_format }}
    {{ input }}
  "#
}

function ExtractPastPapers(modules_json: string) -> PastPaper[] {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at parsing the University of Galway regexam.nuigalway.ie
    archive structure. Given a JSON array of {module_code, year, paper_number,
    pdf_url, marking_scheme_url} records, return a structured PastPaper[] list.

    {{ ctx.output_format }}
    {{ input }}
  "#
}

// =============================================================================
// Authenticated UoA portal extraction (per the 2026-09-23 change)
// =============================================================================

class UoAPortalContent {
  source "regexam" | "canvas"
  module_code string? @description("The module code if visible (e.g. 'CS203')")
  title string @description("Content title (paper title, file name, etc.)")
  file_type "pdf" | "docx" | "pptx" | "mp4" | "image" | "other"
  file_url string @description("URL of the downloaded file (local R2 / S3 path or remote)")
  content_summary string @description("1-3 sentence summary of the content (LLM-generated)")
  scraped_at string @description("ISO-8601 timestamp")
  metadata dict<string, string> @description("Source-specific metadata (year, semester, lecturer, etc.)")
}

function ExtractUoAPortalContent(markdown: string, source: string) -> UoAPortalContent[] {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting structured content from authenticated
    University of Galway portal pages. The source is either 'regexam'
    (exam papers) or 'canvas' (course materials).

    For each item: title, module_code (if visible), file_type, content_summary.

    {{ ctx.output_format }}
    {{ input }}
  "#
}
