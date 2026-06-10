// =============================================================================
// BAML context: tertiary.baml
// Stage-specific system prompt + BAML client defaults for the Tertiary
// (CAO + QQI-FET + Apprenticeship + NUI/HEI matriculation) extraction pipeline.
// =============================================================================

function ExtractCAOCourseListFromUrl(page_url: string, year: int) -> CAOCourse[] {
  client "litellm/gemini-2.0-flash"
  prompt #"
    You are an expert Irish CAO course directory analyst working for
    Cianfhoghlaim Oideachais (the bilingual agentic platform).

    Source: {{ page_url }}
    Year: {{ year }}

    CAO course codes are 2-3 characters: UCD=DN*, UCG=GY*, UCC=CK*, UL=LM*,
    MU=MH*, TCD=TR*, DCU=DC*, ATU=GA*/LY*/SG*/AL*, TUS=LC*/TL*, SETU=WD*/CW*,
    MTU=CR*/MT*, RCSI=RC*, MIC=MI*.

    The 10 NFQ levels (1-10) are defined per Irish National Framework of
    Qualifications. Typical CAO courses are NFQ_7 (Level 7 Ordinary Bachelor)
    or NFQ_8 (Level 8 Honours Bachelor).

    Always extract BOTH English and Irish versions of the title.

    Return CAOCourse[] as {{ ctx.output_format }}.
  "#
}

function ExtractMatriculationRulesFromUrl(page_url: string, institution: string) -> MatriculationRequirement[] {
  client "litellm/gemini-2.0-flash"
  prompt #"
    You are an expert Irish matriculation requirements analyst working for
    Cianfhoghlaim Oideachais.

    Source: {{ page_url }}
    Institution: {{ institution }}

    The NUI standard matriculation rules are:
      - 3 H5s (Higher level) including English, Irish, Mathematics
      - 4 O6/H7s (Ordinary or Higher level) including English, Irish, Mathematics
      - Specific subject + grade requirements for certain courses:
        H4 in Chemistry for Medicine
        H4 in a Modern Continental Language for Modern Languages
        H4 in Physics for Engineering
      - For non-NUI (TCD, DCU, IoTs), different rules apply

    Always capture the institution, pathway, subject, minimum_grade (H4, O6, etc.),
    and any notes (e.g., "required for Modern Languages", "lab science required for
    Medicine").

    Return MatriculationRequirement[] as {{ ctx.output_format }}.
  "#
}

function AuditMatriculationStdLib(
  institution: string,
  applicant_grades: map<string, string>
) -> MatriculationAudit {
  client "litellm/anthropic/claude-sonnet-4-20250514"
  prompt #"
    You are an expert Irish matriculation auditor working for
    Cianfhoghlaim Oideachais.

    INSTITUTION: {{ institution }}
    APPLICANT GRADES: {{ applicant_grades }}

    Check the applicant's LC grades against the matriculation rules for the
    given institution. Capture failed requirements and near-misses (one
    grade short). Produce a bilingual summary explaining the result.

    CAO points table (for context):
      H1: 100, H2: 88, H3: 77, H4: 66, H5: 56, H6: 46, H7: 37, H8: 0
      O1: 56, O2: 46, O3: 37, O4: 28, O5: 20, O6: 12, O7: 0, O8: 0
      Bonus: H6 or higher in Higher Level Mathematics awards +25 points

    Return MatriculationAudit as {{ ctx.output_format }}.
  "#
}
