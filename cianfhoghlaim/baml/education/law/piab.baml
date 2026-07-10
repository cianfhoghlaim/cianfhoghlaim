// =============================================================================
// BAML context: piab.baml
//
// Pick-8 Ireland/law quadrant — PIAB (Personal Injuries Assessment Board)
// extraction schema. One BAML class + one extraction function.
//
// Source: https://www.injuries.ie/eng/ (the front-door for every personal
// injury claim in Ireland).
//
// Re-uses the canonical StatuteReference from
// `processing/legal_case_profile.baml` (cross-file BAML import).
// =============================================================================

// The page kind: process | forms | news | about | consent | permission
enum PIABPageKind {
  PROCESS
  FORMS
  NEWS
  ABOUT
  CONSENT
  PERMISSION_TO_SUE
  OTHER
}

class PIABPage {
  url                    string
  title                  string
  page_kind              PIABPageKind
  process_steps          string[]                        @description("Ordered list of steps in the PIAB process (e.g. 'Apply online', 'PIAB assesses', 'Award issued')")
  forms_mentioned        string[]                        @description("Names of PIAB forms referenced (e.g. 'Form A', 'Form B', 'Consent Form')")
  statutory_deadlines    string[]                        @description("Time limits extracted from the page (e.g. '6 months to apply for PIAB assessment')")
  fees_eur               float?                          @description("PIAB assessment fee in EUR (€) if mentioned")
  permission_to_sue      bool                            @description("True if this page is about the Section 14 / permission-to-sue process")
  statutory_basis        StatuteReference[]              @description("Statutes referenced (e.g. Personal Injuries Assessment Board Act 2003)")
  summary                string                          @description("2-3 sentence summary of the page")
  extraction_confidence  float                           @description("0.0-1.0 — the model's confidence in the extraction")
  @@stream.done
}

function ExtractPIABPage(
  page_url: string,
  page_html: string,
) -> PIABPage {
  client Gemini2FlashAlias
  prompt #"
    You are an expert Personal Injuries Assessment Board (PIAB)
    extraction specialist working for Cianfhoghlaim Oideachais.

    PIAB is the statutory body that assesses personal injury claims in
    Ireland before they can go to court. Most personal injury claims
    must go through PIAB first; the Section 14 / "permission to seek
    judicial review" process is the gate to High Court litigation.

    Statutes to anchor on:
      - Personal Injuries Assessment Board Act 2003
      - Civil Liability and Courts Act 2004 (Part 2)
      - Personal Injuries Assessment Board (Amendment) Act 2019

    Source URL: {{ page_url }}
    HTML content (first 16,000 chars):
    ---
    {{ page_html }}
    ---

    Extract:
      url                  — the source URL
      title                — the page <title>
      page_kind            — PROCESS | FORMS | NEWS | ABOUT | CONSENT | PERMISSION_TO_SUE | OTHER
      process_steps        — ordered list of PIAB process steps
      forms_mentioned      — names of forms referenced
      statutory_deadlines  — time limits (e.g. "6 months to apply")
      fees_eur             — PIAB assessment fee in EUR (€) if mentioned
      permission_to_sue    — true if about Section 14 / permission process
      statutory_basis      — StatuteReference[] citing the relevant Acts
      summary              — 2-3 sentence summary
      extraction_confidence — 0.0-1.0

    {{ ctx.output_format }}
  "#
}
