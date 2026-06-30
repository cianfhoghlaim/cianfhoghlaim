// BAML schema: Leaving Certificate Syllabus Extraction
//
// Two related functions:
//
// 1. `ExtractLeavingCertSyllabus` — extracts topics, learning outcomes, and
//    weighting from a single subject-level syllabus PDF. Used by the
//    per-subject pipeline to generate the syllabus analysis section of the
//    public portal pages.
//
// 2. `ExtractSyllabusStructure` — added per the
//    `ncca-leaving-cert-syllabi-corpus` openspec change (2026-06-30). Splits
//    a combined syllabus PDF into its Higher / Ordinary / Foundation level
//    sections. NCCA does NOT publish separate HL and OL PDFs — the syllabus
//    is one document that contains all levels.
//
// Usage:
//   from oideachais.data_platform.baml_client import b
//   syllabus = b.ExtractLeavingCertSyllabus(pdf_text)
//   structure = b.ExtractSyllabusStructure(pdf_text, "Mathematics", "en")
//
// Re-gen after changes:  `cd oideachais && uv run baml-cli generate`

class SyllabusTopic {
  topicId string
  name string @description("Short display name, e.g. 'Differentiation'")
  description string
  learningOutcomes string[] @description("Full NCCA learning outcome statements for this topic")
  weightPct int @description("Estimated percentage of total exam marks (0-100). 0 if unknown.")
}

class LeavingCertSyllabus {
  subject string @description("Subject name, e.g. 'Mathematics'")
  year int @description("Year this syllabus applies to")
  level string @description("One of: 'Higher', 'Ordinary', 'Foundation', 'Higher+Ordinary'")
  topics SyllabusTopic[] @description("All topics in this syllabus")
}

function ExtractLeavingCertSyllabus(pdf_text: string) -> LeavingCertSyllabus {
  client LitellmClient
  prompt #"
    You are an Irish Leaving Certificate syllabus expert. Extract all topics
    and learning outcomes from the following syllabus PDF text.

    For each topic:
    - `name` is a short display name (e.g. 'Differentiation', 'Cell Biology')
    - `description` is a 1-2 sentence summary of what the topic covers
    - `learningOutcomes` are the full NCCA learning outcome statements
    - `weightPct` is your best estimate of what % of the total exam this
      topic represents (0-100). If unknown, use 0.

    Subject context: {{ ctx.subject }}
    Year context: {{ ctx.year }}

    PDF text:
    {{ pdf_text }}

    {{ ctx.output_format }}
  "#
}

// ---------------------------------------------------------------------------
// Syllabus structure (level-section identification) — added 2026-06-30
// ---------------------------------------------------------------------------

// One logical level section inside a combined syllabus PDF.
class SyllabusLevel {
  level string @description("One of: 'Foundation', 'Ordinary', 'Higher'")
  chapter_count int @description("Number of distinct chapters in this level section")
  topic_count int @description("Number of distinct topics in this level section")
  page_range string @description("Human-readable page range, e.g. 'pp. 12-45' or 'pp. 87-122'")
  learning_outcomes string[] @description("Sample of learning outcomes (3-5 representative examples)")
}

// Whole-syllabus structure: title, subject, language, per-level breakdown, plus
// overview text from the front matter of the PDF.
class SyllabusStructure {
  title string @description("Full syllabus title as printed on the cover page")
  subject string @description("English subject slug, e.g. 'mathematics', 'gaeilge', 'computer-science'")
  language string @description("'en' for English, 'ga' for Irish")
  level_sections SyllabusLevel[] @description("One entry per level this subject is examined at. Mathematics + Gaeilge = 3 levels (Foundation, Ordinary, Higher). English/History/Geography/Chemistry/Applied Maths/Computer Science = 2 levels (Ordinary, Higher).")
  subject_overview string @description("1-3 paragraphs from the front matter describing the subject")
  assessment_overview string @description("1-3 paragraphs from the front matter describing how the subject is assessed")
}

function ExtractSyllabusStructure(pdf_text: string, subject: string, language: string) -> SyllabusStructure {
  client ExtractEnStrong
  prompt #"
    You are an Irish Leaving Certificate syllabus expert. The NCCA does NOT
    publish separate Higher-Level and Ordinary-Level PDFs. Instead, the
    currently-taught syllabus for each subject is ONE PDF that contains
    sections for all examination levels the subject offers.

    Your task: split the syllabus into its logical level sections and report
    the per-level structure.

    Subject: {{ subject }}
    Language: {{ language }}

    Important conventions:
    - For Mathematics and Gaeilge (Irish), there are THREE levels: Foundation,
      Ordinary, Higher. Each must be a separate entry in `level_sections`.
    - For English, History, Geography, Chemistry, Applied Mathematics, and
      Computer Science, there are TWO levels: Ordinary and Higher. There is
      NO Foundation section.
    - For Gaeilge (the Irish language subject), the levels are sometimes
      labelled "Bonnleibhéal" (Foundation), "Gnáthleibhéal" (Ordinary),
      "Ardleibhéal" (Higher) — map these to the English level names.
    - `level_sections` MUST be ordered from lowest to highest (Foundation,
      then Ordinary, then Higher) and contain exactly the levels the subject
      is examined at — no extras, no omissions.

    PDF text:
    {{ pdf_text }}

    {{ ctx.output_format }}
  "#
}
