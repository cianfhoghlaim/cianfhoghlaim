// =============================================================================
// Content Types (6 cianfhoghlaim content types)
// =============================================================================
// 6 content types per the cianfhoghlaim-website-rewrite spec:
// 1. Subject (NCCA Leaving Certificate subject)
// 2. PastPaperStorage (LC past exam paper)
// 3. MarkingScheme (LC marking scheme)
// 4. PracticeItem (formative assessment item)
// 5. Foundation (NCCA root-level programme PDF)
// 6. Notebook (marimo notebook for embedding)
//
// Each content type is rendered as a BAML function that the agents call.
// The functions pull from the existing dlt/ + cocoindex/ + baml_src/
// pipeline. The functions return structured content that the A2UI
// renderer surfaces as components on the web.
//
// Per `openspec/changes/cianfhoghlaim-website-rewrite/proposal.md` and
// `/specs/cianfhoghlaim-website-rewrite/spec.md` Requirement R1 + R6.

// -----------------------------------------------------------------------------
// Hoisted canonical BilingualText (added 2026-07-12-baml-rename-42-duplicates-v1)
// -----------------------------------------------------------------------------
// Merged from the 2 dups the audit resolved:
//   - root_pdf_extraction.baml (kept as the EN/GA-only canonical BilingualText)
//   - isles_education.baml (renamed to BilingualTextIsles, multilingual form)
// The qpack files use MathBilingualText (per-subject prefixed form).

class BilingualText {
  text_en: string @description("English text")
  text_ga: string? @description("Irish (Gaeilge) translation; null if EN-only")
  text_gd: string? @description("Scottish Gaelic (Gàidhlig) translation")
  text_cy: string? @description("Welsh (Cymraeg) translation")
  text_gv: string? @description("Manx (Gaelg) translation")
  text_kw: string? @description("Cornish (Kernewek) translation")
}

class Subject {
  slug: string @description("NCCA subject slug (mathematics, applied_mathematics, ...)")
  name_en: string @description("English subject name (Mathematics, Applied Mathematics, ...)")
  name_ga: string @description("Irish subject name (Mata, Mata Feidhmíoch, ...)")
  code: string @description("NCCA subject code (LC-MA, LC-AM, ...)")
  color: string @description("Subject color (the hex code or the CSS var)")
  eiraic_tier: int? @description("The 13-tier mastery progression tier (1-13)")
  description_en: string @description("English description of the subject")
  description_ga: string? @description("Irish description of the subject (null if EN-only)")
  mastery_matrix: SubjectMasteryRow[]? @description("The 5x8 mastery matrix row for this subject")
}

class SubjectMasteryRow {
  key_competency: string
  key_competency_ga: string?
  weight: int @description("0-100 mastery percentage")
  level: string @description("attempted | familiar | proficient | mastered")
}

class PastPaperStorage {
  year: int
  paper_number: int
  paper_label: string @description("e.g., 'Paper 1' or 'Paper 2 (Higher)'")
  r2_key: string @description("The CF R2 object key for the PDF")
  r2_signed_url: string? @description("The signed URL (generated on demand by the Cloudflare Worker)")
  sha256: string @description("The PDF SHA-256 for SHA-256 dedup")
  byte_size: int
  page_count: int
  topics: string[] @description("List of NCCA LO codes covered")
  marking_scheme_key: string? @description("The R2 key for the marking scheme PDF")
}

class MarkingScheme {
  year: int
  paper_number: int
  subject: string
  r2_key: string
  r2_signed_url: string?
  rubric_style: string @description("analytic, holistic, trait-based, level-based, mixed")
  criteria: MarkingCriterion[]
  common_mistakes: string[]
  penalisations: string[]
  excerpt: string @description("A short excerpt for the UI")
}

class MarkingCriterion {
  name_en: string
  name_ga: string?
  marks: int
  descriptors: MarkingLevel[]
}

class MarkingLevel {
  level: string @description("e.g., Exceptional, Above, In Line, Yet to Meet")
  descriptor: string
}

class PracticeItem {
  id: string
  subject: string
  lo_code: string
  prompt: string
  prompt_ga: string?
  type: string @description("worked_solution, proof, visual_interpretation, word_problem, multiple_choice")
  difficulty: int @description("1-5")
  expected_answer: string
  expected_answer_ga: string?
  marking_scheme: string
  hints: string[]
  eiraic_tier: int?
}

class Foundation {
  pdf_name: string @description("e.g., key-competencies-in-senior-cycle_en.pdf")
  title_en: string
  title_ga: string?
  category: string @description("key_competencies | sc_l1_l2 | scr_advisory | online_learning | online_certification")
  r2_key: string
  r2_signed_url: string?
  page_count: int
  description: string
  description_ga: string?
}

class Notebook {
  id: string
  subject: string
  title: string
  description: string
  marimo_url: string @description("The Cloudflare R2 / Deno Deploy hosted marimo URL")
  cocoindex_path: string @description("Path to the cocoindex pipeline that generates it")
  difficulty: string
}

function GetSubjectList(language: string) -> Subject[] {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"You are the cianfhoghlaim content catalogue. Return the 8 NCCA Leaving Certificate subjects (Mathematics, Applied Mathematics, Chemistry, Geography, History, English, Gaeilge, Computer Science) in {{ language }} with the 5x8 mastery matrix."
}

function GetPastPapers(subject: string, year_from: int, year_to: int) -> PastPaperStorage[] {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"You are the cianfhoghlaim content catalogue. Return the LC past exam papers for {{ subject }} from {{ year_from }} to {{ year_to }}, with the year, paper number, topic tags, and CF R2 keys."
}

function GetMarkingSchemes(subject: string, year_from: int, year_to: int) -> MarkingScheme[] {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"You are the cianfhoghlaim content catalogue. Return the LC marking schemes for {{ subject }} from {{ year_from }} to {{ year_to }}, with the rubric style, criteria, common mistakes, and penalisations."
}

function GetPracticeItems(subject: string, lo_code: string) -> PracticeItem[] {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"You are the cianfhoghlaim formative assessment generator. Generate 3-5 practice items for {{ subject }} {{ lo_code }}, bilingual EN + GA, with the 13-tier éraic mastery progression."
}

function GetFoundations() -> Foundation[] {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"You are the cianfhoghlaim content catalogue. Return the 5 NCCA root-level programme PDFs (key-competencies, sc-l1-l2-programme, scr-advisory, online-learning, online-certification) with the page count and description."
}

function GetNotebooks(subject: string) -> Notebook[] {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"You are the cianfhoghlaim content catalogue. Return the marimo notebooks for {{ subject }} (1 main + any cross-subject notebooks) with the title, marimo URL, cocoindex path, and difficulty."
}