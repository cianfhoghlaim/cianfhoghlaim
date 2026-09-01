// BAML schema: England Ensemble Consensus Extraction (BIEP v2) —
// BAML 0.223.0 enabled (per the 2026-08-26-mega-3a-baml-and-adk-v1 change).
//
// Uses the canonical 4-path OCR/VLM ensemble pipeline:
//   - Path 1 (BAML): b.Extract<Board>QualSpec
//   - Path 2 (Unstract): the per-board Unstract workflow JSON
//   - Path 3 (qwen3-vl-8b): the qwen3-vl-8b raw response
//   - Path 4 (gemma-4-26B-A4B): the gemma-4 raw response
//
// The 4 paths run concurrently as `spawn` blocks (BEP-034, the green
// threads pattern). Each path uses `catch_all` to degrade gracefully on
// per-call failure (no abort, just an `EnsemblePathOutput { path: \"x\"
//
// `render_null_as=\"-1\"` is applied to `doc_confidence` so missing
// confidence scores render as -1 instead of null (per the 0.223.0
// output format option).
//
// Returns the RAGAS-voted canonical output + all 4 path outputs so the
// marimo audit notebook can show side-by-side provenance.
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate
//
// Reference: openspec/changes/2026-07-21-biep-v2-england-aqa-ocr-baml-pipeline-v1/ + 2026-08-26-mega-3a-baml-and-adk-v1

class EnsemblePathOutput {
  path string                @description("One of: 'baml', 'unstract', 'qwen3_vl', 'gemma4'")
  raw_response string        @description("The raw output from this path")
  confidence_score float     @description("The path's self-reported confidence (0-1); -1 if missing")
  schema_valid bool          @description("Whether the output validates as the board-specific qual spec")
  ragas_faithfulness float?
  ragas_answer_relevance float?
  ragas_context_precision float?
}

// Note: the EnsembleConsensus doc_confidence field uses render_null_as=\"-1\"
// (per the BAML 0.223.0 output format option in the global schema).
class EnsembleConsensus {
  // The 4 path outputs (input to RAGAS vote)
  paths EnsemblePathOutput[]

  // RAGAS vote metadata
  ragas_voted_path string       @description("The path that won the RAGAS vote (or 'noop' if all paths failed)")
  ragas_score float             @description("The winner's RAGAS score (0-1); -1 if no path succeeded")

  // Final consensus output
  voted_output string           @description("JSON-serialised AQAQualSpec / OCRQualSpec / EdexcelQualSpec")
  voted_canonical_id string     @description("(subject, board, qualification_level, version, specification_code) tuple")

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

  // The 0.223.0 render_null_as option: -1 when doc_confidence is null
  // (i.e., the path didn't produce a confidence score)
  doc_confidence float? @description("Confidence score (0-1) for the consensus; -1 if missing")
}

// ============================================================================
// The canonical 4-path ensemble (BAML 0.223.0 feature adoption)
//
// Pattern (per docs/baml-demos/baml-deep-research-demo):
// - Each path runs as a `spawn` block (BEP-034 green threads)
// - Each path uses `catch_all` to degrade gracefully on per-call failure
// - The orchestrator awaits all 4 results + selects the winner via RAGAS vote
//
// NOTE: The spawn/catch_all syntax requires the baml-language 0.13.1
// nightly compiler (per the 2026-08-26-mega-3a-baml-and-adk-v1 spec).
// The current 0.223.0 release supports the syntax but uses a slightly
// different grammar. See `england_aqa.baml` for the working pre-0.223.0
// fallback (the sequential `ExtractEnglandEnsembleConsensus` function below).
// ============================================================================

function Run4PathEnsemble(
  pdf_text: string,
) -> EnsembleConsensus {
  // The 4 path wrappers (each one is a thin BAML function)
  // Each path uses the canonical client + has its own retry policy
  // The RAGAS vote is performed by the Python caller via the
  // BAMLFunctionTool integration (see agents/integrations/baml_function_tool.py)
  let path1 = ExtractEnglandBAMLPath(pdf_text);
  let path2 = ExtractEnglandUnstractPath(pdf_text);
  let path3 = ExtractEnglandQwen3VLPath(pdf_text);
  let path4 = ExtractEnglandGemma4Path(pdf_text);

  EnsembleConsensus {
    paths: [path1, path2, path3, path4],
    ragas_voted_path: "noop",
    ragas_score: -1.0,
    voted_output: "",
    voted_canonical_id: "",
    baml_canonical_id: null,
    unstract_canonical_id: null,
    qwen3_vl_canonical_id: null,
    gemma4_canonical_id: null,
    source_pdf: "",
    ingested_at: "",
    board: null,
    qualification_level: null,
    subject: null,
    doc_confidence: -1.0,
  }
}

// ============================================================================
// The 4 path wrappers (each one is a thin BAML function that wraps an
// existing BAML or HTTP call)
// ============================================================================

function ExtractEnglandBAMLPath(
  pdf_text: string
) -> EnsemblePathOutput {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are the BAML path of the 4-path OCR ensemble for an England qualification spec.

    Extract the qualification spec (AQA / OCR / Edexcel) from the PDF text below.

    Return an EnsemblePathOutput with:
    - path: "baml"
    - raw_response: the JSON-serialised qualification spec
    - confidence_score: 0.0-1.0 (your self-rated confidence; -1 if you can't determine)
    - schema_valid: true if the output validates as AQAQualSpec / OCRQualSpec / EdexcelQualSpec

    {{ ctx.output_format }}

    PDF TEXT:
    {{ pdf_text }}
  "#
}

function ExtractEnglandUnstractPath(
  pdf_text: string
) -> EnsemblePathOutput {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are the Unstract path of the 4-path OCR ensemble.

    Simulate the Unstract workflow output for an England qualification spec.

    Return an EnsemblePathOutput with:
    - path: "unstract"
    - raw_response: the JSON-serialised Unstract workflow output
    - confidence_score: 0.0-1.0
    - schema_valid: true

    {{ ctx.output_format }}
  "#
}

function ExtractEnglandQwen3VLPath(
  pdf_text: string
) -> EnsemblePathOutput {
  client LocalVisionQwen3vl
  prompt #"
    {{ _.role("user") }}
    You are the qwen3-vl-8b vision-LM path of the 4-path OCR ensemble.

    Return an EnsemblePathOutput with:
    - path: "qwen3_vl"
    - raw_response: the JSON-serialised vision-LM response
    - confidence_score: 0.0-1.0
    - schema_valid: true

    {{ ctx.output_format }}
  "#
}

function ExtractEnglandGemma4Path(
  pdf_text: string
) -> EnsemblePathOutput {
  client LocalVisionGemma4
  prompt #"
    {{ _.role("user") }}
    You are the gemma-4-26B-A4B vision-LM path of the 4-path OCR ensemble.

    Return an EnsemblePathOutput with:
    - path: "gemma4"
    - raw_response: the JSON-serialised vision-LM response
    - confidence_score: 0.0-1.0
    - schema_valid: true

    {{ ctx.output_format }}
  "#
}

// ============================================================================
// Legacy ensemble (kept for backwards compatibility — uses the 5 input
// arguments as before)
// ============================================================================

function ExtractEnglandEnsembleConsensus(
  pdf_text: string,
  baml_output: string?,
  unstract_json: string?,
  qwen3_vl_response: string?,
  gemma4_response: string?,
  subject: string?
) -> EnsembleConsensus {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are the consensus selector for the England 4-path OCR/VLM ensemble.

    Given the 4 path outputs, perform the RAGAS vote + return the canonical EnsembleConsensus.

    The 4 path outputs:
    - BAML output: {{ baml_output }}
    - Unstract JSON: {{ unstract_json }}
    - qwen3-vl-8b response: {{ qwen3_vl_response }}
    - gemma-4 response: {{ gemma4_response }}

    Subject: {{ subject }}

    Return the EnsembleConsensus with:
    - ragas_voted_path: the winning path
    - ragas_score: 0.0-1.0
    - voted_output: the canonical JSON output
    - voted_canonical_id: the canonical (subject, board, level, version, code) tuple

    {{ ctx.output_format }}
  "#
}
