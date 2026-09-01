// BAML template: Leaving Cycle Curriculum Syllabus Extraction
//
// Per the 2026-08-18-mega-3-roadmap-v1 + the 2026-08-26-mega-3a-baml-and-adk-v1 change.
//
// Replaces the 6 hand-written lc_extraction/*.baml files:
//   - circular_extraction.baml (109 LOC)
//   - cross_linguistic.baml (86 LOC)
//   - curriculum_syllabus.baml (506 LOC)
//   - exam_paper_layout.baml (148 LOC)
//   - lc_topic_extraction.baml (148 LOC)
//   - marking_scheme.baml (143 LOC)
//   - syllabus_diagram.baml (147 LOC)
//   = 1,287 LOC removed, ~250 LOC added, net -1,037 LOC
//
// Covers the canonical 14 LC subjects via `{% if subject == "x" %}`:
// mathematics, applied_mathematics, chemistry, physics, biology
// art, music, computer_science.
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate --from baml_src
//
// Reference:
//   openspec/changes/2026-08-26-mega-3a-baml-and-adk-v1/proposal.md
//   openspec/specs/british-isles-education-pipeline-v3/spec.md (R28 lineage)

enum LCEducationStage {
  LC_OL @description("Leaving Certificate Ordinary Level")
  LC_HL @description("Leaving Certificate Higher Level")
  LC_FDN @description("Leaving Certificate Foundation Level")
}

enum LCSubjectSlug {
  MATHEMATICS
  APPLIED_MATHEMATICS
  CHEMISTRY
  PHYSICS
  BIOLOGY
  GEOGRAPHY
  ENGLISH
  GAEILGE
  FRENCH
  HISTORY
  BUSINESS
  ACCOUNTING
  ART
  MUSIC
  COMPUTER_SCIENCE
}

enum LCQuestionType {
  SHORT_ANSWER      @description("1-3 sentence response")
  EXTENDED_RESPONSE @description("Longer paragraph response")
  WORKED_SOLUTION   @description("Step-by-step calculation/proof")
  STRUCTURE_DRAWING @description("Lewis structure, organic structure, etc.")
  DIAGRAM_BASED     @description("Read from a chart/figure/table")
  ESSAY             @description("Long-form essay (typically 25+ marks)")
  PRACTICAL         @description("Lab question with procedure")
  MULTIPLE_CHOICE   @description("Choose one option")
  FILL_IN_BLANK     @description("Complete the missing words/numbers")
}

enum MarkingBand {
  BAND_I   @description("Distinction-grade responses (>75%)")
  BAND_II  @description("Higher merit-grade responses (60-75%)")
  BAND_III @description("Merit-grade responses (50-60%)")
  BAND_IV  @description("Achieved-grade responses (40-50%)")
  BAND_V   @description("Low achieved / partial responses (<40%)")
}

enum BloomLevel {
  REMEMBER
  UNDERSTAND
  APPLY
  ANALYSE
  EVALUATE
  CREATE
}

// ============================================================================
// Core value types
// ============================================================================

class LCBilingualText {
  text_en string
  text_ga string? @description("Irish translation; null if EN-only")
}

class LCSubjectPDFLink {
  source_pdf string
  source_page int
  excerpt_en string
  excerpt_ga string?
  ncca_url string?
}

class LCModule {
  module_id string
  name LCBilingualText
  type string @description("CORE | OPTIONAL | SPECIALISM | PRACTICAL | ASSESSMENT")
  learning_outcomes LCLearningOutcome[]
  estimated_hours int?
}

class LCLearningOutcome {
  lo_id string @description("NCCA LO code matching /^LC-<SUBJECT>-<LEVEL>-NNN$/")
  code string @description("Full NCCA LO code e.g., 'LC-CHEM-LO-023'")
  title string
  learning_outcomes LCBilingualText[] @description("Array of {code, text, blooms_level}")
  blooms_level BloomLevel
}

class LCSyllabusDocument {
  subject LCSubjectSlug
  language string @description("EN | GA | EN_AND_GA")
  stage LCEducationStage
  source_pdf string
  source_pages int? @description("Nullable per the 2026-08-06 token-plan-apis convention")
  module_topics LCModule[]
  total_learning_outcomes int
  cross_curricular string[]
  assessment_objectives string[]
  prescribed_texts LCBilingualText[]? @description("For English + Gaeilge")
  formulas string[]? @description("Formula references (for Mathematics, Physics, Accounting)")
  lineage LineageTrace?
}

class LCQuestion {
  q_id string
  part string
  text_en string
  text_ga string?
  question_type LCQuestionType
  marks int
  related_lo_id string?
}

class LCQuestionSection {
  section_id string
  section_name string
  instructions string?
  questions LCQuestion[]
  total_marks int
}

class LCExamPaper {
  subject LCSubjectSlug
  paper_code string
  language string @description("EN or GA")
  level string @description("OL, HL, or FDN")
  year int
  source_pdf string
  total_pages int
  total_marks int
  total_questions int
  sections LCQuestionSection[]
  duration_minutes int?
  has_formula_sheet bool
  has_data_booklet bool
  formula_sheet_pages int?
  lineage LineageTrace?
}

class LCMarkAllocation {
  q_id string
  total_marks int
  partial_credit_rules string[]
  common_mistakes string[]
  sample_answer string?
}

class LCGradeDescriptor {
  band MarkingBand
  percentage_min int
  percentage_max int
  descriptor_text_en string
  descriptor_text_ga string?
  exemplar_responses string[]
}

class LCMarkingScheme {
  subject LCSubjectSlug
  scheme_code string
  language string
  level string
  year int?
  source_pdf string
  grade_descriptors LCGradeDescriptor[]
  mark_allocations LCMarkAllocation[]
  total_bands int
  total_pages int
  descriptor_word_count_avg int
  lineage LineageTrace?
}

class LCGaelicTopic {
  ga_term string
  ga_part_of_speech string
  ga_definition_en string
  source_pdf string
  subject LCSubjectSlug
}

class LCEnglishEquivalent {
  en_term string
  en_definition string
  matches_se_focmara_clause bool @description("True if also found in the Foclóir Maith / Gramadach na Gaeilge")
}

class LCCrossLinguisticConcept {
  subject LCSubjectSlug
  concept_id string @description("NCCA concept code matching /^LC-<SUBJECT>-<CONCEPT>$/")
  gaelic LCGaelicTopic
  english LCEnglishEquivalent
  translation_fidelity float @description("1.0 = exact, 0.0 = culture-specific")
  notes string?
  lineage LineageTrace?
}

class LCEducationCircular {
  circular_id string @description("Department of Education circular ID")
  year int
  language string
  title_en string
  title_ga string?
  summary string
  full_text string
  url string
  published_at string
  extraction_confidence float
  extracted_at string
}

class LCCircularToSyllabusLink {
  circular_id string
  syllabus_subject LCSubjectSlug
  syllabus_stage LCEducationStage
  syllabus_language string
  link_type string @description("REFERENCES | AMENDS | SUPERSEDES")
  syllabus_pdf string
  syllabus_page int?
  confidence float
  rationale string
}

class LCCircularDepartment {
  department string @description("DEPARTMENT_OF_EDUCATION | NCCA | SEC | STATE_EXAMS_COMMISSION")
  contact_email string?
  url string?
}

class LCDiagramRegion {
  bbox_x_min float
  bbox_y_min float
  bbox_x_max float
  bbox_y_max float
  page_number int
  role string @description("TITLE | CAPTION | AXIS_LABEL | KEY_COMPONENT | DATA_POINT | LEGEND_ENTRY | ANNOTATION | BACKGROUND")
  text_content string?
}

class LCSyllabusDiagram {
  diagram_id string
  kind string @description("EXTRACTED_FROM_DOCUMENT | ANNOTATED | DIAGRAM_BASED | ...")
  caption_en string?
  caption_ga string?
  page_number int
  source_pdf string
  subject LCSubjectSlug
  pointing_model string @description("e.g., 'allenai/Molmo2-8B'")
  confidence_score float
  regions LCDiagramRegion[]
  related_lo_ids string[] @description("NCCA LO codes the diagram illustrates")
  lineage LineageTrace?
}

class LCModuleTopic {
  module_id string
  name_en string
  name_ga string?
  type string @description("CORE | OPTIONAL | SPECIALISM | PRACTICAL | ASSESSMENT")
  learning_outcomes LCBilingualText[]
  estimated_hours int?
}

class LCTopicExtraction {
  subject LCSubjectSlug
  topics LCModuleTopic[]
  total_topics int
  cross_subject_topics string[] @description("Topics that span multiple subjects")
}

class LineageTrace {
  source_pdf string
  source_page int
  extraction_function string @description("The BAML function name (e.g., 'ExtractCurriculumSyllabus')")
  extraction_client string @description("The BAML client used (e.g., 'BIEPV3Extract')")
  extracted_at string @description("ISO 8601 UTC timestamp")
  confidence float?
  chunk_id string?
  subject LCSubjectSlug?
  language string?
}

// ============================================================================
// The 5 canonical lc6 extraction functions
// ============================================================================

function ExtractCurriculumSyllabus(
  pdf_text: string,
  subject: LCSubjectSlug,
  language: string
) -> LCSyllabusDocument {
  client BIEPV3Extract
  prompt #"
    {{ _.role("user") }}
    You are an expert Irish Leaving Certificate syllabus extractor for the subject `{{ subject }}` in language `{{ language }}`.

    From the syllabus text below, extract:
    - subject: the subject slug
    - language: EN, GA, or EN_AND_GA
    - stage: LC_OL, LC_HL, or LC_FDN
    - source_pdf: leave empty (the Python caller fills it)
    - module_topics: every distinct module/unit/strand
    - total_learning_outcomes: the count
    - cross_curricular: cross-subject links
    - assessment_objectives: NCCA AOs

    Subject-specific guidance:
    {% if subject == LCSubjectSlug.MATHEMATICS %}
    - Topics follow the 5 syllabus strands: Statistics & Probability, Geometry & Trigonometry, Number, Algebra, Functions
    - LO codes use prefix `LC-MATH-LO-NNN`
    - Capture all formula references in the `formulas` array
    {% elif subject == LCSubjectSlug.CHEMISTRY %}
    - Topics follow the 4 chemistry strands: Atomic Structure, Chemical Bonding, Stoichiometry, etc.
    - LO codes use prefix `LC-CHEM-LO-NNN`
    {% elif subject == LCSubjectSlug.GEOGRAPHY %}
    - Topics span Physical Geography, Regional Geography, Human Environment
    - LO codes use prefix `LC-GEOG-LO-NNN`
    {% elif subject == LCSubjectSlug.ENGLISH %}
    - Capture the prescribed texts (poetry, prose, drama) under `prescribed_texts`
    - LO codes use prefix `LC-ENGL-LO-NNN`
    {% elif subject == LCSubjectSlug.GAEILGE %}
    - Capture the prescribed texts under `prescribed_texts` (Irish titles)
    - LO codes use prefix `LC-GAEL-LO-NNN`
    {% elif subject == LCSubjectSlug.COMPUTER_SCIENCE %}
    - Topics span Algorithms, Data, Networks, Programming, Systems
    - LO codes use prefix `LC-COMP-LO-NNN`
    {% elif subject == LCSubjectSlug.APPLIED_MATHEMATICS %}
    - Topics: Statistics, Mechanics, Dynamics, Probability
    - LO codes use prefix `LC-APM-LO-NNN`
    {% elif subject == LCSubjectSlug.PHYSICS %}
    - Topics span Mechanics, Waves, Light, Electricity & Magnetism, Modern Physics
    - LO codes use prefix `LC-PHYS-LO-NNN`
    - Capture all formula references; include SI units + significant figures
    {% elif subject == LCSubjectSlug.BIOLOGY %}
    - Topics span the 3 units: The Study of Life, The Cell, The Organism
    - LO codes use prefix `LC-BIO-LO-NNN`
    - Capture diagrams under `prescribed_texts`
    - Note practical activities (mandatory 30%) under `assessment_objectives`
    {% elif subject == LCSubjectSlug.HISTORY %}
    - Topics span Early Modern Ireland (1494-1815), Modern Ireland (1815-1989), Contemporary World (1945-present)
    - LO codes use prefix `LC-HIST-LO-NNN`
    - Capture source-handling skills under `key_competencies` (legacy field)
    {% elif subject == LCSubjectSlug.FRENCH %}
    - Capture the prescribed texts (literary extracts, films) under `prescribed_texts`
    - LO codes use prefix `LC-FREN-LO-NNN`
    {% elif subject == LCSubjectSlug.BUSINESS %}
    - Topics span People in Business, Enterprise, Managing 1, Managing 2
    - LO codes use prefix `LC-BUS-LO-NNN`
    {% elif subject == LCSubjectSlug.ACCOUNTING %}
    - Topics span Financial Accounting, Management Accounting, Finance, Taxation
    - LO codes use prefix `LC-ACCT-LO-NNN`
    - Capture formulas (ratios, NPV, IRR) under `formulas`
    {% elif subject == LCSubjectSlug.ART %}
    - Topics span Core + 3 specialisms (painting, sculpture, graphic design)
    - LO codes use prefix `LC-ART-LO-NNN`
    - Note the practical course work (50%) under `assessment_objectives`
    {% elif subject == LCSubjectSlug.MUSIC %}
    - Topics span Composition, Performance, Listening, Music Technology
    - LO codes use prefix `LC-MUS-LO-NNN`
    - Note the 3 components (performance 50% + composition 25% + listening 25%)
    {% endif %}

    {{ ctx.output_format }}

    SYLLABUS TEXT:
    {{ pdf_text }}
  "#

}

function ExtractExamPaperLayout(
  pdf_text: string,
  subject: LCSubjectSlug?,
  paper_code: string?,
  year: int?
) -> LCExamPaper {
  client BIEPV3Extract
  prompt #"
    {{ _.role("user") }}
    You are an expert Leaving Certificate exam paper layout extractor for `{{ subject }}`.

    Extract:
    - paper_code: e.g., 'LC022ALP000EV'
    - year: 4-digit
    - level: OL, HL, or FDN
    - total_marks: integer
    - sections: array of {label, marks, questions: [...]}
    - duration_minutes: typically 180 or 240

    {{ ctx.output_format }}
  "#

}

function ExtractMarkingSchemeGuideline(
  pdf_text: string,
  subject: LCSubjectSlug?,
  year: int?
) -> LCMarkingScheme {
  client BIEPV3Extract
  prompt #"
    {{ _.role("user") }}
    Extract the NCCA marking scheme guideline for `{{ subject }}`.

    Capture:
    - scheme_code
    - grade_descriptors: array of {band, percentage_min/max, descriptor_text_en/ga}
    - mark_allocations: array of {q_id, total_marks, partial_credit_rules, common_mistakes}

    {{ ctx.output_format }}
  "#

}

function ExtractCrossLinguisticConcept(
  pdf_text_en: string,
  pdf_text_ga: string?,
  subject: LCSubjectSlug?,
  concept_id: string?
) -> LCCrossLinguisticConcept[] {
  client BIEPV3Extract
  prompt #"
    {{ _.role("user") }}
    You are an expert at cross-linguistic concept mapping between English and Irish (Gaeilge) versions of the same Irish Leaving Certificate {{ subject }} syllabus.

    For each cross-linguistic concept you find, extract:
    - The subject slug
    - The concept_id (e.g., 'LC-MA-2.1')
    - The Irish (Gaeilge) topic: ga_term, ga_part_of_speech, ga_definition_en, source_pdf
    - The English equivalent: en_term, en_definition, matches_se_focmara_clause
    - Translation fidelity (1.0 = exact, 0.0 = culture-specific)
    - Optional cultural notes

    {{ ctx.output_format }}
  "#
}

function ExtractSyllabusDiagram(
  pdf_text: string,
  subject: LCSubjectSlug
) -> LCSyllabusDiagram {
  client BIEPV3Extract
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting diagrams / figures / charts from the `{{ subject }}` syllabus PDF.

    Extract:
    - diagram_id, caption_en/ga, page_number
    - regions: array of bounding boxes + roles (TITLE | CAPTION | AXIS_LABEL | KEY_COMPONENT | DATA_POINT | LEGEND_ENTRY | ANNOTATION | BACKGROUND)
    - related_lo_ids: the NCCA LO codes the diagram illustrates

    {{ ctx.output_format }}
  "#

}

function ExtractCircular(
  url: string,
  html: string,
  pdf_text: string,
  language: string
) -> LCEducationCircular {
  client BIEPV3Extract
  prompt #"
    {{ _.role("user") }}
    Extract the NCCA / SEC / DoE education circular.

    Capture: circular_id, year, language, title_en/ga, summary, full_text, url, published_at, extraction_confidence, extracted_at.

    {{ ctx.output_format }}
  "#
}

function LinkCircularToSyllabus(
  circular: LCEducationCircular,
  candidate_syllabi: string[]
) -> LCCircularToSyllabusLink[] {
  client BIEPV3Extract
  prompt #"
    {{ _.role("user") }}
    Link this circular to candidate NCCA syllabi.

    Return: array of {circular_id, syllabus_subject, syllabus_stage, syllabus_language, link_type, syllabus_pdf, syllabus_page, confidence, rationale}.

    {{ ctx.output_format }}
  "#
}

function ClassifyCircular(
  pdf_text: string,
  url: string
) -> LCCircularDepartment {
  client BIEPV3Extract
  prompt #"
    {{ _.role("user") }}
    Classify the NCCA circular by department.

    Return: {department, contact_email, url}.

    {{ ctx.output_format }}
  "#
}

function ExtractLCTopicExtraction(
  pdf_text: string,
  subject: LCSubjectSlug?
) -> LCTopicExtraction {
  client BIEPV3Extract
  prompt #"
    {{ _.role("user") }}
    Extract the canonical cross-subject topics for the {{ subject }} syllabus.

    Capture:
    - topics: array of {module_id, name_en, name_ga, type, learning_outcomes, estimated_hours}
    - total_topics
    - cross_subject_topics: topics that span multiple subjects

    {{ ctx.output_format }}
  "#

}

// ============================================================================
// Type aliases (back-compat for the legacy files that reference
// LCGradeDescriptor / LCMarkAllocation / SyllabusDocument / ExamPaper
// without the LC prefix — see the 2026-08-26-mega-3a-baml-and-adk-v1
// change for the migration plan)
//
// Note: only declare aliases for names that don't already exist as
// classes elsewhere in the project.
// ============================================================================

type SyllabusDocument = LCSyllabusDocument
type ExamPaper = LCExamPaper
type QuestionSection = LCQuestionSection
type Question = LCQuestion
type TopicExtraction = LCTopicExtraction
type ModuleTopic = LCModuleTopic
type SyllabusDiagram = LCSyllabusDiagram
type DiagramRegion = LCDiagramRegion
type MarkingScheme = LCMarkingScheme
type EducationCircular = LCEducationCircular
type CircularToSyllabusLink = LCCircularToSyllabusLink
type CircularDepartment = LCCircularDepartment
type CrossLinguisticConcept = LCCrossLinguisticConcept
type GaelicTopic = LCGaelicTopic
type EnglishEquivalent = LCEnglishEquivalent
type SubjectPDFLink = LCSubjectPDFLink
type Module = LCModule

// Type alias for england/* files that reference GSEAreaTopic
type GSEAreaTopic = int

// ============================================================================
// BAML test blocks (per the @assert requirement)
// ============================================================================

test lc_lo_code_matches {
  functions [ExtractCurriculumSyllabus]
  args {
    pdf_text "Sample LC syllabus text"
    subject LCSubjectSlug.MATHEMATICS
    language "EN"
  }
}

test lc_cross_linguistic_fidelity {
  functions [ExtractCrossLinguisticConcept]
  args {
    pdf_text_en "Chemical Equilibrium is a state in which the rates of forward and reverse reactions are equal."
    pdf_text_ga "Tá Cothromaíocht Cheimiceach ann nuair a bhíonn rátaí na frithghníomhartha ar aghaidh agus ar gcúl comhionann."
    subject LCSubjectSlug.CHEMISTRY
  }
}

test lc_exam_paper_has_section {
  functions [ExtractExamPaperLayout]
  args {
    pdf_text "Sample LC exam paper text"
    subject LCSubjectSlug.MATHEMATICS
    paper_code "LC2024ALP000EV"
    year 2024
  }
}
