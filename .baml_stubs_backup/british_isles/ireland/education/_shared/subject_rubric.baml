// =============================================================================
// Subject Rubric Functions (split from curriculum_extraction.baml)
// Rubric generation + scoring + comparison functions for Leaving Certificate subjects.
// =============================================================================

function ExtractSubjectRubric(text: string,
  subject: string,
  level: ExamLevel,
  exam_years: int[]) -> SubjectRubric {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}


function ScoreEssayAgainstRubric(essay: string,
  subject: string,
  level: ExamLevel,
  rubric_text: string) -> RubricScore {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}


function CompareMarkingSchemes(year_a: int,
  year_b: int,
  scheme_a: string,
  scheme_b: string,
  subject: string) -> MarkingSchemeDiff {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}


function LazyExtractExamPaper(text: string,
  subject: string,
  year: int,
  level: ExamLevel) -> ExamPaper {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}