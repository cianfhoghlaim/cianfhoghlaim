// =============================================================================
// BAML context: ireland_legal_extraction.baml
//
// Extraction schemas + functions for the 5 Irish legal/government DLT
// sources added in the `2026-07-06-ireland-legal-pipeline` openspec change:
//
//   1. injuries.ie               (PIAB — Personal Injuries Assessment Board)
//   2. courts.ie                 (Courts Service — forms, judgements, fees, rules)
//   3. workplacerelations.ie     (WRC — Workplace Relations Commission)
//   4. citizensinformation.ie    (CIB — Citizens Information Board)
//   5. gov.ie/en/                (Irish Government — all ministerial sub-depts)
//
// Plus the cross-source statute-linkage function (LinkStatutesToActs) that
// joins the BAML-extracted `statutes_cited` arrays to the existing
// `oideachais.education.ie.irish_statute_book.acts` table.
//
// Re-uses the canonical legal types from `legal_case_profile.baml`
// (CaseCategory, Jurisdiction, TimelineEvent, StatuteReference) so we
// avoid duplicating the schema.
//
// Generation: cd cianfhoghlaim && uv run baml-cli generate
//
// Default client: DefaultLiteLLM (routes through http://litellm:4000/v1,
// temperature=0.0 for deterministic extraction).  Falls back to
// Gemini2Flash for the heavier `ExtractJudgement` function (court
// decisions can be 30+ pages of dense legal prose).
// =============================================================================

// =============================================================================
// Section 1: Enums
// =============================================================================

enum CourtLevel {
  DISTRICT
  CIRCUIT
  HIGH
  SUPREME
  COURT_OF_APPEAL
  SPECIAL
}

enum WRCComplaintType {
  UNFAIR_DISMISSAL
  EMPLOYMENT_EQUALITY
  PAYMENT_OF_WAGES
  WORKING_TIME
  REDUNDANCY
  PARENTAL_LEAVE
  CARERS_LEAVE
  ORGANISATION_OF_WORKING_TIME
  TERMS_AND_CONDITIONS_EMPLOYMENT
  PROTECTION_OF_EMPLOYEES_FIXED_TERM
  PROTECTION_OF_EMPLOYEES_PART_TIME
  OTHER
}

enum GovIEDepartment {
  DOJ
  DOH
  DES
  DBEI
  DECC
  DAFM
  DTCAGSM
  DHLGH
  DPER
  DRCD
  DT
  DCEDIY
  DFHERIS
  DSP
  DFA
  DOD
  TAOISEACH
  FINANCE
  OTHER
}

enum CitizensInfoCategory {
  JUSTICE
  EMPLOYMENT
  SOCIAL_WELFARE
  HOUSING
  HEALTH
  CONSUMER
  MONEY_AND_TAX
  BIRTHS_DEATHS_MARRIAGES
  MOVING_COUNTRY
  GOVERNMENT_IN_IRELAND
  ENVIRONMENTAL_INFORMATION
  OTHER
}

// =============================================================================
// Section 2: Class re-uses from legal_case_profile.baml
// =============================================================================
//
// The following types are imported from `legal_case_profile.baml`:
//   - CaseCategory       (LEGAL_STRATEGY | MEDICAL_MALPRACTICE | ...)
//   - Jurisdiction       (IRELAND | NORTHERN_IRELAND | UNITED_KINGDOM | ...)
//   - TimelineEvent      (event_id, event_date, action, parties_involved, ...)
//   - StatuteReference   (act_name, section, jurisdiction, citation_count)
//
// BAML cross-file imports are resolved at codegen time. See
// `legal_case_profile.baml:1-90` for the canonical definitions.

// =============================================================================
// Section 3: Per-source extraction classes
// =============================================================================

class PIABPage {
  url                    string
  title                  string
  page_kind              string                          @description("process | forms | news | about | consent | permission")
  process_steps          string[]                        @description("Ordered list of steps in the PIAB process (e.g. 'Apply online', 'PIAB assesses', 'Award issued')")
  forms_mentioned        string[]                        @description("Names of PIAB forms referenced (e.g. 'Form A', 'Form B', 'Consent Form')")
  statutory_deadlines    string[]                        @description("Time limits extracted from the page (e.g. '6 months to apply for PIAB assessment')")
  fees_gbp               float?                          @description("PIAB assessment fee in EUR (€) if mentioned")
  permission_to_sue      bool                            @description("True if this page is about the Section 14 / permission-to-sue process")
  statutory_basis        StatuteReference[]              @description("Statutes referenced (e.g. Personal Injuries Assessment Board Act 2003)")
  summary                string
  extraction_confidence  float                           @description("0.0-1.0")
}

class CourtForm {
  url                    string
  form_number            string                          @description("e.g. 'Form 1', 'Form 5A', 'HC1', 'CC1'")
  form_title             string
  court_level            CourtLevel
  category               string                          @description("personal_injury | family | criminal | civil | probate | licensing | taxation | other")
  purpose                string                          @description("Plain-English description of when to use this form")
  parties                string[]                        @description("Plaintiff | Defendant | Applicant | Respondent | Petitioner")
  fee_eur                float?
  downloadable_url       string?                         @description("URL to the PDF version of the form")
  fillable_fields        string[]                        @description("Names of fields the form requires (e.g. 'PPSN', 'Date of Birth', 'Solicitor details')")
  related_statutes       StatuteReference[]
  extraction_confidence  float
}

class Judgement {
  url                    string
  neutral_citation       string                          @description("e.g. '[2024] IESC 12' (Supreme), '[2024] IECA 88' (Court of Appeal), '[2024] IEHC 312' (High)")
  case_name              string                          @description("e.g. 'Smith v. Jones'")
  parties                string[]
  judge                  string                          @description("Presiding judge(s)")
  decision_date          string                          @description("ISO 8601 date")
  court_level            CourtLevel
  catchwords             string[]                        @description("Catchword phrases (typically 5-15 keywords for the subject matter)")
  holding                string                          @description("1-3 sentence summary of the decision's holding")
  statutes_cited         StatuteReference[]              @description("Canonical join key against oideachais.education.ie.irish_statute_book.acts")
  cases_cited            string[]                        @description("Other case citations referenced")
  extraction_confidence  float
}

class CourtFee {
  url                    string
  fee_code               string                          @description("e.g. 'A1', 'B2', 'C5'")
  fee_description        string
  amount_eur             float
  court_level            CourtLevel
  effective_date         string?                         @description("ISO 8601 — when the fee schedule came into effect")
  notes                  string?
  extraction_confidence  float
}

class CourtRule {
  url                    string
  rule_number            string                          @description("e.g. 'O. 5 r. 9', 'RSC O. 11'")
  order                  string                          @description("The Order (chapter) this rule belongs to")
  court_level            CourtLevel
  subject                string                          @description("Plain-English subject of the rule")
  full_text              string?                         @description("Full rule text (when available)")
  effective_date         string?
  extraction_confidence  float
}

class WRCDecision {
  url                    string
  case_ref               string                          @description("WRC case reference, e.g. 'ADJ-00012345-2024'")
  decision_date          string                          @description("ISO 8601")
  complaint_type         WRCComplaintType
  outcome                string                          @description("upheld | dismissed | settled | withdrawn | referred | non_monetary")
  award_amount_eur       float?                          @description("Monetary award in EUR (€); null for non-monetary outcomes")
  claimant               string                          @description("The complainant (may be anonymised as 'A Worker')")
  respondent             string                          @description("The employer / respondent")
  judge                  string?
  statutes_cited         StatuteReference[]              @description("Canonical join key against irish_statute_book.acts")
  catchwords             string[]
  summary                string
  extraction_confidence  float
}

class WRCProcedure {
  url                    string
  title                  string
  complaint_type         WRCComplaintType
  time_limits            string[]                        @description("e.g. '6 months from date of dismissal', '12 months from last discrimination act'")
  hearing_steps          string[]                        @description("The full procedural sequence (e.g. 'Referral', 'Mediation', 'Investigation', 'Adjudication', 'Appeal to Labour Court')")
  adr_options            string[]                        @description("Alternative dispute resolution options (mediation, facilitation)")
  forms_required         string[]                        @description("Form names (e.g. 'Form WR1 - Complaint Form')")
  related_statutes       StatuteReference[]
  summary                string
  extraction_confidence  float
}

class CitizensInfoArticle {
  url                    string
  title                  string
  category               CitizensInfoCategory
  topic                  string                          @description("Sub-topic within the category (e.g. 'unfair dismissal' within 'employment')")
  eligibility_criteria   string[]                        @description("Conditions under which the article's content applies")
  entitlements           string[]                        @description("What the person is entitled to under the law/regulation")
  steps                  string[]                        @description("Ordered steps to follow to claim the entitlement / exercise the right")
  agencies               string[]                        @description("Agencies involved (e.g. 'WRC', 'Citizens Information', 'DSP', 'HSE')")
  appeals                string[]                        @description("Appeals procedure if applicable (e.g. 'Social Welfare Appeals Office', 'Labour Court')")
  related_statutes       StatuteReference[]
  last_updated           string?                         @description("ISO 8601 — when the article was last reviewed")
  summary                string
  extraction_confidence  float
}

class GovIEPressRelease {
  url                    string
  title                  string
  department             GovIEDepartment
  publication_date       string                          @description("ISO 8601")
  headline               string
  summary                string                          @description("1-3 sentence summary of the press release / publication")
  key_actions            string[]                        @description("The concrete actions announced (e.g. 'New regulation published', 'Public consultation opened')")
  related_agencies       string[]                        @description("Agencies named in the release (e.g. 'PIAB', 'WRC', 'HSE')")
  related_statutes       StatuteReference[]
  contact                string?
  extraction_confidence  float
}

// =============================================================================
// Section 4: Cross-source statute linkage (the unified search join key)
// =============================================================================

class StatuteLink {
  source                 string                          @description("piab | courts | wrc | citizensinfo | gov_ie")
  source_id              string                          @description("case_ref, neutral_citation, url, or doc_id")
  source_url             string
  statute_name           string                          @description("Raw statute name extracted from the source")
  matched_act_id         string?                         @description("The matched act_id in irish_statute_book.acts (e.g. '1998/0021/act')")
  match_confidence       float                           @description("0.0-1.0 — how confident the match is")
}

class StatuteLinkExtraction {
  links                  StatuteLink[]
}

// =============================================================================
// Section 5: Extraction functions
// =============================================================================

function ExtractPIABPage(
  page_url: string,
  page_html: string,
) -> PIABPage {
  client DefaultLiteLLM
  prompt #"
    You are an expert Personal Injuries Assessment Board (PIAB)
    extraction specialist working for Cianfhoghlaim Oideachais.

    PIAB is the statutory body that assesses personal injury claims in
    Ireland before they can go to court. Most personal injury claims
    must go through PIAB first; the Section 14 / "permission to seek
    judicial review" process is the gate to High Court litigation.

    Statutes to anchor on:
      - Personal Injuries Assessment Board Act 2003
      - Civil Liability and Courts Act 2004 (Part 2)
      - Personal Injuries Assessment Board (Amendment) Act 2019

    Source URL: {{ page_url }}
    HTML content (first 16,000 chars):
    ---
    {{ page_html }}
    ---

    Extract:
      url                  — the source URL
      title                — the page <title>
      page_kind            — process | forms | news | about | consent | permission
      process_steps        — ordered list of PIAB process steps
      forms_mentioned      — names of forms referenced
      statutory_deadlines  — time limits (e.g. "6 months to apply")
      fees_gbp             — PIAB assessment fee in EUR (€) if mentioned
      permission_to_sue    — true if about Section 14 / permission process
      statutory_basis      — StatuteReference[] citing the relevant Acts
      summary              — 2-3 sentence summary
      extraction_confidence — 0.0-1.0

    {{ ctx.output_format }}
  "#
}

function ExtractCourtForm(
  page_url: string,
  page_html: string,
) -> CourtForm {
  client DefaultLiteLLM
  prompt #"
    You are an expert Courts Service of Ireland forms extraction
    specialist working for Cianfhoghlaim Oideachais.

    The Courts Service website (courts.ie) hosts hundreds of forms
    across District, Circuit, High, Supreme, and Court of Appeal.

    Source URL: {{ page_url }}
    HTML content (first 16,000 chars):
    ---
    {{ page_html }}
    ---

    Extract:
      url                — source URL
      form_number        — e.g. "Form 1", "HC1", "CC5A"
      form_title         — title of the form
      court_level        — DISTRICT | CIRCUIT | HIGH | SUPREME | COURT_OF_APPEAL | SPECIAL
      category           — personal_injury | family | criminal | civil | probate | licensing | taxation | other
      purpose            — plain-English description of when to use
      parties            — Plaintiff | Defendant | Applicant | Respondent | Petitioner
      fee_eur            — fee in EUR (€) if listed
      downloadable_url   — PDF URL
      fillable_fields    — names of fields the form requires
      related_statutes   — StatuteReference[] citing relevant Acts
      extraction_confidence — 0.0-1.0

    {{ ctx.output_format }}
  "#
}

function ExtractJudgement(
  page_url: string,
  page_html: string,
) -> Judgement {
  client Gemini2Flash
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
                          against oideachais.education.ie.irish_statute_book.acts)
      cases_cited        — other case citations referenced
      extraction_confidence — 0.0-1.0

    {{ ctx.output_format }}
  "#
}

function ExtractCourtFee(
  page_url: string,
  page_html: string,
) -> CourtFee {
  client DefaultLiteLLM
  prompt #"
    You are an expert Courts Service of Ireland fee-schedule extraction
    specialist.

    Source URL: {{ page_url }}
    HTML content (first 8,000 chars):
    ---
    {{ page_html }}
    ---

    Extract:
      url                 — source URL
      fee_code            — e.g. "A1", "B2", "C5"
      fee_description     — what the fee is for
      amount_eur          — EUR (€)
      court_level         — DISTRICT | CIRCUIT | HIGH | SUPREME | COURT_OF_APPEAL | SPECIAL
      effective_date      — ISO 8601
      notes               — any conditions
      extraction_confidence — 0.0-1.0

    {{ ctx.output_format }}
  "#
}

function ExtractCourtRule(
  page_url: string,
  page_html: string,
) -> CourtRule {
  client DefaultLiteLLM
  prompt #"
    You are an expert Rules of Court extraction specialist.

    Source URL: {{ page_url }}
    HTML content (first 16,000 chars):
    ---
    {{ page_html }}
    ---

    Extract:
      url                 — source URL
      rule_number         — e.g. "O. 5 r. 9", "RSC O. 11"
      order               — the Order (chapter)
      court_level         — DISTRICT | CIRCUIT | HIGH | SUPREME | COURT_OF_APPEAL | SPECIAL
      subject             — plain-English subject
      full_text           — full rule text when available
      effective_date      — ISO 8601
      extraction_confidence — 0.0-1.0

    {{ ctx.output_format }}
  "#
}

function ExtractWRCDecision(
  page_url: string,
  page_html: string,
) -> WRCDecision {
  client DefaultLiteLLM
  prompt #"
    You are an expert Workplace Relations Commission (WRC) extraction
    specialist working for Cianfhoghlaim Oideachais.

    The WRC publishes ~6,000 Adjudication Decisions per year. Each
    decision has a case_ref (ADJ-NNNNNNNN-YYYY), a decision date, a
    complaint type (unfair dismissal, employment equality, payment of
    wages, etc.), an outcome (upheld / dismissed / settled / withdrawn
    / referred / non_monetary), and a monetary award in EUR.

    Statutes to anchor on:
      - Employment Equality Act 1998
      - Unfair Dismissals Act 1977
      - Payment of Wages Act 1991
      - Organisation of Working Time Act 1997
      - Redundancy Payments Act 1967
      - Protection of Employees (Fixed-Term Work) Act 2003
      - Protection of Employees (Part-Time Work) Act 2001
      - Parental Leave Act 1998
      - Carer's Leave Act 2001

    Source URL: {{ page_url }}
    HTML content (first 16,000 chars):
    ---
    {{ page_html }}
    ---

    Extract:
      url                — source URL
      case_ref           — e.g. "ADJ-00012345-2024"
      decision_date      — ISO 8601
      complaint_type     — UNFAIR_DISMISSAL | EMPLOYMENT_EQUALITY | PAYMENT_OF_WAGES | WORKING_TIME | REDUNDANCY | PARENTAL_LEAVE | CARERS_LEAVE | ORGANISATION_OF_WORKING_TIME | TERMS_AND_CONDITIONS_EMPLOYMENT | PROTECTION_OF_EMPLOYEES_FIXED_TERM | PROTECTION_OF_EMPLOYEES_PART_TIME | OTHER
      outcome            — upheld | dismissed | settled | withdrawn | referred | non_monetary
      award_amount_eur   — EUR (€); null for non-monetary
      claimant           — name or anonymised ("A Worker")
      respondent         — employer name
      judge              — presiding adjudication officer
      statutes_cited     — StatuteReference[] (CRITICAL — join key)
      catchwords         — catchword phrases
      summary            — 2-3 sentence summary
      extraction_confidence — 0.0-1.0

    {{ ctx.output_format }}
  "#
}

function ExtractWRCProcedure(
  page_url: string,
  page_html: string,
) -> WRCProcedure {
  client DefaultLiteLLM
  prompt #"
    You are an expert Workplace Relations Commission (WRC) procedure
    extraction specialist.

    Source URL: {{ page_url }}
    HTML content (first 12,000 chars):
    ---
    {{ page_html }}
    ---

    Extract:
      url                — source URL
      title              — page title
      complaint_type     — UNFAIR_DISMISSAL | EMPLOYMENT_EQUALITY | PAYMENT_OF_WAGES | etc.
      time_limits        — e.g. "6 months from dismissal"
      hearing_steps      — the full procedural sequence
      adr_options        — ADR options (mediation, facilitation)
      forms_required     — form names (e.g. "Form WR1 - Complaint Form")
      related_statutes   — StatuteReference[]
      summary            — 2-3 sentence summary
      extraction_confidence — 0.0-1.0

    {{ ctx.output_format }}
  "#
}

function ExtractCitizensInfoArticle(
  page_url: string,
  page_html: string,
) -> CitizensInfoArticle {
  client DefaultLiteLLM
  prompt #"
    You are an expert Citizens Information Board (CIB) extraction
    specialist working for Cianfhoghlaim Oideachais.

    CIB articles are plain-English explanations of Irish rights,
    entitlements, and appeals procedures, written for the public.

    Source URL: {{ page_url }}
    HTML content (first 16,000 chars):
    ---
    {{ page_html }}
    ---

    Extract:
      url                 — source URL
      title               — page title
      category            — JUSTICE | EMPLOYMENT | SOCIAL_WELFARE | HOUSING | HEALTH | CONSUMER | MONEY_AND_TAX | BIRTHS_DEATHS_MARRIAGES | MOVING_COUNTRY | GOVERNMENT_IN_IRELAND | ENVIRONMENTAL_INFORMATION | OTHER
      topic               — sub-topic (e.g. "unfair dismissal" within "employment")
      eligibility_criteria — list of conditions under which the article applies
      entitlements        — list of entitlements described
      steps               — ordered list of steps to follow
      agencies            — agencies involved (WRC, DSP, HSE, etc.)
      appeals             — appeals procedure if any
      related_statutes    — StatuteReference[]
      last_updated        — ISO 8601 if visible
      summary             — 2-3 sentence summary
      extraction_confidence — 0.0-1.0

    {{ ctx.output_format }}
  "#
}

function ExtractGovIEPressRelease(
  page_url: string,
  page_html: string,
) -> GovIEPressRelease {
  client DefaultLiteLLM
  prompt #"
    You are an expert Irish Government (gov.ie) press release extraction
    specialist working for Cianfhoghlaim Oideachais.

    Source URL: {{ page_url }}
    HTML content (first 12,000 chars):
    ---
    {{ page_html }}
    ---

    Extract:
      url                — source URL
      title              — page title
      department         — DOJ | DOH | DES | DBEI | DECC | DAFM | DTCAGSM | DHLGH | DPER | DRCD | DT | DCEDIY | DFHERIS | DSP | DFA | DOD | TAOISEACH | FINANCE | OTHER
      publication_date   — ISO 8601
      headline           — 1-line headline
      summary            — 1-3 sentence summary
      key_actions        — concrete actions announced
      related_agencies   — agencies named (PIAB, WRC, HSE, etc.)
      related_statutes   — StatuteReference[]
      contact            — press contact if listed
      extraction_confidence — 0.0-1.0

    {{ ctx.output_format }}
  "#
}

// =============================================================================
// Section 6: Cross-source statute linkage (the canonical join key)
// =============================================================================

function LinkStatutesToActs(
  source: string,
  source_id: string,
  source_url: string,
  statute_names: string[],
) -> StatuteLinkExtraction {
  client DefaultLiteLLM
  prompt #"
    You are an expert Irish statute-linkage specialist working for
    Cianfhoghlaim Oideachais.

    Given the list of statute names extracted from one of the 5 Irish
    legal sources (PIAB, Courts, WRC, Citizens Info, gov.ie), produce
    a StatuteLink[] entry for each. The `matched_act_id` is the
    act_id in the Irish Statute Book (e.g. "1998/0021/act" for the
    Employment Equality Act 1998).

    Source: {{ source }}
    Source ID: {{ source_id }}
    Source URL: {{ source_url }}

    Statute names:
    {{ statute_names }}

    For each statute name, return:
      source              — the input source
      source_id           — the input source_id
      source_url          — the input source_url
      statute_name        — the raw statute name
      matched_act_id      — best guess at the act_id in the ISB (e.g.
                            "1998/0021/act"); null if not confident
      match_confidence    — 0.0-1.0

    Return StatuteLinkExtraction as {{ ctx.output_format }}.
  "#
}