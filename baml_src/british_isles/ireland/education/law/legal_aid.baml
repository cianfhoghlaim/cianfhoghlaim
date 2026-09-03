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
) -> LegalAidPage {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#

  catch_all (err) {
    LegalAidPage {
      url "",
      title "",
      legal_aid_category legalaidcategory {},
      eligibility_outcome legalaideligibilityoutcome {},
    }
  }
}

function ExtractLegalAidForm(
  page_url: string,
  page_html: string,
) -> LegalAidForm {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#

  catch_all (err) {
    LegalAidForm {
      url "",
      form_title "",
      legal_aid_category legalaidcategory {},
    }
  }
}
