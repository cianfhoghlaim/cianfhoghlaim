// =============================================================================
// Tertiary (post-Leaving Certificate) — BAML Schema
// Bilingual EN/GA extraction of CAO courses, NUI/HEI matriculation, QQI FET awards,
// and Apprenticeship pathways. See:
//   docs/tuatha/Learn-to-Earn Blockchain and AI.md:25 (H6+25 bonus)
//   docs/bonneagar/cognee-entity-resolution.md:144 (CAO points)
//   docs/data_engineering/Ontology and Temporal Graphs Research.md:6,310,348
//   docs/web/BAML, Graphiti, Tanstack AI Pipeline.md:240-314 (CAO points table)
// =============================================================================

// -----------------------------------------------------------------------------
// Enums
// -----------------------------------------------------------------------------

enum NFQLevel {
  NFQ_1  @description("NFQ Level 1 — Foundation")
  NFQ_2  @description("NFQ Level 2 — Foundation")
  NFQ_3  @description("NFQ Level 3 — Junior Cycle equivalent")
  NFQ_4  @description("NFQ Level 4 — Leaving Certificate equivalent")
  NFQ_5  @description("NFQ Level 5 — QQI Level 5 Certificate")
  NFQ_6  @description("NFQ Level 6 — QQI Level 6 Advanced Certificate")
  NFQ_7  @description("NFQ Level 7 — Ordinary Bachelor Degree")
  NFQ_8  @description("NFQ Level 8 — Honours Bachelor Degree")
  NFQ_9  @description("NFQ Level 9 — Masters Degree / Postgraduate Diploma")
  NFQ_10 @description("NFQ Level 10 — Doctoral Degree")
}

enum EQFLevel {
  EQF_3
  EQF_4
  EQF_5
  EQF_6
  EQF_7
  EQF_8
}

enum HEIType {
  UNIVERSITY                @description("NUI/UCD/UCG/UCC/UL/Maynooth, Trinity, etc.")
  INSTITUTE_OF_TECHNOLOGY   @description("ATU (Atlantic TU), TUS, SETU, MTU")
  COLLEGE_OF_EDUCATION      @description("Froebel, Marino, MIC, etc.")
  PRIVATE_COLLEGE           @description("DBS, NCI, etc.")
  RCSI                      @description("Royal College of Surgeons in Ireland")
  MARY_IMMACULATE_COLLEGE   @description("MIC, Limerick")
}

enum EntryPathway {
  LEAVING_CERTIFICATE @description("Standard LC entry")
  QQI_FET             @description("QQI Further Education & Training award")
  MATURE_STUDENT      @description("Mature student entry (23+ for undergrad)")
  DARE                @description("Disability Access Route to Education")
  HEAR                @description("Higher Education Access Route")
  INTERNATIONAL       @description("Non-EU/international student")
  GRADUATE            @description("Postgraduate entry")
  APPRENTICESHIP      @description("Craft/apprenticeship-to-degree progression")
}

enum Specialism {
  SCIENCES
  LANGUAGES
  BUSINESS
  HUMANITIES
  PRACTICAL
  ARTS
  APPLIED
  INTERDISCIPLINARY
}

enum ExamLevel {
  FOUNDATION @description("Foundation level (LC Maths only currently)")
  ORDINARY
  HIGHER
  COMMON   @description("Common level (no foundation/ordinary split)")
}

// -----------------------------------------------------------------------------
// Classes
// -----------------------------------------------------------------------------

class MatriculationRequirement {
  institution string             @description("NUI / University of Galway / Trinity / DCU / UL / UCC / UCD / Maynooth / ATU / TUS / SETU / MTU / RCSI / MIC")
  pathway EntryPathway
  level ExamLevel
  subject string                 @description("LC subject code, e.g., 'mathematics', 'irish', 'english'")
  minimum_grade string           @description("e.g., 'H4', 'O6', 'H6'")
  notes string?                  @description("e.g., 'required for Modern Languages', 'lab science required for Medicine'")
}

class CAOCourse {
  course_code string             @description("e.g., 'GY101' (Arts, UCG), 'GY301' (Medicine, UCG), 'CK101', 'TR001'")
  title_en string
  title_ga string?
  institution string
  hei_type HEIType
  nfq_level NFQLevel
  duration_years int
  points_2024 int?
  points_2023 int?
  points_2022 int?
  points_midpoint int?          @description("Rolling 3-year midpoint for ranking prediction")
  language string                @description("Primary medium: en | ga | bilingual")
  subjects_required MatriculationRequirement[]
  points_required int            @description("Cutoff points from the most recent cycle")
  specialism Specialism?
  cao_url string?
  application_pathways EntryPathway[]
}

class QqiFetAward {
  award_code string              @description("e.g., '5M2787' (Software Development)")
  title_en string
  title_ga string?
  nfq_level NFQLevel
  institution string
  links_to_courses string[]      @description("CAO course codes this FET award can ladder into")
  source_url string
}

class Apprenticeship {
  programme_code string
  title_en string
  title_ga string?
  duration_years int
  nfq_level NFQLevel
  consortia_lead string          @description("Lead coordinating provider")
  consortia_partners string[]
  source_url string
}

class Programme {
  course_code string
  faculty string
  department string
  modules_year_1 string[]
  modules_year_2 string[]
  modules_year_3 string[]
  modules_year_4 string[]
  work_placement bool
  study_abroad bool
  description_en string
  description_ga string?
}

class ApplicationTimeline {
  course_code string
  year int                       @description("Application year, e.g., 2026")
  cao_open_date string           @description("e.g., '2025-11-05'")
  cao_close_date string          @description("e.g., '2026-02-01'")
  late_application_close string?
  offer_round_1 string           @description("e.g., '2026-08-21'")
  offer_round_2 string?
  registration_open string
}

class CAOGradeProfile {
  course_code string
  year int
  median_points int
  median_grades map<string, string>  @description("subject → H1-H8 / O1-O8 typical distribution")
  random_drawn float                  @description("Random selection indicator 0-1")
}

class CoursePointsPrediction {
  course_code string
  predicted_cutoff int
  confidence float
  rationale_en string
  rationale_ga string?
}

class MatriculationAudit {
  institution string
  pathway EntryPathway
  passed bool
  failed_requirements MatriculationRequirement[]
  near_misses MatriculationRequirement[]  @description("One grade short of the requirement")
  summary_en string
  summary_ga string?
}

// -----------------------------------------------------------------------------
// Functions
// -----------------------------------------------------------------------------

function ExtractCAOCourseList(page_markdown: string, year: int) -> CAOCourse[] {
  client "litellm/gemini-2.0-flash"
  prompt #"
    You are an expert Irish CAO course directory analyst.

    Extract the list of CAO courses from the page markdown for the given year.
    For each course capture: course_code, title_en, title_ga, institution, hei_type,
    nfq_level, duration_years, points_required, language, subjects_required,
    specialism, cao_url.

    CRITICAL: Preserve the 3-year points history (points_2022, points_2023, points_2024)
    and the rolling 3-year midpoint (points_midpoint).
    Extract BOTH English and Irish versions of the title.

    YEAR: {{ year }}

    PAGE MARKDOWN:
    {{ page_markdown }}

    Return CAOCourse[] as {{ ctx.output_format }}.
  "#
}

function ExtractMatriculationRules(page_markdown: string, institution: string) -> MatriculationRequirement[] {
  client "litellm/gemini-2.0-flash"
  prompt #"
    You are an expert Irish matriculation requirements analyst.

    Extract the matriculation rules for the given institution.
    For NUI institutions, the standard rules are:
    - 3 H5s (one in English, Irish, Maths)
    - 4 O6/H7s (including Maths and English/Irish)
    - Specific subject + grade requirements for certain courses (e.g., H4 in
      Chemistry for Medicine, H4 in a language for Modern Languages)

    For Trinity (TCD) the rules are:
    - 4 H5s (one in English, Maths, a language, a third subject)
    - 3 O6/H7s
    - Specific course requirements

    For IoTs (ATU/TUS/SETU/MTU), the rules are simpler (5 O6/H7s, Maths required).

    CRITICAL: Capture the institution, pathway, subject, minimum_grade, and any notes.

    INSTITUTION: {{ institution }}

    PAGE MARKDOWN:
    {{ page_markdown }}

    Return MatriculationRequirement[] as {{ ctx.output_format }}.
  "#
}

function ExtractQQIFetAwards(page_markdown: string) -> QqiFetAward[] {
  client "litellm/gemini-2.0-flash"
  prompt #"
    You are an expert Irish QQI FET award directory analyst.

    Extract every QQI FET (Further Education & Training) award from the page markdown.
    For each capture: award_code, title_en, title_ga, nfq_level, institution,
    links_to_courses (CAO course codes this award ladders into).

    PAGE MARKDOWN:
    {{ page_markdown }}

    Return QqiFetAward[] as {{ ctx.output_format }}.
  "#
}

function ExtractApprenticeshipListings(page_markdown: string) -> Apprenticeship[] {
  client "litellm/gemini-2.0-flash"
  prompt #"
    You are an expert Irish Apprenticeship directory analyst.

    Extract every Apprenticeship programme from the page markdown.
    For each capture: programme_code, title_en, title_ga, duration_years, nfq_level,
    consortia_lead, consortia_partners, source_url.

    PAGE MARKDOWN:
    {{ page_markdown }}

    Return Apprenticeship[] as {{ ctx.output_format }}.
  "#
}

function ExtractApplicationTimeline(page_markdown: string, year: int) -> ApplicationTimeline[] {
  client "litellm/gemini-2.0-flash"
  prompt #"
    You are an expert Irish CAO application timeline analyst.

    Extract the CAO application timeline for the given year.
    Capture: cao_open_date, cao_close_date, late_application_close, offer_round_1,
    offer_round_2, registration_open.

    YEAR: {{ year }}

    PAGE MARKDOWN:
    {{ page_markdown }}

    Return ApplicationTimeline[] as {{ ctx.output_format }}.
  "#
}

function EstimateCoursePoints(
  course: CAOCourse,
  applicant_grades: map<string, string>,
  historical: CAOGradeProfile[]
) -> CoursePointsPrediction {
  client "litellm/gemini-2.0-flash"
  prompt #"
    You are an expert Irish CAO points analyst.

    Given the course, the applicant's projected LC grades (subject → H1-H8 / O1-O8),
    and the historical cutoff data, predict the likely cutoff points for this year
    and a confidence score (0-1).

    CRITICAL: Be conservative. Round to the nearest 5 points.

    COURSE: {{ course.title_en }} ({{ course.course_code }})
    HISTORICAL MIDPOINT: {{ course.points_midpoint }}
    APPLICANT GRADES: {{ applicant_grades }}

    Return CoursePointsPrediction as {{ ctx.output_format }}.
  "#
}

function AuditMatriculation(
  institution: string,
  pathway: EntryPathway,
  applicant_grades: map<string, string>,
  rules: MatriculationRequirement[]
) -> MatriculationAudit {
  client "litellm/anthropic/claude-sonnet-4-20250514"
  prompt #"
    You are an expert Irish matriculation auditor.

    Check the applicant's LC grades against the matriculation rules for the institution.
    Capture failed requirements and near-misses (one grade short).
    Produce a bilingual summary explaining the result.

    INSTITUTION: {{ institution }}
    PATHWAY: {{ pathway }}
    APPLICANT GRADES: {{ applicant_grades }}
    RULES: {{ rules }}

    Return MatriculationAudit as {{ ctx.output_format }}.
  "#
}
