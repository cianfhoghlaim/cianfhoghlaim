// BAML Schema for University of Galway Past-Exam-Paper Extraction (M.Sc. AI thesis)
//
// Companion to `university_extraction.baml` (course / module / programme /
// reading-list descriptors) and `_cross/isles_education.baml::ExamPaperIsles`
// (generic Celtic-nations exam paper). This file ADDS the UoG-specific fields
// (module_code, programme_code, NFQ level, sitting, paper_format, language,
// source_kind) needed to wire authenticated exam papers back to the existing
// `module_pages` / `ModuleDescriptor` corpus via the
// `UoGExamPaper-COVERS-UoGModuleDescriptor` Cognee edge (see
// `cognify/rules/uog_exam_cross_archive.py`).
//
// All three extraction functions (`ExtractUoGExamPaper`,
// `ExtractUoGSyllabus`, `MapUoGExamQuestionsToLOs`) route through the
// canonical `ExtractEn` LiteLLM client so the platform keeps one LLM
// surface to operate. The image-mulitmodal path (VLM extraction when the
// PDF has no embedded text layer — most UoG maths papers are scanned)
// is fed via the `image_url` LiteLLM block on the same client, so swapping
// `glm-4.6v-flash` ↔ `qwen3-vl-7b` is a single env-var change.
//
// Reference: openspec/changes/2026-08-23-uog-exam-papers-sso-v1/

// =============================================================================
// Provenance + taxonomy enums
// =============================================================================

enum UoGProvenanceKind {
  PUBLIC_WEB              @description("Scraped from the public catalogue (www.universityofgalway.ie) with no SSO")
  AUTH_PDF                @description("Downloaded from the authenticated exam portal (exams.universityofgalway.ie) after Campus Identity login")
  PUBLIC_WEB_AUTH_PDF_MERGED @description("Public module-page descriptor merged with the authenticated exam PDF (the thesis canonical form)")
}

enum UoGSitting {
  AUTUMN                  @description("Autumn semester exam (Oct–Nov)")
  SPRING                  @description("Spring semester exam (Apr–May)")
  SUMMER                  @description("Resit / summer supplemental")
  AUTUMN_SUPPLEMENTARY    @description("Autumn supplemental / repeat sitting")
  WINTER                  @description("January supplemental")
}

enum UoGPaperFormat {
  WRITTEN_ONLINE          @description("Written online, real-time answer entry")
  MCQ_BANK                @description("Multiple choice via the MCQ bank")
  PDF_UPLOAD              @description("Open-ended PDF the student downloads, writes on, uploads")
  TAKE_HOME               @description("Take-home paper with a 24–72 h window")
  OPEN_BOOK               @description("Open-book exam (allowed to use any resource)")
}

enum UoGBloomLevel {
  REMEMBER                @description("Bloom level 1 — recall (define, list, name)")
  UNDERSTAND             @description("Bloom level 2 — comprehension (explain, summarise)")
  APPLY                  @description("Bloom level 3 — use in a new context")
  ANALYSE                @description("Bloom level 4 — break down, compare")
  EVALUATE               @description("Bloom level 5 — judge, critique")
  CREATE                 @description("Bloom level 6 — synthesise, design")
  UNKNOWN                @description("Bloom level cannot be inferred")
}

// =============================================================================
// UoG-exam-paper class — superset of `_cross/isles_education::ExamPaperIsles`
// =============================================================================

// Re-declared locally so the BAML compiler can statically check the
// superset relationship. The fields mirror `ExamPaperIsles` (Celtic-nations
// generic) with UoG-specific additions on top.
class UoGExamPaper {
  // Cross-jurisdiction features (mirrors ExamPaperIsles)
  title string @description("Paper title, e.g. 'CT516 — Deep Learning, Autumn 2023'")
  paper_number int? @description("Paper 1, Paper 2, etc. (1-indexed; null if no multi-paper structure)")
  duration_minutes int? @description("Exam duration in minutes, e.g. 120")
  total_marks int @description("Total marks available")
  questions ExamQuestionIsles[] @description("All questions (re-uses the Celtic-nations class for cross-jurisdiction feature parity)")
  instructions string? @description("General instructions to candidates (e.g. 'Answer 3 of 5 questions')")

  // UoG-specific fields (the thesis contribution)
  module_code string @description("UoG module code, e.g. 'CT516', 'MA335', 'HI451'")
  programme_code string[] @description("Programme codes the module belongs to, e.g. ['MSCAI', 'BScCS']")
  semester string? @description("Semester string from the UoG registry, e.g. 'Semester 1'")
  academic_year int @description("Academic year, e.g. 2023 for the 2023-24 session")
  sitting UoGSitting @description("Which sitting the paper belongs to (AUTUMN / SPRING / SUMMER / WINTER / AUTUMN_SUPPLEMENTARY)")
  paper_format UoGPaperFormat @description("Delivery format (WRITTEN_ONLINE / MCQ_BANK / PDF_UPLOAD / TAKE_HOME / OPEN_BOOK)")
  language string @description("ISO-639-1 ('en' for almost every UoG paper, 'ga' for Fiontar)")
  nfq_level int? @description("NFQ level of the module hosting this paper (6/7/8/9/10)")

  // Provenance
  source_kind UoGProvenanceKind @description("Where this row came from — always AUTH_PDF for the DLT source; PUBLIC_WEB_AUTH_PDF_MERGED after the syllabus extractor merges with the public ModuleDescriptor")
  source_url string @description("The authenticated index URL (e.g. https://exams.universityofgalway.ie/.../CT516-2023-AUT.pdf)")
  downloaded_at string @description("ISO-8601 timestamp when the PDF was written to local disk")
  content_hash string @description("SHA-256[:16] of the PDF — idempotency key for DLT merge")
  scraped_at string @description("ISO-8601 timestamp of the BAML extraction")
  confidence float @description("Overall extraction confidence 0.0–1.0 (VLM self-reported, validated by the deterministic eval)")
  @@stream.done
}

// =============================================================================
// Syllabus descriptor — superset of `university_extraction::ModuleDescriptor`
// =============================================================================

class UoGSyllabusDescriptor {
  module_code string @description("UoG module code, e.g. 'CT516'")
  module_title string @description("Module title, e.g. 'Deep Learning'")
  ects int @description("ECTS credit value (5 or 10 most common)")
  academic_year int @description("Academic year, e.g. 2025 for 2025-26")
  semester string? @description("Semester the module runs in")
  description string @description("2-4 sentence module description")
  learning_outcomes UoGLearningOutcome[] @description("3-7 learning outcome bullets, each tagged with a Bloom level and an LO code")
  assessment_summary string? @description("1-2 sentence assessment summary (e.g. '40% exam + 60% CA across 3 assignments')")
  prerequisites string[] @description("Module codes that are formal prerequisites")
  syllabus_pdf_url string? @description("URL of the syllabus PDF (authenticated) if downloaded, else null")
  source_kind UoGProvenanceKind @description("PUBLIC_WEB_AUTH_PDF_MERGED when both sources were merged")
  exam_paper_overlap_score float? @description("Cosine similarity (BGE-M3) between the syllabus LOs and the exam question embeddings, 0.0-1.0 — populated by the `uog_exam_los_map` asset")
  source_url string @description("Canonical URL of the source (public page or authenticated index)")
  scraped_at string @description("ISO-8601 timestamp of the extraction")
  confidence float @description("Overall extraction confidence 0.0–1.0")
  @@stream.done
}

class UoGLearningOutcome {
  lo_code string @description("Canonical LO code, e.g. 'CT516-LO1', 'CT516-LO2.1'")
  text string @description("The full learning outcome text")
  bloom_level UoGBloomLevel @description("Bloom level the LO targets")
  action_verbs string[] @description("Action verbs used (e.g. ['explain', 'implement', 'evaluate'])")
}

class UoGExamQuestionBloomTag {
  question_number string @description("Question number, e.g. 'Q1', 'Q2a', 'Q4(ii)'")
  bloom_level UoGBloomLevel @description("Bloom level the question targets")
  estimated_difficulty string @description("Estimated difficulty, one of 'easy', 'medium', 'hard'")
  // The thesis eval: did the Bloom tag survive the M.Sc. AI grader review?
  grader_agreement bool? @description("True if the human grader agreed with this tag (null if not yet graded)")
}

class UoGModuleCatalogueRow {
  module_code string @description("UoG module code")
  module_title string @description("Module title")
  school string @description("Owning school / department slug")
  ects int @description("ECTS credit value")
  nfq_level int? @description("NFQ level (6–10)")
  programme_codes string[] @description("Programmes this module belongs to")
  module_url string @description("Public catalogue URL")
  academic_year int @description("Latest academic year with a verified listing")
  scraped_at string @description("ISO-8601 timestamp")
  confidence float @description("Overall extraction confidence 0.0–1.0")
  @@stream.done
}

// =============================================================================
// Extraction functions
// =============================================================================

function ExtractUoGExamPaper(
  pdf_text: string,
  module_code: string,
  academic_year: int
) -> UoGExamPaper {  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting University of Galway (or Irish university) past exam paper
    data from PDF.

    Source: PDF text (or OCR'd text from a Vision Language Model) of a single exam paper.

    Module code: {{ module_code }}
    Academic year: {{ academic_year }} (e.g. 2023 for the 2023-24 session)

    Extract:
    - title: paper title (e.g. 'CT516 — Deep Learning — Autumn 2023')
    - paper_number: 1 for Paper 1, 2 for Paper 2, etc.; null if no multi-paper structure
    - duration_minutes: total duration the student gets to answer
    - total_marks: sum of all marks on the paper
    - questions[]: every question with number, marks, full text, and any sub-parts
      - each question should be a `ExamQuestionIsles` shape (number, marks, text, parts?, topic?, skill_type?)
      - topic should be the strand being assessed (e.g. 'Transformers', 'Backpropagation')
      - skill_type should be one of: knowledge / comprehension / application / analysis / synthesis / evaluation
    - instructions: free-form general instructions block
    - programme_code[]: which programme(s) the module belongs to (e.g. ['MSCAI'])
    - semester: e.g. 'Semester 1', 'Semester 2', 'Year-long'
    - sitting: AUTUMN (Oct–Nov) / SPRING (Apr–May) / SUMMER (resit) / WINTER (Jan) / AUTUMN_SUPPLEMENTARY
    - paper_format: WRITTEN_ONLINE / MCQ_BANK / PDF_UPLOAD / TAKE_HOME / OPEN_BOOK
      - infer from the question type and any preamble; most M.Sc. AI papers are PDF_UPLOAD
    - language: 'en' for almost every paper, 'ga' for Fiontar / Scoil na Gaeilge
    - nfq_level: NFQ level of the module (6 Higher Cert / 7 Ord BA / 8 Hons BA / 9 Masters / 10 PhD)
    - confidence: overall extraction confidence 0.0–1.0

    Special considerations:
    - Most M.Sc. AI module codes use the 'CT', 'MA', 'HI', 'ED', 'PS', 'SP', 'LW', 'BCT',
      'EC', 'MG', 'MK' prefixes — cross-reference with the UoG module registry.
    - Sub-parts (a, b, c, d) carry their own marks; the parent question marks = sum of sub-parts.
    - Preserve all mathematical notation verbatim — \\\\frac{}{}, \\\\sqrt{}, \\\\int_{}^{} etc.

    {{ ctx.output_format }}
  "#

  catch_all (err) {
    UoGExamPaper {
      module_code "{{ module_code }}"
      academic_year {{ academic_year }}
      total_marks 0
      questions []
      confidence 0.0
    }
  }
}

function ExtractUoGSyllabus(
  syllabus_pdf_text: string
) -> UoGSyllabusDescriptor {  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting University of Galway module syllabus data from PDF.

    Source: PDF text of a single module descriptor (the 'Module Outline' that UoG hands
    out to enrolled students, accessed from the authenticated module page).

    Extract:
    - module_code: e.g. 'CT516', 'MA335'
    - module_title: e.g. 'Deep Learning'
    - ects: 5 or 10 most common; 30 for the dissertation module
    - academic_year: 2025 for the 2025-26 descriptor
    - semester: 'Semester 1' / 'Semester 2' / 'Year-long'
    - description: 2-4 sentence module description (verbatim)
    - learning_outcomes[]: every bullet
      - lo_code: synthesise 'CT516-LO1', 'CT516-LO2' etc., in display order
      - text: the verbatim outcome text
      - bloom_level: REMEMBER / UNDERSTAND / APPLY / ANALYSE / EVALUATE / CREATE
      - action_verbs: ['explain', 'implement'] etc.
    - assessment_summary: 1-2 sentences
    - prerequisites: module codes that are formal prerequisites
    - syllabus_pdf_url: the URL this PDF was downloaded from
    - source_kind: always AUTH_PDF for a syllabus extractor
    - source_url: the canonical URL (same as syllabus_pdf_url)
    - confidence: overall extraction confidence 0.0–1.0

    UoG module descriptors follow a common template (Learning Outcomes → Assessment →
    Prerequisites → Recommended Reading). The `module_code` is the canonical identifier
    that ties back to the public `ModuleDescriptor` row.

    {{ ctx.output_format }}
  "#

  catch_all (err) {
    UoGSyllabusDescriptor {
      module_code "UNKNOWN"
      ects 0
      academic_year 0
      learning_outcomes []
      confidence 0.0
    }
  }
}

function MapUoGExamQuestionsToLOs(
  exam_paper_json: string,
  syllabus_los_json: string
) -> map<string, string[]> {  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an M.Sc. AI evaluator mapping exam questions to module learning outcomes.

    Given a `UoGExamPaper` JSON blob (with `questions[]`) and a list of `UoGLearningOutcome`
    rows (with `lo_code`, `text`, `bloom_level`), return a `map<string, string[]>` where
    the key is the LO code and the value is the ordered list of question numbers that
    primarily assess that LO.

    Rules:
    - A question can map to AT MOST 2 LOs (most map to 1).
    - A single LO can be mapped by multiple questions.
    - Only include mappings you are >= 60% confident in.
    - If a question is about general exam technique (e.g. "sign your name") or
      is a tutorial/admin question, do NOT map it to an LO.
    - Use the question's Bloom level to disambiguate LO matches (a REMEMBER question
      maps to a REMEMBER LO, not an APPLY LO).

    Exam paper:
    {{ exam_paper_json }}

    Learning outcomes:
    {{ syllabus_los_json }}

    Return a JSON object like:
    {
      "CT516-LO1": ["Q1a", "Q1b", "Q3"],
      "CT516-LO3": ["Q2", "Q4"],
      "CT516-LO5": ["Q4a", "Q4b"]
    }

    {{ ctx.output_format }}
  "#

  catch_all (err) {
    {}
  }
}

function ExtractUoGModuleCatalogueRow(
  catalogue_page_markdown: string,
  module_code: string
) -> UoGModuleCatalogueRow {  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting University of Galway module catalogue rows from the
    public module registry (no SSO required).

    Source: markdown from a single module page (e.g. https://www.universityofgalway.ie/.../ct516)
    OR a row from the public module listing (e.g. https://www.universityofgalway.ie/.../courses-and-programmes/...).

    Module code: {{ module_code }}

    Extract:
    - module_code: canonical module code, e.g. 'CT516'
    - module_title: e.g. 'Deep Learning'
    - school: e.g. 'computer-science', 'mathematical-science', 'education'
    - ects: 5 or 10 most common
    - nfq_level: 6..10
    - programme_codes[]: e.g. ['MSCAI', 'BScCS']
    - module_url: the canonical module page URL
    - academic_year: 2025 for the 2025-26 academic year
    - confidence: 0.0–1.0

    {{ ctx.output_format }}
  "#

  catch_all (err) {
    UoGModuleCatalogueRow {
      module_code "{{ module_code }}"
      ects 0
      scraped_at "1970-01-01T00:00:00Z"
    }
  }
}

// =============================================================================
// Tests
// =============================================================================

test ExtractUoGExamPaperTest {
  functions [ExtractUoGExamPaper]
  args {
    pdf_text #"
      CT516 — Deep Learning
      Autumn 2023
      University of Galway — School of Computer Science
      MSc in Artificial Intelligence (MSCAI)
      M.Chem. / M.Sc. — Semester 1
      Time allowed: 2 hours
      Total marks: 100

      Answer THREE of the following FIVE questions. All questions carry equal marks.

      Q1.
      (a) Derive the backpropagation algorithm for a feedforward neural
          network with one hidden layer, starting from the chain rule.
          [10 marks]
      (b) Explain how the vanishing gradient problem arises in deep
          networks, and describe two techniques (e.g. residual connections,
          batch normalisation) that mitigate it. [15 marks]

      Q2.
      Given a convolutional filter with weights
      w = [[1, 0, -1], [1, 0, -1], [1, 0, -1]]
      applied to a 5×5 input, compute the output feature map. Show your
      working. [25 marks]

      Q3.
      Implement in PyTorch a transformer encoder block with multi-head
      self-attention (4 heads, d_model=128). Discuss the role of layer
      normalisation. [25 marks]

      Q4.
      Compare and contrast stochastic gradient descent (SGD) with the
      Adam optimiser, citing at least two published papers. What is the
      role of the momentum term? [25 marks]

      Q5.
      Critically evaluate the claim that "scale is all you need" for
      modern large language models. Cite at least one paper from 2020–2024.
      [25 marks]
    "#
    module_code "CT516"
    academic_year 2023
  }
}

test MapUoGExamQuestionsToLOsTest {
  functions [MapUoGExamQuestionsToLOs]
  args {
    exam_paper_json #"
      {
        "module_code": "CT516",
        "questions": [
          {"number": "Q1a", "marks": 10, "text": "Derive backprop...", "topic": "Backprop", "skill_type": "application"},
          {"number": "Q1b", "marks": 15, "text": "Vanishing gradient mitigation...", "topic": "Backprop", "skill_type": "analysis"},
          {"number": "Q2",  "marks": 25, "text": "Conv arithmetic...", "topic": "CNNs", "skill_type": "application"},
          {"number": "Q3",  "marks": 25, "text": "Transformer encoder in PyTorch...", "topic": "Transformers", "skill_type": "synthesis"},
          {"number": "Q4",  "marks": 25, "text": "SGD vs Adam...", "topic": "Optimisers", "skill_type": "evaluation"},
          {"number": "Q5",  "marks": 25, "text": "Scale is all you need...", "topic": "LLMs", "skill_type": "evaluation"}
        ]
      }
    "#
    syllabus_los_json #"
      [
        {"lo_code": "CT516-LO1", "text": "Derive backprop and discuss vanishing gradients", "bloom_level": "APPLY"},
        {"lo_code": "CT516-LO2", "text": "Compute conv layer arithmetic", "bloom_level": "APPLY"},
        {"lo_code": "CT516-LO3", "text": "Implement a transformer encoder in PyTorch", "bloom_level": "CREATE"},
        {"lo_code": "CT516-LO4", "text": "Compare SGD and Adam", "bloom_level": "EVALUATE"},
        {"lo_code": "CT516-LO5", "text": "Critically evaluate the role of scale in modern LLMs", "bloom_level": "EVALUATE"}
      ]
    "#
  }
}
