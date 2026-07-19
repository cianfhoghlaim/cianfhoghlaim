// =============================================================================
// BAML context: senior_cycle.baml
// Stage-specific system prompt + BAML client defaults for the Senior Cycle
// (Leaving Certificate) extraction pipeline.
// =============================================================================

function ExtractSeniorCycleSpecFromUrl(
  source_url: string,
  subject: LeavingCertSubject
) -> SubjectRubric {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

function ScoreEssayAgainstRubricStdLib(
  essay: string,
  subject: LeavingCertSubject
) -> RubricScore {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
