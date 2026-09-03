// =============================================================================
// BAML context: senior_cycle.baml
// Stage-specific system prompt + BAML client defaults for the Senior Cycle
// (Leaving Certificate) extraction pipeline.
// =============================================================================

function ExtractSeniorCycleSpecFromUrl(
  source_url: string,
  subject: LeavingCertSubject
) -> SubjectRubric {  client ExtractEn
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

function ScoreEssayAgainstRubricStdLib(
  essay: string,
  subject: LeavingCertSubject
) -> RubricScore {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}
