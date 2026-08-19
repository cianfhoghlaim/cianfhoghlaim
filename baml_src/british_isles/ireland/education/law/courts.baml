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
  @@stream.done
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
  @@stream.done
}

function ExtractCourtForm(
  page_url: string,
  page_html: string,
) -> CourtForm {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#

  catch_all (err) {
    CourtForm {
      url "",
      form_title "",
      court_level courtlevel {},
    }
  }
}

function ExtractCourtFee(
  page_url: string,
  page_html: string,
) -> CourtFee {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#

  catch_all (err) {
    CourtFee {
      url "",
      court_level courtlevel {},
    }
  }
}
