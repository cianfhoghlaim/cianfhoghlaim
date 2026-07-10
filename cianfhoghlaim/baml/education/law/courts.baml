// =============================================================================
// BAML context: courts.baml
//
// Pick-8 Ireland/law quadrant — Courts Service of Ireland extraction
// schema. Two BAML classes + two extraction functions (forms + fees).
//
// Source: https://www.courts.ie/ (forms + fees sub-trees only;
// Judgements are in `judgements.baml` and Rules are in `court_rules.baml`).
//
// Re-uses:
//   - CourtLevel  from `ie/law/shared_legal_enums.baml`
//   - StatuteReference from `processing/legal_case_profile.baml`
// =============================================================================

class CourtForm {
  url                    string
  form_number            string                          @description("e.g. 'Form 1', 'Form 5A', 'HC1', 'CC1'")
  form_title             string
  court_level            CourtLevel
  category               string                          @description("personal_injury | family | criminal | civil | probate | licensing | taxation | other")
  purpose                string                          @description("Plain-English description of when to use this form")
  parties                string[]                        @description("Plaintiff | Defendant | Applicant | Respondent | Petitioner")
  fee_eur                float?                          @description("Filing fee in EUR (€) if listed")
  downloadable_url       string?                         @description("URL to the PDF version of the form")
  fillable_fields        string[]                        @description("Names of fields the form requires (e.g. 'PPSN', 'Date of Birth', 'Solicitor details')")
  related_statutes       StatuteReference[]              @description("Statutes referenced by this form")
  extraction_confidence  float                           @description("0.0-1.0")
}

class CourtFee {
  url                    string
  fee_code               string                          @description("e.g. 'A1', 'B2', 'C5'")
  fee_description        string                          @description("What the fee is for")
  amount_eur             float                           @description("Amount in EUR (€)")
  court_level            CourtLevel
  effective_date         string?                         @description("ISO 8601 — when the fee schedule came into effect")
  notes                  string?                         @description("Any conditions or exemptions")
  extraction_confidence  float                           @description("0.0-1.0")
}

function ExtractCourtForm(
  page_url: string,
  page_html: string,
) -> CourtForm {
  client Gemini2Flash
  prompt #"
    You are an expert Courts Service of Ireland forms extraction
    specialist working for Cianfhoghlaim Oideachais.

    The Courts Service website (courts.ie) hosts hundreds of forms
    across District, Circuit, High, Supreme, and Court of Appeal.

    Source URL: {{ page_url }}
    HTML content (first 16,000 chars):
    ---
    {{ page_html }}
    ---

    Extract:
      url                — source URL
      form_number        — e.g. "Form 1", "HC1", "CC5A"
      form_title         — title of the form
      court_level        — DISTRICT | CIRCUIT | HIGH | SUPREME | COURT_OF_APPEAL | SPECIAL
      category           — personal_injury | family | criminal | civil | probate | licensing | taxation | other
      purpose            — plain-English description of when to use
      parties            — Plaintiff | Defendant | Applicant | Respondent | Petitioner
      fee_eur            — fee in EUR (€) if listed
      downloadable_url   — PDF URL
      fillable_fields    — names of fields the form requires
      related_statutes   — StatuteReference[] citing relevant Acts
      extraction_confidence — 0.0-1.0

    {{ ctx.output_format }}
  "#
}

function ExtractCourtFee(
  page_url: string,
  page_html: string,
) -> CourtFee {
  client Gemini2Flash
  prompt #"
    You are an expert Courts Service of Ireland fee-schedule extraction
    specialist.

    Source URL: {{ page_url }}
    HTML content (first 8,000 chars):
    ---
    {{ page_html }}
    ---

    Extract:
      url                 — source URL
      fee_code            — e.g. "A1", "B2", "C5"
      fee_description     — what the fee is for
      amount_eur          — EUR (€)
      court_level         — DISTRICT | CIRCUIT | HIGH | SUPREME | COURT_OF_APPEAL | SPECIAL
      effective_date      — ISO 8601
      notes               — any conditions
      extraction_confidence — 0.0-1.0

    {{ ctx.output_format }}
  "#
}
