// =============================================================================
// Curriculum Relationship Functions (split from curriculum_extraction.baml)
// Cross-stage relationship extraction functions for the 5-stage cognify pass.
// =============================================================================

function ExtractLearningOutcomeRelationships(
  source_outcome: LearningOutcome,
  target_outcomes: LearningOutcome[],
  subject_context: string
) -> RelationshipExtractionResult {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
  "#
}


function ExtractSkillsFromOutcome(
  outcome: LearningOutcome,
  curriculum_context: string
) -> SkillExtractionResult {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
  "#
}


function ExtractCurriculumFromDocument(
  document_text: string,
  subject: string,
  level: EducationLevel
) -> ExtractedCurriculumDocument {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
  "#
}


function IdentifyPrerequisiteChain(
  target_outcome: LearningOutcome,
  available_outcomes: LearningOutcome[],
  max_depth: int
) -> LearningOutcome[] {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
  "#
}
