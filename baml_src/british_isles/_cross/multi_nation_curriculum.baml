// multi_nation_curriculum.baml
// BAML schemas for cross-nation curriculum comparison and alignment
// Extends isles_education.baml with nation-specific types and comparison functions

// ============================================================================
// NATION AND EDUCATION SYSTEM ENUMS
// ============================================================================

enum Nation {
  IRELAND @description("Republic of Ireland - NCCA/SEC system")
  ENGLAND @description("England - DfE National Curriculum + AQA/Edexcel/OCR")
  SCOTLAND @description("Scotland - Curriculum for Excellence + SQA")
  WALES @description("Wales - Curriculum for Wales + WJEC/CBAC")
  NORTHERN_IRELAND @description("Northern Ireland - NI Curriculum + CCEA")
  ISLE_OF_MAN @description("Isle of Man - follows UK with Manx additions")
}

enum NationEducationLevel {
  // Ireland
  IE_EARLY_CHILDHOOD @description("Aistear framework, ages 0-6")
  IE_PRIMARY @description("Primary school, classes 1-6")
  IE_JUNIOR_CYCLE @description("Junior Certificate, years 1-3")
  IE_TRANSITION_YEAR @description("Optional TY, year 4")
  IE_SENIOR_CYCLE @description("Leaving Certificate, years 5-6")

  // England
  EN_EARLY_YEARS @description("EYFS, ages 0-5")
  EN_KEY_STAGE_1 @description("Years 1-2, ages 5-7")
  EN_KEY_STAGE_2 @description("Years 3-6, ages 7-11")
  EN_KEY_STAGE_3 @description("Years 7-9, ages 11-14")
  EN_KEY_STAGE_4 @description("Years 10-11, GCSE, ages 14-16")
  EN_KEY_STAGE_5 @description("Years 12-13, A-Level, ages 16-18")

  // Scotland
  SC_EARLY_LEVEL @description("Pre-school to P1")
  SC_FIRST_LEVEL @description("P2-P4")
  SC_SECOND_LEVEL @description("P5-P7")
  SC_THIRD_LEVEL @description("S1-S3")
  SC_FOURTH_LEVEL @description("S4-S6 with National Qualifications")
  SC_NATIONAL_5 @description("SQA National 5")
  SC_HIGHER @description("SQA Higher")
  SC_ADVANCED_HIGHER @description("SQA Advanced Higher")

  // Wales
  WA_FOUNDATION_PHASE @description("Ages 3-7")
  WA_PROGRESSION_STEP_2 @description("Ages 7-11")
  WA_PROGRESSION_STEP_3 @description("Ages 11-14")
  WA_PROGRESSION_STEP_4 @description("Ages 14-16, GCSE")
  WA_POST_16 @description("A-Level and vocational")

  // Northern Ireland
  NI_FOUNDATION @description("Years 1-2, ages 4-6")
  NI_KEY_STAGE_1 @description("Years 3-4, ages 6-8")
  NI_KEY_STAGE_2 @description("Years 5-7, ages 8-11")
  NI_KEY_STAGE_3 @description("Years 8-10, ages 11-14")
  NI_KEY_STAGE_4 @description("Years 11-12, GCSE, ages 14-16")
  NI_POST_16 @description("A-Level and vocational")
}

enum QualificationBoard {
  // Ireland
  SEC @description("State Examinations Commission")
  NCCA @description("National Council for Curriculum and Assessment")

  // England
  AQA @description("Assessment and Qualifications Alliance")
  EDEXCEL @description("Pearson Edexcel")
  OCR @description("Oxford Cambridge and RSA")
  EDUQAS @description("WJEC Eduqas - in England")

  // Scotland
  SQA @description("Scottish Qualifications Authority")

  // Wales
  WJEC @description("Welsh Joint Education Committee")
  CBAC @description("Cyd-bwyllgor Addysg Cymru - Welsh language")

  // Northern Ireland
  CCEA @description("Council for the Curriculum, Examinations & Assessment")
}

// ============================================================================
// CURRICULUM FRAMEWORK TYPES
// ============================================================================

enum CurriculumFramework {
  // Ireland
  AISTEAR @description("Early childhood curriculum framework")
  PRIMARY_CURRICULUM @description("NCCA Primary Curriculum")
  JUNIOR_CYCLE @description("Junior Cycle Framework")
  SENIOR_CYCLE @description("Leaving Certificate programmes")

  // England
  EYFS @description("Early Years Foundation Stage")
  NATIONAL_CURRICULUM @description("National Curriculum for England")

  // Scotland
  CURRICULUM_FOR_EXCELLENCE @description("Curriculum for Excellence (CfE)")

  // Wales
  CURRICULUM_FOR_WALES @description("Curriculum for Wales (2022)")
  FOUNDATION_PHASE @description("Foundation Phase Framework")

  // Northern Ireland
  NI_CURRICULUM @description("Northern Ireland Curriculum")
}

// ============================================================================
// CROSS-NATION LEARNING OUTCOME
// ============================================================================

class CrossNationLearningOutcome {
  outcome_id string @description("Unique identifier")
  nation Nation
  level NationEducationLevel
  framework CurriculumFramework

  code string? @description("Official outcome code if available")
  title string @description("Brief outcome title")
  description string @description("Full outcome description")
  description_native string? @description("Description in native Celtic language if applicable")

  subject string @description("Subject area")
  strand string? @description("Curriculum strand or unit")
  sub_strand string? @description("Sub-strand or element")

  skills string[] @description("Skills developed")
  knowledge_areas string[] @description("Knowledge content areas")
  attitudes string[]? @description("Attitudes and values")

  is_core bool @description("Core/mandatory vs optional")
  difficulty_level string? @description("Bloom's taxonomy level or similar")

  cross_curricular_links string[]? @description("Links to other subjects")
  prerequisite_outcomes string[]? @description("Required prior learning")

  source_url string
  source_document string?
}

class CrossNationCurriculumSpec {
  spec_id string @description("Unique specification identifier")
  nation Nation
  level NationEducationLevel
  framework CurriculumFramework
  board QualificationBoard?

  title string @description("Specification title in English") @stream.not_null
  title_native string? @description("Title in native Celtic language")

  subject string
  subject_code string? @description("Official subject code")

  version string? @description("Specification version")
  effective_from string? @description("Date specification became effective")
  valid_until string? @description("Date specification expires")

  rationale string? @description("Subject rationale/purpose")
  aims string[] @description("Subject aims")

  learning_outcomes CrossNationLearningOutcome[]
  assessment_structure AssessmentStructure?

  recommended_hours int? @description("Recommended teaching hours")
  resources_required string[]?

  source_url string
  last_crawled string
  content_hash string? @description("For change detection")
  @@stream.done
}

class AssessmentStructure {
  total_marks int?
  components AssessmentComponent[]
  grading_scale GradingScale?
}

class AssessmentComponent {
  name string
  weight_percentage int
  format string @description("written, oral, practical, coursework, project")
  duration_minutes int?
  is_external bool @description("External vs school-based assessment")
  description string?
}

class GradingScale {
  scale_type string @description("points, grades, levels")
  grades GradeLevel[]
}

class GradeLevel {
  grade string @description("Grade label (A, B, H1, 8, etc.)")
  points int? @description("Points value if applicable")
  description string? @description("Grade descriptor")
  percentage_range string? @description("Percentage range (e.g., '90-100')")
}

// ============================================================================
// CURRICULUM ALIGNMENT
// ============================================================================

enum AlignmentType {
  EQUIVALENT @description("Functionally equivalent outcomes")
  PARTIAL_OVERLAP @description("Some overlap in content/skills")
  PREREQUISITE @description("One is prerequisite for the other")
  EXTENSION @description("One extends/deepens the other")
  COMPLEMENTARY @description("Different aspects of same topic")
  DIFFERENT_APPROACH @description("Same topic, different methodology")
}

enum AlignmentMethod {
  SEMANTIC @description("AI semantic similarity")
  KEYWORD @description("Keyword matching")
  MANUAL @description("Human expert alignment")
  LLM_REASONING @description("LLM chain-of-thought")
  HYBRID @description("Combination of methods")
}

class OutcomeAlignment {
  alignment_id string
  source_outcome_id string
  source_nation Nation
  target_outcome_id string
  target_nation Nation

  alignment_type AlignmentType
  confidence_score float @description("0.0 to 1.0")
  method AlignmentMethod

  reasoning string? @description("Explanation of alignment")
  shared_concepts string[] @description("Concepts in common")
  differences string[]? @description("Key differences noted")

  validated_by string? @description("Human validator if applicable")
  validated_at string?
}

class CrossNationComparison {
  comparison_id string
  subject string
  levels_compared NationEducationLevel[]
  nations_compared Nation[]

  alignments OutcomeAlignment[]

  summary string @description("Executive summary of comparison")
  key_similarities string[]
  key_differences string[]
  recommendations string[]? @description("Recommendations for resource sharing")

  coverage_matrix CoverageMatrix? @description("Which outcomes map to which")
}

class CoverageMatrix {
  rows Nation[]
  columns Nation[]
  cells CoverageCell[]
}

class CoverageCell {
  row_nation Nation
  column_nation Nation
  outcome_count int
  aligned_count int
  coverage_percentage float
}

// ============================================================================
// EXTRACTION FUNCTIONS
// ============================================================================

function ExtractCrossNationSpec(
  document: string,
  nation: Nation,
  level: NationEducationLevel
) -> CrossNationCurriculumSpec {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#

  catch_all (err) {
    CrossNationCurriculumSpec {
      nation nation {},
      level nationeducationlevel {},
      framework curriculumframework {},
      board null,
      subject "",
      learning_outcomes null,
      assessment_structure null,
      resources_required null,
      source_url "",
      last_crawled "",
    }
  }
}

function AlignOutcomes(
  source_outcomes: CrossNationLearningOutcome[],
  target_outcomes: CrossNationLearningOutcome[]
) -> OutcomeAlignment[] {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

function CompareCurricula(
  specs: CrossNationCurriculumSpec[],
  subject: string
) -> CrossNationComparison {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

function IdentifyResourceSharing(
  source_spec: CrossNationCurriculumSpec,
  target_specs: CrossNationCurriculumSpec[]
) -> ResourceSharingRecommendation[] {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

class ResourceSharingRecommendation {
  source_nation Nation
  target_nation Nation
  source_outcome_ids string[]
  target_outcome_ids string[]

  resource_type string @description("lesson plan, worksheet, assessment, video, etc.")
  adaptation_needed string @description("none, minor, significant")
  translation_needed bool
  target_languages string[]?

  rationale string
  implementation_notes string?
}

// ============================================================================
// LEVEL EQUIVALENCE MAPPING
// ============================================================================

function MapLevelEquivalence(level: NationEducationLevel) -> NationEducationLevel[] {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

// ============================================================================
// CELTIC LANGUAGE TRANSLATION SUPPORT
// ============================================================================

class TranslationRequest {
  source_language string @description("en, ga, cy, gd, gv")
  target_language string
  source_text string
  context string @description("curriculum, assessment, resource")
  domain string @description("mathematics, science, history, etc.")
}

class TranslationResult {
  source_text string
  target_text string
  confidence float
  needs_review bool
  review_notes string?
  terminology_used string[]? @description("Official terminology applied")
}

function TranslateEducationalContent(request: TranslationRequest) -> TranslationResult {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

// ============================================================================
// CLIENT CONFIGURATION
// ============================================================================

client<llm> Claude {
  provider anthropic
  options {
    model claude-sonnet-4-20250514
    max_tokens 8192
  }
}

client<llm> ClaudeOpus {
  provider anthropic
  options {
    model claude-opus-4-20250514
    max_tokens 16384
  }
}

client<llm> ClaudeMini {
  provider anthropic
  options {
    model claude-3-5-haiku-20241022
    max_tokens 4096
  }
}

// ============================================================================
// TEST CASES
// ============================================================================

// test ExtractIrishJCSpec {
//   functions [ExtractCrossNationSpec]
//   args {
//     document #"
//       Junior Cycle Mathematics Specification
//       NCCA 2023
// 
//       Strands:
//       1. Number (25%)
//       2. Algebra (20%)
//       3. Geometry and Trigonometry (30%)
//       4. Statistics and Probability (25%)
// 
//       Learning Outcomes:
//       N.1 Students should be able to use whole numbers, fractions, decimals...
//       A.1 Students should be able to investigate patterns and relationships...
// 
//       Assessment:
//       - Classroom-Based Assessment 1: 10%
//       - Classroom-Based Assessment 2: 10%
//       - Final Examination: 80%
//     "#
//     nation "IRELAND"
//     level "IE_JUNIOR_CYCLE"
//   }
// }

// test AlignMathsOutcomes {
//   functions [AlignOutcomes]
//   args {
//     source_outcomes [
//       {
//         outcome_id: "IE_JC_MATH_N1",
//         nation: "IRELAND",
//         level: "IE_JUNIOR_CYCLE",
//         framework: "JUNIOR_CYCLE",
//         title: "Number operations",
//         description: "Use whole numbers, fractions, decimals and percentages",
//         subject: "mathematics",
//         strand: "number",
//         skills: ["calculation", "estimation", "problem-solving"],
//         knowledge_areas: ["arithmetic", "fractions"],
//         is_core: true,
//         source_url: "https://curriculumonline.ie"
//       }
//     ]
//     target_outcomes [
//       {
//         outcome_id: "SC_N5_MATH_NUM1",
//         nation: "SCOTLAND",
//         level: "SC_NATIONAL_5",
//         framework: "CURRICULUM_FOR_EXCELLENCE",
//         title: "Numerical calculations",
//         description: "Apply numerical skills in real-life contexts",
//         subject: "mathematics",
//         strand: "numeracy",
//         skills: ["calculation", "application", "reasoning"],
//         knowledge_areas: ["number operations"],
//         is_core: true,
//         source_url: "https://sqa.org.uk"
//       }
//     ]
//   }
// }
