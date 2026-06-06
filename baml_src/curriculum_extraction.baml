// BAML Schema for Curriculum Extraction
// Type-safe extraction of learning outcome relationships

// =============================================================================
// Relationship Types
// =============================================================================

enum RelationshipType {
  PREREQUISITE_FOR  @description("Source outcome must be learned before target")
  BUILDS_ON         @description("Target extends concepts from source")
  ASSESSES          @description("Outcome assesses a specific skill")
  RELATED_TO        @description("Outcomes share conceptual overlap")
  PART_OF           @description("Outcome is part of a larger competency")
  ENABLES           @description("Source outcome enables target")
  CONTRASTS_WITH    @description("Outcomes represent contrasting concepts")
}

enum DifficultyLevel {
  FOUNDATION        @description("Basic foundational level")
  ORDINARY          @description("Standard ordinary level")
  HIGHER            @description("Advanced higher level")
  EXTENSION         @description("Extension or enrichment")
}

enum EducationLevel {
  PRIMARY           @description("Primary school (ages 4-12)")
  JUNIOR_CYCLE      @description("Junior Cycle (ages 12-15)")
  SENIOR_CYCLE      @description("Senior Cycle (ages 15-18)")
  TRANSITION_YEAR   @description("Transition Year (age 15-16)")
}

// =============================================================================
// Learning Outcome Types
// =============================================================================

class LearningOutcome {
  code string @description("Unique outcome identifier, e.g., 'LO-MATH-JC-2.1'")
  description_en string @description("Description in English")
  description_ga string? @description("Description in Irish (Gaeilge)")
  subject string @description("Subject code, e.g., 'mathematics', 'irish'")
  level EducationLevel @description("Education level")
  difficulty DifficultyLevel @description("Difficulty level")
  strand string? @description("Curriculum strand")
  strand_unit string? @description("Strand unit within the strand")
  key_skills string[] @description("Key skills this outcome develops")
}

class ExtractedRelationship {
  target_code string @description("Code of the target learning outcome")
  relationship_type RelationshipType @description("Type of relationship")
  confidence float @description("Confidence score 0.0-1.0")
  reasoning string @description("Brief explanation for this relationship")
}

class RelationshipExtractionResult {
  source_code string @description("Code of the source learning outcome")
  relationships ExtractedRelationship[] @description("Extracted relationships")
  processing_notes string? @description("Any notes about the extraction")
}

// =============================================================================
// Skill Extraction
// =============================================================================

enum SkillCategory {
  COGNITIVE         @description("Thinking, reasoning, problem-solving")
  LINGUISTIC        @description("Language, communication, literacy")
  MATHEMATICAL      @description("Numeracy, calculation, logic")
  CREATIVE          @description("Creativity, imagination, design")
  SOCIAL            @description("Collaboration, teamwork, empathy")
  PHYSICAL          @description("Motor skills, coordination")
  DIGITAL           @description("Technology, digital literacy")
  METACOGNITIVE     @description("Self-awareness, learning-to-learn")
}

class Skill {
  id string @description("Unique skill identifier")
  name string @description("Skill name")
  category SkillCategory @description("Category of skill")
  description string @description("Detailed description")
  proficiency_levels string[] @description("Levels of proficiency")
}

class SkillExtractionResult {
  outcome_code string @description("Learning outcome being analyzed")
  skills Skill[] @description("Skills assessed by this outcome")
  primary_skill string? @description("ID of the primary skill")
}

// =============================================================================
// Curriculum Document Extraction
// =============================================================================

class CurriculumSection {
  title string @description("Section title")
  content string @description("Section content text")
  section_type string @description("Type: strand, unit, outcome, assessment")
  page_number int? @description("Page number in source document")
}

class ExtractedCurriculumDocument {
  document_id string @description("Document identifier")
  title string @description("Document title")
  subject string @description("Subject covered")
  level EducationLevel @description("Education level")
  year int @description("Curriculum year")
  sections CurriculumSection[] @description("Extracted sections")
  learning_outcomes LearningOutcome[] @description("Extracted learning outcomes")
}

// =============================================================================
// Functions
// =============================================================================

function ExtractLearningOutcomeRelationships(source_outcome: LearningOutcome,
  target_outcomes: LearningOutcome[],
  subject_context: string) -> RelationshipExtractionResult {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"Extract the requested data.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}

"#
}

function ExtractSkillsFromOutcome(outcome: LearningOutcome,
  curriculum_context: string) -> SkillExtractionResult {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"Extract the requested data.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}

"#
}

function ExtractCurriculumFromDocument(document_text: string,
  subject: string,
  level: EducationLevel) -> ExtractedCurriculumDocument {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"Extract the requested data.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}

"#
}

function IdentifyPrerequisiteChain(target_outcome: LearningOutcome,
  available_outcomes: LearningOutcome[],
  max_depth: int) -> LearningOutcome[] {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"Extract the requested data.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}

"#
}

// =============================================================================
// Enhanced Curriculum Specification Types
// =============================================================================

class EnhancedLearningOutcome {
  outcome_code string @description("Unique code, e.g., 'LO-MATH-JC-2.1'")
  text string @description("Full outcome text")
  text_ga string? @description("Irish language version")
  strand string @description("e.g., 'Algebra', 'Statistics'")
  strand_unit string? @description("Sub-unit within strand")
  level string? @description("Foundation/Ordinary/Higher")
  action_verbs string[] @description("Action verbs (apply, analyse, evaluate)")
  cross_curricular bool @description("Links to other subjects")
  linked_subjects string[] @description("Related subject codes if cross-curricular")
  key_skills string[] @description("Irish curriculum key skills")
  assessment_focus string? @description("How this outcome is typically assessed")
}

class CurriculumStrand {
  name string @description("Strand name")
  name_ga string? @description("Irish name")
  description string @description("Strand description")
  learning_outcomes EnhancedLearningOutcome[] @description("Outcomes in this strand")
  weighting float? @description("Percentage weighting in assessment")
}

class AssessmentComponent {
  name string @description("Component name (Written Exam, Coursework, Oral)")
  weighting int @description("Percentage weighting")
  duration string? @description("Duration if timed (e.g., '2h 30min')")
  description string? @description("Component description")
  levels string[] @description("Levels offered (Foundation, Ordinary, Higher)")
}

class AssessmentInfo {
  components AssessmentComponent[] @description("Assessment components")
  total_marks int? @description("Total marks available")
  coursework_percentage int? @description("Percentage for coursework")
  external_percentage int? @description("Percentage for external exam")
  grading_scheme string? @description("Grading approach")
}

class CurriculumSpecification {
  document_id string @description("Unique document identifier")
  title string @description("Full document title")
  title_ga string? @description("Irish title")
  subject string @description("Subject code")
  cycle EducationLevel @description("Education cycle")
  language string @description("Document language (en/ga)")
  version_year int @description("Specification version year")
  specification_type string @description("syllabus or specification")
  development_status string @description("current, redevelopment, etc.")
  strands CurriculumStrand[] @description("Curriculum strands")
  learning_outcomes EnhancedLearningOutcome[] @description("All learning outcomes")
  assessment_info AssessmentInfo? @description("Assessment information")
  key_skills_mapping map<string, string[]> @description("Key skills to outcomes mapping")
  rationale string? @description("Subject rationale/aims")
  total_hours int? @description("Recommended teaching hours")
}

// =============================================================================
// Examination Paper Types
// =============================================================================

enum ExamLevel {
  HIGHER           @description("Higher Level")
  ORDINARY         @description("Ordinary Level")
  FOUNDATION       @description("Foundation Level")
  COMMON           @description("Common Level")
}

enum QuestionType {
  MULTIPLE_CHOICE  @description("MCQ questions")
  SHORT_ANSWER     @description("Brief written response")
  LONG_ANSWER      @description("Extended written response")
  CALCULATION      @description("Mathematical calculation")
  ESSAY            @description("Essay or extended writing")
  PRACTICAL        @description("Practical/coursework based")
  COMPREHENSION    @description("Reading comprehension")
  TRANSLATION      @description("Language translation")
  AURAL            @description("Listening comprehension")
  ORAL             @description("Speaking assessment")
}

class ExamQuestion {
  question_number string @description("Question number (e.g., '1', '2a', '3bii')")
  marks int @description("Marks allocated")
  question_type QuestionType @description("Type of question")
  topic string? @description("Topic or strand covered")
  difficulty_estimate DifficultyLevel? @description("Estimated difficulty")
  text string @description("Question text")
  sub_questions ExamQuestion[] @description("Sub-parts if any")
  learning_outcomes string[] @description("LO codes this question assesses")
}

class ExamSection {
  section_name string @description("Section identifier (A, B, C or name)")
  title string? @description("Section title")
  instructions string? @description("Section-specific instructions")
  total_marks int @description("Total marks for section")
  questions ExamQuestion[] @description("Questions in this section")
  choice_instructions string? @description("e.g., 'Answer 3 of 5'")
}

class ExamPaper {
  subject string @description("Subject code")
  year int @description("Examination year")
  level ExamLevel @description("Exam level")
  paper_number int @description("Paper 1, Paper 2, etc.")
  language string @description("Paper language (en/ga)")
  duration string @description("Exam duration")
  total_marks int @description("Total marks available")
  sections ExamSection[] @description("Paper sections")
  general_instructions string? @description("General exam instructions")
  materials_allowed string[] @description("Permitted materials (calculator, etc.)")
  pdf_url string? @description("Source PDF URL")
}

class MarkingScheme {
  subject string @description("Subject code")
  year int @description("Examination year")
  level ExamLevel @description("Exam level")
  paper_number int @description("Paper number")
  language string @description("Scheme language")
  sections MarkingSection[] @description("Marking sections")
  general_guidelines string? @description("General marking guidelines")
}

class MarkingSection {
  section_name string @description("Section identifier")
  questions MarkingCriteria[] @description("Marking criteria per question")
}

class MarkingCriteria {
  question_number string @description("Question number")
  total_marks int @description("Marks available")
  marking_points MarkingPoint[] @description("Breakdown of marks")
  acceptable_answers string[] @description("List of acceptable answers")
  notes string? @description("Examiner notes")
}

class MarkingPoint {
  description string @description("What is being marked")
  marks int @description("Marks for this point")
  partial_credit bool @description("Whether partial credit allowed")
}

class ExaminerReport {
  subject string @description("Subject code")
  year int @description("Examination year")
  level ExamLevel @description("Exam level")
  language string @description("Report language")
  overall_commentary string @description("General commentary")
  candidate_performance string @description("Summary of performance")
  recommendations string[] @description("Recommendations for teachers/students")
  question_analyses QuestionAnalysis[] @description("Per-question analysis")
  statistics ExamStatistics? @description("Statistical information")
}

class QuestionAnalysis {
  question_number string @description("Question analyzed")
  performance_summary string @description("How candidates performed")
  common_errors string[] @description("Frequently observed errors")
  exemplar_answers string[] @description("Examples of good answers")
  recommendations string[] @description("Teaching recommendations")
}

class ExamStatistics {
  total_candidates int? @description("Number of candidates")
  mean_mark float? @description("Mean mark achieved")
  grade_distribution map<string, float>? @description("% at each grade")
  year_on_year_comparison string? @description("Comparison with previous years")
}

// =============================================================================
// Extraction Functions for Exam Papers
// =============================================================================

function ExtractExamPaperStructure(document_text: string,
  subject: string,
  year: int,
  level: ExamLevel,
  paper_number: int) -> ExamPaper {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"Extract the requested data.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}

"#
}

function ExtractMarkingScheme(document_text: string,
  subject: string,
  year: int,
  level: ExamLevel) -> MarkingScheme {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"Extract the requested data.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}

"#
}

function ExtractExaminerReportInsights(document_text: string,
  subject: string,
  year: int,
  level: ExamLevel) -> ExaminerReport {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"Extract the requested data.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}

"#
}

function ExtractCurriculumSpecification(document_text: string,
  subject: string,
  cycle: EducationLevel,
  language: string) -> CurriculumSpecification {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"Extract the requested data.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}

"#
}

function MapOutcomesToExamQuestions(specification: CurriculumSpecification,
  exam_papers: ExamPaper[]
) -> map<string, string[]> {
  client LiteLLM
  prompt #"
    You are an expert curriculum analyst.

    Map learning outcomes to examination questions.

    CURRICULUM SPECIFICATION:
    Subject: {{ specification.subject }}
    Cycle: {{ specification.cycle }}

    LEARNING OUTCOMES:
    {% for outcome in specification.learning_outcomes %}
    - {{ outcome.outcome_code }}: {{ outcome.text }}
    {% endfor %}

    EXAM PAPERS:
    {% for paper in exam_papers %}
    Paper {{ paper.paper_number }} ({{ paper.year }}, {{ paper.level }}):
    {% for section in paper.sections %}
      {% for q in section.questions %}
      - Q{{ q.question_number }}: {{ q.text }}
      {% endfor %}
    {% endfor %}
    {% endfor %}

    For each learning outcome, identify which exam questions assess it.
    Return a mapping of outcome codes to lists of question identifiers.

    Format question identifiers as: YEAR-LEVEL-PAPER-QUESTION
    e.g., "2023-H-1-3a" for 2023 Higher Paper 1 Question 3a

    Return as {{ ctx.output_format }}.
  "#
}

// =============================================================================
// Test Cases
// =============================================================================

test ExtractRelationshipsTest {
  functions [ExtractLearningOutcomeRelationships]
  args {
    source_outcome {
      code "LO-MATH-JC-2.3"
      description_en "Solve linear equations with one unknown"
      subject "mathematics"
      level JUNIOR_CYCLE
      difficulty ORDINARY
      strand "Algebra"
      strand_unit "Equations"
      key_skills ["Problem Solving", "Logical Reasoning"]
    }
    target_outcomes [
      {
        code "LO-MATH-JC-2.1"
        description_en "Understand and use variables in expressions"
        subject "mathematics"
        level JUNIOR_CYCLE
        difficulty FOUNDATION
        strand "Algebra"
        strand_unit "Expressions"
        key_skills ["Symbolic Representation"]
      },
      {
        code "LO-MATH-JC-2.4"
        description_en "Solve systems of linear equations"
        subject "mathematics"
        level JUNIOR_CYCLE
        difficulty HIGHER
        strand "Algebra"
        strand_unit "Equations"
        key_skills ["Problem Solving", "Logical Reasoning"]
      }
    ]
    subject_context "Irish Junior Cycle Mathematics curriculum"
  }
}

test ExtractSkillsTest {
  functions [ExtractSkillsFromOutcome]
  args {
    outcome {
      code "LO-IRISH-JC-3.2"
      description_en "Engage in conversations on everyday topics using appropriate vocabulary"
      description_ga "Páirt a ghlacadh i gcomhráite ar ábhair laethúla le stór focal oiriúnach"
      subject "irish"
      level JUNIOR_CYCLE
      difficulty ORDINARY
      strand "Communication"
      strand_unit "Oral Skills"
      key_skills ["Communication", "Language Awareness"]
    }
    curriculum_context "Junior Cycle Irish language curriculum focusing on communicative competence"
  }
}

// =============================================================================
// Document Metadata Extraction
// =============================================================================

enum DocumentCategory {
  SPECIFICATION           @description("Modern curriculum specifications")
  SYLLABUS                @description("Older curriculum syllabi")
  MEETING_MINUTES         @description("Curriculum development group meeting minutes")
  ASSESSMENT_GUIDELINES   @description("Guidelines for CBAs or final assessments")
  FRAMEWORK               @description("Overarching educational frameworks")
  CONSULTATION_DOCUMENT   @description("Drafts or feedback on proposed changes")
  EXAM_PAPER              @description("State examination papers")
  MARKING_SCHEME          @description("State examination marking schemes")
  EXAMINER_REPORT         @description("Chief examiner reports")
  OTHER                   @description("Other documents")
}

class DocumentMetadata {
  title string           @description("The contextual title, e.g. \"Leaving Certificate English Specification\"")
  category DocumentCategory
  subject_slug string?
  cycle EducationLevel?   
  year_effective int?    @description("Extracted from phrases like \"effect earlier than 2027\"")
  year_examined int?     @description("Extracted from phrases like \"examination to 2028\"")
  language string?       @description("en or ga")
  url string             @description("The exact URL to the PDF")
}

function ExtractAllPdfMetadata(
  page_markdown: string,
  pdf_urls: string[]) -> DocumentMetadata[] {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"Extract the requested data.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    {{ subject }}
    {{ cycle }}
    {{page_markdown}}
    {{pdf_urls}}
"#
}

// =============================================================================
// Senior Cycle (Leaving Certificate) — 50+ subjects, multi-paper, multi-level
// See: docs/bonneagar/education-subject-inventory.md:107-145
//      docs/data_engineering/education/Leaving Certificate Subject Analysis Plan.md
// =============================================================================

enum LeavingCertSubject {
  LC_MATHS                      @description("Mathematics")
  LC_APPLIED_MATHS              @description("Applied Mathematics")
  LC_ENGLISH                    @description("English")
  LC_GAEILGE                    @description("Gaeilge / Irish")
  LC_FRENCH                     @description("French")
  LC_GERMAN                     @description("German")
  LC_SPANISH                    @description("Spanish")
  LC_ITALIAN                    @description("Italian")
  LC_JAPANESE                   @description("Japanese")
  LC_RUSSIAN                    @description("Russian")
  LC_ARABIC                     @description("Arabic")
  LC_MANDARIN                   @description("Mandarin Chinese")
  LC_LATIN                      @description("Latin")
  LC_GREEK                      @description("Ancient Greek")
  LC_CLASSICAL_STUDIES          @description("Classical Studies")
  LC_HISTORY                    @description("History")
  LC_GEOGRAPHY                  @description("Geography")
  LC_PHYSICS                    @description("Physics")
  LC_CHEMISTRY                  @description("Chemistry")
  LC_BIOLOGY                    @description("Biology")
  LC_AGRICULTURAL_SCIENCE       @description("Agricultural Science")
  LC_BUSINESS                   @description("Business")
  LC_ACCOUNTING                 @description("Accounting")
  LC_ECONOMICS                  @description("Economics")
  LC_HOME_ECONOMICS_SOCIAL      @description("Home Economics — Social and Scientific")
  LC_ART                        @description("Art")
  LC_MUSIC                      @description("Music")
  LC_DCG                        @description("Design and Communication Graphics")
  LC_ENGINEERING                @description("Engineering")
  LC_TECHNOLOGY                 @description("Technology")
  LC_CONSTRUCTION_STUDIES       @description("Construction Studies")
  LC_PHYSICAL_EDUCATION         @description("Physical Education")
  LC_COMPUTER_SCIENCE           @description("Computer Science")
  LC_PHILOSOPHY                  @description("Philosophy")
  LC_POLITICS_AND_SOCIETY       @description("Politics and Society")
  LC_RELIGIOUS_EDUCATION        @description("Religious Education")
  LC_LINK_MODULES_LCVP          @description("Link Modules (LCVP)")
  LC_TRANSITION_YEAR            @description("Transition Year")
  LC_CAREERS_PORTFOLIO          @description("Careers Portfolio")
  LC_LCA_VOCATIONAL_PREP        @description("Leaving Certificate Applied — Vocational Preparation")
  LC_LCA_ENGLISH_COMM           @description("LCA — English and Communication")
  LC_LCA_GAEILGE_CUM            @description("LCA — Gaeilge Chumarsáideach")
  LC_LCA_MATHEMATICAL           @description("LCA — Mathematical Applications")
  LC_LCA_SOCIAL_EDUCATION       @description("LCA — Social Education")
  LC_LCA_HOTEL_CATERING         @description("LCA — Hotel, Catering and Tourism")
  LC_LCA_OFFICE_ADMIN           @description("LCA — Office Administration and Customer Care")
  LC_LCA_ICT                    @description("LCA — Information and Communication Technology")
  LC_LCA_ACTIVE_LEISURE         @description("LCA — Active Leisure Studies")
  LC_LCA_AGRICULTURE            @description("LCA — Agriculture/Horticulture")
  LC_LCA_CHILDCARE              @description("LCA — Childcare/Community Care")
  LC_LCA_CRAFT_DESIGN           @description("LCA — Craft and Design")
  LC_LCA_DANCE                  @description("LCA — Dance")
  LC_LCA_DRAMA                  @description("LCA — Drama")
  LC_LCA_ENGINEERING_LCA        @description("LCA — Engineering")
  LC_LCA_GRAPHICS_CONSTRUCTION  @description("LCA — Graphics and Construction Studies")
  LC_LCA_HAIR_BEAUTY            @description("LCA — Hair and Beauty")
  LC_LCA_LEISURE_RECREATION     @description("LCA — Leisure and Recreation")
  LC_LCA_MUSIC_LCA              @description("LCA — Music")
  LC_LCA_RELIGIOUS_ED           @description("LCA — Religious Education")
  LC_LCA_SCIENCE_LCA            @description("LCA — Science")
  LC_LCA_SIGN_LANGUAGE          @description("LCA — Sign Language")
  LC_LCA_TECHNOLOGY_LCA         @description("LCA — Technology")
  LC_LCA_VISUAL_ART             @description("LCA — Visual Art")
  LC_OTHER                      @description("Fallback for new subjects not yet catalogued")
}

enum Specialism {
  SCIENCES
  LANGUAGES
  BUSINESS
  HUMANITIES
  PRACTICAL
  ARTS
  APPLIED
  INTERDISCIPLINARY
}

enum AssessmentComponentType {
  WRITTEN
  ORAL
  AURAL
  PRACTICAL
  COURSEWORK
  CBA
  PROJECT
  PORTFOLIO
}

class ExamAssessmentComponent {
  type AssessmentComponentType
  weight_pct int
  duration_minutes int?
  language string
  levels ExamLevel[]
}

enum RubricStyle {
  PCLM                            @description("Purpose / Coherence / Language / Mechanics — English")
  SRP                             @description("Significant Relevant Points — Geography, History")
  EQUATION_STEPS                  @description("Step-by-step equation solving — Mathematics, Physics")
  KEYWORD_MATCH_DIAGRAM            @description("Mandatory keyword + diagram labels — Biology, Science")
  COMPREHENSION_EXPRESSION        @description("Compréhension / expression — French, German, Spanish")
  SECTION_B_KEYWORD                @description("Section B keyword marks — Business, Accounting")
  DIAGRAM_SKETCH_STEPS            @description("Diagram / sketch + reasoning — Construction Studies, DCG")
  BALANCED_EQUATION_STATE_SYMBOLS @description("Balanced equations with state symbols — Chemistry")
  DEFINITION_UNIT_FORMULA          @description("Definition + unit + formula — Physics, Ag Science")
  RUBRIC_PCLM_IRISH                @description("Cumarsáid / Léamhthuiscint / Litríocht / Gramadach — Gaeilge")
  LINGUISTIC_PRINCIPLES            @description("Linguistic principles + examples — MFL, Classical languages")
}

class SpecialismRubric {
  specialism Specialism
  rubric_style RubricStyle
  descriptors RubricDescriptor[]  @description("From junior_cycle.baml (cross-BAML reference)")
  weight_per_descriptor_pct float?
}

class SubjectRubric {
  subject LeavingCertSubject
  style RubricStyle
  descriptors RubricDescriptor[]
  source_url string               @description("Link to NCCA spec or SEC examiner report")
  document_year int
}

class RubricScore {
  subject LeavingCertSubject
  total_score float               @description("0-100")
  descriptor_scores map<string, float>  @description("descriptor text → score 0-100")
  strengths string[]
  improvements string[]
  reviewer_notes_en string
  reviewer_notes_ga string?
}

class MarkingSchemeDiff {
  subject LeavingCertSubject
  year_a int
  year_b int
  added_questions string[]        @description("Question IDs only in year_b")
  removed_questions string[]      @description("Question IDs only in year_a")
  changed_marks map<string, int>   @description("Question ID → year_b marks - year_a marks")
  topic_drift_en string           @description("Plain English summary of the drift")
  topic_drift_ga string?
}

class ExtractionBudget {
  session_id string
  papers_extracted int            @description("Number of papers extracted in this session")
  tokens_consumed int
  last_extraction_at string
  reset_at string                 @description("ISO 8601 timestamp when the budget resets")
  remaining_papers int            @description("5 - papers_extracted, default daily budget")
}

function ExtractSubjectRubric(text: string,
  subject: LeavingCertSubject) -> SubjectRubric {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"Extract the requested data.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    {{text}}
    {{subject}}
"#
}

function ScoreEssayAgainstRubric(essay: string,
  rubric: SubjectRubric) -> RubricScore {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"Extract the requested data.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    {{essay}}
    {{rubric}}
"#
}

function CompareMarkingSchemes(year_a: int,
  year_b: int,
  subject: LeavingCertSubject) -> MarkingSchemeDiff {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"Extract the requested data.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    {{year_a}}
    {{year_b}}
    {{subject}}
"#
}

function LazyExtractExamPaper(text: string,
  subject: LeavingCertSubject,
  year: int,
  level: ExamLevel,
  paper_number: int) -> ExamPaper {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"Extract the requested data.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    {{text}}
    {{subject}}
    {{year}}
    {{level}}
    {{paper_number}}
"#
}

