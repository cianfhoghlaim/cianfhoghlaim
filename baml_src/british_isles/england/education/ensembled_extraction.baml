// BAML schema: England Ensemble Consensus Extraction (BIEP v2)
//
// The input contract for Change 3's 4-path OCR/VLM ensemble pipeline.
// Accepts the outputs from:
//   - Path 1 (BAML): b.Extract<Board>QualSpec
//   - Path 2 (Unstract): the per-board Unstract workflow JSON
//   - Path 3 (qwen3-vl-8b): the qwen3-vl-8b raw response
//   - Path 4 (gemma-4-26B-A4B): the gemma-4 raw response
//
// Returns the RAGAS-voted canonical output. The 4 path outputs are also
// returned so the marimo audit notebook (Change 4) can show side-by-side
// provenance.
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate
//
// Reference: openspec/changes/2026-07-21-biep-v2-england-aqa-ocr-baml-pipeline-v1/

class EnsemblePathOutput {
  path string                @description("One of: 'baml', 'unstract', 'qwen3_vl', 'gemma4'")
  raw_response string        @description("The raw output from this path")
  confidence_score float     @description("The path's self-reported confidence (0-1)")
  schema_valid bool          @description("Whether the output validates as the board-specific qual spec")
  ragas_faithfulness float?
  ragas_answer_relevance float?
  ragas_context_precision float?
}

class EnsembleConsensus {
  // The 4 path outputs (input to RAGAS vote)
  paths EnsemblePathOutput[]

  // RAGAS vote metadata
  ragas_voted_path string       @description("The path that won the RAGAS vote")
  ragas_score float             @description("The winner's RAGAS score (0-1)")

  // Final consensus output
  voted_output string           @description("JSON-serialised AQAQualSpec / OCRQualSpec / EdexcelQualSpec")
  voted_canonical_id string     @description("(subject, board, qualification_level, version, specification_code) tuple"

  // Provenance trail
  baml_canonical_id string?
  unstract_canonical_id string?
  qwen3_vl_canonical_id string?
  gemma4_canonical_id string?

  // Cross-references
  source_pdf string
  ingested_at string
  board string?
  qualification_level string?
  subject string?

  doc_confidence float?
}

function ExtractEnglandEnsembleConsensus(
  pdf_text: string,
  baml_output: string?,
  unstract_json: string?,
  qwen3_vl_response: string?,
  gemma4_response: string?,
  subject: string?,
) -> EnsembleConsensus {
  client ExtractEnStrong
  prompt #"
    You are the England BIEP v2 ensemble coordinator. Given the outputs
    from the 4 OCR/VLM paths, run the canonical RAGAS vote + return the
    per-path provenance.

    Subject: { subject }

    Path 1 (BAML): { baml_output }
    Path 2 (Unstract): { unstract_json }
    Path 3 (qwen3-vl-8b): { qwen3_vl_response }
    Path 4 (gemma-4-26B-A4B): { gemma4_response }

    {{ ctx.output_format }}
  "#
}
