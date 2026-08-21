// BAML Schema for Author Archive Extraction
//
// Structured extraction of three personal-archive document types:
//   1. Gemini Deep Research PDFs (agentic-research output)
//   2. University of Galway academic artefacts (assignments, placements, etc.)
//   3. Handwritten equations from OCR'd pages
//
// English-only for this change (per the user). All extractions route through
// the canonical LiteLLM gateway via the `extract_en` client alias.

enum GeminiDomain {
  LAW            @description("Legal / citizenship / justice topics")
  MEDICAL        @description("Healthcare / medical access / disability")
  POLITICS       @description("Political parties / elections / policy")
  TECHNOLOGY     @description("Tech industry / regulation / diplomacy")
  CULTURE        @description("Cultural identity / heritage / arts")
  OTHER          @description("None of the above")
  IDENTITY       @description("Personal / familial / identity documents")
  EDUCATION      @description("Education policy / academic / curriculum")
}

enum UoGArtifactKind {
  ASSIGNMENT         @description("Coursework assignment (B.Ed, PGCE, B.A., etc.)")
  EXAM               @description("Exam paper or revision material")
  LECTURE_NOTES      @description("Lecture notes or class handouts")
  ACTION_RESEARCH    @description("Action-research project (B.Ed, PGCE)")
  PLACEMENT          @description("School placement / internship portfolio")
  CODE_FILE          @description("Code file (software_development/)")
  SCANNED_PAGES      @description("Scanned PDF or Apple Pages file (handwriting candidate)")
  PRESENTATION       @description("PowerPoint / Keynote presentation")
  TRANSCRIPT         @description("Academic transcript or record")
  OTHER              @description("None of the above")
}

enum UoGStage {
  UNDERGRADUATE      @description("Undergraduate (B.A., B.Sc., etc.)")
  PGCE               @description("Professional Master of Education")
  MASTERS            @description("Taught or research Masters")
  PHD                @description("Doctoral research")
  PROFESSIONAL       @description("Professional development / CPD")
  UNKNOWN            @description("Stage cannot be inferred from the file")
}

enum UoGLanguage {
  EN                 @description("English (only language for this change)")
  GA                 @description("Irish (Gaeilge)")
  MIXED              @description("Bilingual English/Irish content")
  UNKNOWN            @description("Language cannot be inferred")
}

enum EquationConfidence {
  HIGH               @description("OCR + VLM agree, LaTeX is well-formed")
  MEDIUM             @description("One back-end available, LaTeX is plausible")
  LOW                @description("Best-effort LaTeX, may be incomplete")
  UNREADABLE         @description("OCR produced no usable signal")
}

// =============================================================================
// Cited URL
// =============================================================================

class CitedUrl {
  url string @description("The cited URL (https/http)")
  anchor_text string? @description("Anchor text from a markdown link, if any")
  source string @description("Where the URL was found: pymupdf_link, markdown_inline, first_page_header")
}

// =============================================================================
// Zotero Paper (leabharlann/zotero/)
// =============================================================================

enum PaperKind {
  ARXIV_PREPRINT     @description("Pre-print hosted on arXiv (or arXiv-only paper)")
  JOURNAL_ARTICLE    @description("Peer-reviewed journal article")
  CONFERENCE_PAPER   @description("Conference or workshop paper")
  THESIS             @description("MSc, MPhil, or PhD thesis")
  BOOK_CHAPTER       @description("A chapter within an edited book")
  BOOK               @description("An entire book")
  OTHER              @description("None of the above (blog post, technical report, etc.)")
}

class Author {
  name string @description("Full author name, e.g. 'Cian Hughes'")
  affiliation string? @description("Author affiliation, if discernible")
}

class ZoteroPaper {
  paper_kind PaperKind @description("What kind of academic artefact this is")
  arxiv_id string? @description("arXiv identifier, e.g. '2504.02890', or '2402' for pre-DOI arXiv IDs")
  doi string? @description("Digital Object Identifier, if known")
  title string @description("One-sentence paper title")
  authors Author[] @description("Ordered list of paper authors")
  year int? @description("Publication year, if discernible")
  abstract string? @description("Paper abstract, if present in the first page")
  venue string? @description("Journal name, conference name, or institution (for theses)")
  irish_relevant bool @description("True if the paper is about the Irish language, Celtic NLP, or Irish HTR/OCR")
  htr_relevant bool @description("True if the paper is about handwritten text recognition (HTR) or handwriting in general")
  confidence float @description("Overall extraction confidence 0.0-1.0")
}

// =============================================================================
// Gemini Deep Research Report
// =============================================================================

class GeminiDeepResearchReport {
  topic string @description("One-sentence topic of the report, e.g. 'cross-border medical malpractice'")
  domain GeminiDomain @description("High-level topical domain")
  summary string @description("2-3 sentence summary of the report's main thesis")
  key_findings string[] @description("3-7 bullet-point findings, each a single sentence")
  cited_urls CitedUrl[] @description("Inline citations extracted from the PDF")
  gemini_account string? @description("Gemini account label if known (e.g. 'cian_personal'), else null")
  research_date string? @description("Date the report was generated, ISO-8601 (YYYY-MM-DD) if discernible, else null")
  confidence float @description("Overall extraction confidence 0.0-1.0")
}

// =============================================================================
// University of Galway Artefact
// =============================================================================

class UniversityOfGalwayArtifact {
  artifact_kind UoGArtifactKind @description("What kind of academic artefact this is")
  course_code string? @description("Course code if extractable, e.g. 'CT511', 'GA101', 'ED305'")
  module_title string? @description("Module / paper title, e.g. 'History of Irish Education'")
  stage UoGStage @description("Programme stage")
  language UoGLanguage @description("Always 'en' for this change")
  key_topics string[] @description("3-7 topical tags")
  requires_handwriting_ocr bool @description("True if the artefact contains handwriting (handwritten notes, scanned equations, .pages files)")
  word_count int? @description("Approximate word count of the extracted text, if known")
  confidence float @description("Overall extraction confidence 0.0-1.0")
}

// =============================================================================
// Handwritten Equation
// =============================================================================

class HandwrittenEquation {
  latex string @description("LaTeX representation of the equation, e.g. '\\\\int_0^1 x^2 \\\\, dx'")
  verbatim string @description("Verbatim character-level transcription of the handwritten text")
  context string @description("Surrounding text (the sentence or paragraph the equation appears in)")
  confidence float @description("OCR + VLM agreement 0.0-1.0")
  equation_confidence EquationConfidence @description("Categorical confidence bucket")
}

// =============================================================================
// Functions
// =============================================================================

function ExtractGeminiReport(pdf_text: string, file_name: string) -> GeminiDeepResearchReport {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert at extracting author/creator metadata from an archival document.

    Source type: PDF text + filename

    Extract:
    - author_name: full name of the primary author/creator
    - author_role: their role/title at time of creation
    - organization: the affiliated organization (if any)
    - publication_year: ISO year of publication or creation
    - archive_collection: the canonical archive collection name
    - shelfmark: the canonical shelfmark / call number

    

    The author archive includes a mix of academics, politicians, and educators. Use the document content (not the filename) to determine role and organization.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

function ExtractUoGArtifact(pdf_text: string, file_name: string, file_type: string) -> UniversityOfGalwayArtifact {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert at extracting author/creator metadata from an archival document.

    Source type: PDF text + filename

    Extract:
    - author_name: full name of the primary author/creator
    - author_role: their role/title at time of creation
    - organization: the affiliated organization (if any)
    - publication_year: ISO year of publication or creation
    - archive_collection: the canonical archive collection name
    - shelfmark: the canonical shelfmark / call number

    

    The author archive includes a mix of academics, politicians, and educators. Use the document content (not the filename) to determine role and organization.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

function ExtractHandwrittenEquations(ocr_text: string, file_name: string) -> HandwrittenEquation[] {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert at extracting author/creator metadata from an archival document.

    Source type: PDF text + filename

    Extract:
    - author_name: full name of the primary author/creator
    - author_role: their role/title at time of creation
    - organization: the affiliated organization (if any)
    - publication_year: ISO year of publication or creation
    - archive_collection: the canonical archive collection name
    - shelfmark: the canonical shelfmark / call number

    

    The author archive includes a mix of academics, politicians, and educators. Use the document content (not the filename) to determine role and organization.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

function ExtractZoteroMetadata(pdf_text: string, file_name: string, arxiv_id: string?) -> ZoteroPaper {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert at extracting author/creator metadata from an archival document.

    Source type: PDF text + filename

    Extract:
    - author_name: full name of the primary author/creator
    - author_role: their role/title at time of creation
    - organization: the affiliated organization (if any)
    - publication_year: ISO year of publication or creation
    - archive_collection: the canonical archive collection name
    - shelfmark: the canonical shelfmark / call number

    

    The author archive includes a mix of academics, politicians, and educators. Use the document content (not the filename) to determine role and organization.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

// =============================================================================
// Tests
// =============================================================================

// test ExtractGeminiReportTest {
//   functions [ExtractGeminiReport]
//   args {
//     pdf_text #"
//       # Cross-border Medical Malpractice: A Comparative Study
// 
//       This report examines the legal recourse available to dual British-Irish
//       citizens who experience medical malpractice in either jurisdiction.
// 
//       Key findings:
//       1. The Common Travel Area provides limited reciprocal enforcement.
//       2. Statute of limitations varies by jurisdiction.
//       3. Expert witness requirements differ significantly.
//     "#
//     file_name "cross_border_medical_malpractice_and_data_breach.pdf"
//   }
// }

// test ExtractUoGArtifactTest {
//   functions [ExtractUoGArtifact]
//   args {
//     pdf_text #"
//       ED305 Assignment 2: A reflective account of a 4th-year B.Ed placement
//       at an urban DEIS school. Topics: lesson planning, classroom management,
//       inclusive education, assessment for learning.
//     "#
//     file_name "ed305_assignment_2.pdf"
//     file_type "pdf"
//   }
// }

// test ExtractHandwrittenEquationsTest {
//   functions [ExtractHandwrittenEquations]
//   args {
//     ocr_text #"
//       Q1. Compute the definite integral
//         \int_0^1 x^2 \, dx
//       using the Fundamental Theorem of Calculus.
//     "#
//     file_name "measurements.pages"
//   }
// }

// test ExtractZoteroMetadataTest {
//   functions [ExtractZoteroMetadata]
//   args {
//     pdf_text #"
//       gaHealth: An English-Irish Bilingual Corpus of Health
//       Records for Irish NLP
// 
//       Lankford, Mark and others
// 
//       Abstract: We present gaHealth, a bilingual (English-Irish) corpus of
//       de-identified health records, designed to support downstream NLP tasks
//       including named-entity recognition, translation, and clinical text
//       summarisation in the Irish language.
// 
//       1. Introduction
//       The Irish language is severely under-resourced in health NLP...
//     "#
//     file_name "Lankford et al. - 2024 - gaHealth An English-Irish Bilingual Corpus of Hea.pdf"
//     arxiv_id "2402.02890"
//   }
// }


// =============================================================================
// Author Archive v1: pre-research + condensation + UI identification
// =============================================================================
//
// Added in `author-archive-v1`. These functions drive the
// `official_media.research_sitemap`, `official_media.condensed_pages`, and
// `official_media.ui_elements` Dagster assets. They consume the raw output
// of the ScrapeStrategist (Firecrawl /agent pre-research, Crawl4AI bulk
// scrape, Stagehand observe() for visual grounding) and produce structured
// records that the marimo dashboards can render.
//
// All functions route through the canonical LiteLLM gateway. We deliberately
// avoid the BAML `firecrawl_agent` client (which would call the Firecrawl
// API directly) — Firecrawl's /agent is only used for the *raw* pre-research
// scrape (the BAML calls run after that, on the cached output).

// -----------------------------------------------------------------------------
// 1. PreResearchSite — wraps a Firecrawl /agent response into a typed map.
//    Used as a free fallback when the credit budget is exhausted (the router
//    then calls SummarizeSite on a Crawl4AI sitemap+sample instead).
// -----------------------------------------------------------------------------

class ResearchSiteMap {
  url string @description("The root URL of the site under research")
  goal string @description("The natural-language goal that drove the pre-research")
  sitemap_urls string[] @description("Up to 50 URLs discovered in the sitemap")
  primary_content_types string[] @description("2-5 content types present on the site, e.g. ['press_releases', 'case_decisions', 'policy_documents']")
  site_structure_summary string @description("2-3 sentence summary of the site's structure")
  recommended_strategy string @description("One of: 'crawl4ai-static' (default), 'firecrawl-agent' (heavy content), 'stagehand-interactive' (login wall, search, dashboard)")
  recommended_schema JsonSchema @description("A JSON schema describing the per-page extraction shape, suitable for Crawl4AI's LLM extraction")
  estimated_pages int @description("Approximate number of pages in the sitemap")
  estimated_credits int @description("Estimated Firecrawl credits if every page were scraped by Firecrawl (used for cost-vs-benefit analysis)")
  backend_used string? @description("Which backend ran the pre-research (firecrawl_mcp, crawl4ai_local, etc.) or null if no call was made")
  pre_researched_at string? @description("ISO-8601 timestamp of the pre-research call, or null")
  credits_spent int @description("Credits actually spent on this pre-research call (0 if free fallback used)")
  raw_response string? @description("Truncated raw response from the backend, for debugging")
  confidence float @description("Overall extraction confidence 0.0-1.0")
}

class JsonSchema {
  type string @description("JSON Schema type, typically 'object'")
  properties map<string, string> @description("Schema properties keyed by field name, with BAML-style types as values (e.g. 'string', 'string[]', 'int?')")
  required string[]? @description("List of required field names")
}

function PreResearchSite(
  url: string,
  goal: string,
  backend_payload: string,
  backend_name: string
) -> ResearchSiteMap {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert at extracting author/creator metadata from an archival document.

    Source type: PDF text + filename

    Extract:
    - author_name: full name of the primary author/creator
    - author_role: their role/title at time of creation
    - organization: the affiliated organization (if any)
    - publication_year: ISO year of publication or creation
    - archive_collection: the canonical archive collection name
    - shelfmark: the canonical shelfmark / call number

    

    The author archive includes a mix of academics, politicians, and educators. Use the document content (not the filename) to determine role and organization.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

// -----------------------------------------------------------------------------
// 2. CondenseToCriticalInfo — turn a full Crawl4AI/Firecrawl markdown into
//    the bytes we actually want to keep. The user said: "we want to know what
//    data we have and how it was sourced" — this function enforces that by
//    returning a 1-2 KB record with key facts, entities, and source links.
// -----------------------------------------------------------------------------

class ExtractedEntity {
  kind string @description("Entity type: 'person', 'org', 'date', 'place', 'case_ref', 'statute', 'policy_doc', 'amount'")
  value string @description("The entity's display value, e.g. '2024-01-15' or 'Crown Prosecution Service'")
  url string? @description("Optional source URL for the entity, e.g. the page it was found on")
}

class CondensedPage {
  url string @description("The URL this condensation is for")
  title string @description("The page title, as extracted from the markdown")
  one_sentence_summary string @description("One sentence describing what this page is about")
  key_facts string[] @description("3-7 atomic fact statements, each a single sentence")
  entities ExtractedEntity[] @description("0-10 named entities found on the page")
  ui_indicators UiIndicator[] @description("0-N UI indicators, filled in by IdentifyUiPatterns")
  bytes_in int @description("Number of bytes in the input markdown")
  bytes_out int @description("Number of bytes in the condensed output (typically 1-2% of bytes_in)")
  confidence float @description("Overall extraction confidence 0.0-1.0")
}

function CondenseToCriticalInfo(
  raw_markdown: string,
  goal: string,
  max_output_bytes: int
) -> CondensedPage {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert at extracting author/creator metadata from an archival document.

    Source type: PDF text + filename

    Extract:
    - author_name: full name of the primary author/creator
    - author_role: their role/title at time of creation
    - organization: the affiliated organization (if any)
    - publication_year: ISO year of publication or creation
    - archive_collection: the canonical archive collection name
    - shelfmark: the canonical shelfmark / call number

    

    The author archive includes a mix of academics, politicians, and educators. Use the document content (not the filename) to determine role and organization.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

// -----------------------------------------------------------------------------
// 3. IdentifyUiPatterns — scan condensed content for UI signals. Used to
//    decide whether to take a screenshot + run visual grounding.
// -----------------------------------------------------------------------------

enum UiType {
  SEARCH_BOX          @description("A text search input that the user can type into")
  FORM                @description("A multi-field form for login, application, contact, etc.")
  DASHBOARD           @description("A dashboard with charts/tables that the user can interact with")
  MAP                 @description("An interactive map (Leaflet, Google Maps, etc.)")
  LOGIN_WALL          @description("A login wall that blocks content until authenticated")
  FILE_DOWNLOAD       @description("A link to download a PDF/DOCX/CSV file")
  CAROUSEL            @description("A horizontal/vertical carousel of cards or images")
  TIMELINE            @description("A timeline visualisation of events")
  OTHER               @description("Any other interactive element")
  NONE                @description("No UI detected on this page")
}

class UiIndicator {
  has_ui bool @description("True if this page has at least one interactive element worth identifying")
  ui_type UiType @description("The dominant UI category, or NONE if has_ui is false")
  element_label string? @description("Natural-language description of the element, e.g. 'the case search input field'")
  grounding_query string? @description("A natural-language query that VisualGroundingFromScreenshot can use to find the element on a screenshot")
  confidence float @description("Your confidence that the UI type is correct, 0.0-1.0")
}

function IdentifyUiPatterns(
  raw_markdown: string,
  goal: string
) -> UiIndicator[] {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert at extracting author/creator metadata from an archival document.

    Source type: PDF text + filename

    Extract:
    - author_name: full name of the primary author/creator
    - author_role: their role/title at time of creation
    - organization: the affiliated organization (if any)
    - publication_year: ISO year of publication or creation
    - archive_collection: the canonical archive collection name
    - shelfmark: the canonical shelfmark / call number

    

    The author archive includes a mix of academics, politicians, and educators. Use the document content (not the filename) to determine role and organization.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

// -----------------------------------------------------------------------------
// 4. VisualGroundingFromScreenshot — find an element on a screenshot.
//    Currently invoked by the Stagehand or Browserbase backend (free paths),
//    or by Z.AI vision (paid). This BAML function normalises the response
//    shape for storage in the ui_elements table.
// -----------------------------------------------------------------------------

class BoundingBox {
  x_min float @description("Left edge in normalised 0-1 coordinates")
  y_min float @description("Top edge in normalised 0-1 coordinates")
  x_max float @description("Right edge in normalised 0-1 coordinates")
  y_max float @description("Bottom edge in normalised 0-1 coordinates")
}

class GroundedElement {
  label string @description("Short label for the element, e.g. 'Search box'")
  bbox BoundingBox @description("Normalised bounding box in 0-1 image coordinates")
  action string @description("What the user would do with this element: 'click', 'type', 'select', 'hover', 'drag', 'submit'")
  selector string? @description("Best-guess CSS selector, if derivable from the screenshot context")
  confidence float @description("Your confidence in this grounding, 0.0-1.0")
}

function VisualGroundingFromScreenshot(
  screenshot_description: string,
  natural_language_query: string
) -> GroundedElement {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert at extracting author/creator metadata from an archival document.

    Source type: PDF text + filename

    Extract:
    - author_name: full name of the primary author/creator
    - author_role: their role/title at time of creation
    - organization: the affiliated organization (if any)
    - publication_year: ISO year of publication or creation
    - archive_collection: the canonical archive collection name
    - shelfmark: the canonical shelfmark / call number

    

    The author archive includes a mix of academics, politicians, and educators. Use the document content (not the filename) to determine role and organization.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

// -----------------------------------------------------------------------------
// 5. SummarizeSite — free-fallback for PreResearchSite when the credit budget
//    is exhausted. Called on a Crawl4AI sitemap + sample page (both free).
// -----------------------------------------------------------------------------

function SummarizeSite(
  url: string,
  goal: string,
  sitemap_urls: string[],
  sample_markdown: string
) -> ResearchSiteMap {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert at extracting author/creator metadata from an archival document.

    Source type: PDF text + filename

    Extract:
    - author_name: full name of the primary author/creator
    - author_role: their role/title at time of creation
    - organization: the affiliated organization (if any)
    - publication_year: ISO year of publication or creation
    - archive_collection: the canonical archive collection name
    - shelfmark: the canonical shelfmark / call number

    

    The author archive includes a mix of academics, politicians, and educators. Use the document content (not the filename) to determine role and organization.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

// -----------------------------------------------------------------------------
// 6. ClassifySiteCivic — classify a pre-researched source into one of the 10
//    official_media categories. The Dagster asset uses this to route the
//    source to the right marimo tab.
// -----------------------------------------------------------------------------

enum AuthorArchiveCivicCategory {
  INTELLIGENCE         @description("MI5, MI6, GCHQ, HMGCC, etc.")
  UNIVERSITY           @description("Universities and constituent colleges")
  CELTIC_COLLEGE       @description("Coláiste Feirste, Sabhal Mòr Ostaig, etc.")
  SCHOOL               @description("Primary/secondary schools (Irish-medium etc.)")
  LANGUAGE_PROJECT     @description("Turas Belfast, Foras na Gaeilge, etc.")
  PARTY                @description("Political parties and party wings")
  POLICE               @description("Police forces (PSNI, Gardaí, etc.)")
  DEFENCE              @description("Royal Navy, Irish Defence Forces, etc.")
  NATIONAL_INFO        @description("Met Office, BBC, etc.")
  JURISDICTION         @description("CPS, courts.ie, etc.")
  OTHER                @description("None of the above")
}

function ClassifySiteCivic(
  url: string,
  site_structure_summary: string,
  primary_content_types: string[]
) -> AuthorArchiveCivicCategory {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert at extracting author/creator metadata from an archival document.

    Source type: PDF text + filename

    Extract:
    - author_name: full name of the primary author/creator
    - author_role: their role/title at time of creation
    - organization: the affiliated organization (if any)
    - publication_year: ISO year of publication or creation
    - archive_collection: the canonical archive collection name
    - shelfmark: the canonical shelfmark / call number

    

    The author archive includes a mix of academics, politicians, and educators. Use the document content (not the filename) to determine role and organization.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

// =============================================================================
// Tests for the new functions
// =============================================================================

// test PreResearchSiteTest {
//   functions [PreResearchSite]
//   args {
//     url "https://www.cps.gov.uk"
//     goal "Identify all press releases, prosecution guidance, and case decision databases published 2020-2026."
//     backend_payload #"
//       Sitemap (3,847 URLs):
//         https://www.cps.gov.uk/
//         https://www.cps.gov.uk/legal-guidance
//         https://www.cps.gov.uk/legal-guidance/prosecution-guidance
//         https://www.cps.gov.uk/legal-guidance/legal-guidance-corporate-manslaughter
//         https://www.cps.gov.uk/news
//         https://www.cps.gov.uk/news/press-releases
//         https://www.cps.gov.uk/legal-guidance/case-decisions
//         https://www.cps.gov.uk/legal-guidance/case-decisions/r-v-...
//         https://www.cps.gov.uk/about
//       Primary content types: prosecution_guidance, case_decisions, press_releases, statistics
//       Estimated pages: 3,847
//     "#
//     backend_name "firecrawl_mcp"
//   }
// }

// test CondenseToCriticalInfoTest {
//   functions [CondenseToCriticalInfo]
//   args {
//     raw_markdown #"
//       # CPS publishes new guidance on prosecuting sexual offences
// 
//       The Crown Prosecution Service has today (15 January 2024) published
//       new legal guidance on prosecuting sexual offences. The guidance
//       updates the previous 2017 edition and reflects the latest case law
//       from the Court of Appeal.
// 
//       Key changes include:
//       - New section on digital evidence handling
//       - Updated thresholds for charging decisions
//       - Revised guidance on consent and capacity
// 
//       Director of Public Prosecutions Max Hill KC said: "This guidance
//       represents our most comprehensive review in seven years. It is the
//       product of extensive consultation with victims' groups, defence
//       practitioners, and the judiciary."
// 
//       The full guidance is available on the CPS website at
//       https://www.cps.gov.uk/legal-guidance/prosecuting-sexual-offences.
// 
//       For media enquiries, contact the CPS press office on 020 3357 0897.
//     "#
//     goal "Extract press release summary and key changes"
//     max_output_bytes 2048
//   }
// }

// test IdentifyUiPatternsTest {
//   functions [IdentifyUiPatterns]
//   args {
//     raw_markdown #"
//       # CPS Case Decisions
// 
//       Search the CPS case decisions database:
// 
//       [search box: "Enter case name, citation, or keyword"]
// 
//       Filters:
//       - Date range: [from] [to]
//       - Charge type: [dropdown]
//       - Court: [dropdown]
// 
//       Results (showing 1-10 of 4,521):
//     "#
//     goal "Find the case search input box for the research workflow"
//   }
// }

// test VisualGroundingFromScreenshotTest {
//   functions [VisualGroundingFromScreenshot]
//   args {
//     screenshot_description "Page with a header containing the CPS logo, a horizontal navigation bar, a search box labelled 'Search CPS', a sidebar with topic links (Legal guidance, Case decisions, News), and a main content area showing 'Press releases'."
//     natural_language_query "the case search input box at the top of the page"
//   }
// }

// test SummarizeSiteTest {
//   functions [SummarizeSite]
//   args {
//     url "https://www.cps.gov.uk"
//     goal "Extract press releases and legal guidance"
//     sitemap_urls [
//       "https://www.cps.gov.uk/",
//       "https://www.cps.gov.uk/news",
//       "https://www.cps.gov.uk/legal-guidance",
//       "https://www.cps.gov.uk/about"
//     ]
//     sample_markdown #"
//       # Crown Prosecution Service
// 
//       The Crown Prosecution Service is the principal public prosecution
//       service for England and Wales. We prosecute criminal cases investigated
//       by the police and other investigative bodies.
// 
//       Our work includes:
//       - Deciding whether to charge suspects
//       - Preparing cases for court
//       - Conducting prosecutions in magistrates' and crown courts
//     "#
//   }
// }

// test ClassifySiteCivicTest {
//   functions [ClassifySiteCivic]
//   args {
//     url "https://www.cps.gov.uk"
//     site_structure_summary "Crown Prosecution Service — the principal public prosecution service for England and Wales. Site hosts legal guidance, case decisions, press releases, and statistics on prosecution outcomes."
//     primary_content_types ["press_releases", "legal_guidance", "case_decisions", "statistics"]
//   }
// }
