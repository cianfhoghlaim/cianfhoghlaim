// =============================================================================
// BAML context: legal_aid.baml
//
// Pick-8 Ireland/law quadrant — Legal Aid Board extraction schema.
// Two BAML classes + two extraction functions (pages + forms).
//
// Source: https://www.legalaidboard.ie/ — the Legal Aid Board provides
// civil legal aid and family mediation services to qualifying applicants
// in Ireland.
//
// Re-uses:
//   - LegalAidCategory, LegalAidEligibilityOutcome
//                       from `ie/law/shared_legal_enums.baml`
//   - StatuteReference from `processing/legal_case_profile.baml`
// =============================================================================

class LegalAidPage {
  url                    string
  title                  string
  page_kind              string                          @description("services | apply | about | news | publication | other")
  legal_aid_category     LegalAidCategory
  eligibility_outcome    LegalAidEligibilityOutcome
  eligibility_criteria   string[]                        @description("Conditions under which the page's content applies (income thresholds, asset limits, etc.)")
  services_offered       string[]                        @description("Concrete services described (e.g. 'Civil legal aid', 'Family mediation')")
  application_steps      string[]                        @description("Steps to apply for legal aid")
  statutory_basis        StatuteReference[]              @description("Statutes referenced (e.g. Civil Legal Aid Act 1995)")
  summary                string                          @description("2-3 sentence summary of the page")
  extraction_confidence  float                           @description("0.0-1.0")
  @@stream.done
}

class LegalAidForm {
  url                    string
  form_number            string                          @description("e.g. 'LAB-1', 'Civil Legal Aid Application Form'")
  form_title             string
  legal_aid_category     LegalAidCategory
  purpose                string                          @description("Plain-English description of when to use this form")
  downloadable_url       string?                         @description("URL to the PDF version of the form")
  fillable_fields        string[]                        @description("Names of fields the form requires (e.g. 'PPSN', 'Income', 'Assets')")
  related_statutes       StatuteReference[]              @description("Statutes the form is made under")
  extraction_confidence  float                           @description("0.0-1.0")
  @@stream.done
}

function ExtractLegalAidPage(
  page_url: string,
  page_html: string,
) -> LegalAidPage {
  client Gemini2FlashAlias
  prompt #"
    You are an expert Legal Aid Board (Ireland) extraction specialist
    working for Cianfhoghlaim Oideachais.

    The Legal Aid Board (legalaidboard.ie) administers civil legal aid
    and family mediation services. Their site documents the eligibility
    criteria, services, and application process for legal aid.

    Statutes to anchor on:
      - Civil Legal Aid Act 1995
      - Civil Legal Aid (Amendment) Act 2022
      - Family Law Act 2019 (Part 4 — family mediation)

    Source URL: {{ page_url }}
    HTML content (first 16,000 chars):
    ---
    {{ page_html }}
    ---

    Extract:
      url                    — source URL
      title                  — page <title>
      page_kind              — services | apply | about | news | publication | other
      legal_aid_category     — CIVIL | CRIMINAL | FAMILY_MEDIATION | ASYLUM | OTHER
      eligibility_outcome    — ELIGIBLE | PARTIALLY_ELIGIBLE | INELIGIBLE | UNKNOWN
      eligibility_criteria   — conditions (income thresholds, asset limits, etc.)
      services_offered       — concrete services described
      application_steps      — ordered steps to apply
      statutory_basis        — StatuteReference[] citing relevant Acts
      summary                — 2-3 sentence summary
      extraction_confidence  — 0.0-1.0

    {{ ctx.output_format }}
  "#
}

function ExtractLegalAidForm(
  page_url: string,
  page_html: string,
) -> LegalAidForm {
  client Gemini2FlashAlias
  prompt #"
    You are an expert Legal Aid Board (Ireland) forms extraction
    specialist.

    Source URL: {{ page_url }}
    HTML content (first 8,000 chars):
    ---
    {{ page_html }}
    ---

    Extract:
      url                    — source URL
      form_number            — e.g. "LAB-1", "Civil Legal Aid Application Form"
      form_title             — title of the form
      legal_aid_category     — CIVIL | CRIMINAL | FAMILY_MEDIATION | ASYLUM | OTHER
      purpose                — plain-English description of when to use
      downloadable_url       — PDF URL
      fillable_fields        — names of fields the form requires
      related_statutes       — StatuteReference[] citing relevant Acts
      extraction_confidence  — 0.0-1.0

    {{ ctx.output_format }}
  "#
}
