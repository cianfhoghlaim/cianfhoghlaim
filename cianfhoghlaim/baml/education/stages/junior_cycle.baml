// =============================================================================
// Junior Cycle (ages 12-15) — BAML Schema
// Bilingual EN/GA extraction of the NCCA Junior Cycle specifications.
// 18 core subjects + 16 short courses + Level 1/2 Learning Programmes.
// Merged from:
//   - baml/junior_cycle.baml (229 LOC) — the canonical JC schema
//   - baml/oideachais_other/junior_cycle.baml (39 LOC) — the URL-extraction variant
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

class JCWellbeingStatement {
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

class JCSubjectSpec {
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

function ExtractJCSpec(text: string,
  subject: string) -> JCSubjectSpec {
  client Claude
  prompt #"You are an expert at parsing NCCA Junior Cycle subject specifications (Irish secondary school, ages 12-15).

Parse a complete Junior Cycle specification for a subject.

SUBJECT: {{ subject }}

DOCUMENT TEXT:
{{ text }}

Extract:
1. Specification metadata (title_en, title_ga, year, NCCA reference, version)
2. Aims and rationale (bilingual)
3. Strands (typically 2-5 per subject) with codes, titles (EN/GA), descriptions
4. Strand units within each strand
5. Learning outcomes (each with code, bilingual descriptions)
6. 2 Classroom-Based Assessments (CBAs):
   - CBA 1 details (task type, duration, learning outcomes assessed)
   - CBA 2 details
7. Assessment components:
   - Written examination structure and mark allocation
   - CBA mark contribution to final grade
8. Achievement levels (4 levels: Exceptional, Above Expectations, In Line With, Yet to Meet Expectations)
9. Key skills and short courses that link to this subject

The 18 Junior Cycle subjects are: Art, Business Studies, CSPE, Classics, English, French, Geography, German, Graphics, History, Home Economics, Irish, Italian, Mathematics, Music, Religious Education, Science, Spanish.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    SUBJECT: {{ subject }}
"#
}


function ExtractCBADescriptor(text: string,
  task_name: string) -> CBATask {
  client Claude
  prompt #"You are an expert at parsing NCCA Junior Cycle Classroom-Based Assessment (CBA) task descriptors.

Parse a single CBA task description.

TASK NAME: {{ task_name }}

CBA TEXT:
{{ text }}

Extract:
1. Task name (English and Irish)
2. Subject (which Junior Cycle subject)
3. CBA number (1 or 2)
4. Duration (in weeks or class periods)
5. Format (research project, practical investigation, portfolio, oral presentation, etc.)
6. Learning outcomes assessed (cite specific codes)
7. Key skills developed
8. Assessment criteria and descriptors for each achievement level:
   - Exceptional
   - Above Expectations
   - In Line With Expectations
   - Yet to Meet Expectations
9. Student reflection requirements
10. Teacher guidance and supports
11. Submission format and deadlines

CBAs account for a significant portion of the Junior Cycle final grade, so extract all details that would help students prepare and teachers assess.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    TASK: {{ task_name }}
"#
}


function ExtractShortCourse(text: string,
  course_name: string) -> JuniorCycleShortCourse {
  client Claude
  prompt #"You are an expert at parsing NCCA Junior Cycle Short Course specifications.

Parse a Junior Cycle Short Course (typically 100 hours of student work over 1-2 years).

COURSE NAME: {{ course_name }}

DOCUMENT TEXT:
{{ text }}

Extract:
1. Course metadata (title_en, title_ga, year, NCCA reference)
2. Course aim and rationale
3. Strands and learning outcomes (bilingual)
4. Assessment components (project, portfolio, presentation)
5. Achievement levels (4 levels)
6. Linkages to main Junior Cycle subjects
7. Cross-curricular skills (Coding, Digital Media Literacy, Civic Action, etc.)

The 16 NCCA Short Courses include: Coding, Digital Media Literacy, Civic Action, Chinese Language, Philosophy, Astronomy, Climate Action, etc.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    COURSE: {{ course_name }}
"#
}


function ExtractJCSpecFromUrl(
  source_url: string,
  subject: JuniorCycleSubject
) -> JCSubjectSpec {
  client Gemini2FlashAlias
  prompt #"
    You are an expert Irish Junior Cycle curriculum analyst working for
    Cianfhoghlaim Oideachais (the bilingual agentic platform).

    Source: {{ source_url }}
    Subject: {{ subject }}

    Junior Cycle is the 3-year programme at ages 12-15, ending in a state
    examination at the end of 3rd Year. Each subject has:
      - A specification (NCCA-issued)
      - 2 Classroom-Based Assessments (CBAs) — formative
      - A final examination — summative
      - 4 Achievement Levels on the rubric: Exceptional, AboveExpectations,
        InLineWithExpectations, YetToMeetExpectations

    For Science specifically, there is a 'Nature of Science' Unifying Strand
    and contextual strands (Physical World, Biological World, Chemical World,
    Earth & Space).

    For Languages, the assessment includes an aural component.

    For Mathematics, the assessment has 2 papers at Common Level.

    Always extract BOTH English and Irish versions of every field.

    Return the structured JCSubjectSpec as {{ ctx.output_format }}.
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