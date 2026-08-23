// BAML Schema for UoG Official Documents + NUI Federation + Students' Union
//
// Companion to `uog_exam_paper_extraction.baml` (the prior change's
// authenticated exam papers schema). Together they form the
// M.Sc. AI thesis canonical extraction layer for the UoG / NUI /
// Students' Union universe.
//
// This file ADDS the public-side classes + enums + functions:
//   - UoGOfficialDocumentType { ACADEMIC_REGISTER, EXAM_BOARD_MINUTES, ... }
//   - UoGNUIMemberKind { CONSTITUENT_UNIVERSITY, HISTORICAL_MEMBER, ... }
//   - UoGSUResourceKind { POLICY, HANDBOOK, ELECTION_MANIFESTO, ... }
//   - UoGOfficialDocument
//   - UoGNUIMemberDescriptor
//   - UoGStudentsUnionDocument
//   - UoGNUISyllabusDescriptor (cross-NUI module equivalence)
//   - ExtractUoGOfficialDocument(prompt)
//   - ExtractUoGNUIMemberPage(prompt)
//   - ExtractUoGStudentsUnionDocument(prompt)
//   - ExtractUniversityOfficialDocUniversal(prompt) — the generalised
//     extraction for any British Isles university
//
// All routes through the canonical `ExtractEn` LiteLLM client.
// Reference: openspec/changes/2026-08-23-uog-official-docs-and-nui-superset-v1/

// =============================================================================
// Enums
// =============================================================================

enum UoGOfficialDocumentType {
  ACADEMIC_REGISTER        @description("The university's academic register / academic calendar / handbook for the year (e.g. 'Academic Register 2025-26')")
  EXAM_BOARD_MINUTES       @description("Minutes of the university's exams board / academic standards committee")
  STATUTES                 @description("The university's charter + statutes + academic regulations")
  CALENDAR                 @description("The university's term dates / key-dates calendar (start/end of each semester)")
  KEY_DATES_CIRCULAR       @description("Circular letters to staff / schools with key dates or policy updates")
  TIMETABLE                @description("Programme or school timetables for the academic year")
  SCHOOL_REGISTER          @description("The official register of schools, faculties, and departments")
  FACULTY_MINUTES          @description("Faculty board minutes")
  RESEARCH_ETHICS          @description("Research ethics committee minutes / policies")
  OTHER                    @description("Other official documents not listed above")
}

enum UoGNUIMemberKind {
  CONSTITUENT_UNIVERSITY   @description("A current NUI constituent university (UCD, UCC, MU, UoG)")
  HISTORICAL_MEMBER        @description("A historical NUI member (QUB pre-1908, RCPI, RCSI pre-1989, etc.)")
  AFFILIATED_COLLEGE       @description("An NUI-recognised college (e.g. NUI's recognised international colleges)")
  UNKNOWN                  @description("Membership kind is not inferrable from the page")
}

enum UoGSUResourceKind {
  POLICY                   @description("The SU constitution + standing orders + policy handbook")
  HANDBOOK                 @description("The class-rep handbook / sabbatical officer handbook / incoming-officer handbook")
  ELECTION_MANIFESTO       @description("Manifestos from sabbatical elections (President, Education Officer, Welfare Officer, etc.)")
  REFERENDUM               @description("A referendum submitted to students (text of the motion + argument for/against)")
  WELFARE_GUIDE            @description("Student welfare guides (mental health, sexual health, hardship funds)")
  ANNUAL_REPORT            @description("SU annual report / audited accounts")
  OTHER                    @description("Other SU documents not listed above")
}

// =============================================================================
// UoGOfficialDocument
// =============================================================================

class UoGOfficialDocument {
  // Identifiers
  document_id string @description("Stable identifier for the document, e.g. 'uog-academic-register-2025-26'")
  document_type UoGOfficialDocumentType @description("Type of official document")
  document_kind string? @description("A finer-grained kind, e.g. 'academic_register' or 'exam_board_minutes_2024_06'")

  // Body
  title string @description("Document title")
  body string @description("Full body text (markdown or plain text). If very long, truncate to the first 5,000 chars.")
  summary string? @description("1-3 sentence executive summary")
  effective_date string? @description("Date the document takes effect, ISO-8601")
  published_date string? @description("Date the document was published, ISO-8601")
  version string? @description("Version number or revision label")

  // Context
  school_slug string? @description("The owning school / department slug (e.g. 'computer-science'), null if university-wide")
  programme_codes string[] @description("Related programme codes if applicable (e.g. ['MSCAI'])")
  nfqs string[] @description("NFQ levels this document is relevant to (e.g. ['9'] for NFQ Level 9 Masters)")
  tags string[] @description("Free-form keywords (e.g. ['graduation', 'cap', 'dean_honours'])")

  // Source
  source_url string @description("The canonical URL this document was scraped from")
  source_kind string @description("One of: 'PUBLIC_WEB' (no SSO) — used by the official docs; 'AUTH_PDF' (SSO) for sensitive boards; 'MERGED' for the public+auth combination")
  scraped_at string @description("ISO-8601 timestamp of the scrape")
  content_hash string @description("SHA-256[:16] of the document — idempotency key")
  confidence float @description("Overall extraction confidence 0.0-1.0")
  @@stream.done
}

// =============================================================================
// UoGNUIMemberDescriptor
// =============================================================================

class UoGNUIMemberDescriptor {
  // Identifiers
  member_id string @description("Kebab-case member id, e.g. 'ie-nui-ucd', 'ie-nui-qub-historical', 'ie-nui-ucc'")
  member_name string @description("Full name, e.g. 'University College Dublin', 'Queen's University Belfast (pre-1908 NUI)'")

  // NUI-specific
  member_kind UoGNUIMemberKind @description("CONSTITUENT_UNIVERSITY / HISTORICAL_MEMBER / AFFILIATED_COLLEGE")
  nfq_min int? @description("Lowest NFQ level the member awards (typically 6 for constituent universities)")
  nfq_max int? @description("Highest NFQ level (always 10)")
  joined_nui_year int? @description("Year joined NUI (e.g. 1908 for UoG/UCD/UCC; 1850 for QUB pre-1908)")
  left_nui_year int? @description("Year left NUI (e.g. 1908 for QUB; null if still a constituent)")

  // Public profile
  home_url string? @description("Canonical home URL (e.g. 'https://www.ucd.ie')")
  wikipedia_title string? @description("Wikipedia article title (used for cross-referencing)")
  registrar_email string? @description("The university's registrar / admissions email")
  ig_username string? @description("The university's instagram handle, if known")

  // Source
  source_url string @description("The canonical NUI page URL (e.g. 'https://www.nui.ie/about/members')")
  scraped_at string @description("ISO-8601 timestamp")
  confidence float @description("Overall extraction confidence 0.0-1.0")
  @@stream.done
}

// =============================================================================
// UoGStudentsUnionDocument
// =============================================================================

class UoGStudentsUnionDocument {
  document_id string @description("Stable identifier, e.g. 'uog-su-constitution-2024', 'uog-su-welfare-w2024'")
  resource_kind UoGSUResourceKind @description("POLICY / HANDBOOK / ELECTION_MANIFESTO / REFERENDUM / WELFARE_GUIDE / ANNUAL_REPORT / OTHER")
  title string @description("Document title")
  body string @description("Full body text (markdown or plain text). Cap at 5,000 chars in the extraction.")
  summary string? @description("1-3 sentence summary, esp. for the SU constitution or the latest welfare guide")
  effective_year int? @description("Academic year this document applies to (e.g. 2024 for 2024-25)")
  published_date string? @description("Date the document was published")
  tags string[] @description("Free-form keywords")

  // SU-specific
  elected_officer string? @description("If this is an election manifesto, the name of the candidate")
  officer_role string? @description("If this is an election manifesto, the role (President, Education Officer, Welfare Officer)")
  is_constitution bool @description("True if this is the SU constitution (the canonical governance document)")

  // Source
  source_url string @description("The canonical SU page URL")
  source_kind string @description("Always 'PUBLIC_WEB' for the SU")
  scraped_at string @description("ISO-8601 timestamp")
  confidence float @description("Overall extraction confidence 0.0-1.0")
  @@stream.done
}

// =============================================================================
// UoGNUISyllabusDescriptor (cross-NUI module equivalence)
// =============================================================================

class UoGNUISyllabusDescriptor {
  member_id string @description("The NUI member id, e.g. 'ie-nui-ucd'")
  module_code string @description("Module code at that member, e.g. 'CS-UCD-403'")
  module_title string @description("Module title")
  description string @description("2-4 sentence description")
  ects int @description("ECTS credit value")
  nfq_level int? @description("NFQ level of the module (6..10)")
  equivalent_module_codes string[] @description("Equivalent module codes at OTHER NUI members (e.g. ['CT516','MAI-721'])")
  source_url string @description("The canonical module page at the member's home website")
  scraped_at string @description("ISO-8601 timestamp")
  confidence float @description("0.0-1.0")
  @@stream.done
}

// =============================================================================
// Functions
// =============================================================================

function ExtractUoGOfficialDocument(
  prompt: string,
  source_url: string
) -> UoGOfficialDocument {  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting University of Galway (or Irish university)
    official-document data from rendered HTML / PDF text.

    Source: {{ source_url }}

    Document body (markdown or plain text):
    {{ prompt }}

    Extract every field described in the UoGOfficialDocument shape. Use
    UoGOfficialDocumentType, NOT free-form strings.

    The 10 most common document types at UoG are: ACADEMIC_REGISTER,
    EXAM_BOARD_MINUTES, STATUTES, CALENDAR, KEY_DATES_CIRCULAR,
    TIMETABLE, SCHOOL_REGISTER, FACULTY_MINUTES, RESEARCH_ETHICS, OTHER.

    Special considerations:
    - Academic Register / Calendar: extract every key date as a tag.
    - Exam Board Minutes: the `summary` field should be a 1-sentence
      summary of the most important decision in the minutes.
    - Faculty Minutes: tag with the faculty slug (e.g. 'science-engineering').
    - Preserve Irish-language titles verbatim (e.g. 'Clár Acadúil 2025-26').

    {{ ctx.output_format }}
  #

  catch_all (err) {
    UoGOfficialDocument {
      document_id "UNKNOWN"
      document_type OTHER
      title ""
      body ""
      source_url "{{ source_url }}"
      source_kind "PUBLIC_WEB"
      scraped_at "1970-01-01T00:00:00Z"
      content_hash ""
      confidence 0.0
    }
  }
}

function ExtractUoGNUIMemberPage(
  prompt: string,
  source_url: string
) -> UoGNUIMemberDescriptor {  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting National University of Ireland (NUI)
    member-descriptor data from a member-university page.

    Source: {{ source_url }}

    Page body:
    {{ prompt }}

    Extract:
    - member_id: kebab-case, e.g. 'ie-nui-ucd'
    - member_name: full institutional name (historical if applicable)
    - member_kind: CONSTITUENT_UNIVERSITY / HISTORICAL_MEMBER / AFFILIATED_COLLEGE
    - nfq_min + nfq_max: 6..10
    - joined_nui_year, left_nui_year: integers or null
    - home_url, wikipedia_title, registrar_email, ig_username
    - source_url

    The 4 current NUI constituents are: UCD, UCC, MU, UoG.
    Historical members include: QUB (pre-1908), the 3 Queen's Colleges
    before the Royal University of Ireland merger.

    {{ ctx.output_format }}
  #

  catch_all (err) {
    UoGNUIMemberDescriptor {
      member_id "UNKNOWN"
      member_name ""
      member_kind UNKNOWN
      source_url "{{ source_url }}"
      scraped_at "1970-01-01T00:00:00Z"
      confidence 0.0
    }
  }
}

function ExtractUoGStudentsUnionDocument(
  prompt: string,
  source_url: string
) -> UoGStudentsUnionDocument {  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting University of Galway Students' Union
    (Students' Union / SU) document data from rendered HTML.

    Source: {{ source_url }}

    Page body:
    {{ prompt }}

    Extract:
    - document_id, resource_kind (POLICY / HANDBOOK / ELECTION_MANIFESTO /
      REFERENDUM / WELFARE_GUIDE / ANNUAL_REPORT / OTHER)
    - title, body, summary
    - effective_year (academic year, e.g. 2024 for 2024-25)
    - elected_officer, officer_role if it's a manifesto
    - is_constitution: TRUE if this is the SU Constitution
    - tags

    If the source is an election manifesto, the candidate's name should be
    in the `elected_officer` field and the role in `officer_role`. If unsure,
    leave them null.

    {{ ctx.output_format }}
  #

  catch_all (err) {
    UoGStudentsUnionDocument {
      document_id "UNKNOWN"
      resource_kind OTHER
      title ""
      body ""
      source_url "{{ source_url }}"
      source_kind "PUBLIC_WEB"
      scraped_at "1970-01-01T00:00:00Z"
      confidence 0.0
    }
  }
}

function ExtractUniversityOfficialDocUniversal(
  prompt: string,
  institution_id: string,
  source_url: string
) -> UoGOfficialDocument {  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting official-document data from the website of
    "{{ institution_id }}". Works for any British Isles university.

    Source: {{ source_url }}

    Page body:
    {{ prompt }}

    Extract every field described in the UoGOfficialDocument shape. Use
    UoGOfficialDocumentType.

    Differences per institution:
    - UoG uses 'universityofgalway.ie', UCD uses 'ucd.ie', etc.
    - Scottish universities don't have NFQ levels — use the SCQF level
      (1..12) instead, and the `nfqs` field stores the SCQF level as a string.
    - Cambridge / Oxford: use 'university of cambridge' / 'university of oxford'
      idiomatic conventions.

    {{ ctx.output_format }}
  #

  catch_all (err) {
    UoGOfficialDocument {
      document_id "UNKNOWN"
      document_type OTHER
      title ""
      body ""
      source_url "{{ source_url }}"
      source_kind "PUBLIC_WEB"
      scraped_at "1970-01-01T00:00:00Z"
      content_hash ""
      confidence 0.0
    }
  }
}

// =============================================================================
// Tests
// =============================================================================

test ExtractUoGOfficialDocumentTest {
  functions [ExtractUoGOfficialDocument]
  args {
    prompt #"
      # University of Galway — Academic Register 2025-26

      The Academic Year runs from 1 September 2025 to 31 August 2026.
      Semester 1: 8 September 2025 – 12 December 2025.
      Semester 2: 12 January 2026 – 24 April 2026.

      School of Computer Science:
      - Head of School: Dr. Jane Smith
      - Programmes: B.Sc. CS, M.Sc. AI, M.Sc. CS

      ### Statutes, Chapter 4 — Academic Regulations
      1. Every candidate for a degree must be matriculated.
      2. A candidate who fails any module three times is debarred.
    "#
    source_url "https://www.universityofgalway.ie/academic-register/2025-26.pdf"
  }
}

test ExtractUoGNUIMemberPageTest {
  functions [ExtractUoGNUIMemberPage]
  args {
    prompt #"
      University College Dublin (UCD) is one of the 4 current constituent
      universities of the National University of Ireland. Founded 1854,
      joined the NUI in 1908. UCD awards NFQ Level 6 through NFQ Level 10.
      Home: https://www.ucd.ie
    "#
    source_url "https://www.nui.ie/about/members/ucd"
  }
}

test ExtractUoGStudentsUnionDocumentTest {
  functions [ExtractUoGStudentsUnionDocument]
  args {
    prompt #"
      UoG Students' Union Constitution (Revised 2024)
      
      The Students' Union represents every registered student of the
      University of Galway. The sabbatical officer team includes:
      President, Vice-President / Education Officer, Vice-President /
      Welfare Officer, Vice-President / Welfare Officer, and 4 part-time
      officers.
    "#
    source_url "https://su.universityofgalway.ie/constitution-2024"
  }
}
