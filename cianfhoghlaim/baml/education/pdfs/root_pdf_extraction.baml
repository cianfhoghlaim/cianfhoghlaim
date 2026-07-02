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

class BilingualText {
  text_en: string @description("English text")
  text_ga: string? @description("Irish translation; null if EN-only")
}

class EvidenceLink {
  source_pdf: string @description("Filename of the source NCCA root-level PDF")
  source_page: int @description("PDF page where the content appears (1-indexed)")
  excerpt_en: string @description("Verbatim English excerpt from the source")
  excerpt_ga: string? @description("Verbatim Irish excerpt (if available)")
}

// ============================================================================
// Function 1: Extract the 5 NCCA Key Competencies
// ============================================================================

class NCCAKeyCompetency {
  code: string @description("Canonical NCCA competency code, e.g., 'KC-IP', 'KC-CO', 'KC-WO', 'KC-PE', 'KC-CT'")
  name: BilingualText @description("The full competency name (EN + GA)")
  definition: BilingualText @description("The full competency definition statement")
  evidence: EvidenceLink
}

function ExtractKeyCompetencies(pdf_text: string) -> NCCAKeyCompetency[] {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"You are an expert at extracting the 5 NCCA Senior Cycle Key Competencies from the official NCCA document.

Given the text of the `key-competencies-in-senior-cycle_en.pdf` document, extract exactly 5 NCCA Key Competencies. Each competency has a code, a name, and a definition statement.

The 5 NCCA Key Competencies are:
1. Information Processing (KC-IP)
2. Communicating (KC-CO)
3. Working with Others (KC-WO)
4. Personal Effectiveness (KC-PE)
5. Critical & Creative Thinking (KC-CT)

For each competency, extract:
- `code`: the canonical NCCA competency code
- `name_en`: the English name
- `name_ga`: the Irish translation (use null if the syllabus is EN-only)
- `definition_en`: the verbatim English definition statement
- `definition_ga`: the verbatim Irish definition (or null if EN-only)
- `source_pdf`: 'key-competencies-in-senior-cycle_en.pdf'
- `source_page`: the PDF page where the competency appears
- `excerpt_en`: a verbatim English excerpt from the source
- `excerpt_ga`: a verbatim Irish excerpt (or null)

Return the 5 competencies in this exact order:
1. Information Processing
2. Communicating
3. Working with Others
4. Personal Effectiveness
5. Critical & Creative Thinking

{{ ctx.output_format(prefix="Answer with this format:\n") }}
"#
}

// ============================================================================
// Function 2: Extract the online learning pedagogy
// ============================================================================

class PedagogySet {
  introduction: BilingualText
  pedagogical_principles: BilingualText[] @description("The 6-10 pedagogical principles for online learning")
  recommended_practices: BilingualText[] @description("The recommended practices for educators")
  technology_recommendations: BilingualText[] @description("The technology recommendations")
  evidence: EvidenceLink
}

function ExtractOnlineLearningPedagogy(pdf_text: string) -> PedagogySet {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"You are an expert at extracting pedagogical guidance from the NCCA document on online learning environments.

Given the text of `the-potential-of-online-learning-environments_en.pdf`, extract:
- The introduction (the document's opening statement)
- 6-10 pedagogical principles for online learning (bilingual EN+GA)
- The recommended practices for educators (bilingual EN+GA)
- The technology recommendations (bilingual EN+GA)
- The source PDF page references

{{ ctx.output_format(prefix="Answer with this format:\n") }}
"#
}

// ============================================================================
// Function 3: Extract the certification + reporting guidance
// ============================================================================

class CertGuidance {
  introduction: BilingualText
  certification_mechanisms: BilingualText[] @description("The mechanisms for online certification (e.g., digital badges, e-portfolios, blockchain credentials)"]
  reporting_recommendations: BilingualText[] @description("The recommendations for online reporting"]
  technology_requirements: BilingualText[] @description("The technology requirements for online certification"]
  evidence: EvidenceLink
}

function ExtractCertificationGuidance(pdf_text: string) -> CertGuidance {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"You are an expert at extracting certification + reporting guidance from the NCCA document.

Given the text of `the-potential-of-technology-to-support-online-certification-and-reporting.pdf`, extract:
- The introduction
- The certification mechanisms for online assessment (digital badges, e-portfolios, blockchain credentials, etc.) — bilingual EN+GA
- The reporting recommendations — bilingual EN+GA
- The technology requirements — bilingual EN+GA
- The source PDF page references

{{ ctx.output_format(prefix="Answer with this format:\n") }}
"#
}

// ============================================================================
// Function 4: Extract the SCR Advisory (Chief Examiner commentary)
// ============================================================================

class ExaminerCommentary {
  introduction: BilingualText
  paper_by_paper_guidance: BilingualText[] @description("The paper-by-paper guidance from the Chief Examiner"]
  common_mistakes: BilingualText[] @description("The common mistakes flagged by the Chief Examiner"]
  marker_expectations: BilingualText[] @description("The marker expectations (PCLM conventions, marking patterns)"]
  evidence: EvidenceLink
}

function ExtractSCRAdvisory(pdf_text: string) -> ExaminerCommentary {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"You are an expert at extracting Chief Examiner commentary from the SEC State Examinations Commission Advisory Report.

Given the text of `scr-advisory-report_en.pdf`, extract:
- The introduction
- The paper-by-paper guidance from the Chief Examiner (per subject, per paper, per level) — bilingual EN+GA
- The common mistakes flagged by the Chief Examiner — bilingual EN+GA
- The marker expectations (PCLM conventions, marking patterns) — bilingual EN+GA
- The source PDF page references

{{ ctx.output_format(prefix="Answer with this format:\n") }}
"#
}

// ============================================================================
// Function 5: Extract the Senior Cycle L1 + L2 Programme Statement
// ============================================================================

class AimsExpectations {
  introduction: BilingualText
  aims: BilingualText[] @description("The 4-8 aims of the Senior Cycle programme"]
  expectations: BilingualText[] @description("The expectations for students at L1 (Foundation) and L2 (Ordinary) levels"]
  rationale: BilingualText @description("The rationale for the Senior Cycle curriculum"]
  evidence: EvidenceLink
}

function ExtractProgrammeStatement(pdf_text: string) -> AimsExpectations {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"You are an expert at extracting the Senior Cycle L1 + L2 Programme Statement from the NCCA document.

Given the text of `SC-L1-L2-Programme-Statement.pdf`, extract:
- The introduction
- The 4-8 aims of the Senior Cycle programme — bilingual EN+GA
- The expectations for students at L1 (Foundation) and L2 (Ordinary) levels — bilingual EN+GA
- The rationale for the Senior Cycle curriculum — bilingual EN+GA
- The source PDF page references

{{ ctx.output_format(prefix="Answer with this format:\n") }}
"#
}