// BAML schema: NCCA JC CBA (Classroom-Based Assessment) Descriptor Extraction
//
// Used by the BIEP v2 JC pipeline to extract structured CBA descriptors
// from NCCA + examinations.ie CBA PDF sheets. Each JC subject has 2 CBAs
// (one for Year 2, one for Year 3) — 18 subjects × 2 CBAs = 36 total.
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate
//
// Reference: openspec/changes/2026-07-20-biep-v2-junior-cycle-extraction-v1/

class CBATask {
  // Subject + CBA identifiers
  subject string            @description("Subject slug (e.g. 'english', 'mathematics')")
  cba_id string             @description("e.g. 'english_cba_1' (subject_scoped)")
  subject_code string?      @description("NCCA subject code, e.g. 'JC001EN'")

  // Metadata
  title_en string
  title_ga string?
  descriptor_en string
  descriptor_ga string?
  year YearBand
  weighting int             @description("Marks assigned to the CBA")

  // Evidence of learning + assessment criteria
  evidence_of_learning string[]  @description("Bullet list of EOL criteria")
  success_criteria string[]      @description("Bullet list of success criteria")
  exemplar_responses string[]    @description("Sample student work examples")

  // Heuristic metrics
  duration_minutes int?
  has_oral_component bool
  has_written_component bool
  has_practical_component bool

  // Cross-cutting
  source_pdf string
  source_pages int
  specification_code string?
}

enum YearBand {
  YEAR_1
  YEAR_2
  YEAR_3
  TY
}

// ============================================================================
// BAML function — the canonical CBA extractor (BIEP v2)
// ============================================================================
// Replaces the legacy `b.ExtractCBADescriptor` from
// `baml/education/stages/junior_cycle.baml` (which returned a thin stub).
//
// Returns the canonical `CBATask` Pydantic class with per-CBA
// `evidence_of_learning[]` + `success_criteria[]` + `exemplar_responses[]`.

function ExtractCBADescriptor(
  pdf_text: string,
  subject: string?,
  cba_id: string?,
) -> CBATask {
  client ExtractEn
  prompt #"
    You are an Irish Junior Cycle CBA (Classroom-Based Assessment) analyst.
    Given the text of a NCCA CBA descriptor PDF (typically a 1-4 page
    document), extract the structured CBA descriptor.

    Subject: { subject }
    CBA ID: { cba_id }

    {{ ctx.output_format }}
  "#
}
