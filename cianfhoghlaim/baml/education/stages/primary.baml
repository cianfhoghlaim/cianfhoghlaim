// =============================================================================
// Primary Curriculum (ages 4-12) — BAML Schema
// Bilingual EN/GA extraction of the NCCA Primary Curriculum Framework.
// Merged from:
//   - baml/primary.baml (171 LOC) — the canonical primary curriculum
//   - baml/oideachais_other/primary.baml (45 LOC) — the URL-extraction variant
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

enum PrimaryAreaCode {
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
  area PrimaryAreaCode
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
  name PrimaryAreaCode
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

function ExtractPrimaryFramework(text: string,
  stage: PrimaryStage,
  area: PrimaryAreaCode) -> PrimaryCurriculumArea {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"You are an expert at parsing the Irish Primary School Curriculum (NCCA, ages 4-12).

Parse a Primary curriculum area document for a specific stage and area.

STAGE: {{ stage }}
AREA: {{ area }}

DOCUMENT TEXT:
{{ text }}

Extract:
1. Curriculum area metadata (title, code, year, NCCA reference)
2. Rationale (both English and Irish)
3. Strands within this curriculum area with codes, titles (EN/GA), and descriptions
4. Strand units within each strand
5. Learning outcomes for this stage and area
6. Key competencies and skills developed
7. Assessment approaches
8. Integration links to other curriculum areas
9. Differentiation guidance

For bilingual content, provide both description_en and description_ga variants. The 12 Primary curriculum areas are: English, Irish, Mathematics, SESE (Science, History, Geography), Visual Arts, Music, Drama, Physical Education, SPHE, Religion.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    STAGE: {{ stage }}
    AREA: {{ area }}
"#
}


function ExtractPrimaryLearningOutcomes(text: string,
  stage: PrimaryStage,
  area: PrimaryAreaCode) -> PrimaryLearningOutcome[] {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"You are an expert at extracting individual learning outcomes from the Irish Primary School Curriculum.

Parse learning outcomes for a specific stage and curriculum area.

STAGE: {{ stage }}
AREA: {{ area }}

DOCUMENT TEXT:
{{ text }}

Extract all learning outcomes, each with:
1. Outcome code (e.g., "M-1.1" for Mathematics stage 1 strand 1)
2. Bilingual description (description_en and description_ga)
3. Strand it belongs to
4. Strand unit
5. Sub-strand (if any)
6. Key skills (Numeracy, Literacy, etc.)
7. Evidence of learning (what students should demonstrate)
8. Integration with other areas
9. Differentiation notes

The 4 stages of Primary are:
- Junior Infants and Senior Infants (ages 4-6)
- First and Second Class (ages 6-8)
- Third and Fourth Class (ages 8-10)
- Fifth and Sixth Class (ages 10-12)

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    STAGE: {{ stage }}
    AREA: {{ area }}
"#
}


function ExtractPrimaryFrameworkFromUrl(source_url: string,
  stage: PrimaryStage,
  area: PrimaryAreaCode) -> PrimaryCurriculumArea {
  client "litellm/gemini-2.0-flash"
  prompt #"
    You are an expert Irish primary curriculum analyst working for
    Cianfhoghlaim Oideachais (the bilingual agentic platform).

    Source: {{ source_url }}
    Stage: {{ stage }}
    Area: {{ area }}

    The NCCA Primary Curriculum Framework has 12 curriculum areas:
      1. Language (English)
      2. Language (Irish) / Gaeilge
      3. Mathematics / Matamaitic
      4. SESE — Science, History, Geography
      5. Visual Arts / Ealaín
      6. Music / Ceol
      7. Drama / Drámaíocht
      8. Physical Education / Corpoideachas
      9. SPHE / OSPS (Social, Personal and Health Education)
     10. Religion / Reiligiún
     11. Stand-alone Gaeilge (in Irish-medium schools)

    The 4 stages are: Junior/Senior Infants (4-6), 1st/2nd Class (6-8),
    3rd/4th Class (8-10), 5th/6th Class (10-12).

    The Framework uses a matrix of Strands and Elements. Key Competencies
    (Being a Digital Learner, Being Creative, Communicating, etc.) cut across
    all areas.

    Always extract BOTH English and Irish versions of every field.

    Return the structured PrimaryCurriculumArea as {{ ctx.output_format }}.
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