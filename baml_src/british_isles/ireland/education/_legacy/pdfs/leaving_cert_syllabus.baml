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

function ExtractLeavingCertSyllabus(
  pdf_text: string
) -> LeavingCertSyllabus {
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

function ExtractSyllabusStructure(
  pdf_text: string,
  subject: string,
  language: string
) -> SyllabusStructure {
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
