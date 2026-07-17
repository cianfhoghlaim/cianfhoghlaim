// =============================================================================
// BAML context: judgements.baml
//
// Pick-8 Ireland/law quadrant — Judgements.ie extraction schema.
// One BAML class + one extraction function (the canonical case-law
// join key against the ISB `acts` table).
//
// Source: https://www.courts.ie/judgements (Courts Service of Ireland)
// ~30,000 published decisions from Supreme, Court of Appeal, High,
// Circuit, and District courts.
//
// Re-uses:
//   - CourtLevel       from `ie/law/shared_legal_enums.baml`
//   - StatuteReference from `processing/legal_case_profile.baml`
// =============================================================================

class Judgement {
  url                    string
  neutral_citation       string                          @description("e.g. '[2024] IESC 12' (Supreme), '[2024] IECA 88' (Court of Appeal), '[2024] IEHC 312' (High)")
  case_name              string                          @description("e.g. 'Smith v. Jones'")
  parties                string[]                        @description("Parties to the action")
  judge                  string                          @description("Presiding judge(s)")
  decision_date          string                          @description("ISO 8601 date")
  court_level            CourtLevel
  catchwords             string[]                        @description("Catchword phrases (typically 5-15 keywords for the subject matter)")
  holding                string                          @description("1-3 sentence summary of the decision's holding")
  statutes_cited         StatuteReference[]              @description("Canonical join key against cianfhoghlaim.education.ie.irish_statute_book.acts")
  cases_cited            string[]                        @description("Other case citations referenced")
  extraction_confidence  float                           @description("0.0-1.0")
  @@stream.done
}

function ExtractJudgement(
  page_url: string,
  page_html: string,
) -> Judgement {
  client Gemini2FlashAlias
  prompt #"
    You are an expert Irish case-law extraction specialist working for
    Cianfhoghlaim Oideachais.

    Judgements.ie (operated by the Courts Service) hosts ~30,000
    published decisions from the Supreme Court ([IESC]), Court of
    Appeal ([IECA]), High Court ([IEHC]), and Circuit Court ([IECCA]).
    Each judgement has a neutral citation, catchwords, a holding, and
    cites statutes + other cases.

    Source URL: {{ page_url }}
    HTML content (first 24,000 chars):
    ---
    {{ page_html }}
    ---

    Extract:
      url                — source URL
      neutral_citation   — e.g. "[2024] IESC 12" or "[2024] IEHC 312"
      case_name          — e.g. "Smith v. Jones"
      parties            — parties to the action
      judge              — presiding judge(s)
      decision_date      — ISO 8601
      court_level        — DISTRICT | CIRCUIT | HIGH | SUPREME | COURT_OF_APPEAL | SPECIAL
      catchwords         — the catchword phrases (5-15 subject keywords)
      holding            — 1-3 sentence summary of the holding
      statutes_cited     — StatuteReference[] (CRITICAL — the join key
                          against cianfhoghlaim.education.ie.irish_statute_book.acts)
      cases_cited        — other case citations referenced
      extraction_confidence — 0.0-1.0

    {{ ctx.output_format }}
  "#
}
