// =============================================================================
// Tertiary (post-Leaving Certificate) — BAML Schema
// Bilingual EN/GA extraction of CAO courses, NUI/HEI matriculation, QQI FET awards,
// and Apprenticeship pathways. Merged from:
//   - baml/tertiary.baml (332 LOC) — the canonical tertiary schema
//   - baml/oideachais_other/tertiary.baml (79 LOC) — the URL-extraction variant
// See:
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
  @@stream.done
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
  cao_url string?
  application_pathways EntryPathway[]
  @@stream.done
}

class QqiFetAward {
  award_code string              @description("e.g., '5M2787' (Software Development)")
  title_en string
  title_ga string?
  nfq_level NFQLevel
  institution string
  links_to_courses string[]      @description("CAO course codes this FET award can ladder into")
  source_url string
  @@stream.done
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
  @@stream.done
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
  @@stream.done
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

function ExtractApprenticeshipListings(page_markdown: string) -> Apprenticeship {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"You are an expert at parsing Irish Apprenticeship programme listings.

Parse the SOLAS (or equivalent) apprenticeship directory.

PAGE MARKDOWN:
{{ page_markdown }}

For each apprenticeship programme, extract:
1. Programme name (e.g., "Electrician", "Carpentry & Joinery", "Plumbing", "Software Developer")
2. Trade/sector classification
3. Awarding body (SOLAS, ETB, IMI, etc.)
4. Duration (typically 2-4 years)
5. NFQ level (5-8)
6. Off-the-job training location
7. On-the-job employer requirements
8. Entry requirements (minimum age, education)
9. Progression routes to higher education (CAO courses, university pathways)
10. Source URL

Apprenticeships are an ALTERNATIVE pathway to CAO courses, particularly for craft and technical trades.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    ENTRIES: {{ page_markdown|length }} chars
"#
}


function ExtractApplicationTimeline(page_markdown: string,
  year: int) -> ApplicationTimeline {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"You are an expert at parsing the Irish CAO (Central Applications Office) application timeline.

Parse the CAO application timeline for a specific year.

YEAR: {{ year }}

PAGE MARKDOWN:
{{ page_markdown }}

Extract all critical dates and milestones:
1. Application opens (typically November of preceding year)
2. Application closes (typically February 1st)
3. Change of mind opens (typically May)
4. Change of mind closes (typically July 1st)
5. Round 1 offers (typically August)
6. Round 2 offers (typically late August)
7. Acceptance deadlines
8. Late application window
9. HEAR/DARE scheme deadlines
10. Mature applicant deadlines
11. QQI FET application deadlines

These dates power the ApplicationTimelineGuide agent in the Tertiary team. Be exact with dates and provide both year-specific and rolling calendar info.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    YEAR: {{ year }}
"#
}


function EstimateCoursePoints(course: CAOCourse,
  historical_points: int[],
  applicant_profile: string) -> CoursePointsPrediction {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"You are an expert at predicting CAO course points for an applicant.

Given a course's historical points data and an applicant's profile, estimate the points they'll need.

COURSE: {{ course.course_code }} - {{ course.title_en }}
HISTORICAL POINTS: {{ historical_points|join(", ") }}

APPLICANT PROFILE:
{{ applicant_profile }}

Provide:
1. Predicted points range (low and high)
2. Confidence level (high if data is strong, low if volatile)
3. Trend analysis (rising, falling, stable)
4. Key factors that could shift points this year (e.g., "new supply from neighbouring school", "popularity surge")
5. Recommendation (apply, strong backup needed, or re-consider)
6. Alternative courses to consider (similar level, similar subject, nearby institution)

This powers the Tertiary team's points estimation feature.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    COURSE: {{ course.course_code }}
    YEARS: {{ historical_points|length }}
"#
}


function AuditMatriculation(institution: string,
  course_code: string,
  applicant_grades: string) -> MatriculationAudit {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"You are an expert at auditing a student's Leaving Certificate grades against NUI/HEI matriculation requirements.

Audit the applicant's grades against the matriculation rules for a specific course.

INSTITUTION: {{ institution }}
COURSE: {{ course_code }}

APPLICANT GRADES:
{{ applicant_grades }}

Provide:
1. Overall pass/fail status
2. Per-requirement analysis (which subject/grade combinations meet/fail/miss)
3. Near-miss subjects (one grade short of meeting the requirement)
4. Failed requirements (subjects not taken or grades too low)
5. Compensating subjects (if NUI allows compensation)
6. Recommendations (could the applicant re-sit, apply for QQI FET, etc.)
7. Alternative courses that match the applicant's profile
8. Bilingual feedback labels

This audit is the critical decision-support feature for the MatriculationCheck agent.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    INSTITUTION: {{ institution }}
    COURSE: {{ course_code }}
"#
}


// =============================================================================
// From-URL extraction functions (merged from oideachais_other/tertiary.baml)
// =============================================================================

function ExtractCAOCourseListFromUrl(page_url: string, year: int) -> CAOCourse[] {
  client "litellm/gemini-2.0-flash"
  prompt #"
    You are an expert Irish CAO course directory analyst working for
    Cianfhoghlaim Oideachais (the bilingual agentic platform).

    Source: {{ page_url }}
    Year: {{ year }}

    CAO course codes are 2-3 characters: UCD=DN*, UCG=GY*, UCC=CK*, UL=LM*,
    MU=MH*, TCD=TR*, DCU=DC*, ATU=GA*/LY*/SG*/AL*, TUS=LC*/TL*, SETU=WD*/CW*,
    MTU=CR*/MT*, RCSI=RC*, MIC=MI*.

    The 10 NFQ levels (1-10) are defined per Irish National Framework of
    Qualifications. Typical CAO courses are NFQ_7 (Level 7 Ordinary Bachelor)
    or NFQ_8 (Level 8 Honours Bachelor).

    Always extract BOTH English and Irish versions of the title.

    Return CAOCourse[] as {{ ctx.output_format }}.
  "#
}

function ExtractMatriculationRulesFromUrl(page_url: string, institution: string) -> MatriculationRequirement[] {
  client "litellm/gemini-2.0-flash"
  prompt #"
    You are an expert Irish matriculation requirements analyst working for
    Cianfhoghlaim Oideachais.

    Source: {{ page_url }}
    Institution: {{ institution }}

    The NUI standard matriculation rules are:
      - 3 H5s (Higher level) including English, Irish, Mathematics
      - 4 O6/H7s (Ordinary or Higher level) including English, Irish, Mathematics
      - Specific subject + grade requirements for certain courses:
        H4 in Chemistry for Medicine
        H4 in a Modern Continental Language for Modern Languages
        H4 in Physics for Engineering
      - For non-NUI (TCD, DCU, IoTs), different rules apply

    Always capture the institution, pathway, subject, minimum_grade (H4, O6, etc.),
    and any notes (e.g., "required for Modern Languages", "lab science required for
    Medicine").

    Return MatriculationRequirement[] as {{ ctx.output_format }}.
  "#
}

function AuditMatriculationStdLib(
  institution: string,
  applicant_grades: map<string, string>
) -> MatriculationAudit {
  client "litellm/anthropic/claude-sonnet-4-20250514"
  prompt #"
    You are an expert Irish matriculation auditor working for
    Cianfhoghlaim Oideachais.

    INSTITUTION: {{ institution }}
    APPLICANT GRADES: {{ applicant_grades }}

    Check the applicant's LC grades against the matriculation rules for the
    given institution. Capture failed requirements and near-misses (one
    grade short). Produce a bilingual summary explaining the result.

    CAO points table (for context):
      H1: 100, H2: 88, H3: 77, H4: 66, H5: 56, H6: 46, H7: 37, H8: 0
      O1: 56, O2: 46, O3: 37, O4: 28, O5: 20, O6: 12, O7: 0, O8: 0
      Bonus: H6 or higher in Higher Level Mathematics awards +25 points

    Return MatriculationAudit as {{ ctx.output_format }}.
  "#
}