// =============================================================================
// Junior Cycle (ages 12-15) — BAML Schema
// Bilingual EN/GA extraction of the NCCA Junior Cycle specifications.
// 18 core subjects + 16 short courses + Level 1/2 Learning Programmes.
// See: docs/bonneagar/education-subject-inventory.md:58-105
// =============================================================================

// -----------------------------------------------------------------------------
// Enums
// -----------------------------------------------------------------------------

enum JuniorCycleSubject {
  JC_GAEILGE
  JC_ENGLISH
  JC_MATHS
  JC_SCIENCE
  JC_BUSINESS
  JC_GEOGRAPHY
  JC_HISTORY
  JC_FRENCH
  JC_GERMAN
  JC_SPANISH
  JC_ITALIAN
  JC_ART
  JC_MUSIC
  JC_HOME_ECONOMICS
  JC_ENGINEERING
  JC_TECHNOLOGY
  JC_GRAPHICS
  JC_CLASSICS
  JC_RELIGIOUS_EDUCATION
  JC_WELLBEING                  @description("Wellbeing is mandatory but not a graded subject")
}

enum JuniorCycleShortCourse {
  JCS_CODING
  JCS_CSPE                     @description("Civic, Social and Political Education")
  JCS_DIGITAL_MEDIA_LITERACY
  JCS_PHILOSOPHY
  JCS_PE                        @description("Physical Education (short course)")
  JCS_SPHE                      @description("Social, Personal and Health Education (short course)")
  JCS_CHINESE_LANGUAGE_CULTURE
  JCS_ARTISTIC_PERFORMANCE
  JCS_CSI_FORENSIC
  JCS_L2LP_HISTORY
  JCS_L2LP_ENTERPRISE_ANIMATION
  JCS_OTHER_A
  JCS_OTHER_B
  JCS_OTHER_C
  JCS_OTHER_D
  JCS_OTHER_E
}

enum AchievementLevel {
  Exceptional            @description("Exceptional achievement of the learning outcomes")
  AboveExpectations      @description("Above expectations of the learning outcomes")
  InLineWithExpectations @description("In line with expectations of the learning outcomes")
  YetToMeetExpectations  @description("Yet to meet the expectations of the learning outcomes")
}

// -----------------------------------------------------------------------------
// Classes

// -----------------------------------------------------------------------------

class RubricDescriptor {
  level AchievementLevel
  text_en string              @description("The full descriptive paragraph in English")
  text_ga string?             @description("Irish translation")
  key_qualities string[]      @description("Extracted phrases indicating quality")
  negative_indicators string[] @description("Phrases indicating what is missing")
}

class CBATask {
  name_en string
  name_ga string?
  year int                    @description("Year 1, 2, or 3 of Junior Cycle")
  descriptor RubricDescriptor[]
  weight_pct int?             @description("CBAs are formative; this is for display only")
  duration_weeks int?
}

class JCWellbeingStatement {
  statement_en string
  statement_ga string?
  indicator string            @description("e.g., 'physical activity', 'mental health', 'citizenship'")
}

class JCSubjectSpec {
  subject JuniorCycleSubject
  short_course JuniorCycleShortCourse?  @description("Populated only for short courses")
  specification_year int
  strands CurriculumStrand[]              @description("Reused from senior_cycle extraction (or moved to common.baml)")
  cba_tasks CBATask[]
  learning_outcomes LearningOutcome[]     @description("Reused from curriculum_extraction.baml")
  specification_url string
  language string                         @description("en | ga | bilingual")
}

class L2LPOutcome {
  id string
  text_en string
  text_ga string?
  priority_learning_unit string
  stage string                            @description("e.g., 'Junior Cycle 1st Year'")
}

// -----------------------------------------------------------------------------
// Functions
// -----------------------------------------------------------------------------

function ExtractJCSpec(text: string,
  subject: JuniorCycleSubject) -> JCSubjectSpec {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"Extract the requested data.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    {{text}}
    {{subject}}
"#
}

function ExtractCBADescriptor(text: string,
  task_name: string) -> RubricDescriptor[] {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"Extract the requested data.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    {{text}}
    {{task_name}}
"#
}

function ExtractShortCourse(text: string,
  course: JuniorCycleShortCourse) -> JCSubjectSpec {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"Extract the requested data.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    {{text}}
    {{course}}
"#
}

// -----------------------------------------------------------------------------
// Tests
// -----------------------------------------------------------------------------

test ExtractJCScienceTest {
  functions [ExtractJCSpec]
  args {
    text "Junior Cycle Science — Nature of Science strand. Earth & Space, Physical World, Biological World, Chemical World. CBA 1: Science in Society Investigation. CBA 2: Research Investigation."
    subject JC_SCIENCE
  }
}
