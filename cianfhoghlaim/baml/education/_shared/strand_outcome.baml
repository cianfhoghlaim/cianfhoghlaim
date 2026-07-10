// =============================================================================
// Strand & Outcome Classes (split from curriculum_extraction.baml)
// Cross-stage curriculum data classes shared across all NCCA stages.
// =============================================================================

// -----------------------------------------------------------------------------
// Learning Outcome Types
// -----------------------------------------------------------------------------

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

// -----------------------------------------------------------------------------
// Skill Extraction
// -----------------------------------------------------------------------------

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

// -----------------------------------------------------------------------------
// Curriculum Document Extraction
// -----------------------------------------------------------------------------

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

// -----------------------------------------------------------------------------
// Enhanced Curriculum Specification Types
// -----------------------------------------------------------------------------

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

class AssessmentComponentStrand {
  name string @description("Component name (Written Exam, Coursework, Oral)")
  weighting int @description("Percentage weighting")
  duration string? @description("Duration if timed (e.g., '2h 30min')")
  description string? @description("Component description")
  levels string[] @description("Levels offered (Foundation, Ordinary, Higher)")
}

class AssessmentInfo {
  components AssessmentComponentStrand[] @description("Assessment components")
  total_marks int? @description("Total marks available")
  coursework_percentage int? @description("Percentage for coursework")
  external_percentage int? @description("Percentage for external exam")
  grading_scheme string? @description("Grading approach")
}

class CurriculumSpecStrand {
  document_id string @description("Unique document identifier")
  title string @description("Full document title") @stream.not_null
  title_ga string? @description("Irish title")
  subject string @description("Subject code")
  cycle EducationLevel @description("Education cycle")
  language string @description("Document language (en/ga)")
  version_year int @description("Specification version year")
  specification_type string @description("syllabus or specification")
  development_status string @description("current, redevelopment, etc.")
  strands CurriculumStrand[] @description("Curriculum strands") @stream.with_state
  learning_outcomes EnhancedLearningOutcome[] @description("All learning outcomes") @stream.with_state
  assessment_info AssessmentInfo? @description("Assessment information")
  key_skills_mapping map<string, string[]> @description("Key skills to outcomes mapping")
  rationale string? @description("Subject rationale/aims")
  total_hours int? @description("Recommended teaching hours")
}

// -----------------------------------------------------------------------------
// Examination Paper Types
// -----------------------------------------------------------------------------

class ExamQuestionStrand {
  question_number string @description("Question number (e.g., '1', '2a', '3bii')")
  marks int @description("Marks allocated")
  question_type QuestionType @description("Type of question")
  topic string? @description("Topic or strand covered")
  difficulty_estimate DifficultyLevel? @description("Estimated difficulty")
  text string @description("Question text")
  sub_questions ExamQuestionStrand[] @description("Sub-parts if any")
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

class ExamSectionStrand {
  section_name string @description("Section identifier (A, B, C or name)")
  title string? @description("Section title")
  instructions string? @description("Section-specific instructions")
  total_marks int @description("Total marks for section")
  questions ExamQuestionStrand[] @description("Questions in this section")
  choice_instructions string? @description("e.g., 'Answer 3 of 5'")
}

class ExamPaperStrand {
  subject string @description("Subject code")
  year int @description("Examination year")
  level ExamLevel @description("Exam level")
  paper_number int @description("Paper 1, Paper 2, etc.")
  language string @description("Paper language (en/ga)")
  duration string @description("Exam duration")
  total_marks int @description("Total marks available")
  sections ExamSectionStrand[] @description("Paper sections")
  general_instructions string? @description("General exam instructions")
  materials_allowed string[] @description("Permitted materials (calculator, etc.)")
  pdf_url string? @description("Source PDF URL")
}

// -----------------------------------------------------------------------------
// Marking Scheme Types
// -----------------------------------------------------------------------------

class MarkingSchemeStrand {
  subject string @description("Subject code") @stream.not_null
  year int @description("Examination year")
  level ExamLevel @description("Exam level")
  paper_number int @description("Paper number")
  language string @description("Scheme language")
  sections MarkingSection[] @description("Marking sections") @stream.with_state
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

// -----------------------------------------------------------------------------
// Examiner Report Types
// -----------------------------------------------------------------------------

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

// -----------------------------------------------------------------------------
// Rubric Types (Subject Rubric)
// -----------------------------------------------------------------------------

class RubricDescriptor {
  level string  @description("Achievement level")
  text_en string @description("The full descriptive paragraph in English")
  text_ga string? @description("Irish translation")
  key_qualities string[] @description("Extracted phrases indicating quality")
  negative_indicators string[] @description("Phrases indicating what is missing")
}

class SpecialismRubric {
  specialism Specialism
  rubric_style RubricStyle
  descriptors RubricDescriptor[] @description("Per-level rubric descriptors")
  weight_per_descriptor_pct float?
}

class ExamAssessmentComponent {
  type AssessmentComponentType
  weight_pct int
  duration_minutes int?
  language string
  levels ExamLevel[]
}

class SubjectRubric {
  subject LeavingCertSubject
  style RubricStyle
  descriptors RubricDescriptor[]
  source_url string @description("Link to NCCA spec or SEC examiner report")
  document_year int
}

class RubricScore {
  subject LeavingCertSubject
  total_score float @description("0-100")
  descriptor_scores map<string, float> @description("descriptor text → score 0-100")
  strengths string[]
  improvements string[]
  reviewer_notes_en string
  reviewer_notes_ga string?
}

class MarkingSchemeDiff {
  subject LeavingCertSubject
  year_a int
  year_b int
  added_questions string[] @description("Question IDs only in year_b")
  removed_questions string[] @description("Question IDs only in year_a")
  changed_marks map<string, int> @description("Question ID → year_b marks - year_a marks")
  topic_drift_en string @description("Plain English summary of the drift")
  topic_drift_ga string?
}

class ExtractionBudget {
  session_id string
  papers_extracted int @description("Number of papers extracted in this session")
  tokens_consumed int
  last_extraction_at string
  reset_at string @description("ISO 8601 timestamp when the budget resets")
  remaining_papers int @description("5 - papers_extracted, default daily budget")
}