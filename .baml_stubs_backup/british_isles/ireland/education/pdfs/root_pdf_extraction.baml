// baml/education/pdfs/root_pdf_extraction.baml
//
// Extracts structured data from the 5 NCCA root-level programme PDFs at
// `cianfhoghlaim/leaving_certificate/*.pdf`. The 5 PDFs are:
//   1. key-competencies-in-senior-cycle_en.pdf
//   2. the-potential-of-online-learning-environments_en.pdf
//   3. the-potential-of-technology-to-support-online-certification-and-reporting.pdf
//   4. scr-advisory-report_en.pdf
//   5. SC-L1-L2-Programme-Statement.pdf
//
// Each function returns a structured BAML object with bilingual EN+GA fields.
// Generated clients ship to `shared/baml_client/` (Python) and
// `shared/baml_client_ts/` (TypeScript).
//
// Re-gen after changes:  `cd cianfhoghlaim && uv run baml-cli generate`

// ============================================================================
// Shared types
// ============================================================================

class BilingualTextRootPdf {
  text_en string @description("English text")
  text_ga string? @description("Irish translation; null if EN-only")
}

class EvidenceLink {
  source_pdf string @description("Filename of the source NCCA root-level PDF")
  source_page int @description("PDF page where the content appears (1-indexed)")
  excerpt_en string @description("Verbatim English excerpt from the source")
  excerpt_ga string? @description("Verbatim Irish excerpt (if available)")
}

// ============================================================================
// Function 1: Extract the 5 NCCA Key Competencies
// ============================================================================

class NCCAKeyCompetencyRootPdf {
  code string @description("Canonical NCCA competency code, e.g., 'KC-IP', 'KC-CO', 'KC-WO', 'KC-Prince Edward Island', 'KC-CT'")
  name BilingualTextRootPdf @description("The full competency name (EN + GA)")
  definition BilingualTextRootPdf @description("The full competency definition statement")
  evidence EvidenceLink
  @@stream.done
}

function ExtractKeyCompetencies(pdf_text: string) -> NCCAKeyCompetencyRootPdf[] {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

// ============================================================================
// Function 2: Extract the online learning pedagogy
// ============================================================================

class PedagogySet {
  introduction BilingualTextRootPdf
  pedagogical_principles BilingualTextRootPdf[] @description("The 6-10 pedagogical principles for online learning")
  recommended_practices BilingualTextRootPdf[] @description("The recommended practices for educators")
  technology_recommendations BilingualTextRootPdf[] @description("The technology recommendations")
  evidence EvidenceLink
  @@stream.done
}

function ExtractOnlineLearningPedagogy(pdf_text: string) -> PedagogySet {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

// ============================================================================
// Function 3: Extract the certification + reporting guidance
// ============================================================================

class CertGuidance {
  introduction BilingualTextRootPdf
  certification_mechanisms BilingualTextRootPdf[] @description("The mechanisms for online certification (e.g., digital badges, e-portfolios, blockchain credentials)")
  reporting_recommendations BilingualTextRootPdf[] @description("The recommendations for online reporting")
  technology_requirements BilingualTextRootPdf[] @description("The technology requirements for online certification")
  evidence EvidenceLink
  @@stream.done
}

function ExtractCertificationGuidance(pdf_text: string) -> CertGuidance {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

// ============================================================================
// Function 4: Extract the SCR Advisory (Chief Examiner commentary)
// ============================================================================

class ExaminerCommentary {
  introduction BilingualTextRootPdf
  paper_by_paper_guidance BilingualTextRootPdf[] @description("The paper-by-paper guidance from the Chief Examiner")
  common_mistakes BilingualTextRootPdf[] @description("The common mistakes flagged by the Chief Examiner")
  marker_expectations BilingualTextRootPdf[] @description("The marker expectations (PCLM conventions, marking patterns)")
  evidence EvidenceLink
  @@stream.done
}

function ExtractSCRAdvisory(pdf_text: string) -> ExaminerCommentary {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

// ============================================================================
// Function 5: Extract the Senior Cycle L1 + L2 Programme Statement
// ============================================================================

class AimsExpectations {
  introduction BilingualTextRootPdf
  aims BilingualTextRootPdf[] @description("The 4-8 aims of the Senior Cycle programme")
  expectations BilingualTextRootPdf[] @description("The expectations for students at L1 (Foundation) and L2 (Ordinary) levels")
  rationale BilingualTextRootPdf @description("The rationale for the Senior Cycle curriculum")
  evidence EvidenceLink
  @@stream.done
}

function ExtractProgrammeStatement(pdf_text: string) -> AimsExpectations {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}