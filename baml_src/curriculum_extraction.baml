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

function ExtractLearningOutcomeRelationships(
  source_outcome LearningOutcome,
  target_outcomes LearningOutcome[],
  subject_context string
) -> RelationshipExtractionResult {
  client LiteLLM
  prompt #"
    You are an expert curriculum analyst specializing in Irish education.

    Analyze relationships between learning outcomes in {{ subject_context }}.

    SOURCE LEARNING OUTCOME:
    Code: {{ source_outcome.code }}
    Description (EN): {{ source_outcome.description_en }}
    {{ if source_outcome.description_ga }}Description (GA): {{ source_outcome.description_ga }}{{ endif }}
    Subject: {{ source_outcome.subject }}
    Level: {{ source_outcome.level }}
    Difficulty: {{ source_outcome.difficulty }}
    {{ if source_outcome.strand }}Strand: {{ source_outcome.strand }}{{ endif }}
    {{ if source_outcome.strand_unit }}Unit: {{ source_outcome.strand_unit }}{{ endif }}
    Key Skills: {{ source_outcome.key_skills }}

    POTENTIAL TARGET OUTCOMES:
    {{ for target in target_outcomes }}
    - {{ target.code }}: {{ target.description_en }}
      Level: {{ target.level }}, Difficulty: {{ target.difficulty }}
    {{ endfor }}

    For each meaningful relationship found:
    1. Identify the relationship type (PREREQUISITE_FOR, BUILDS_ON, ASSESSES, RELATED_TO, PART_OF, ENABLES, CONTRASTS_WITH)
    2. Assign a confidence score (0.0-1.0)
    3. Provide brief reasoning

    Only include relationships with confidence >= 0.6.
    Consider curriculum progression, conceptual dependencies, and skill development.

    Return your analysis as {{ ctx.output_format }}.
  "#
}

function ExtractSkillsFromOutcome(
  outcome LearningOutcome,
  curriculum_context string
) -> SkillExtractionResult {
  client LiteLLM
  prompt #"
    You are an expert curriculum analyst.

    Analyze this learning outcome to identify the skills it develops and assesses.

    LEARNING OUTCOME:
    Code: {{ outcome.code }}
    Description: {{ outcome.description_en }}
    Subject: {{ outcome.subject }}
    Level: {{ outcome.level }}
    Key Skills Listed: {{ outcome.key_skills }}

    CURRICULUM CONTEXT:
    {{ curriculum_context }}

    Extract all skills this outcome develops, including:
    - The skill category (COGNITIVE, LINGUISTIC, MATHEMATICAL, CREATIVE, SOCIAL, PHYSICAL, DIGITAL, METACOGNITIVE)
    - A clear name and description
    - Proficiency levels expected

    Identify which skill is the primary focus.

    Return your analysis as {{ ctx.output_format }}.
  "#
}

function ExtractCurriculumFromDocument(
  document_text string,
  subject string,
  level EducationLevel
) -> ExtractedCurriculumDocument {
  client LiteLLM
  prompt #"
    You are an expert curriculum analyst for Irish education.

    Extract curriculum structure from this document.

    DOCUMENT:
    Subject: {{ subject }}
    Level: {{ level }}

    {{ document_text }}

    Extract:
    1. Document metadata (title, year)
    2. All sections (strands, units, assessment criteria)
    3. All learning outcomes with:
       - Unique codes
       - Descriptions in English and Irish (if present)
       - Associated strand/unit
       - Difficulty level
       - Key skills

    Ensure learning outcome codes follow the pattern: LO-SUBJECT-LEVEL-STRAND.UNIT.NUMBER

    Return structured extraction as {{ ctx.output_format }}.
  "#
}

function IdentifyPrerequisiteChain(
  target_outcome LearningOutcome,
  available_outcomes LearningOutcome[],
  max_depth int
) -> LearningOutcome[] {
  client LiteLLM
  prompt #"
    You are an expert curriculum analyst.

    Identify the prerequisite learning chain for this outcome:

    TARGET OUTCOME:
    {{ target_outcome.code }}: {{ target_outcome.description_en }}
    Level: {{ target_outcome.level }}, Difficulty: {{ target_outcome.difficulty }}

    AVAILABLE OUTCOMES (potential prerequisites):
    {{ for outcome in available_outcomes }}
    - {{ outcome.code }}: {{ outcome.description_en }} ({{ outcome.level }}, {{ outcome.difficulty }})
    {{ endfor }}

    Return an ordered list of prerequisite outcomes, from foundational to advanced.
    Maximum chain length: {{ max_depth }}

    Consider:
    - Conceptual dependencies (what must be understood first)
    - Skill progression (simpler skills before complex)
    - Curriculum sequencing (earlier levels before later)

    Return as {{ ctx.output_format }}.
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

function ExtractExamPaperStructure(
  document_text string,
  subject string,
  year int,
  level ExamLevel,
  paper_number int
) -> ExamPaper {
  client LiteLLM
  prompt #"
    You are an expert at analyzing Irish State Examination papers.

    Extract the complete structure of this examination paper.

    PAPER DETAILS:
    Subject: {{ subject }}
    Year: {{ year }}
    Level: {{ level }}
    Paper: {{ paper_number }}

    DOCUMENT TEXT:
    {{ document_text }}

    Extract:
    1. General instructions and duration
    2. Each section with its title and instructions
    3. All questions with:
       - Question numbers (including sub-parts)
       - Marks allocated
       - Question type (MCQ, short answer, essay, etc.)
       - Topic/strand covered
       - The actual question text
    4. Materials allowed (calculators, log tables, etc.)

    For Mathematics/Science: identify calculation vs. theory questions.
    For Languages: identify comprehension, writing, aural components.

    Return as {{ ctx.output_format }}.
  "#
}

function ExtractMarkingScheme(
  document_text string,
  subject string,
  year int,
  level ExamLevel
) -> MarkingScheme {
  client LiteLLM
  prompt #"
    You are an expert at analyzing SEC marking schemes.

    Extract the marking criteria from this document.

    MARKING SCHEME DETAILS:
    Subject: {{ subject }}
    Year: {{ year }}
    Level: {{ level }}

    DOCUMENT TEXT:
    {{ document_text }}

    Extract:
    1. General marking guidelines
    2. For each question:
       - Mark allocation breakdown
       - Acceptable answers
       - Partial credit rules
       - Examiner notes

    Be precise about mark allocations - these are used for grading.

    Return as {{ ctx.output_format }}.
  "#
}

function ExtractExaminerReportInsights(
  document_text string,
  subject string,
  year int,
  level ExamLevel
) -> ExaminerReport {
  client LiteLLM
  prompt #"
    You are an expert curriculum analyst.

    Extract insights from this Chief Examiner Report.

    REPORT DETAILS:
    Subject: {{ subject }}
    Year: {{ year }}
    Level: {{ level }}

    DOCUMENT TEXT:
    {{ document_text }}

    Extract:
    1. Overall candidate performance commentary
    2. For each question analyzed:
       - Performance summary
       - Common errors and misconceptions
       - Examples of good answers
       - Teaching recommendations
    3. Statistical information if present
    4. General recommendations for teachers and students

    Focus on actionable insights for curriculum improvement.

    Return as {{ ctx.output_format }}.
  "#
}

function ExtractCurriculumSpecification(
  document_text string,
  subject string,
  cycle EducationLevel,
  language string
) -> CurriculumSpecification {
  client LiteLLM
  prompt #"
    You are an expert Irish curriculum analyst.

    Extract the complete curriculum specification structure.

    SPECIFICATION DETAILS:
    Subject: {{ subject }}
    Cycle: {{ cycle }}
    Language: {{ language }}

    DOCUMENT TEXT:
    {{ document_text }}

    Extract:
    1. Document metadata (title, version year, type)
    2. Rationale and aims
    3. All strands with:
       - Names (English and Irish)
       - Descriptions
       - Learning outcomes within each strand
    4. For each learning outcome:
       - Unique code (generate if not present: LO-SUBJECT-CYCLE-STRAND.NUMBER)
       - Full text in both languages if available
       - Action verbs used
       - Cross-curricular links
       - Key skills developed
    5. Assessment information:
       - Components and weightings
       - Levels offered
       - Grading approach
    6. Key skills mapping

    Ensure learning outcomes are comprehensive and correctly categorized.

    Return as {{ ctx.output_format }}.
  "#
}

function MapOutcomesToExamQuestions(
  specification CurriculumSpecification,
  exam_papers ExamPaper[]
) -> map<string, string[]> {
  client LiteLLM
  prompt #"
    You are an expert curriculum analyst.

    Map learning outcomes to examination questions.

    CURRICULUM SPECIFICATION:
    Subject: {{ specification.subject }}
    Cycle: {{ specification.cycle }}

    LEARNING OUTCOMES:
    {{ for outcome in specification.learning_outcomes }}
    - {{ outcome.outcome_code }}: {{ outcome.text }}
    {{ endfor }}

    EXAM PAPERS:
    {{ for paper in exam_papers }}
    Paper {{ paper.paper_number }} ({{ paper.year }}, {{ paper.level }}):
    {{ for section in paper.sections }}
      {{ for q in section.questions }}
      - Q{{ q.question_number }}: {{ q.text }}
      {{ endfor }}
    {{ endfor }}
    {{ endfor }}

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
  language string?       @description(\"en\" or \"ga\")
  url string             @description("The exact URL to the PDF")
}

function ExtractAllPdfMetadata(
  page_markdown: string,
  pdf_urls: string[]
) -> DocumentMetadata[] {
  client LiteLLM
  prompt #"
    You are an expert curriculum analyst specializing in Irish education.

    Analyze the markdown context surrounding these PDF links to extract metadata.

    PDF URLS TO ANALYZE:
    {{ for url in pdf_urls }}
    - {{ url }}
    {{ endfor }}

    PAGE MARKDOWN:
    {{ page_markdown }}

    Extract the following metadata for EACH PDF URL:
    1. The exact URL matching one of the URLs provided.
    2. A clear, descriptive title based on the link text or preceding heading.
    3. The most appropriate category (Specification, Syllabus, Meeting Minutes, etc.).
    4. The subject slug (e.g., "mathematics", "english", "history").
    5. The education cycle (JUNIOR_CYCLE, SENIOR_CYCLE, etc.).
    6. The year it becomes effective (if mentioned, e.g., "no earlier than September 2027" -> 2027).
    7. The year it is examined (if mentioned, e.g., "examination to 2028" -> 2028).
    8. The language ("en" for English, "ga" for Irish). Use context clues.

    Return the structured extraction as {{ ctx.output_format }}.
  "#
}
