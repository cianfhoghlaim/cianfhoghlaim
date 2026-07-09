// =============================================================================
// BAML context: court_rules.baml
//
// Pick-8 Ireland/law quadrant — Court Rules library extraction schema.
// One BAML class + one extraction function.
//
// Source: https://www.courts.ie/rules (Rules of Court PDF library per
// jurisdiction — District Court Rules, Circuit Court Rules, Rules of
// the Superior Courts, District Court Rules of Procedure, etc.).
//
// Re-uses:
//   - CourtLevel       from `ie/law/shared_legal_enums.baml`
//   - StatuteReference from `processing/legal_case_profile.baml`
// =============================================================================

class CourtRule {
  url                    string
  rule_number            string                          @description("e.g. 'O. 5 r. 9', 'RSC O. 11', 'DCR O. 39'")
  order                  string                          @description("The Order (chapter) this rule belongs to")
  court_level            CourtLevel
  subject                string                          @description("Plain-English subject of the rule")
  full_text              string?                         @description("Full rule text (when available)")
  effective_date         string?                         @description("ISO 8601 — when the rule came into effect")
  related_statutes       StatuteReference[]              @description("Statutes the rule is made under")
  extraction_confidence  float                           @description("0.0-1.0")
}

function ExtractCourtRule(
  page_url: string,
  page_html: string,
) -> CourtRule {
  client Gemini2Flash
  prompt #"
    You are an expert Irish Court Rules extraction specialist working
    for Cianfhoghlaim Oideachais.

    The Court Rules library (courts.ie/rules) hosts the Rules of Court
    for District, Circuit, High, Supreme, and Court of Appeal. Each
    rule is identified by an Order + rule number (e.g. 'O. 5 r. 9').

    Source URL: {{ page_url }}
    HTML content (first 20,000 chars):
    ---
    {{ page_html }}
    ---

    Extract:
      url                — source URL
      rule_number        — e.g. "O. 5 r. 9", "RSC O. 11", "DCR O. 39"
      order              — the Order (chapter) this rule belongs to
      court_level        — DISTRICT | CIRCUIT | HIGH | SUPREME | COURT_OF_APPEAL | SPECIAL
      subject            — plain-English subject of the rule
      full_text          — full rule text when available
      effective_date     — ISO 8601
      related_statutes   — StatuteReference[] citing the parent Acts
      extraction_confidence — 0.0-1.0

    {{ ctx.output_format }}
  "#
}
