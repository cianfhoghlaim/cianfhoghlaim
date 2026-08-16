// BAML extraction: GCSE (England) — canonical 9-subject curriculum
//
// Per the 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1 change
// (Phase 4), this file is the canonical 8 BAML extraction entrypoint for
// the 9 priority GCSE subjects (the 9 core subjects offered by all 3
// boards — AQA / OCR / Edexcel). Existing BAML at
// `baml_src/british_isles/england/education/subject_taxonomy.baml` covers
// 43 GCSE subjects × 3 boards; this file is the canonical PRIORITY-9
// surface that the codegen pipeline (Phase 5) consumes.
//
// The 8 BAML functions exported below mirror the LC pattern exactly
// (per-subject conditional prompts for the 9 priority subjects). The
// 4-path OCR/VLM ensemble + RAGAS consensus produces the canonical
// row that's ingested into the BIEP DuckLake table.
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate
//
// Reference:
//   openspec/changes/2026-08-10-england-biiep-pipeline-v1/
//   openspec/changes/2026-08-13-web-monorepo-consolidation-and-agent-integration-v1/

// ============================================================================
// Enums (the canonical 9 GCSE priority subjects + 3 boards)
// ============================================================================

enum GCSEPrioritySubjectSlug {
  MATHEMATICS
  ENGLISH_LANGUAGE
  ENGLISH_LITERATURE
  BIOLOGY
  CHEMISTRY
  PHYSICS
  COMPUTER_SCIENCE
  HISTORY
  GEOGRAPHY
}

enum GCSEExamBoard {
  AQA
  OCR
  EDEXCEL
}

enum GCSELevel {
  FOUNDATION
  HIGHER
}

enum GCSELanguage {
  EN
  EN_AND_FR
  EN_AND_DE
  EN_AND_ES
  EN_AND_OTHER
}

// ============================================================================
// Core value types (the typed outputs from the 8 BAML extractions)
// ============================================================================

class GCSEUnit {
  unit_code string                    @description("e.g. 'AQA-8462-B1'")
  unit_title string
  unit_overview string
  learning_objectives GCSELearningObjective[]
  assessment_weight_pct float
}

class GCSELearningObjective {
  lo_code string
  lo_text string
  blooms_level GCSEBloomsLevel
}

enum GCSEBloomsLevel {
  REMEMBER
  UNDERSTAND
  APPLY
  ANALYSE
  EVALUATE
  CREATE
}

class GCSEExamPaper {
  exam_year int
  exam_board GCSEExamBoard
  subject GCSEPrioritySubjectSlug
  qualification string                  @description("GCSE")
  tier GCSELevel
  paper_number int
  total_marks int
  duration_minutes int
  sections GCSEExamSection[]
}

class GCSEExamSection {
  section_label string
  section_marks int
  questions GCSEExamQuestion[]
}

class GCSEExamQuestion {
  q_number string
  q_text string
  marks int
  topic_id string
}

class GCSEGradeBoundary {
  grade string
  percentage_min int
  percentage_max int
}

class GCSEPerQuestionScheme {
  q_number string
  total_marks int
  marking_notes string[]
  sample_answer string?
}

class GCSEExamPaperMarkingScheme {
  exam_year int
  exam_board GCSEExamBoard
  subject GCSEPrioritySubjectSlug
  tier GCSELevel
  grade_boundaries GCSEGradeBoundary[]
  per_question_scheme GCSEPerQuestionScheme[]
}

class GCSESyllabusDiagram {
  diagram_id string
  caption string
  diagram_type string
  associated_topic_id string
}

class GCSEBilingualConcept {
  en_concept GCSEConcept
  other_language_concept GCSEConcept?
  equivalence_score float
}

class GCSEConcept {
  term string
  definition string
  lo_code string
}

class GCSEAreaOfStudy {
  area_topics GCSEAreaTopic[]
  total_topics int
}

class GCSEAreaTopic {
  topic_id string
  topic_title string
  exam_weight_pct float
}

class GCSECrossSubjectTopicSet {
  subject GCSEPrioritySubjectSlug
  topics GCSEAreaTopic[]
  total_topics int
  cross_subject_bridges int
}

class GCSECrossSubjectTopic {
  topic_id string
  subject GCSEPrioritySubjectSlug
  topic_label string
  exam_weight_pct float
  related_subjects GCSEPrioritySubjectSlug[]
  cross_subject_topic_ids string[]
}

class GCSEAssessmentObjective {
  ao_code string
  ao_description string
  ao_weight_pct float
}

class GCSEPreparationPoint {
  level GCSELevel
  description string
  preparation_required string
}

class GCSEUnitAssessment {
  unit_code string
  assessment_type string                @description("written | practical | coursework")
  assessment_weight_pct float
  tier_restriction GCSELevel?
}

class GCSESyllabusSpec {
  subject GCSEPrioritySubjectSlug
  exam_board GCSEExamBoard
  qualification string
  tiered bool
  preparation_points GCSEPreparationPoint[]
  units GCSEUnit[]
  tiers GCSELevel[]
  assessment_objectives GCSEAssessmentObjective[]
  unit_assessments GCSEUnitAssessment[]
  areas_of_study GCSEAreaOfStudy[]
  cross_curricular string[]
  metadata GCSESyllabusMetadata
}

class GCSESyllabusMetadata {
  total_units int
  total_assessment_objectives int
  total_topics int
  total_learning_objectives int
  cross_subject_bridges int
}

class GCSECurriculumInfo {
  subject GCSEPrioritySubjectSlug
  exam_board GCSEExamBoard
  qualification string
  tier GCSELevel
  source_pdf string
}

class GCSEPedagogicalApproach {
  approach_name string
  approach_description string
  subject_alignment string
}

class GCSEAssessmentStructure {
  structure_name string
  structure_components string[]
  weighting_pct float
  subject GCSEPrioritySubjectSlug
}

class GCSEOCRStrand {
  strand_code string
  strand_name string
  strand_topics GCSEAreaTopic[]
}

class GCSEBoard {
  exam_board GCSEExamBoard
  qualification GCSEPrioritySubjectSlug
  spec_units GCSEUnit[]
  assessment_objectives GCSEAssessmentObjective[]
}

class GCSEAOASpec {
  subject GCSEPrioritySubjectSlug
  spec_id string
  qualification string
  exam_board GCSEExamBoard
  units GCSEUnit[]
  assessment_objectives GCSEAssessmentObjective[]
  tiered bool
  areas_of_study GCSEAreaOfStudy[]
  cross_curricular string[]
}

class GCSEPedagogicalStrategy {
  subject GCSEPrioritySubjectSlug
  exam_board GCSEExamBoard
  strategy_name string
  strategy_description string
}

class GCSEQualifier {
  qualification string
  subject GCSEPrioritySubjectSlug
  exam_board GCSEExamBoard
  tier GCSELevel
  spec_id string
  units GCSEUnit[]
  assessment_objectives GCSEAssessmentObjective[]
}

class GCSEComponent {
  component_name string
  component_weight_pct float
  component_type string
  subject_area_weight_pct float
}

class GCSEEDEXCELUnit {
  unit_code string
  unit_title string
  exam_pct float
  tier_restriction GCSELevel?
}

class GCSEEDEXCELSpec {
  subject GCSEPrioritySubjectSlug
  spec_id string
  qualification string
  exam_board GCSEExamBoard
  units GCSEEDEXCELUnit[]
  tier_options GCSELevel[]
  assessment_objectives GCSEAssessmentObjective[]
}

class GCSEOverviewDescription {
  subject GCSEPrioritySubjectSlug
  exam_board GCSEExamBoard
  overview_text string
}

class GCSEAssessmentGuide {
  subject GCSEPrioritySubjectSlug
  exam_board GCSEExamBoard
  assessment_components GCSEComponent[]
  total_marks int
  grading_scale string
}

class GCSEUnitSpecification {
  spec_id string
  subject GCSEPrioritySubjectSlug
  qual_level string
  unit_code string
  unit_title string
  overview string
  learning_objectives GCSELearningObjective[]
  assessment_weight_pct float
}

class GCSEUnitContent {
  unit_code string
  unit_title string
  topics GSEAreaTopic[]
  conceptual_depth string
}

class GCSEAssessmentMethod {
  method_name string
  method_weight_pct float
  subject_area_weight_pct float
  qualification string
  exam_board GCSEExamBoard
}

class GCSEUnitPerformance {
  unit_code string
  assessment_objectives GCSELearningObjective[]
  exam_weight_pct float
  weight_pct float
}

class GCSEAOAStrand {
  strand_code string
  strand_name string
  strand_learning_objectives GCSELearningObjective[]
  topics GCSEAreaTopic[]
}

class GCSEEuroBilingualTerm {
  en_term string
  language string
  term_translation string
  source_year string
}

class GCSEAreaOfStudyTopic {
  topic_id string
  topic_title string
  topic_learning_objectives GCSELearningObjective[]
}

class GCSEExamQuota {
  subject GCSEPrioritySubjectSlug
  exam_board GCSEExamBoard
  tier GCSELevel
  questions_count int
  total_marks int
}

// ============================================================================
// BAML function 1: ExtractGCSECurriculumSyllabus (the canonical GCSE extractor)
// ============================================================================

function ExtractGCSECurriculumSyllabus(
  pdf_text: string,
  subject: GCSEPrioritySubjectSlug,
  exam_board: GCSEExamBoard,
) -> GCSESyllabusSpec {
  client MiniMaxM3Client
  prompt #"
    {{ _.role("user") }}
    You are an expert at reading official awarding-body GCSE specification
    documents (AQA / OCR / Edexcel) and extracting their structure with
    complete fidelity — every fact below MUST be grounded in the PDF text
    given; never invent a unit, learning objective, or AO code that is not
    actually present.

    Subject: {{ subject }}
    Exam Board: {{ exam_board }}

    From the spec PDF text below, extract:
    - subject: the subject slug
    - exam_board: AQA | OCR | EDEXCEL
    - qualification: "GCSE"
    - tiered: bool (whether the spec has Foundation + Higher tiers)
    - preparation_points: array of {level, description, preparation_required}
      - level: GCSELevel (FOUNDATION | HIGHER)
      - description: brief description of the tier
      - preparation_required: what preparation is recommended
    - units: array of {unit_code, unit_title, unit_overview, learning_objectives: [{lo_code, lo_text, blooms_level}], assessment_weight_pct}
    - tiers: array of GCSELevel
    - assessment_objectives: array of {ao_code, ao_description, ao_weight_pct}
    - unit_assessments: array of {unit_code, assessment_type, assessment_weight_pct, tier_restriction}
    - areas_of_study: array of {area_topics: [{topic_id, topic_title, exam_weight_pct}], total_topics}
    - cross_curricular: any named cross-curricular links
    - metadata: {total_units, total_assessment_objectives, total_topics, total_learning_objectives, cross_subject_bridges}

    Subject-specific guidance:
    {% if subject == GCSEPrioritySubjectSlug.MATHEMATICS %}
    - 3 papers: Paper 1 (non-calculator), Paper 2 (calculator), Paper 3 (calculator)
    - Foundation tier: 1-5 grades; Higher tier: 4-9 grades
    - Capture formulas as separate formula arrays (e.g. "Volume of sphere = 4/3πr³")
    - AQA spec code 8462; OCR J560; Edexcel 1MA1
    {% elif subject == GCSEPrioritySubjectSlug.ENGLISH_LANGUAGE %}
    - 2 papers: Paper 1 (explorations in creative reading + writing), Paper 2 (writers' viewpoints + perspectives)
    - 3 components: 1 non-exam assessment + 2 external exams
    - AQA spec code 8700; OCR J351; Edexcel 1EN0
    {% elif subject == GCSEPrioritySubjectSlug.ENGLISH_LITERATURE %}
    - 2 papers: Paper 1 (Shakespeare + 19th century novel), Paper 2 (modern text + poetry)
    - 3 components: 1 non-exam assessment + 2 external exams
    - AQA spec code 8702; OCR J352; Edexcel 1ET0
    - Capture the prescribed texts (Shakespeare + 19th century novel + modern + poetry)
    {% elif subject == GCSEPrioritySubjectSlug.BIOLOGY %}
    - 2 papers: Paper 1 (cell biology + organisation), Paper 2 (infection + bioenergetics + ecosystems)
    - 10 required practical activities
    - AQA spec code 8461; OCR J247; Edexcel 1BI0
    - Capture the 7 key topics (cell biology, organisation, infection, bioenergetics, etc.)
    {% elif subject == GCSEPrioritySubjectSlug.CHEMISTRY %}
    - 2 papers: Paper 1 (atomic structure + bonding), Paper 2 (rates + equilibrium + organic)
    - 10 required practical activities
    - AQA spec code 8462; OCR J248; Edexcel 1CH0
    - Capture the 5 required practical headings (titration, distillation, etc.)
    {% elif subject == GCSEPrioritySubjectSlug.PHYSICS %}
    - 2 papers: Paper 1 (energy + particles + waves), Paper 2 (forces + electricity + magnetism + modern physics)
    - 10 required practical activities
    - AQA spec code 8463; OCR J249; Edexcel 1PH0
    - Capture formulas: F=ma, V=IR, E=mc², etc.
    - 7 SI base units
    {% elif subject == GCSEPrioritySubjectSlug.COMPUTER_SCIENCE %}
    - 2 papers: Paper 1 (computational thinking + programming), Paper 2 (data + algorithms + networks)
    - Programming project (controlled assessment)
    - AQA spec code 8525; OCR J277; Edexcel 1CP2
    - Capture pseudocode algorithms (sort, search, etc.)
    - 10 algorithms you must know
    {% elif subject == GCSEPrioritySubjectSlug.HISTORY %}
    - 3 papers: Paper 1 (thematic study + historic environment), Paper 2 (period study + breadth study), Paper 3 (modern depth study)
    - AQA spec code 8145; OCR J410; Edexcel 1HI0
    - Capture the prescribed topics (e.g. Medicine through time, Weimar Germany)
    {% elif subject == GCSEPrioritySubjectSlug.GEOGRAPHY %}
    - 3 papers: Paper 1 (Living with the physical environment), Paper 2 (Challenges in the human environment), Paper 3 (Geographical applications)
    - 2 field work investigations (mandatory)
    - AQA spec code 8035; OCR J383; Edexcel 1GA0
    - Capture the 3 synoptic themes (climate change, sustainable development, globalisation)
    {% endif %}

    GCSE Specification PDF text:
    {{ pdf_text }}

    {{ ctx.output_format }}
  "#
}

// ============================================================================
// BAML functions 2-8: Exam paper, Marking scheme, Diagram, Cross-linguistic, Cross-subject
// (canonical exports — mirror the LC pattern exactly)
// ============================================================================

function ExtractGCSEExamPaperLayout(
  pdf_text: string,
  subject: GCSEPrioritySubjectSlug,
  exam_board: GCSEExamBoard,
) -> GCSEExamPaper {
  client MiniMaxM3Client
  prompt #"
    {{ _.role("user") }}
    You are an expert GCSE exam paper layout extractor for `{{ subject }}` (board: {{ exam_board }}).

    Extract:
    - exam_year
    - exam_board: AQA | OCR | EDEXCEL
    - subject
    - qualification: "GCSE"
    - tier: FOUNDATION | HIGHER
    - paper_number
    - total_marks
    - duration_minutes (typically 60-105 for GCSE)
    - sections: array of {section_label, section_marks, questions: [{q_number, q_text, marks, topic_id}]}

    Subject-specific guidance:
    {% if subject == GCSEPrioritySubjectSlug.MATHEMATICS %}
    - 3 papers: P1 (90 min, 80 marks), P2 (90 min, 80 marks), P3 (90 min, 80 marks)
    - Non-calculator (P1) vs calculator (P2, P3)
    {% elif subject == GCSEPrioritySubjectSlug.ENGLISH_LANGUAGE %}
    - 2 papers: P1 (1h 45min, 80 marks), P2 (1h 30min, 80 marks)
    - Non-exam assessment: Spoken Language endorsement (0% weighted)
    {% elif subject == GCSEPrioritySubjectSlug.BIOLOGY %}
    - 2 papers: P1 (1h 45min, 100 marks), P2 (1h 45min, 100 marks)
    - 10 required practicals assessed
    {% elif subject == GCSEPrioritySubjectSlug.CHEMISTRY %}
    - 2 papers: P1 (1h 45min, 100 marks), P2 (1h 45min, 100 marks)
    - 10 required practicals
    {% elif subject == GCSEPrioritySubjectSlug.PHYSICS %}
    - 2 papers: P1 (1h 45min, 100 marks), P2 (1h 45min, 100 marks)
    - 10 required practicals
    {% elif subject == GCSEPrioritySubjectSlug.HISTORY %}
    - 3 papers: P1 (1h 15min, 55 marks), P2 (1h 45min, 80 marks), P3 (1h 20min, 65 marks)
    {% elif subject == GCSEPrioritySubjectSlug.GEOGRAPHY %}
    - 3 papers: P1 (1h 30min, 88 marks), P2 (1h 30min, 88 marks), P3 (1h 15min, 76 marks)
    {% endif %}

    Exam paper PDF text:
    {{ pdf_text }}

    {{ ctx.output_format }}
  "#
}

function ExtractGCSEMarkingSchemeGuideline(
  pdf_text: string,
  subject: GCSEPrioritySubjectSlug,
  exam_board: GCSEExamBoard,
) -> GCSEExamPaperMarkingScheme {
  client MiniMaxM3Client
  prompt #"
    {{ _.role("user" }}
    You are an expert GCSE marking scheme extractor for `{{ subject }}` (board: {{ exam_board }}).

    Extract:
    - exam_year
    - exam_board
    - subject
    - tier: FOUNDATION | HIGHER
    - grade_boundaries: array of {grade, percentage_min, percentage_max}
    - per_question_scheme: array of {q_number, total_marks, marking_notes, sample_answer}

    Subject-specific guidance:
    {% if subject == GCSEPrioritySubjectSlug.MATHEMATICS %}
    - Foundation tier: 9-1 to 5-3 grades (grade 9 = 78-100%, 5-3 = 0-22%)
    - Higher tier: 9-4 to 4-1 grades
    {% elif subject == GCSEPrioritySubjectSlug.ENGLISH_LANGUAGE %}
    - Grade boundaries range 9-1 to 5-2 (Foundation) or 9-9 to 4-1 (Higher)
    - 240 marks total across 2 papers
    {% elif subject == GCSEPrioritySubjectSlug.BIOLOGY %}
    - Grade boundaries: 9-9 (top), 4-4 (bottom pass)
    - 200 marks total
    {% endif %}

    Marking scheme PDF text:
    {{ pdf_text }}

    {{ ctx.output_format }}
  "#
}

function ExtractGCSESyllabusDiagram(
  pdf_text: string,
  subject: GCSEPrioritySubjectSlug,
) -> GCSESyllabusDiagram[] {
  client MiniMaxM3Client
  prompt #"
    {{ _.role("user" }}
    Extract diagrams from the GCSE `{{ subject }}` syllabus.

    For each diagram:
    - diagram_id
    - caption
    - diagram_type: "graph" | "table" | "flowchart" | "diagram" | "equation" | "map" | "other"
    - associated_topic_id (the LO code the diagram supports)

    Subject-specific guidance:
    {% if subject == GCSEPrioritySubjectSlug.MATHEMATICS %}
    - Diagrams are typically graphs, charts, or geometric diagrams
    {% elif subject == GCSEPrioritySubjectSlug.CHEMISTRY %}
    - Diagrams are typically molecular structures, reaction mechanisms, or apparatus
    {% elif subject == GCSEPrioritySubjectSlug.BIOLOGY %}
    - Diagrams are typically cell structures, food webs, or genetic crosses
    {% elif subject == GCSEPrioritySubjectSlug.PHYSICS %}
    - Diagrams are typically circuit diagrams, force diagrams, or ray diagrams
    {% elif subject == GCSEPrioritySubjectSlug.GEOGRAPHY %}
    - Diagrams are typically maps, climate cross-sections, or population pyramids
    {% elif subject == GCSEPrioritySubjectSlug.HISTORY %}
    - Diagrams are typically timelines, source matrices, or cause-effect diagrams
    {% endif %}

    Syllabus PDF text:
    {{ pdf_text }}

    {{ _.role("user" }}
    {{ ctx.output_format }}
  "#
}

function ExtractGCSECrossSubjectTopics(
  pdf_text: string,
  subject: GCSEPrioritySubjectSlug,
  exam_board: GCSEExamBoard,
) -> GCSECrossSubjectTopicSet {
  client BiepGeneralClient
  prompt #"
    {{ _.role("user" }}
    Extract the cross-subject topic map for GCSE `{{ subject }}` (board: {{ exam_board }}).

    For each topic:
    - topic_id (e.g. "MATH-NUM-CALA-001")
    - subject: {{ subject }}
    - topic_label
    - exam_weight_pct
    - related_subjects: array of GCSEPrioritySubjectSlug
    - cross_subject_topic_ids: array of bridging topic IDs

    GCSE syllabus PDF text:
    {{ pdf_text }}

    {{ ctx.output_format }}
  "#
}

// ============================================================================
// Clients (the 4 extraction backends)
// ============================================================================

client<llm> MiniMaxM3Client {
  provider "openai-generic"
  options {
    base_url env.MINIMAX_BASE_URL
    api_key env.MINIMAX_API_KEY
    model "minimax-m3"
  }
}

client<llm> BiepGeneralClient {
  provider "openai-generic"
  options {
    base_url env.MINIMAX_BASE_URL
    api_key env.MINIMAX_API_KEY
    model "minimax-m3"
  }
}
