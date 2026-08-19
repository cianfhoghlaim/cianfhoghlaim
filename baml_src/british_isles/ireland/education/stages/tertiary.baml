// =============================================================================
// Tertiary (post-Leaving Certificate) — BAML Schema
// Bilingual EN/GA extraction of CAO courses, NUI/HEI matriculation, QQI FET awards,
// and Apprenticeship pathways. Merged from:
//   - baml/tertiary.baml (332 LOC) — the canonical tertiary schema
//   - baml/cianfhoghlaim_other/tertiary.baml (79 LOC) — the URL-extraction variant
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

class CaliforniaOCourse {
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

class CaliforniaOGradeProfile {
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

function ExtractCaliforniaOCourseList(page_markdown: string, year: int) -> CaliforniaOCourse[] {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#

  catch_all (err) {
    CaliforniaOCourse[] {}
  }
}

function ExtractMatriculationRules(page_markdown: string, institution: string) -> MatriculationRequirement[] {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#

  catch_all (err) {
    MatriculationRequirement[] {}
  }
}

function ExtractQQIFetAwards(page_markdown: string) -> QqiFetAward[] {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#

  catch_all (err) {
    QqiFetAward[] {}
  }
}

function ExtractApprenticeshipListings(page_markdown: string) -> Apprenticeship {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#

  catch_all (err) {
    Apprenticeship {
      programme_code "",
      title_en "",
      title_ga null,
      duration_years 0,
      nfq_level nfqlevel {},
      consortia_partners null,
      source_url "",
    }
  }
}


function ExtractApplicationTimeline(page_markdown: string,
  year: int) -> ApplicationTimeline {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#

  catch_all (err) {
    ApplicationTimeline {
      course_code "",
      late_application_close null,
      offer_round_2 null,
      registration_open "",
    }
  }
}


function EstimateCoursePoints(course: SOLASCourse,
  historical_points: int[],
  applicant_profile: string) -> CoursePointsPrediction {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}


function AuditMatriculation(institution: string,
  course_code: string,
  applicant_grades: string) -> MatriculationAudit {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}


// =============================================================================
// From-URL extraction functions (merged from cianfhoghlaim_other/tertiary.baml)
// =============================================================================

function ExtractCaliforniaOCourseListFromUrl(page_url: string, year: int) -> CaliforniaOCourse[] {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#

  catch_all (err) {
    CaliforniaOCourse[] {}
  }
}

function ExtractMatriculationRulesFromUrl(page_url: string, institution: string) -> MatriculationRequirement[] {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#

  catch_all (err) {
    MatriculationRequirement[] {}
  }
}

function AuditMatriculationStdLib(
  institution: string,
  applicant_grades: map<string, string>
) -> MatriculationAudit {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}