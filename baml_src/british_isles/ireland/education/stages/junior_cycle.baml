// =============================================================================
// Junior Cycle (ages 12-15) — BAML Schema
// Bilingual EN/GA extraction of the NCCA Junior Cycle specifications.
// 18 core subjects + 16 short courses + Level 1/2 Learning Programmes.
// Merged from:
//   - baml/junior_cycle.baml (229 LOC) — the canonical JC schema
//   - baml/cianfhoghlaim_other/junior_cycle.baml (39 LOC) — the URL-extraction variant
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

// DEPRECATED 2026-08-15: the `enum JuniorCycleShortCourse` block
// below was a legacy duplicate of the canonical
// `class JuniorCycleShortCourse` declared at
// baml_src/british_isles/ireland/education/junior_cycle/jc_short_course.baml:13.
// The class is the SSOT per the centralized-schema-registry
// capability. Removed to unblock `mise run baml:generate`.
//
// enum JuniorCycleShortCourse {
//   JCS_CODING
//   JCS_CSPE                     @description("Civic, Social and Political Education")
//   JCS_DIGITAL_MEDIA_LITERACY
//   JCS_PHILOSOPHY
//   JCS_PE                        @description("Physical Education (short course)")
//   JCS_SPHE                      @description("Social, Personal and Health Education (short course)")
//   JCS_CHINESE_LANGUAGE_CULTURE
//   JCS_ARTISTIC_PERFORMANCE
//   JCS_CSI_FORENSIC
//   JCS_L2LP_HISTORY
//   JCS_L2LP_ENTERPRISE_ANIMATION
//   JCS_OTHER_A
//   JCS_OTHER_B
//   JCS_OTHER_C
//   JCS_OTHER_D
//   JCS_OTHER_E
// }

enum AchievementLevel {
  Exceptional            @description("Exceptional achievement of the learning outcomes")
  AboveExpectations      @description("Above expectations of the learning outcomes")
  InLineWithExpectations @description("In line with expectations of the learning outcomes")
  YetToMeetExpectations  @description("Yet to meet the expectations of the learning outcomes")
}

// -----------------------------------------------------------------------------
// Classes

// -----------------------------------------------------------------------------

class JcRubricDescriptor {
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
  descriptor JcRubricDescriptor[]
  weight_pct int?             @description("CBAs are formative; this is for display only")
  duration_weeks int?
  @@stream.done
}

class JuniorCycleWellbeingStatement {
  statement_en string
  statement_ga string?
  indicator string            @description("e.g., 'physical activity', 'mental health', 'citizenship'")
}

class JcCurriculumStrand {
  name string
  name_ga string?
  description string
  description_ga string?
  outcomes JcLearningOutcome[]
}

class JcLearningOutcome {
  code string
  description_en string
  description_ga string?
  strand string?
  strand_unit string?
}

class JuniorCycleSubjectSpec {
  subject JuniorCycleSubject
  short_course JuniorCycleShortCourse?  @description("Populated only for short courses")
  specification_year int
  strands JcCurriculumStrand[]              @description("Strands with learning outcomes")
  cba_tasks CBATask[]
  learning_outcomes JcLearningOutcome[]     @description("Bilingual learning outcomes")
  specification_url string
  language string                         @description("en | ga | bilingual")
  @@stream.done
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

function ExtractJuniorCycleSpec(text: string,
  subject: string) -> JuniorCycleSubjectSpec {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert Irish Junior Cycle (ages 12-15) curriculum extractor for the 8 NCCA JC subjects.

    Source type: PDF text from NCCA Junior Cycle specifications

    Extract:
    - subject: the JC subject slug
    - learning_outcomes: list of LOs with codes (JC-<SUBJ>-LO-NNN)
    - strand_elements: list of strand elements
    - cba_objectives: Classroom-Based Assessment objectives
    - assessment_objectives: final exam assessment objectives

    {% if subject == 'JCSubjectSlug.MATHEMATICS' %}
    - Topics span Number, Algebra, Functions, Geometry, Statistics
    - LO codes use prefix `JC-MATH-LO-NNN`
    {% elif subject == 'JCSubjectSlug.ENGLISH' %}
    - Capture the prescribed texts under `prescribed_texts`
    {% endif %}

    Junior Cycle has a different assessment structure (CBA + final exam) than Leaving Cert. Always capture both the CBA objectives and the final exam objectives.

    {{ ctx.output_format }}

    {{ input }}
  "#

  catch_all (err) {
    JuniorCycleSubjectSpec {
      subject juniorcyclesubject {},
      specification_year 0,
      cba_tasks null,
      specification_url "",
    }
  }
}





function ExtractShortCourse(text: string,
  course_name: string) -> JuniorCycleShortCourse {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert Irish Junior Cycle (ages 12-15) curriculum extractor for the 8 NCCA JC subjects.

    Source type: PDF text from NCCA Junior Cycle specifications

    Extract:
    - subject: the JC subject slug
    - learning_outcomes: list of LOs with codes (JC-<SUBJ>-LO-NNN)
    - strand_elements: list of strand elements
    - cba_objectives: Classroom-Based Assessment objectives
    - assessment_objectives: final exam assessment objectives

    {% if subject == 'JCSubjectSlug.MATHEMATICS' %}
    - Topics span Number, Algebra, Functions, Geometry, Statistics
    - LO codes use prefix `JC-MATH-LO-NNN`
    {% elif subject == 'JCSubjectSlug.ENGLISH' %}
    - Capture the prescribed texts under `prescribed_texts`
    {% endif %}

    Junior Cycle has a different assessment structure (CBA + final exam) than Leaving Cert. Always capture both the CBA objectives and the final exam objectives.

    {{ ctx.output_format }}

    {{ input }}
  "#

  catch_all (err) {
    JuniorCycleShortCourse {}
  }
}


function ExtractJuniorCycleSpecFromUrl(
  source_url: string,
  subject: JuniorCycleSubject
) -> JuniorCycleSubjectSpec {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert Irish Junior Cycle (ages 12-15) curriculum extractor for the 8 NCCA JC subjects.

    Source type: PDF text from NCCA Junior Cycle specifications

    Extract:
    - subject: the JC subject slug
    - learning_outcomes: list of LOs with codes (JC-<SUBJ>-LO-NNN)
    - strand_elements: list of strand elements
    - cba_objectives: Classroom-Based Assessment objectives
    - assessment_objectives: final exam assessment objectives

    {% if subject == 'JCSubjectSlug.MATHEMATICS' %}
    - Topics span Number, Algebra, Functions, Geometry, Statistics
    - LO codes use prefix `JC-MATH-LO-NNN`
    {% elif subject == 'JCSubjectSlug.ENGLISH' %}
    - Capture the prescribed texts under `prescribed_texts`
    {% endif %}

    Junior Cycle has a different assessment structure (CBA + final exam) than Leaving Cert. Always capture both the CBA objectives and the final exam objectives.

    {{ ctx.output_format }}

    {{ input }}
  "#

  catch_all (err) {
    JuniorCycleSubjectSpec {
      subject juniorcyclesubject {},
      specification_year 0,
      cba_tasks null,
      specification_url "",
    }
  }
}


// -----------------------------------------------------------------------------
// Tests
// -----------------------------------------------------------------------------

// test ExtractJCScienceTest {
//   functions [ExtractJCSpec]
//   args {
//     text "Junior Cycle Science — Nature of Science strand. Earth & Space, Physical World, Biological World, Chemical World. CBA 1: Science in Society Investigation. CBA 2: Research Investigation."
//     subject JC_SCIENCE
//   }
// }