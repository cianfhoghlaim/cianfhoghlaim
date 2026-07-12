// =============================================================================
// BAML context: shared_legal_enums.baml
//
// Cross-source enums for the Pick-8 Ireland/law BAML registry.
// Lives at `cianfhoghlaim/baml.education.law/shared_legal_enums.baml`.
//
// Re-used by the 5 source-specific BAML files:
//   - piab.baml              (PIABPage, ExtractPIABPage)
//   - courts.baml            (CourtForm, CourtFee, ExtractCourtForm, ExtractCourtFee)
//   - judgements.baml        (Judgement, ExtractJudgement)
//   - court_rules.baml       (CourtRule, ExtractCourtRule)
//   - legal_aid.baml         (LegalAidPage, LegalAidForm, ExtractLegalAidPage, ExtractLegalAidForm)
//
// The 4 shared *Reference / *Event types are imported from
// `processing/legal_case_profile.baml` (the canonical home of
// CaseCategory, Jurisdiction, TimelineEvent, StatuteReference).
// =============================================================================

// CourtLevel — the 6 court levels in Ireland's court hierarchy
// (matches the absorbed ireland_legal_extraction.baml enum)
enum CourtLevel {
  DISTRICT
  CIRCUIT
  HIGH
  SUPREME
  COURT_OF_APPEAL
  SPECIAL
}

// LegalAidCategory — the 4 categories of legal aid the Board provides
enum LegalAidCategory {
  CIVIL
  CRIMINAL
  FAMILY_MEDIATION
  ASYLUM
  OTHER
}

// LegalAidEligibilityOutcome — the result of a financial eligibility
// assessment (used by ExtractLegalAidPage)
enum LegalAidEligibilityOutcome {
  ELIGIBLE
  PARTIALLY_ELIGIBLE
  INELIGIBLE
  UNKNOWN
}
