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
  prompt #"You are an expert curriculum analyst specializing in Irish education.

Analyze relationships between learning outcomes in {{ subject_context }}.

SOURCE LEARNING OUTCOME:
- Code: {{ source_outcome.code }}
- Description (EN): {{ source_outcome.description_en }}
{% if source_outcome.description_ga %}- Description (GA): {{ source_outcome.description_ga }}{% endif %}
- Subject: {{ source_outcome.subject }}
- Level: {{ source_outcome.level }}
- Difficulty: {{ source_outcome.difficulty }}
{% if source_outcome.strand %}- Strand: {{ source_outcome.strand }}{% endif %}
{% if source_outcome.strand_unit %}- Unit: {{ source_outcome.strand_unit }}{% endif %}
- Key Skills: {{ source_outcome.key_skills }}

POTENTIAL TARGET OUTCOMES:
{% for target in target_outcomes %}
- {{ target.code }}: {{ target.description_en }}
  Level: {{ target.level }}, Difficulty: {{ target.difficulty }}
{% endfor %}

For each meaningful relationship found, identify:
- Edge type (PREREQUISITE_FOR, BUILDS_ON, ASSESSES, RELATED_TO, PART_OF, ENABLES, CONTRASTS_WITH)
- Confidence score (0.0-1.0)
- Brief rationale (1-2 sentences citing the source outcome's code)
- Any Irish-language curriculum terminology (use bilingual labels)

The relationships should form a directed graph that captures prerequisite chains, skill dependencies, and conceptual connections across the Irish curriculum. Cite specific learning outcome codes in rationales.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    SOURCE: {{ source_outcome.code }}
    CONTEXT: {{ subject_context }}
"#
}


function ExtractSkillsFromOutcome(outcome: LearningOutcome,
  curriculum_context: string) -> SkillExtractionResult {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"You are an expert Irish education curriculum analyst.

Extract the key skills, competencies, and learning dimensions embedded in a single learning outcome from the Irish curriculum.

CURRICULUM CONTEXT:
{{ curriculum_context }}

LEARNING OUTCOME:
- Code: {{ outcome.code }}
- Description (EN): {{ outcome.description_en }}
{% if outcome.description_ga %}- Description (GA): {{ outcome.description_ga }}{% endif %}
- Subject: {{ outcome.subject }}
- Level: {{ outcome.level }}

For each skill extracted, identify:
- The skill name (use canonical Irish education terminology)
- The skill category (Cognitive, Creative, Communication, Physical, Personal, Social, Numeracy, Literacy, Digital)
- A proficiency level indicator
- Specific evidence from the outcome description that demonstrates this skill

Use bilingual labels (English and Irish) for skill names where the Irish curriculum has a specific term.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    OUTCOME: {{ outcome.code }}
    CONTEXT: {{ curriculum_context }}
"#
}


function ExtractCurriculumFromDocument(document_text: string,
  subject: string,
  level: EducationLevel) -> ExtractedCurriculumDocument {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"You are an expert curriculum document parser specializing in the Irish education system.

Parse a curriculum specification document and extract its complete structure.

SUBJECT: {{ subject }}
LEVEL: {{ level }}

DOCUMENT TEXT:
{{ document_text }}

Extract:
1. Document metadata (title, year, cycle, language, URL, document_type)
2. Aims and objectives (with both English and Irish versions where available)
3. Strands with their codes, titles (EN/GA), and descriptions
4. Strand units within each strand
5. Learning outcomes grouped by strand, with full bilingual text
6. Key skills, cross-curricular themes, and assessment approaches mentioned
7. Any explicit references to related NCCA publications

For bilingual content, extract both English (description_en) and Irish (description_ga) variants. If Irish is not present, leave description_ga as null.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    SUBJECT: {{ subject }}
    LEVEL: {{ level }}
"#
}


function IdentifyPrerequisiteChain(target_outcome: LearningOutcome,
  available_outcomes: LearningOutcome[],
  max_depth: int) -> LearningOutcome[] {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"You are an expert at identifying prerequisite learning outcome chains in the Irish education curriculum.

TARGET OUTCOME:
- Code: {{ target_outcome.code }}
- Description: {{ target_outcome.description_en }}
- Level: {{ target_outcome.level }}, Subject: {{ target_outcome.subject }}

AVAILABLE OUTCOMES (the full corpus you can choose from):
{% for available in available_outcomes %}
- {{ available.code }}: {{ available.description_en }} (Level: {{ available.level }})
{% endfor %}

Identify the prerequisite chain (up to {{ max_depth }} levels deep) by selecting the outcomes that a student must master BEFORE attempting the target outcome.

Prerequisites should:
- Be at a LOWER difficulty level or earlier in the learning progression
- Be from the same subject or directly cross-curricular foundation subjects
- Be necessary (not merely helpful) for understanding the target
- Be ordered from most fundamental to most advanced

Return the chain in dependency order (foundational first).

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    TARGET: {{ target_outcome.code }}
    DEPTH: {{ max_depth }}
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

class OutcomeQuestionMapping {
  learning_outcome_code string @description("Curriculum learning outcome code (e.g., 'ML-3.1')")
  learning_outcome_description string? @description("Description of the LO for context")
  primary_questions string[] @description("Question numbers that primarily assess this LO")
  secondary_questions string[] @description("Question numbers that partially cover this LO")
  confidence_score float @description("Strength of the mapping (0.0-1.0)")
  rationale string? @description("Why this question maps to this LO")
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
  prompt #"You are an expert at parsing Irish Leaving Certificate and Junior Cycle examination papers.

Parse a SEC exam paper and extract its complete question structure.

SUBJECT: {{ subject }}
YEAR: {{ year }}
LEVEL: {{ level }}
PAPER NUMBER: {{ paper_number }}

EXAM PAPER TEXT:
{{ document_text }}

Extract:
1. Paper metadata (total marks, duration in minutes, structure type)
2. Section structure (Section A, Section B, etc. with their mark allocations)
3. Each question with:
   - Question number and full text
   - Question type (multiple_choice, short_answer, long_answer, essay, calculation)
   - Mark allocation
   - Topic reference (which strand/learning outcome)
   - Required skills (cite specific syllabus codes)
4. Optional questions or compulsory elements
5. Section-level instructions or constraints

Note: Higher level papers often have more advanced questions; Ordinary level focuses on core competencies; Foundation level (Mathematics, Irish) has simplified structure.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    SUBJECT: {{ subject }}
    YEAR: {{ year }}
"#
}


function ExtractMarkingScheme(document_text: string,
  subject: string,
  year: int,
  level: ExamLevel) -> MarkingScheme {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"You are an expert at parsing Irish State Examination Commission (SEC) marking schemes.

Parse a SEC marking scheme document and extract its complete grading structure.

SUBJECT: {{ subject }}
YEAR: {{ year }}
LEVEL: {{ level }}

MARKING SCHEME TEXT:
{{ document_text }}

Extract:
1. Scheme metadata (total marks, grade boundaries, special instructions)
2. Question-by-question marking allocation:
   - Question number
   - Required answer content (key terms, concepts, equations)
   - Mark allocation per answer element (partial credit breakdown)
   - Specific marking notes (e.g., "accept equivalent wording", "penalise 1 mark for unit error")
3. Common errors and misconceptions to penalise
4. Grade descriptors (the descriptor that defines each grade level for the subject)
5. Any cross-reference to the syllabus learning outcomes being assessed

The marking scheme is the AUTHORITATIVE source for grading. Be exact and preserve all marking notes verbatim where they affect scoring.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    SUBJECT: {{ subject }}
    YEAR: {{ year }}
"#
}


function ExtractExaminerReportInsights(document_text: string,
  subject: string,
  year: int,
  level: ExamLevel) -> ExaminerReport {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"You are an expert at analyzing Irish State Examination Commission (SEC) Chief Examiner reports.

Parse a Chief Examiner's report and extract pedagogical insights about student performance.

SUBJECT: {{ subject }}
YEAR: {{ year }}
LEVEL: {{ level }}

EXAMINER REPORT TEXT:
{{ document_text }}

Extract:
1. Report metadata (chief examiner name, total candidates, grade distribution)
2. Overall performance commentary
3. Per-question performance analysis:
   - Question number
   - Performance summary (excellent, good, fair, poor)
   - Common errors observed
   - Topics students found most difficult
4. Pedagogical recommendations for teachers
5. Trends across the candidate cohort

Focus on actionable insights that can guide teaching practice and help students avoid common mistakes in future examinations.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    SUBJECT: {{ subject }}
    YEAR: {{ year }}
"#
}


function ExtractCurriculumSpecification(document_text: string,
  subject: string,
  cycle: EducationLevel,
  language: string) -> CurriculumSpecification {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"You are an expert at parsing Irish NCCA Curriculum Specifications for both Junior Cycle and Senior Cycle.

Parse a complete NCCA curriculum specification document.

SUBJECT: {{ subject }}
CYCLE: {{ cycle }}
LANGUAGE: {{ language }}

DOCUMENT TEXT:
{{ document_text }}

Extract:
1. Document metadata (title_en, title_ga, year, specification version, language, URL, NCCA publication reference)
2. Aims and rationale (bilingual where available)
3. Strands with codes, titles (EN/GA), and descriptions
4. Strand units within each strand
5. Learning outcomes (each with code, bilingual descriptions)
6. Key skills framework mapping
7. Assessment arrangements (examination and classroom-based)
8. Differentiation and inclusion guidance
9. Cross-curricular links

This is the canonical NCCA specification for a subject — extract everything that would help a teacher, student, or parent understand the curriculum intent and structure.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    SUBJECT: {{ subject }}
    CYCLE: {{ cycle }}
"#
}


function MapOutcomesToExamQuestions(specification: CurriculumSpecification,
  exam_papers: ExamPaper[]) -> OutcomeQuestionMapping[] {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"You are an expert at mapping NCCA curriculum specification learning outcomes to SEC exam paper questions.

Build a mapping between the learning outcomes in a curriculum specification and the questions that assess them in past exam papers.

CURRICULUM SPECIFICATION:
- Subject: {{ specification.subject }}
- Year: {{ specification.year }}
- {{ specification.learning_outcomes|length }} learning outcomes total

EXAM PAPERS PROVIDED:
{% for paper in exam_papers %}
- {{ paper.subject }} {{ paper.year }} Paper {{ paper.paper_number }} ({{ paper.level }})
{% endfor %}

For each exam question, identify the learning outcome(s) it primarily assesses and any secondary outcomes it partially covers.

The mapping should be bidirectional (outcome -> question AND question -> outcome) to enable both:
- Teachers: "Which questions cover outcome X?"
- Students: "What outcomes does question Q test?"

Be precise about the strength of the mapping (primary vs secondary assessment).

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    SUBJECT: {{ specification.subject }}
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

function ExtractAllPdfMetadata(page_markdown: string,
  pdf_urls: string[]) -> DocumentMetadata[] {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"You are an expert at extracting metadata from Irish education PDF documents.

Parse metadata for a batch of PDFs from their pre-extracted text content.

PDF URLS: {{ pdf_urls|join(", ") }}

PAGES MARKDOWN:
{{ page_markdown }}

For each PDF, extract:
1. Document type (curriculum_specification, exam_paper, marking_scheme, examiner_report, annual_report, policy_document)
2. Title (English and Irish if available)
3. Author/publisher (NCCA, SEC, Department of Education, etc.)
4. Year of publication
5. Subject (if applicable, use the canonical subject slug)
6. Educational cycle/level (early_childhood, primary, junior_cycle, senior_cycle, tertiary)
7. Language (en, ga, bilingual)
8. Year of examination (if exam material)
9. URL of the source PDF
10. Brief description of content

Group results by document type for downstream routing. This metadata enables efficient caching and topic-graph construction in the knowledge graph.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    BATCH: {{ pdf_urls|length }} URLs
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
  subject: string,
  level: ExamLevel,
  exam_years: int[]) -> SubjectRubric {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"You are an expert at synthesizing assessment rubrics for Irish Leaving Certificate subjects.

Given a subject specification and recent exam years, build a comprehensive scoring rubric that captures both the official marking scheme patterns and trends observed across multiple exam years.

SUBJECT: {{ subject }}
LEVEL: {{ level }}
EXAM YEARS: {{ exam_years|join(", ") }}

SOURCE TEXT:
{{ text }}

Extract:
1. Rubric style (e.g., "analytic", "holistic", "trait-based", "level-based", "mixed")
2. Common assessment criteria with bilingual labels (e.g., "Knowledge & Understanding" / "Eolas agus Tuiscint")
3. Performance levels with descriptors (4-6 levels typically: Exceptional, Above Expectations, In Line With, Yet to Meet Expectations)
4. Mark allocation per criterion
5. Common deductions/pénalisations (unit errors, arithmetic slips, off-by-one)
6. Bilingual terminology (canonical Irish-language assessment terms)

The rubric should be reusable across exam years and help teachers apply consistent grading.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    SUBJECT: {{ subject }}
    LEVEL: {{ level }}
"#
}


function ScoreEssayAgainstRubric(essay: string,
  subject: string,
  level: ExamLevel,
  rubric_text: string) -> RubricScore {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"You are an expert at applying an assessment rubric to score an Irish Leaving Certificate student essay.

Apply the rubric rigorously and provide detailed feedback.

SUBJECT: {{ subject }}
LEVEL: {{ level }}

RUBRIC:
{{ rubric_text }}

STUDENT ESSAY:
{{ essay }}

Score the essay on each rubric criterion, providing:
1. Per-criterion score (numeric, with maximum)
2. Per-criterion feedback explaining the score (cite specific parts of the essay)
3. Strengths demonstrated
4. Areas for improvement
5. Overall score (sum of criteria scores)
6. Suggested grade band (e.g., H1, H2, O1, O2 for Leaving Cert)
7. Bilingual feedback labels where appropriate (use both English and Irish)

Be fair, consistent, and pedagogically constructive. Reference the rubric criteria explicitly in your justification.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    SUBJECT: {{ subject }}
    LEVEL: {{ level }}
"#
}


function CompareMarkingSchemes(year_a: int,
  year_b: int,
  scheme_a: string,
  scheme_b: string,
  subject: string) -> MarkingSchemeDiff {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"You are an expert at comparing State Examination Commission (SEC) marking schemes across years to identify patterns, trends, and shifts in assessment emphasis.

SUBJECT: {{ subject }}
YEAR A: {{ year_a }}
YEAR B: {{ year_b }}

MARKING SCHEME A ({{ year_a }}):
{{ scheme_a }}

MARKING SCHEME B ({{ year_b }}):
{{ scheme_b }}

Compare the two schemes and identify:
1. Question structure changes (added/removed/merged questions)
2. Mark allocation shifts (which questions got more/fewer marks)
3. Topic emphasis changes (which strands got more coverage)
4. Difficulty progression (easier/harder than prior year)
5. New question types introduced
6. Removed question types
7. Overall assessment philosophy shift (e.g., "more focus on application vs recall")
8. Predicted implications for future years (e.g., "this pattern suggests X")

This comparison helps teachers identify assessment trends and predict future exam patterns.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    SUBJECT: {{ subject }}
    YEARS: {{ year_a }} vs {{ year_b }}
"#
}


function LazyExtractExamPaper(text: string,
  subject: string,
  year: int,
  level: ExamLevel) -> ExamPaper {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"You are an expert at lazy/on-demand extraction of exam paper data for the Cianfhoghlaim Oideachais platform.

This is a cost-optimized extraction function used when a user requests specific exam paper data. The function only extracts what is needed to answer the user's request, not the full exam paper structure.

SUBJECT: {{ subject }}
YEAR: {{ year }}
LEVEL: {{ level }}

EXAM PAPER TEXT:
{{ text }}

For lazy extraction, focus on the highest-value structured data:
1. Paper metadata (total marks, duration, structure type)
2. Question summary (count by type, total marks per section)
3. Topic distribution (which strands/learning outcomes are most heavily tested)
4. Difficulty profile (estimated proportion of Easy/Medium/Hard questions)
5. Notable patterns (e.g., "calculations cluster in Section B", "essay is 30% of total marks")

This is a SPARSE extraction — return only the structured metadata needed to populate UI components, not the full question text.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    SUBJECT: {{ subject }}
    YEAR: {{ year }}
"#
}


