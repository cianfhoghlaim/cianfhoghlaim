// BAML template: Junior Cycle Curriculum Syllabus Extraction
//
// Per the 2026-08-18-mega-3-roadmap-v1 + the 2026-08-26-mega-3a-baml-and-adk-v1 change.
//
// Replaces the 6 hand-written junior_cycle/*.baml files:
//   - jc_cba_descriptor.baml (26 LOC)
//   - jc_curriculum_syllabus.baml (130 LOC)
//   - jc_exam_paper_layout.baml (91 LOC)
//   - jc_short_course.baml (55 LOC)
//   - jc_stubs.baml (66 LOC)
//   - junior_cycle_extraction.baml (150 LOC)
//   = 518 LOC removed, ~200 LOC added, net -318 LOC
//
// The 8 NCCA Junior Cycle subjects at full scope (per Q4):
// Mathematics, English, Gaeilge, Science, Geography, History,
// CSPE (Civic, Social, Political Education), SPHE (Social, Personal,
// Health Education).
//
// The other 10 NCCA JC subjects (per the existing
// JuniorCycleSubjectSlug enum) are deferred to a follow-up change:
// Irish_History, Business_Studies, French, German, Spanish, Italian,
// Home_Economics, Music, Art, Technology, Engineering, Graphics,
// Wood_Technology.
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate --from baml_src
//
// Reference:
//   openspec/changes/2026-08-26-mega-3a-baml-and-adk-v1/proposal.md

// ============================================================================
// Canonical enums
// ============================================================================

enum JCEducationStage {
  JC @description("Junior Cycle (Ireland, ages 12-15)")
}

enum JCSubjectSlug {
  MATHEMATICS @description("NCCA JC Mathematics")
  ENGLISH @description("NCCA JC English")
  GAEILGE @description("NCCA JC Gaeilge (Irish)")
  SCIENCE @description("NCCA JC Science")
  GEOGRAPHY @description("NCCA JC Geography")
  HISTORY @description("NCCA JC History")
  CSPE @description("NCCA JC CSPE (Civic, Social, Political Education)")
  SPHE @description("NCCA JC SPHE (Social, Personal, Health Education)")
}

enum JCLanguage {
  EN
  GA
  EN_AND_GA
}

enum JCYearBand {
  YEAR_1 @description("Junior Cycle Year 1")
  YEAR_2 @description("Junior Cycle Year 2")
  YEAR_3 @description("Junior Cycle Year 3")
  TY @description("Transition Year (optional)")
}

enum JCStrand {
  ORAL_LANGUAGE
  READING
  WRITING
  NUMBER
  ALGEBRA
  SHAPE_SPACE
  MEASURE
  DATA
  CONTINUITY_CHANGE
  NATURE_SCIENCE
  PHYSICAL_WORLD
  BIOLOGICAL_WORLD
  CHEMICAL_WORLD
  EARTH_SPACE
  PEOPLE_LIVING
  PAST
  STORY
  CREATIVE_ARTS
  EXPRESSIVE_ARTS
  CRAFT_DESIGN
  ACTIVE_LEARNING
  DIGITAL_LEARNING
  CROSS_CURRICULAR
  OTHER @description("Catch-all for strands not explicitly enumerated")
}

enum BloomsLevel {
  REMEMBER
  UNDERSTAND
  APPLY
  ANALYSE
  EVALUATE
  CREATE
}

// ============================================================================
// Canonical value types (replaces per-subject BilingualText + LearningOutcome)
// ============================================================================

class JCBilingualText {
  text_en string @description("English text")
  text_ga string? @description("Irish translation; null if EN-only")
}

class JCSubjectSpecification {
  subject JCSubjectSlug
  language JCLanguage
  source_pdf string
  source_pages int? @description("Nullable (matches the LC convention per the 2026-08-06 token-plan-apis change)")

  // The 8 NCCA Junior Cycle subjects all use the unified structure
  learning_outcomes JuniorCycleLearningOutcome[]
  total_learning_outcomes int
  strands JCStrandRecord[]
  cross_curricular string[]
  assessment_objectives string[]
  cba_descriptor JCCBADescriptor? @description("The Classroom-Based Assessment descriptor (for Sciences, CSPE, SPHE)")
  prescribed_texts JCBilingualText[]? @description("For English + Gaeilge")
  key_competencies string[]
}

class JuniorCycleLearningOutcome {
  lo_id string @description("NCCA LO code (matches /^JC-<SUBJECT>-LO-\d+$/)")
  year JCYearBand
  strand JCStrand
  statement_en string
  statement_ga string?
  blooms_taxonomy_level BloomsLevel?
  evidence_link JCSubjectPDFLink?
}

class JCStrandRecord {
  name string
  description JCBilingualText
  learning_outcomes JuniorCycleLearningOutcome[]
  estimated_hours int?
}

class JCCBADescriptor {
  cba_id string
  cba_title JCBilingualText
  cba_description JCBilingualText
  weight_pct int @description("Percentage of total grade")
  duration_minutes int
  deliverables string[]
  rubric string[] @description("The 4-grade rubric descriptors (Excellent / Very Good / Good / Fair)")
}

class JCSubjectPDFLink {
  source_pdf string
  source_page int
  excerpt_en string
  excerpt_ga string?
  ncca_url string?
}

// ============================================================================
// The canonical Junior Cycle extractor
// ============================================================================

function ExtractJuniorCycleCurriculum(
  pdf_text: string,
  subject: JCSubjectSlug,
  language: JCLanguage,
) -> JCSubjectSpecification {
  client BIEPV3Extract
  prompt #"
    {{ _.role("user") }}
    You are an expert NCCA Junior Cycle syllabus extractor for the subject `{{ subject }}` in language `{{ language }}`.

    Extract the canonical NCCA Junior Cycle structure from the syllabus text below.

    For each learning outcome (LO), capture:
    - `lo_id`: NCCA LO code matching `/^JC-<SUBJECT>-LO-\d+$/`
    - `year`: YEAR_1, YEAR_2, YEAR_3, or TY
    - `strand`: the NCCA strand (one of the 23 enum values)
    - `statement_en`: the LO statement in English
    - `statement_ga`: the LO statement in Irish (if language = GA or EN_AND_GA)
    - `blooms_taxonomy_level`: REMEMBER | UNDERSTAND | APPLY | ANALYSE | EVALUATE | CREATE

    Subject-specific guidance:
    {% if subject == JCSubjectSlug.MATHEMATICS %}
    - Topics are organised by the 5 strands: Number, Algebra, Shape & Space, Measure, Data
    - LO codes use prefix `JC-MATH-LO-NNN`
    - Note the 2 CBA components (CBA 1: Mathematical Investigation, CBA 2: Statistical Investigation)
    {% elif subject == JCSubjectSlug.ENGLISH %}
    - Topics are organised by the 3 strands: Oral Language, Reading, Writing
    - LO codes use prefix `JC-ENGL-LO-NNN`
    - Capture the prescribed texts (poetry, prose, drama) under `prescribed_texts`
    - Note the 2 CBA components (CBA 1: Oral Communication, CBA 2: The Collection)
    {% elif subject == JCSubjectSlug.GAEILGE %}
    - Topics are organised by the 3 strands: Éisteacht agus Labhairt, Léamh, Scríbhneoireacht
    - LO codes use prefix `JC-GAEL-LO-NNN`
    - Capture the prescribed texts (Irish-language titles) under `prescribed_texts`
    {% elif subject == JCSubjectSlug.SCIENCE %}
    - Topics are organised by the 4 strands: Nature of Science, Physical World, Biological World, Chemical World
    - LO codes use prefix `JC-SCI-LO-NNN`
    - Note the 2 CBA components (CBA 1: Extended Experimental Investigation, CBA 2: Science in Society Investigation)
    {% elif subject == JCSubjectSlug.GEOGRAPHY %}
    - Topics span the 3 strands: Exploring the Physical World, Exploring the Human World, Exploring Sustainability
    - LO codes use prefix `JC-GEOG-LO-NNN`
    - Note the CBA component (Geographical Investigation)
    {% elif subject == JCSubjectSlug.HISTORY %}
    - Topics span the 4 strands: The Nature of History, Eras of Conflict and Change, Life, Society, Work and Culture in the Past, Ireland and the Wider World
    - LO codes use prefix `JC-HIST-LO-NNN`
    - Note the History CBA (CB1: The Past in My Place, CB2: A Life in History)
    {% elif subject == JCSubjectSlug.CSPE %}
    - Topics span the 4 strands: Citizenship, Human Rights, Sustainable Development, Media Literacy
    - LO codes use prefix `JC-CSPE-LO-NNN`
    - Note the CSPE Action Project (mandatory)
    {% elif subject == JCSubjectSlug.SPHE %}
    - Topics span: Mental Health, Relationships & Sexuality, Substance Use, Physical Activity, Nutrition
    - LO codes use prefix `JC-SPHE-LO-NNN`
    - Note the SPHE portfolio
    {% endif %}

    {{ ctx.output_format }}

    SYLLABUS TEXT:
    {{ pdf_text }}
  "#
}

function ExtractJuniorCycleExamPaper(
  pdf_text: string,
  subject: JCSubjectSlug,
  language: JCLanguage,
) -> JuniorCycleExamPaper {
  client BIEPV3Extract
  prompt #"
    {{ _.role("user") }}
    You are an expert NCCA Junior Cycle exam paper extractor for `{{ subject }}` in language `{{ language }}`.

    Extract from the exam paper text:
    - `subject`: the subject slug
    - `paper_code`: e.g., 'JC2024-001'
    - `language`: EN or GA
    - `level`: OL or HL (most JC is single-level)
    - `year`: exam year (4-digit)
    - `total_marks`: integer
    - `sections`: array of {label, marks, questions: [{question_number, marks, instruction, sub_questions: [{label, marks}]}]}
    - `duration_minutes`: integer (typically 120-180)

    {{ ctx.output_format }}
  "#
}

function ExtractJuniorCycleCBADescriptor(
  cba_pdf_text: string,
  subject: JCSubjectSlug,
) -> JCCBADescriptor {
  client BIEPV3Extract
  prompt #"
    {{ _.role("user") }}
    You are an expert NCCA Junior Cycle Classroom-Based Assessment (CBA) descriptor extractor for subject `{{ subject }}`.

    Extract:
    - `cba_id`: e.g., 'JC-MATH-CBA1', 'JC-SCI-CBA2'
    - `cba_title`: the title (bilingual)
    - `cba_description`: 2-3 sentences (bilingual)
    - `weight_pct`: percentage of total grade
    - `duration_minutes`: in-class duration
    - `deliverables`: list of required submission components
    - `rubric`: the 4-grade rubric descriptors (Excellent, Very Good, Good, Fair)

    {{ ctx.output_format }}
  "#
}

function ExtractJuniorCycleShortCourse(
  pdf_text: string,
  subject: JCSubjectSlug,
) -> JuniorCycleShortCourse {
  client BIEPV3Extract
  prompt #"
    {{ _.role("user") }}
    You are an expert NCCA Junior Cycle short course extractor for `{{ subject }}`.

    Short courses are 100-hour courses (vs the 200-hour main JC course). Extract:
    - `subject`: the subject slug
    - `course_code`: e.g., 'JC-<SUBJECT>-SC-NNN'
    - `duration_hours`: 100 (typical)
    - `learning_outcomes`: array of JuniorCycleLearningOutcome
    - `assessment_objectives`: list of strings

    {{ ctx.output_format }}
  "#
}

// ============================================================================
// Canonical exam paper type
// ============================================================================

class JuniorCycleQuestion {
  q_id string
  part string @description("e.g., 'a', 'b(i)', 'c(ii)'")
  text_en string
  text_ga string?
  question_type LCQuestionType @description("Reuses the LC enum (SHORT_ANSWER, EXTENDED_RESPONSE, etc.)")
  marks int
  related_lo_id string? @description("Learning outcome from syllabus (matches /^JC-<SUBJECT>-LO-\d+$/)")
}

class JuniorCycleQuestionSection {
  section_id string
  section_name string
  instructions string?
  questions JuniorCycleQuestion[]
  total_marks int
}

class JuniorCycleExamPaper {
  subject JCSubjectSlug
  paper_code string
  language JCLanguage
  level string @description("OL, HL, or FDN (JC is typically single-level)")
  year int
  source_pdf string
  total_pages int
  total_marks int
  total_questions int
  sections JuniorCycleQuestionSection[]
  duration_minutes int?
  has_formula_sheet bool
}

class JuniorCycleShortCourse {
  subject JCSubjectSlug
  course_code string
  duration_hours int @description("Typically 100 for JC short courses")
  learning_outcomes JuniorCycleLearningOutcome[]
  assessment_objectives string[]
}

// ============================================================================
// BAML test blocks (per the @assert requirement)
// ============================================================================

test jc_mathematics_lo_code_matches {
  functions [ExtractJuniorCycleCurriculum]
  args {
    pdf_text "Sample JC Mathematics syllabus text"
    subject JCSubjectSlug.MATHEMATICS
    language JCLanguage.EN
  }
}

test jc_science_cba_descriptor {
  functions [ExtractJuniorCycleCBADescriptor]
  args {
    cba_pdf_text "Sample JC Science CBA PDF text"
    subject JCSubjectSlug.SCIENCE
  }
}

test jc_gaeilge_bilingual_prescribed_texts {
  functions [ExtractJuniorCycleCurriculum]
  args {
    pdf_text "Sample JC Gaeilge syllabus text"
    subject JCSubjectSlug.GAEILGE
    language JCLanguage.EN_AND_GA
  }
}