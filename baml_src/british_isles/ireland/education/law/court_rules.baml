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
  @@stream.done
}

function ExtractCourtRule(
  page_url: string,
  page_html: string,
) -> CourtRule {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#

  catch_all (err) {
    CourtRule {
      url "",
      court_level courtlevel {},
    }
  }
}
