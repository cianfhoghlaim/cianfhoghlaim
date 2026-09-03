// =============================================================================
// Subject Rubric Functions (split from curriculum_extraction.baml)
// Rubric generation + scoring + comparison functions for Leaving Certificate subjects.
// =============================================================================

function ExtractSubjectRubric(text: string,
  subject: string,
  level: ExamLevel,
  exam_years: int[]) -> SubjectRubric {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#

  catch_all (err) {
    SubjectRubric {}
  }
}


function ScoreEssayAgainstRubric(essay: string,
  subject: string,
  level: ExamLevel,
  rubric_text: string) -> RubricScore {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}


function CompareMarkingSchemes(year_a: int,
  year_b: int,
  scheme_a: string,
  scheme_b: string,
  subject: string) -> MarkingSchemeDiff {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}


function LazyExtractExamPaper(text: string,
  subject: string,
  year: int,
  level: ExamLevel) -> ExamPaper {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}