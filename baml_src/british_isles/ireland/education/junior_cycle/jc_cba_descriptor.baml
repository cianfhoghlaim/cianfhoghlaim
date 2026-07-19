// BAML schema: NCCA JC CBA (Classroom-Based Assessment) Descriptor Extraction
//
// Used by the BIEP v2 JC pipeline to extract structured CBA descriptors
// from NCCA + examinations.ie CBA PDF sheets. Each JC subject has 2 CBAs
// (one for Year 2, one for Year 3) — 18 subjects × 2 CBAs = 36 total.
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate
//
// Reference: openspec/changes/2026-07-20-biep-v2-junior-cycle-extraction-v1/

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
) -> CBATask {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
