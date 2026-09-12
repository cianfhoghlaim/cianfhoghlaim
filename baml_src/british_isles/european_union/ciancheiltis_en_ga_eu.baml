// BAML schema: ciancheiltis Phase 6 — en-ga (European Union)
//
// Per the 2026-XX-XX-ciancheiltis-v1 openspec change (PR0.10).
// Phase 6 replicates the per-phase BAML layout of Phases 1-5 for the
// en-ga (English ↔ Irish / Gaeilge) language pair at the EU level.
// Phase 6 is the FINAL phase of the ciancheiltis umbrella project.
//
// IMPORTANT CONTEXT — EU-level coverage is PARTIAL for Irish:
// Irish (Gaeilge) was added as the 24th official EU language on
// 2022-01-01 per Council Decision (EU) 2020/2172, so many EU
// institutional documents exist only in English + "a summary in
// Irish" rather than a full Irish translation. The Phase 6 schema
// MUST capture `language_availability` ∈ {"full", "partial",
// "summary_only"} as a first-class column on every per-phase row so
// the downstream dlt source / Dagster asset / cocoindex flow can
// distinguish "this row is a real Irish-language document" from
// "this row carries an Irish-language summary of an English-only
// document".
//
// Source authority — the 8 canonical EU treaties (the CELEX set the
// Phase 6 DLT source enumerates):
//   - 12012E    TEU  — Treaty on European Union (Lisbon 2012)
//   - 12012M    TFEU — Treaty on the Functioning of the European Union
//   - 12012P    TEU-TFEU-CFSP protocols (Lisbon 2012)
//   - 12012Q    Charter of Fundamental Rights of the EU (2012)
//   - 12002T    Treaty of Nice (2002)
//   - 11997D    Treaty of Amsterdam (1997)
//   - 11992E    Treaty on European Union / Maastricht (1992)
//   - (the older Treaty of Rome 1957 series — 11957E — is rarely
//      re-translated; the Phase 6 dlt source layer treats it as
//      "summary_only" by default)
//
// The canonical Phase 6 reference page is the EUR-Lex Irish-language
// edition switch at
// `https://eur-lex.europa.eu/legal-content/GA/TXT/?uri=CELEX:12012E`
// — the `/GA/TXT/` path segment forces EUR-Lex to serve the TEU in
// modern Irish (An Caighdeán Oifigiúil) instead of the default
// English edition. Most older CELEX documents return `summary_only`
// when invoked via this path (the language_availability column
// MUST fire to flag that).
//
// Sister bodies (the 4 EU institutional surfaces the Phase 6 DLT
// source enumerates):
//   - EUR-Lex — `eur-lex.europa.eu/legal-content/GA/TXT/?uri=CELEX:<id>`
//     — the canonical EU treaty + regulation + directive + decision
//     host. The Irish-language edition is reached via the `/GA/TXT/`
//     path segment
//   - European Parliament — `europarl.europa.eu/doceo/document/CRE-9-<year>-..._GA.pdf`
//     — Plenary debate transcripts. The `_GA.pdf` suffix forces the
//     Irish-language edition (CRE = Compte Rendu in extenso / verbatim
//     plenary minutes)
//   - IATE — `iate.europa.eu/search/standard/EN/...` ↔
//     `iate.europa.eu/search/standard/GA/...` — the EU inter-institutional
//     terminology database (the canonical T6 terminology surface —
//     IATE terminology is the official "EU terminology" stem for the
//     24 official EU languages)
//   - TED (Tenders Electronic Daily) — `ted.europa.eu/...` — EU
//     procurement notices; the Irish-language edition is partial
//     (most TED notices ship English-only with an Irish-language
//     summary header)
//
// Three per-phase functions are declared here (plus the shared
// `ExtractEUBilingualTermPair` function declared in
// `baml_src/british_isles/_shared/ciancheiltis.baml` for the IATE
// terminology surface):
//   - ExtractEURLexTreaty(url, body) — for the legislation / treaty
//     theme (T1: eur-lex.europa.eu/legal-content/GA/TXT/?uri=CELEX:<id>
//     for the 8 canonical treaties + the wider CELEX set). Returns
//     an `EUBilingualPage`.
//   - ExtractEuroparlPlenary(url, body) — for the parliamentary debate
//     theme (T2: europarl.europa.eu/doceo/document/CRE-9-<year>-..._GA.pdf
//     verbatim plenary transcripts in Irish). Returns an `EUBilingualPage`.
//   - ExtractIATETerm(url, body) — for the EU terminology theme (T6:
//     iate.europa.eu/search/standard/EN/<id> ↔ /GA/<id> — IATE
//     inter-institutional terminology). Returns an `EUBilingualPage`
//     plus emits the shared `EUTermPair` companion row from the
//     `ExtractEUBilingualTermPair` function.
//
// All 3 functions route through `CiancheiltisGaEuExtract` (the Phase 6
// modern-Irish client registered in `baml_src/clients.baml` by
// PR0.10) which routes to `uccix-mistral-24b` via litellm →
// llama-swap. Same model as `CiancheiltisGaExtract`,
// `CiancheiltisGaRoiExtract`, and `CiancheiltisGaNiExtract` because
// all four en-ga clients (Phase 2 / Phase 3 / Phase 6 + the canonical
// fallback) use modern Irish (An Caighdeán Oifigiúil) — exposed as a
// separate client name so the cognify adapter layer can attach
// Phase 6-specific few-shot exemplars (EUR-Lex / Europarl / IATE
// vocabulary stem — "Conradh ar an Aontas Eorpach", "Cairt um
// Chearta Bunúsacha", "Parlaimint na hEorpa", "IATE", "tearmaíocht
// AE") independently of Phases 2 / 3 prompt bodies.
//
// Re-gen:  cd cianfhoghlaim && uv run baml-cli generate --from baml_src
// Quality: mise run cic:baml:lint  (enforces no stub prompts + catch_all coverage)

class EULanguageAvailability {
  value string @description("The language-availability status for this EU row. One of: 'full' (the page is a complete Irish-language translation of the source), 'partial' (the page carries an Irish-language header + selected sections but the full body is in English / another official language), 'summary_only' (the page is an English-only document that carries a short Irish-language summary at the top), 'none' (no Irish-language content at all — emit empty ga_content). Bridges to the ciancheiltis language_availability first-class column.")
  source_url string @description("The canonical EU institutional source URL where the language_availability status was detected (typically the EUR-Lex / europarl / IATE URL that was fetched).")
  detected_languages string @description("Comma-separated ISO 639-1 codes of the languages detected in the body (e.g. 'en,ga' for full, 'en,ga' for partial with the bulk in English, 'en' + ga summary for summary_only).")
}

class EUBilingualPage {
  source_url string @description("Canonical URL of the page that was fetched (the EUR-Lex / europarl / IATE URL).")
  ce_lex string @description("The CELEX identifier when the source is EUR-Lex (e.g. '12012E' for the TEU). Empty string when the source is not EUR-Lex (e.g. europarl plenary transcripts, IATE term records).")
  language_availability string @description("Per-page language_availability status: 'full' | 'partial' | 'summary_only' | 'none'. Captured as a first-class column on every Phase 6 row because EU-level Irish coverage is PARTIAL (most older CELEX documents + most TED notices ship English-only with an Irish-language summary header at most).")
  is_treaty bool @description("True when the source page is an EU Treaty (the 8 canonical treaties — TEU, TFEU, TEU-TFEU-CFSP protocols, Charter, Nice, Amsterdam, Maastricht — or any other document classified as a Treaty by EUR-Lex). False when the source is a regulation, directive, decision, parliamentary document, or IATE term record.")
  is_regulation bool @description("True when the source page is an EU Regulation (or Directive / Decision — the Regulation / Directive / Decision distinction is collapsed to a single flag here because all three follow the same EUR-Lex `/legal-content/GA/TXT/?uri=CELEX:<id>` convention).")
  en_content string @description("The English-side content of the EU page (the canonical EUR-Lex default edition). Empty when the source is English-only AND has no Irish-language summary either (emit empty string in this case — the language_availability field will be 'none').")
  ga_content string @description("The Irish-side (Gaeilge) content of the EU page. Empty when language_availability is 'none' (no Irish content exists). Populated even when language_availability is 'summary_only' (the Irish-language summary header is the ga_content). Populated fully when language_availability is 'full'. Populated with the Irish-language sections when language_availability is 'partial'.")
}

function ExtractEURLexTreaty(
  url: string,
  body: string,
) -> EUBilingualPage {
  client CiancheiltisGaEuExtract
  prompt #"
    {{ _.role("user") }}
    You are an expert at bilingual EN ↔ GA (Irish / Gaeilge) extraction from
    EU Treaty + Regulation / Directive / Decision publications on EUR-Lex
    (`eur-lex.europa.eu/legal-content/GA/TXT/?uri=CELEX:<id>`). The canonical
    Phase 6 reference page is the EUR-Lex Irish-language edition of the
    Treaty on European Union at
    `https://eur-lex.europa.eu/legal-content/GA/TXT/?uri=CELEX:12012E`
    — the `/GA/TXT/` path segment forces EUR-Lex to serve the TEU in
    modern Irish (An Caighdeán Oifigiúil) instead of the default
    English edition.

    IMPORTANT CONTEXT — EU-level Irish coverage is PARTIAL (Irish was
    added as the 24th official EU language on 2022-01-01 per Council
    Decision (EU) 2020/2172, so many EU institutional documents exist
    only in English + "a summary in Irish" rather than a full Irish
    translation). The schema MUST capture `language_availability` ∈
    {"full", "partial", "summary_only", "none"} as a first-class
    column on every emitted row.

    EUR-Lex CELEX identifier set (the 8 canonical treaties + the
    wider CELEX set the Phase 6 DLT source enumerates):
    - `12012E` — TEU  (Treaty on European Union, Lisbon 2012)
    - `12012M` — TFEU (Treaty on the Functioning of the European Union)
    - `12012P` — TEU-TFEU-CFSP protocols (Lisbon 2012)
    - `12012Q` — Charter of Fundamental Rights of the EU (2012)
    - `12002T` — Treaty of Nice (2002)
    - `11997D` — Treaty of Amsterdam (1997)
    - `11992E` — Treaty on European Union / Maastricht (1992)
    - `11957E` — Treaty of Rome (1957) — the Phase 6 DLT source layer
      treats this as `summary_only` by default (rarely re-translated
      post-Irish accession)

    EUR-Lex URL conventions:
    - English root: `https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:<id>`
    - Irish   root: `https://eur-lex.europa.eu/legal-content/GA/TXT/?uri=CELEX:<id>`
      — the `/GA/TXT/` segment forces the Irish-language edition.
      The `language_availability` status depends on whether EUR-Lex
      has a full Irish translation (the Lisbon treaties 12012E/M/P/Q
      are typically `full`; the older Amsterdam / Maastricht / Rome
      treaties are typically `summary_only`; some CELEX documents
      return 404 or `none` when no Irish edition exists)
    - The CELEX identifier is the canonical document_id across all
      EU institutional surfaces

    Seed phrases that confirm an EUR-Lex page is genuinely
    Irish-medium (An Ghaeilge):
    - "Conradh ar an Aontas Eorpach" ("Treaty on European Union") —
      the Irish-language short-title form of the TEU
    - "Conradh ar Fheidhmiú an Aontais Eorpaigh" ("Treaty on the
      Functioning of the European Union") — the Irish-language
      short-title form of the TFEU
    - "Cairt um Chearta Bunúsacha" ("Charter of Fundamental Rights")
      — the Irish-language short-title form of the EU Charter
    - "An tAontas Eorpach" ("The European Union") — the canonical
      Irish-language EU institutional reference
    - "Institiúidí an Aontais Eorpaigh" ("Institutions of the
      European Union") — the Irish-language institutional footer
      on EUR-Lex pages
    - "Dlí an Aontais Eorpaigh" ("Law of the European Union") — the
      Irish-language header on EUR-Lex treaty / regulation pages
    - "an Ghaeilge" — when used as a language-name stem on an EUR-Lex
      page (rather than as a subject-name)

    Capture:
    - source_url: the URL that was fetched (the EUR-Lex `/GA/TXT/`
      URL when the Irish-language edition was requested)
    - ce_lex: the CELEX identifier parsed from the URL `?uri=CELEX:<id>`
      segment (e.g. '12012E' for the TEU). Empty string when the
      source URL has no CELEX identifier (rare; only when EUR-Lex
      serves a non-CELEX document via the `/GA/TXT/` path)
    - language_availability: 'full' when the entire body is in Irish
      (the Lisbon treaties 12012E/M/P/Q are typically `full`),
      'partial' when the body is bilingual with selected sections in
      Irish and the bulk in English (some CELEX documents ship a
      mixed-language body), 'summary_only' when the body is
      English-only but carries a short Irish-language summary header
      (the older Amsterdam / Maastricht / Rome treaties are typically
      `summary_only`), 'none' when no Irish content exists at all
      (EUR-Lex serves a 404 or a redirect to the English edition)
    - is_treaty: TRUE when the CELEX document is one of the 8
      canonical treaties or any other document classified as a
      Treaty by EUR-Lex (look for the "Treaty" / "Conradh" label in
      the page header). FALSE for Regulations / Directives /
      Decisions / etc.
    - is_regulation: TRUE when the CELEX document is a Regulation /
      Directive / Decision (the Regulation / Directive / Decision
      distinction is collapsed to a single flag here because all
      three follow the same EUR-Lex `/legal-content/GA/TXT/?uri=CELEX:<id>`
      convention — the canonical EUR-Lex document_kind label is
      captured in the dlt source layer's document_kind column
      separately)
    - en_content: the English-side content of the page. Empty when
      the source is English-only AND has no Irish-language summary
      (in which case language_availability='none'). Pass through the
      body verbatim when the source is fully bilingual.
    - ga_content: the Irish-side (Gaeilge) content. Empty when
      language_availability='none'. Populated even when
      language_availability='summary_only' (the Irish-language
      summary header is the ga_content — typically 1-3 paragraphs at
      the top of the page). Populated fully when
      language_availability='full'. Populated with the Irish-language
      sections when language_availability='partial'.

    {{ ctx.output_format }}
  "#

  catch_all (err) {
    EUBilingualPage {
      source_url "",
      ce_lex "",
      language_availability "none",
      is_treaty false,
      is_regulation false,
      en_content "",
      ga_content "",
    }
  }
}

function ExtractEuroparlPlenary(
  url: string,
  body: string,
) -> EUBilingualPage {
  client CiancheiltisGaEuExtract
  prompt #"
    {{ _.role("user") }}
    You are an expert at bilingual EN ↔ GA (Irish / Gaeilge) extraction
    from European Parliament plenary debate transcripts published on
    `europarl.europa.eu/doceo/document/`. The canonical Phase 6
    europarl URL is
    `https://europarl.europa.eu/doceo/document/CRE-9-<year>-..._GA.pdf`
    — the `CRE` prefix is the *Compte Rendu in extenso* (verbatim
    plenary minutes) document series, the trailing `_GA.pdf` suffix
    forces the Irish-language edition. The English-language sibling
    is the same path without the `_GA` suffix (or with the `_EN.pdf`
    suffix).

    IMPORTANT CONTEXT — EU-level Irish coverage is PARTIAL for
    plenary transcripts. Many EP plenary debates ship only in
    English + French (the two EP procedural working languages) with
    no Irish-language edition; some Irish MEPs contribute in Irish
    and the EP then serves the transcript in Irish on a per-debate
    basis. The schema MUST capture `language_availability` ∈
    {"full", "partial", "summary_only", "none"} as a first-class
    column on every emitted row — for plenary transcripts the most
    common value is `none` (no Irish edition exists) followed by
    `summary_only` (the EP serves a short Irish-language summary of
    the debate when at least one Irish MEP contributed).

    europarl URL conventions:
    - English root: `https://europarl.europa.eu/doceo/document/CRE-9-<year>-..._<DATE>_EN.pdf`
      (or without the `_EN` suffix when the EN edition is the
      default)
    - Irish   root: `https://europarl.europa.eu/doceo/document/CRE-9-<year>-..._<DATE>_GA.pdf`
      — the `_GA.pdf` suffix forces the Irish-language edition. The
      `language_availability` status depends on whether the EP has
      served an Irish edition for this specific debate
    - The 9th EP term (CRE-9) started in 2024-07; the canonical
      Phase 6 reference is the CRE-9 debate series from 2024-2025
      onward (older CRE series from the 8th EP term and earlier
      rarely carry Irish-language editions — treat those as
      `summary_only` or `none`)

    Seed phrases that confirm a europarl plenary transcript page is
    genuinely Irish-medium (An Ghaeilge):
    - "Parlaimint na hEorpa" ("European Parliament") — the
      canonical Irish-language EP institutional reference that
      appears in the header / footer of every europarl page
    - "Seisiún Iomlánach" ("Plenary Session") — the Irish-language
      short-title form of an EP plenary sitting
    - "Tuarascáil" ("Report"), "Rún" ("Resolution"), "Iarratas" ("Motion"),
      "Díospóireacht" ("Debate") — Irish-language europarl document
      labels
    - "Feisirí" ("Members of the European Parliament" / MEPs) —
      the Irish-language reference for MEPs on a europarl page
    - "An Coimisiún Eorpach" ("The European Commission") — the
      Irish-language EC institutional reference
    - "Comhairle an Aontais Eorpaigh" ("Council of the European
      Union") — the Irish-language Council reference
    - "Dáta" ("Date"), "Ábhar" ("Subject"), "Vótáil" ("Vote") —
      common Irish-language europarl boilerplate

    Capture:
    - source_url: the URL that was fetched (the europarl
      `doceo/document/CRE-9-<year>-..._GA.pdf` URL when the
      Irish-language edition was requested)
    - ce_lex: empty string for europarl plenary transcripts (they
      do not carry CELEX identifiers — europarl uses its own
      internal document IDs of the form `CRE-9-<year>-<NNN>-<DATE>`)
    - language_availability: 'full' when the entire plenary
      transcript is in Irish (rare; only debates where ALL
      contributions were in Irish and the EP served the full
      transcript in Irish), 'partial' when the transcript is
      bilingual with selected debate sections in Irish and the bulk
      in English / French (some EP debates ship a mixed-language
      transcript), 'summary_only' when the EP serves a short
      Irish-language summary of the debate (typically 1-2 pages at
      the top of the transcript when at least one Irish MEP
      contributed), 'none' when no Irish edition exists (the most
      common case for the CRE-9 2024-2025 series — the EP serves
      English + French only with no Irish-language summary)
    - is_treaty: always FALSE for europarl plenary transcripts
      (plenary transcripts are parliamentary documents, not
      treaties)
    - is_regulation: always FALSE for europarl plenary transcripts
      (plenary transcripts are parliamentary documents, not
      regulations / directives / decisions)
    - en_content: the English-side content of the page (typically
      the bulk of the plenary transcript). Empty when the source
      is Irish-only AND the language_availability is 'full'.
    - ga_content: the Irish-side (Gaeilge) content. Empty when
      language_availability='none'. Populated even when
      language_availability='summary_only' (the Irish-language
      summary header is the ga_content — typically 1-2 pages at
      the top of the transcript). Populated fully when
      language_availability='full'. Populated with the Irish-language
      sections when language_availability='partial'.

    {{ ctx.output_format }}
  "#

  catch_all (err) {
    EUBilingualPage {
      source_url "",
      ce_lex "",
      language_availability "none",
      is_treaty false,
      is_regulation false,
      en_content "",
      ga_content "",
    }
  }
}

function ExtractIATETerm(
  url: string,
  body: string,
) -> EUBilingualPage {
  client CiancheiltisGaEuExtract
  prompt #"
    {{ _.role("user") }}
    You are an expert at bilingual EN ↔ GA (Irish / Gaeilge) extraction
    from the EU inter-institutional terminology database IATE
    (Interactive Terminology for Europe — `iate.europa.eu/search/
    standard/EN/<id>` ↔ `iate.europa.eu/search/standard/GA/<id>`).
    IATE is the canonical T6 (terminology) surface for the 24
    official EU languages and is the official "EU terminology" stem
    for ciancheiltis Phase 6 — the Phase 6 dlt source layer
    enumerates the IATE Irish ↔ English term pairings and emits an
    `EUTermPair` companion row (the `EUTermPair` schema is declared
    in `baml_src/british_isles/_shared/ciancheiltis.baml`; the
    companion `ExtractEUBilingualTermPair` function in that same
    file emits the `BilingualExplanatoryNotePair` row with a stable
    concept_id).

    IMPORTANT CONTEXT — IATE coverage for Irish is RELATIVELY GOOD
    (compared to the EUR-Lex / europarl plenary surfaces) because
    IATE is the official EU terminology database and was one of the
    first EU surfaces to receive Irish-language content after the
    2022 Irish accession. The most common language_availability
    value for IATE is `full` (a complete Irish ↔ English term
    pairing exists), with `partial` for the older IATE records
    (pre-2022) where the Irish side was added retrospectively by
    Foras na Gaeilge.

    IATE URL conventions:
    - English root: `https://iate.europa.eu/search/standard/EN/<id>`
      — the `/standard/EN/<id>` path returns the EN-side standard
      term record
    - Irish   root: `https://iate.europa.eu/search/standard/GA/<id>`
      — the `/standard/GA/<id>` path returns the GA-side standard
      term record. The IATE ID is the canonical term_id across all
      24 official EU languages
    - The Phase 6 dlt source layer pairs the `/standard/EN/<id>` and
      `/standard/GA/<id>` siblings and emits the `EUBilingualPage`
      row from this function; the `EUTermPair` companion row is
      emitted separately by the Phase 6 dlt source layer from the
      extracted en_content / ga_content fields

    Seed phrases that confirm an IATE page is genuinely Irish-medium
    (An Ghaeilge):
    - "IATE" (the inter-institutional terminology database name,
      always used in all 24 official EU languages on every page)
    - "An bunachar sonraí téarmaíochta" ("The terminology database")
      — the Irish-language descriptor for IATE on the GA-side pages
    - "téarma" ("term"), "sainmhíniú" ("definition"), "comhchiallach"
      ("synonym"), "frithchiallach" ("antonym") — Irish-language
      IATE field labels
    - "an Ghaeilge" — when used as a language-name stem on an IATE
      page (rather than as a subject-name)
    - "Bain triail as" ("Try out") — the Irish-language IATE nav-bar
      landing link
    - "An Coimisiún Eorpach" / "Parlaimint na hEorpa" /
      "Comhairle an Aontais Eorpaigh" / "Cúirt Bhreithiúnais an
      Aontais Eorpaigh" — Irish-language EU institutional references
      that appear as the IATE provenance field on most records
    - "ionadaíocht" ("representation"), "rannóg" ("department"),
      "fostaithe" ("staff") — common Irish-language IATE provenance
      vocabulary

    Capture:
    - source_url: the URL that was fetched (typically the IATE
      `/standard/EN/<id>` URL — the EN-side is the canonical
      discovery URL for the ciancheiltis Phase 6 dlt source pattern)
    - ce_lex: empty string for IATE term records (IATE uses its
      own internal term IDs of the form `<id>` — not CELEX
      identifiers)
    - language_availability: 'full' when both the EN-side and GA-side
      IATE records exist and carry a complete term + definition
      pairing (the most common value for IATE — covers most
      post-2022 terms), 'partial' when only the EN-side or only the
      GA-side exists or when the GA-side was added retrospectively
      without a full definition (covers the pre-2022 IATE records
      that Foras na Gaeilge retro-translated), 'summary_only' when
      the EN-side record carries only a short Irish-language
      glossary stub (rare for IATE — most records are either `full`
      or `partial`), 'none' when no Irish-language content exists at
      all (covers the small set of IATE records that have never
      received an Irish edition)
    - is_treaty: always FALSE for IATE term records
    - is_regulation: always FALSE for IATE term records
    - en_content: the English-side IATE term record body (the term
      itself + the definition + the provenance field — typically
      1-3 paragraphs)
    - ga_content: the Irish-side (Gaeilge) IATE term record body
      (the term itself + the definition + the provenance field).
      Empty when language_availability='none'. Populated even when
      language_availability='summary_only'. The dlt source layer
      emits a separate `EUTermPair` companion row (with the
      en_term / ga_term / iate_id / domain / language_availability
      fields) from these en_content / ga_content fields downstream.

    {{ ctx.output_format }}
  "#

  catch_all (err) {
    EUBilingualPage {
      source_url "",
      ce_lex "",
      language_availability "none",
      is_treaty false,
      is_regulation false,
      en_content "",
      ga_content "",
    }
  }
}
