// BAML schema: UK NCCE Cross-Jurisdiction Equivalencies
//
// Per the 2026-09-01-cianfhoghlaim-nua-biep-ncce-showcase-v1 change
// (Phase 4 of the cianfhoghlaim-nua v6 era plan). Lifted + OSS-ified
// from ~/dev/gemini_hackathon/baml_extracts/extract_equivalency.baml
//
// The 48 cell-level cross-jurisdiction equivalencies that map NCCE
// learning-graph cells to their equivalents in Ireland (NCCA LC +
// JC), England (AQA GCSE + A-Level), Scotland (SQA), Wales (WJEC),
// Northern Ireland (CCEA), Jersey, Guernsey, Isle of Man.
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate --from baml_src

// ============================================================================
// Canonical enums
// ============================================================================

enum EquivalencyJurisdiction {
  UK_NCCE     @description("United Kingdom NCCE")
  IE_NCCA_LC  @description("Ireland NCCA Leaving Certificate")
  IE_NCCA_JC  @description("Ireland NCCA Junior Cycle")
  EN_AQA_GCSE @description("England AQA GCSE")
  EN_AQA_AL   @description("England AQA A-Level")
  SC_SQA_NQ   @description("Scotland SQA National Qualifications")
  WL_WJEC     @description("Wales WJEC")
  NI_CCEA     @description("Northern Ireland CCEA")
  JE_GSSE     @description("Jersey")
  GG_GSEG     @description("Guernsey")
  IM_GSMI     @description("Isle of Man")
}

// ============================================================================
// Output classes
// ============================================================================

class EquivalencyCell {
  source_jurisdiction EquivalencyJurisdiction
  source_lo_code string @description("The source cell's LO code (e.g. 'UK-NCCE-CS-Y8-3.2')")
  source_outcome_text string @description("The source cell's outcome text")
  source_year_level string? @description("e.g. 'Y8', 'LC_OL', 'GCSE'")
  source_subject string @description("e.g. 'computer_science', 'mathematics'")
}

class CrossJurisdictionEquivalency {
  source_cell EquivalencyCell
  target_cells EquivalencyCell[] @description("All equivalent cells across other jurisdictions")
  rationale string @description("Why these cells are equivalent")
  confidence float @description("0.0-1.0")
  bidirectional bool @description("True if the equivalency holds in both directions")
}

class EquivalencyGraph {
  equivalencies CrossJurisdictionEquivalency[]
  total_cells int
  total_jurisdictions int
  generated_at string @description("ISO-8601 timestamp")
}

// ============================================================================
// Function
// ============================================================================

function ExtractCrossJurisdictionEquivalencies(
  ncce_learning_graph_json: string,
  jurisdiction_text_map: string,
  equivalency_table_csv: string
) -> EquivalencyGraph {
  client Primary
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting cross-jurisdiction cell-level
    equivalencies from NCCE learning graphs and the canonical
    equivalency table. For each NCCE cell, identify the equivalent
    cell (or cells) in every other jurisdiction (Ireland NCCA LC + JC,
    England AQA GCSE + A-Level, Scotland SQA, Wales WJEC, Northern
    Ireland CCEA, Jersey, Guernsey, Isle of Man).

    NCCE learning graph JSON: {{ ncce_learning_graph_json }}

    Jurisdiction text map: {{ jurisdiction_text_map }}

    Equivalency table CSV: {{ equivalency_table_csv }}

    {{ ctx.output_format }}
  "#
}

// ============================================================================
// BAML test block
// ============================================================================

test equivalencies_sanity {
  functions [ExtractCrossJurisdictionEquivalencies]
  args {
    ncce_learning_graph_json "{}"
    jurisdiction_text_map "{}"
    equivalency_table_csv "src_lo,target_lo\\nUK-NCCE-CS-Y8-3.2,LC-COMP-LO-3.2"
  }
}