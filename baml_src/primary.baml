// =============================================================================
// Primary Curriculum (ages 4-12) — BAML Schema
// Bilingual EN/GA extraction of the NCCA Primary Curriculum Framework.
// Moved (and extended) from docs/agents/BAML_COMPREHENSIVE_GUIDE.md:683-728.
// =============================================================================

// -----------------------------------------------------------------------------
// Enums
// -----------------------------------------------------------------------------

enum PrimaryStage {
  STAGE1_JUNIOR_SENIOR_INFANTS
    @description("Naíonáin Shóisearacha agus Shinsearacha, ages 4-6")
  STAGE2_FIRST_SECOND_CLASS
    @description("Rang 1 & 2, ages 6-8")
  STAGE3_THIRD_FOURTH_CLASS
    @description("Rang 3 & 4, ages 8-10")
  STAGE4_FIFTH_SIXTH_CLASS
    @description("Rang 5 & 6, ages 10-12")
}

enum PrimaryCurriculumArea {
  PRIMARY_LANGUAGE_ENGLISH
  PRIMARY_LANGUAGE_IRISH
  PRIMARY_MATHEMATICS
  PRIMARY_SESE_SCIENCE
  PRIMARY_SESE_HISTORY
  PRIMARY_SESE_GEOGRAPHY
  PRIMARY_VISUAL_ARTS
  PRIMARY_MUSIC
  PRIMARY_DRAMA
  PRIMARY_PHYSICAL_EDUCATION
  PRIMARY_SPHE
  PRIMARY_RELIGION
  PRIMARY_STAND_ALONE_GAELGE
}

// -----------------------------------------------------------------------------
// Classes (moved from BAML_COMPREHENSIVE_GUIDE.md:693-717 and extended)
// -----------------------------------------------------------------------------

class CompetencyLink {
  competency_name string   @description("e.g., 'Being a Digital Learner'")
  context string           @description("How this specific outcome supports the competency")
}

class PrimaryLearningOutcome {
  id string?
  text_en string
  text_ga string?           @description("Irish translation of the outcome text")
  element string            @description("The 'Element' of learning")
  stage PrimaryStage
  area PrimaryCurriculumArea
  progression_continuum string?  @description("Description of how the outcome progresses across stages")
  key_competencies CompetencyLink[]
  action_verbs string[]      @description("e.g., 'investigate', 'analyse', 'create'")
  cross_curricular_links string[] @description("Other primary areas this outcome links to")
}

class PrimaryStrand {
  name string              @description("e.g., 'Number', 'Data and Chance'")
  name_ga string?           @description("Irish name of the strand")
  description string
  description_ga string?
  outcomes PrimaryLearningOutcome[]
  weighting_pct float?     @description("Approximate percentage weighting in the curriculum")
}

class PrimaryCurriculumArea {
  name PrimaryCurriculumArea
  rationale string
  rationale_ga string?
  strands PrimaryStrand[]
  integration_links string[] @description("Explicit text mentioning other curriculum areas")
  source_url string
  document_year int
  language string          @description("en | ga | bilingual")
}

// -----------------------------------------------------------------------------
// Functions
// -----------------------------------------------------------------------------

function ExtractPrimaryFramework(
  text: string,
  stage: PrimaryStage,
  area: PrimaryCurriculumArea
) -> PrimaryCurriculumArea {
  client "litellm/gemini-2.0-flash"
  prompt #"
    You are an expert Irish primary curriculum analyst.

    Analyze the text from the Primary Curriculum Framework for a specific stage and area.
    CRITICAL: The Primary Framework uses a matrix of 'Strands' and 'Elements'.
    Look for specific icons or text labels that indicate 'Key Competencies'.
    Always extract BOTH English and Irish versions of every field.

    STAGE: {{ stage }}
    AREA: {{ area }}

    Text: {{ text }}

    Return the structured PrimaryCurriculumArea as {{ ctx.output_format }}.
  "#
}

function ExtractPrimaryLearningOutcomes(
  text: string,
  stage: PrimaryStage,
  area: PrimaryCurriculumArea
) -> PrimaryLearningOutcome[] {
  client "litellm/gemini-2.0-flash"
  prompt #"
    You are an expert Irish primary curriculum analyst.

    Extract all learning outcomes from this Primary Curriculum text for the given stage and area.
    Each outcome should have a unique ID, the element it belongs to, the action verbs,
    and any cross-curricular links to other primary areas.

    STAGE: {{ stage }}
    AREA: {{ area }}
    Text: {{ text }}

    Return PrimaryLearningOutcome[] as {{ ctx.output_format }}.
  "#
}

// -----------------------------------------------------------------------------
// Tests
// -----------------------------------------------------------------------------

test ExtractPrimaryMathsTest {
  functions [ExtractPrimaryFramework]
  args {
    text "Number: count, compare, order. Strand 1: Number — Infants through 6th Class. Children explore numbers 0-20 (Infants), 0-100 (1st/2nd), 0-1000 (3rd/4th), 0-1,000,000 (5th/6th). Place value, operations, fractions."
    stage STAGE1_JUNIOR_SENIOR_INFANTS
    area PRIMARY_MATHEMATICS
  }
}
