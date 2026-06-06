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
  // (see below for additional enums)
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
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"Extract the requested data.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    {{page_markdown}}
"#
}

function ExtractMatriculationRules(page_markdown: string, institution: string) -> MatriculationRequirement[] {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"Extract the requested data.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    {{page_markdown}}
"#
}

function ExtractQQIFetAwards(page_markdown: string) -> QqiFetAward[] {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"Extract the requested data.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    {{page_markdown}}
"#
}

function ExtractApprenticeshipListings(page_markdown: string) -> Apprenticeship[] {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"Extract the requested data.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    {{page_markdown}}
"#
}

function ExtractApplicationTimeline(page_markdown: string, year: int) -> ApplicationTimeline[] {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"Extract the requested data.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    {{page_markdown}}
"#
}

function EstimateCoursePoints(course: CAOCourse,
  applicant_grades: map<string, string>,
  historical: CAOGradeProfile[]) -> CoursePointsPrediction {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"Extract the requested data.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    {{course}}
    {{applicant_grades}}
    {{historical}}
"#
}

function AuditMatriculation(institution: string,
  pathway: EntryPathway,
  applicant_grades: map<string, string>,
  rules: MatriculationRequirement[]) -> MatriculationAudit {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"Extract the requested data.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    {{institution}}
    {{pathway}}
    {{applicant_grades}}
    {{rules}}
"#
}
