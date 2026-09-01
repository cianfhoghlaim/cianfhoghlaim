// BAML Schema for the Leabharlann Corpus (v4) Extraction
//
// Unified structured extraction for any document in the personal + academic
// archive under `leabharlann/`. The leabharlann corpus is the union of the
// 6 Plan 1 sub-corpora:
//
//   1. `leabharlann/gaeilge/`           — Irish-language books (PDF + DOCX + EPUB + MD)
//   2. `leabharlann/aigne/`            — English-language books (PDF)
//   3. `leabharlann/mata/`             — Mathematics hand-written pages (.pages, scanned PDFs)
//   4. `leabharlann/ollscoil_na_gaillimhe/` — University of Galway artefacts (PDF + DOCX + .pages)
//   5. `leabharlann/zotero/`           — Academic papers in real Zotero storage format
//   6. `leabharlann/gemini_deep_research/` — Gemini deep-research PDFs with inline citations
//
// All extractions route through the `Default` client alias (per commit
// 667635dfd, the single text-extraction generator is `minimax-m3` on the
// coding plan API). The litellm clients (`ExtractEn`, `LitellmClient`
// change in `clients.baml`.
//
// Reference: openspec/changes/2026-07-15-oideachais-leabharlann-v1/
//            + openspec/specs/oideachais-leabharlann/spec.md
//            + openspec/specs/oideachais-baml-schemas/spec.md

// =============================================================================
// Sub-corpus discriminator + topic enums
// =============================================================================

enum LeabharlannSubcorpus {
  GAEILGE            @description("Irish-language books (PDF + DOCX + EPUB + MD) from leabharlann/gaeilge/")
  AIGNE              @description("English-language books (PDF) from leabharlann/aigne/")
  MATA               @description("Mathematics handwritten pages from leabharlann/mata/")
  OLLSCOIL_NA_GAILLIMHE
                     @description("University of Galway artefacts (PDF + DOCX + .pages) from leabharlann/ollscoil_na_gaillimhe/")
  ZOTERO             @description("Academic papers in real Zotero storage format from leabharlann/zotero/")
  GEMINI_DEEP_RESEARCH
                     @description("Gemini deep-research PDFs with inline citations from leabharlann/gemini_deep_research/")
  UNKNOWN            @description("None of the above (fallback)")
}

enum LeabharlannLanguage {
  GA    @description("Irish (Gaeilge)")
  EN    @description("English")
  MIXED @description("Mixed GA + EN (e.g. a UoG bilingual lecture handout)")
  OTHER @description("Latin / Greek / mathematical / other non-natural language")
}

enum LeabharlannDocKind {
  BOOK_CHAPTER       @description("A single chapter or section of a longer book")
  BOOK_FULL          @description("An entire short book or monograph")
  PAPER              @description("An academic paper / arXiv preprint / journal article")
  COURSEWORK         @description("A university assignment, exam, lecture notes, or placement portfolio")
  EXAM_PAPER         @description("A formal exam paper or revision material")
  LECTURE_NOTES      @description("Lecture notes or class handouts")
  RESEARCH_REPORT    @description("A Gemini / agentic deep-research report")
  CODE_FILE          @description("A code file (.py / .ipynb / .js / .ts)")
  SCANNED_PAGES      @description("Scanned PDF or Apple Pages file (OCR candidate)")
  PRESENTATION       @description("PowerPoint / Keynote presentation")
  TRANSCRIPT         @description("Academic transcript or grade list")
  CITATION_INDEX     @description("Zotero citation index entry (.cff / .bib)")
  OTHER              @description("None of the above")
}

// =============================================================================
// Main extraction record
// =============================================================================

class LeabharlannDoc {
  // ---- Identity ----
  file_name               string             @description("The basename of the file (e.g. 'CT511_assignment_2024.pdf')")
  source_subdir           LeabharlannSubcorpus @description("Which of the 6 sub-corpora (gaeilge | aigne | mata | ollscoil_na_gaillimhe | zotero | gemini_deep_research)")
  file_type               string             @description("Lowercased extension: pdf | docx | epub | md | pages | py | ipynb | bib")

  // ---- Document classification ----
  doc_kind                LeabharlannDocKind @description("The kind of document (book chapter, paper, coursework, exam, ...)")
  doc_language            LeabharlannLanguage @description("Primary language of the document")
  doc_title               string             @description("Cleaned title of the document, with newline artefacts removed")
  doc_summary             string             @description("2-3 sentence summary of the document content")
  author_names            string[]           @description("Ordered list of author names (best-effort from the text); empty for anonymous")
  publication_year        int?               @description("4-digit publication year, or null if not discernible")
  course_code             string?            @description("Course code (e.g. CT511, GA101, ED305, MA335) if discernible; null for non-coursework")
  programme_code          string?            @description("Programme code (e.g. HDSD, BScMS) if discernible; null for non-coursework")

  // ---- Topics + indexing ----
  key_topics              string[]           @description("3-7 single-sentence topics, ordered by importance")
  irish_relevant          bool               @description("True if the document is about the Irish language, in Irish, or related to Celtic studies")
  math_relevant           bool               @description("True if the document contains mathematical content (LaTeX, equations, statistics)")

  // ---- Zotero-only fields ----
  arxiv_id                string?            @description("Bare arXiv identifier (e.g. '2504.02890') if the document is an arXiv preprint; null otherwise")
  arxiv_version           string?            @description("arXiv version (e.g. 'v2') if discernible; null otherwise")
  doi                     string?            @description("Digital Object Identifier (formatted '10.xxxx/xxxx' without the 'doi:' prefix); null if not visible")
  paper_venue             string?            @description("Journal or conference name for journal/conference papers; null otherwise")
  paper_abstract          string?            @description("Abstract if visible in the first 2 pages; null otherwise")

  // ---- Gemini-only fields ----
  gemini_research_date    string?            @description("ISO 8601 (YYYY-MM-DD) Gemini deep-research date, or null")
  cited_urls              string[]           @description("Cited URLs in the Gemini deep-research PDF (deduplicated); empty for non-Gemini")

  // ---- UoG-only fields ----
  programme_stage         string?            @description("Programme stage: undergraduate, PGCE, masters, PhD, professional, or unknown (UoG artefacts only)")
  needs_ocr               bool               @description("True if the document contains handwriting that needs OCR / HTR (.pages files, scanned PDFs)")
  approximate_word_count  int?               @description("Approximate word count if discernible (within +/- 20%); null otherwise")

  // ---- Citations / cross-archive edges ----
  cited_paper_arxiv_ids   string[]           @description("arXiv IDs of papers cited by this document; empty if none detected")
  references_uog_codes    string[]           @description("UoG course codes referenced by this document; empty if none detected")

  // ---- Quality ----
  confidence              float              @description("Overall LLM self-rated confidence 0.0-1.0")
}

// =============================================================================
// BAML functions
// =============================================================================

/// Extract structured metadata from any document in the leabharlann corpus.
/// Routes via the `Default` client (minimax-m3 on the coding plan API).
function ExtractLeabharlannDoc(
  text: string,
  file_name: string,
  subcorpus: LeabharlannSubcorpus
) -> LeabharlannDoc {
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

// =============================================================================
// Test (smoke check for the BAML harness)
// =============================================================================

// test ExtractLeabharlannDocTest {
//   functions [ExtractLeabharlannDoc]
//   args {
//     text #"
//       Táim ag foghlaim Gaeilge gach lá. Is maith liom an cultúr Gaelach.
//       Scríobh mé leabhar dar teideal 'An Ghaeilge Bheo' i 2024.
//     "#
//     file_name "an_gaeilge_bheo_cap1.md"
//     subcorpus "GAEILGE"
//   }
// }
