// =============================================================================
// BAML context: senior_cycle.baml
// Stage-specific system prompt + BAML client defaults for the Senior Cycle
// (Leaving Certificate) extraction pipeline.
// =============================================================================

function ExtractSeniorCycleSpecFromUrl(
  source_url: string,
  subject: LeavingCertSubject
) -> SubjectRubric {
  client Gemini2FlashAlias
  prompt #"
    You are an expert Irish Senior Cycle (Leaving Certificate) curriculum
    analyst working for Cianfhoghlaim Oideachais (the bilingual agentic
    platform).

    Source: {{ source_url }}
    Subject: {{ subject }}

    The 50+ Leaving Certificate subjects fall into 7 families:
      - Sciences (Maths, Physics, Chemistry, Biology, Ag Science, Applied Maths,
        Computer Science)
      - Languages (English, Gaeilge, French, German, Spanish, Italian, Japanese,
        Russian, Arabic, Mandarin, Latin, Greek, Classical Studies)
      - Business (Business, Accounting, Economics, LCVP)
      - Humanities (History, Geography, Philosophy, Politics & Society, Religious
        Education, Art, Music)
      - Practical (Construction, Engineering, Technology, DCG, PE)
      - LCA (Leaving Certificate Applied — 27 modules)

    The 10 RubricStyle values are:
      PCLM, SRP, EQUATION_STEPS, KEYWORD_MATCH_DIAGRAM,
      COMPREHENSION_EXPRESSION, SECTION_B_KEYWORD, DIAGRAM_SKETCH_STEPS,
      BALANCED_EQUATION_STATE_SYMBOLS, DEFINITION_UNIT_FORMULA,
      RUBRIC_PCLM_IRISH

    The CAO points table is:
      H1: 100, H2: 88, H3: 77, H4: 66, H5: 56, H6: 46, H7: 37, H8: 0
      O1: 56, O2: 46, O3: 37, O4: 28, O5: 20, O6: 12, O7: 0, O8: 0
      Bonus: H6 or higher in Higher Level Mathematics awards +25 points

    Always extract BOTH English and Irish versions of every field.

    Return the structured SubjectRubric as {{ ctx.output_format }}.
  "#
}

function ScoreEssayAgainstRubricStdLib(
  essay: string,
  subject: LeavingCertSubject
) -> RubricScore {
  client Claude
  prompt #"
    You are an expert Leaving Certificate assessor for {{ subject }}.

    Score the student's essay against the appropriate rubric style:
      - English: PCLM (Purpose, Coherence, Language, Mechanics)
      - Gaeilge: Cumarsáid · Léamhthuiscint · Litríocht · Gramadach
      - History / Geography: SRP (Significant Relevant Points, 2 marks each)
      - Mathematics / Physics: step-by-step equation solving
      - Biology: mandatory keywords (10+) · experiment steps · diagram labels
      - Chemistry: balanced equations · state symbols · calculation steps
      - Physics: definitions · units · formula manipulation · significant figures
      - MFL (French/German/Spanish): compréhension/expression · grammaire ·
        vocabulaire
      - Business / Accounting: Section B keyword marks

    Award 0-100 per rubric dimension. Summarise strengths, improvements, and
    reviewer notes in both English and Irish.

    ESSAY:
    {{ essay }}

    Return RubricScore as {{ ctx.output_format }}.
  "#
}
