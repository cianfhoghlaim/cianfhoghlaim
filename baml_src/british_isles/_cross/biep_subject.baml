// BAML schema: Cianfhoghlaim British Isles Subject Registry (BIEP v3)
//
// Per the 2026-07-27-biep-v3-canonical-registry-v1 change.
//
// The canonical British Isles subject taxonomy. Stored in DuckDB as
// 3 tables:
//   cianfhoghlaim.education._registry.subjects
//   cianfhoghlaim.education._registry.jurisdiction_overrides
//   cianfhoghlaim.education._registry.cross_jurisdiction_bridges
//
// The 8 canonical enums below define the slug vocabulary for every
// (jurisdiction, stage, subject, board, qualification_level) tuple.
//
// The companion notebook `notebooks/18_cianfhoghlaim_subject_registry.py`
// renders the registry as 4 tabs:
//   1. Format doc + this BAML schema
//   2. Nation comparison (IE vs EN vs SCT vs WLS vs NI vs JEY vs GGY vs IOM)
//   3. Cross-jurisdiction bridge explorer
//   4. Drift detector (live registry vs official NCCA/SQA/WJEC/CCEA via
//      ChangeDetection.io)
//
// Reference: openspec/changes/2026-07-27-biep-v3-canonical-registry-v1/

// ----------------------------------------------------------------------------
// Canonical enums
// ----------------------------------------------------------------------------

enum Jurisdiction {
  IRELAND
  ENGLAND
  SCOTLAND
  WALES
  NORTHERN_IRELAND
  JERSEY
  GUERNSEY
  ISLE_OF_MAN
}

enum EducationalStage {
  PRIMARY
  JUNIOR_CYCLE            // Ireland Year 1-3
  SENIOR_CYCLE            // Ireland Senior Cycle (pre-LC)
  LEAVING_CERTIFICATE     // Ireland LC
  GCSE                    // England GCSE
  AS_LEVEL                 // England AS-Level
  A_LEVEL                  // England A-Level
  NATIONAL_5               // Scotland National 5
  HIGHER                   // Scotland Higher
  ADVANCED_HIGHER          // Scotland Advanced Higher
  FOUNDATION               // Foundation tier
}

enum AwardingBody {
  NONE                     // Ireland (NCCA + SEC)
  AQA                      // England
  OCR                      // England
  EDEXCEL                  // England (Pearson)
  WJEC                     // Wales
  CCEA                     // Northern Ireland
  SQA                      // Scotland
}


enum Language {
  EN                       // English
  GA                       // Irish (Gaeilge)
  CY                       // Welsh (Cymraeg)
  GD                       // Scottish Gaelic
  GV                       // Manx
}

enum CrossJurisdictionConcept {
  // Core 10 subjects that span most jurisdictions
  MATHEMATICS
  ENGLISH
  BIOLOGY
  CHEMISTRY
  PHYSICS
  HISTORY
  GEOGRAPHY
  COMPUTER_SCIENCE
  FRENCH
  GERMAN
  SPANISH
  // Single-jurisdiction subjects
  IRISH_LANGUAGE           // IE only
  BUSINESS_STUDIES         // IE JC, EN GCSE/A-Level, SCT, WLS, NI
  LATIN                    // IE LC, EN GCSE/A-Level, WLS
  CLASSICAL_STUDIES        // IE LC, EN GCSE/A-Level
  DESIGN_AND_COMMUNICATION_GRAPHICS  // IE LC only
  // Catch-alls
  OTHER
}

enum RegistrySource {
  NCCA_OFFICIAL            // https://www.ncca.ie
  JCQ_OFFICIAL             // https://www.jcq.org.uk (England)
  AQA_OFFICIAL             // https://www.aqa.org.uk
  OCR_OFFICIAL             // https://www.ocr.org.uk
  PEARSON_EDEXCEL_OFFICIAL // https://qualifications.pearson.com
  WJEC_OFFICIAL            // https://www.wjec.co.uk
  CCEA_OFFICIAL            // https://ccea.org.uk
  SQA_OFFICIAL             // https://www.sqa.org.uk
  JERSEY_CURRICULUM
  GUERNSEY_CURRICULUM
  ISLE_OF_MAN_CURRICULUM
  USER_SUBMITTED
}

enum RegistryStatus {
  ACTIVE
  DEPRECATED
  PROPOSED
  UNDER_REVIEW
}

// ----------------------------------------------------------------------------
// Canonical British Isles Subject class
// ----------------------------------------------------------------------------

class SubjectSlug {
  jurisdiction Jurisdiction
  stage EducationalStage
  subject_slug string             @description("Lowercase snake_case, e.g. 'mathematics', 'english_language'")
  board AwardingBody
  qualification_level QualificationLevel?
  language Language
}

class SubjectRegistryRow {
  // Identity (composite primary key)
  jurisdiction Jurisdiction
  stage EducationalStage
  subject_slug string
  board AwardingBody
  qualification_level QualificationLevel?
  language Language

  // Display
  display_name_en string
  display_name_local string?
  concept CrossJurisdictionConcept
  source_url string?              @description("Official spec page URL (NCCA, AQA, OCR, etc.)")
  ncca_spec_code string?          @description("NCCA spec code, e.g. 'LC003' (Ireland only)")

  // Operational
  baml_function string             @description("Which @function to call, e.g. 'b.ExtractCurriculumSyllabus'")
  source RegistrySource
  status RegistryStatus
  first_introduced string         @description("ISO date, e.g. '2024-09'")
  last_verified string             @description("ISO date, e.g. '2026-07-17'")
  notes string?
}

class JurisdictionOverride {
  jurisdiction Jurisdiction
  subject_slug string
  override_field string            @description("The field being overridden, e.g. 'display_name_local', 'baml_function'")
  override_value string
  reason string
  effective_from string            @description("ISO date")
}

class CrossJurisdictionBridge {
  concept CrossJurisdictionConcept
  jurisdiction_slug_map string     @description("JSON: {ireland: 'gaeilge', northern_ireland: 'irish'}")
  display_name string
  notes string?
}

// ----------------------------------------------------------------------------
// Canonical query functions
// ----------------------------------------------------------------------------

function QueryRegistryByJurisdiction(
  jurisdiction: "baml_src.british_isles._cross.biep_subject.Jurisdiction"
) -> SubjectRegistryRow[] {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
  "#
}

function QueryRegistryByConcept(
  concept: CrossJurisdictionConcept
) -> SubjectRegistryRow[] {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
  "#
}
