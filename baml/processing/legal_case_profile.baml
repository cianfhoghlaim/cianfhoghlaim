// BAML schema: Legal + Medical Case Profile Extraction
//
// Used by the Gemini 6-corpus pipeline (change C) to extract
// structured data from agent-generated PDFs in
// `leabharlann/gemini_deep_research/{law,medical,politics,culture,
// technology,other}/`. Each corpus has its own per-corpus variants
// (LegalCaseProfile for law; MedicalCaseProfile for medical; etc.)
// but the 4 shared classes below are used across all 6 corpora.
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate

enum CaseCategory {
  LEGAL_STRATEGY
  MEDICAL_MALPRACTICE
  DISCRIMINATION
  FAMILY_LAW
  CRIMINAL_DEFENSE
  HATE_CRIME
  TENANCY_DISPUTE
  DUAL_CITIZENSHIP
  UNIVERSITY_DISPUTE
  GARDA_MISCONDUCT
  MEDICAL_GASLIGHTING
  EDUCATION_DISPUTE
  CIVIL_LITIGATION
  ECHR_HUMAN_RIGHTS
  OTHER
}

enum Jurisdiction {
  IRELAND
  NORTHERN_IRELAND
  UNITED_KINGDOM
  CROSS_BORDER
  EUROPEAN_UNION
  ECHR
  UNITED_STATES
  INTERNATIONAL
  UNKNOWN
}

class TimelineEvent {
  event_id string
  event_date string                 @description("ISO 8601 date extracted from the PDF's prose (BAML event_time)")
  action string
  parties_involved string[]
  location string?
  is_critical bool
  source_pdf string
}

class LegalCaseProfile {
  case_id string                     @description("UUID derived from file_hash + corpus")
  category CaseCategory
  jurisdiction Jurisdiction[]
  title string
  summary string
  key_parties string[]
  statutes_referenced string[]       @description("e.g. 'Irish Constitution Art. 40', 'Employment Equality Act 1998'")
  key_legal_issues string[]
  outcome_or_status string?
  next_steps string[]
  source_pdf string

  timeline_events TimelineEvent[]
}

class MedicalCaseProfile {
  case_id string
  jurisdiction Jurisdiction[]
  condition_or_complaint string
  providers_involved string[]
  facilities string[]
  diagnoses_or_findings string[]
  timeline_events TimelineEvent[]
  source_pdf string
}

class StatuteReference {
  act_name string
  section string?
  jurisdiction Jurisdiction
  citation_count int                @description("How many PDFs in the corpus cite this statute")
}
