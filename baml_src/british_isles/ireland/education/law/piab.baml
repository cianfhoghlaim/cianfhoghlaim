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
) -> PIABPage {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#

  catch_all (err) {
    PIABPage {
      url "",
      title "",
      page_kind piabpagekind {},
    }
  }
}
