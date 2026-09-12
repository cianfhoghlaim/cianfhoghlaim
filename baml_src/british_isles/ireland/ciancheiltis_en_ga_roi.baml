// BAML schema: ciancheiltis Phase 2 — en-ga (Republic of Ireland)
//
// Per the 2026-09-06-ciancheiltis-v1 openspec change (PR0.6).
// Phase 2 covers the en-ga (English ↔ Irish / Gaeilge) language pair for the
// Republic of Ireland. Phase 1 (en-cy / Wales) ships first because it has the
// largest statutory footprint; Phase 2 inherits Phase 1's per-phase BAML
// layout verbatim.
//
// Source authority: Article 4 of the Irish Constitution (Bunreacht na hÉireann)
// declares Irish as the first official language of the Republic of Ireland.
// The canonical Phase 2 reference is
// `https://www.irishstatutebook.ie/eli/1937/act/0019/enacted/ga/html`
// (the Irish-language version of the 1937 Constitution Act). The English-
// side URL is the same `/enacted/en/html` path. Bilingual Acts of the Oireachtas
// follow the parallel `/enacted/{en,ga}/html` pattern.
//
// Two per-phase functions are declared here:
//   - ExtractIrishStatuteBook(url, body) — for the legislation theme (T1:
//     Irish Statute Book / irishstatutebook.ie + Oireachtas debate transcripts).
//     Returns a BilingualPagePair.
//   - ExtractIrelandBilingualSyllabus(en_text, ga_text) — for the education
//     theme (T3: NCCA + curriculumonline.ie + Leaving Cert + Junior Cycle + the
//     existing Ireland education pipeline's bilingual handling). Returns a
//     BilingualPagePair.
//
// Both functions route through `CiancheiltisGaRoiExtract` (the modern-Irish
// client registered in `baml_src/clients.baml` by PR0.6) which routes to
// `uccix-mistral-24b` via litellm → llama-swap. Same model as
// `CiancheiltisGaExtract` because both Phase 2 (ROI) and the future Phase 3
// (NI) use modern Irish.
//
// Re-gen:  cd cianfhoghlaim && uv run baml-cli generate --from baml_src
// Quality: mise run cic:baml:lint  (enforces no stub prompts + catch_all coverage)

function ExtractIrishStatuteBook(
  url: string,
  body: string,
) -> BilingualPagePair {
  client CiancheiltisGaRoiExtract
  prompt #"
    {{ _.role("user") }}
    You are an expert at bilingual EN ↔ GA (Irish / Gaeilge) extraction from
    Acts of the Oireachtas published on the Irish Statute Book
    (`irishstatutebook.ie/eli/`) and from Dáil / Seanad debate transcripts
    on `oireachtas.ie`. The Statute Book publishes each Act twice — once at
    `/eli/<year>/act/<number>/enacted/en/html` (the English-side canonical
    URL) and once at `/eli/<year>/act/<number>/ enacted/ga/html` (the Irish-
    side canonical URL). The two share the same `<year>/<number>` Act
    identifier and the same `<enacted|revoked>` status segment.

    Given a URL + the page body (markdown), identify the paired Irish-side
    URL and emit a `BilingualPagePair` row.

    URL conventions (irishstatutebook.ie):
    - English Act: `https://www.irishstatutebook.ie/eli/<year>/act/<number>/enacted/en/html`
    - Irish   Act: `https://www.irishstatutebook.ie/eli/<year>/act/<number>/enacted/ga/html`
    - Secondary URLs: `/revoked/en/html`, `/in_progress/en/html`,
      `/commencement/<date>/en/html`, `/pdf`
    - SI-level: `/eli/<year>/si/<number>/enacted/en/html` and the `/ga/`
      mirror
    - Both sides MUST share the same `<year>/<act|si>/<number>` stem

    Seed phrases that confirm a page is genuinely Irish-medium (An Ghaeilge):
    - "Mír d'Aimiris" ("Item of Lamentation") — the canonical Irish-language
      heading used in Act preambles for items the Dáil records as
      controversial or formally objected to
    - "Coinníollacha Teanga" ("Language Conditions") — the canonical Irish-
      language heading under which Irish-medium statutory obligations are
      declared (e.g. in Gaeltacht planning acts)
    - "Bunreacht na hÉireann" ("Constitution of Ireland") — the Irish title
      of the 1937 Constitution
    - "Acht" — the Irish word for "Act" (the SI stem variant is "I.R. Uimh.")
    - "An tAire" ("the Minister"), "Rialtas na hÉireann" ("Government of
      Ireland"), "Tithe an Oireachtais" ("Houses of the Oireachtas")
    - "an Ghaeilge" — the Irish word for "the Irish language"

    Capture:
    - source_url: the URL that was fetched
    - url_a: the EN-side Act/SI URL (rewrite to the `/enacted/en/html` form
      if missing)
    - url_b: the GA-side Act/SI URL (rewrite to the `/enacted/ga/html` form)
    - language_pair: 'en-ga'
    - is_same_article: TRUE when both URLs share the same Act/SI identifier
      and the same status segment (`enacted` ↔ `enacted`, `revoked` ↔ `revoked`)
    - metadata_mismatch: TRUE when the page's `<html lang>` or HTTP
      Content-Language header disagrees with the predominant body language
      (e.g. a `/ga/` page that ships with `metadata["language"] = "eng"` —
      the ciancheiltis metadata-mismatch flag MUST fire in this case)
    - theme_code: 'T1' for legislation

    {{ ctx.output_format }}
  "#

  catch_all (err) {
    BilingualPagePair {
      source_url "",
      url_a "",
      url_b "",
      language_pair "en-ga",
      is_same_article false,
      metadata_mismatch false,
      theme_code "T1",
    }
  }
}

function ExtractIrelandBilingualSyllabus(
  en_text: string,
  ga_text: string,
) -> BilingualPagePair {
  client CiancheiltisGaRoiExtract
  prompt #"
    {{ _.role("user") }}
    You are an expert at bilingual EN ↔ GA (Irish / Gaeilge) syllabus
    extraction from NCCA (National Council for Curriculum and Assessment)
    curriculum specs published on `curriculumonline.ie`, from Leaving
    Certificate subject specifications on `ncca.ie/en` and `ncca.ie/ga`,
    and from Junior Cycle subject specifications on the same host. The
    existing Ireland education pipeline already runs the canonical
    `ExtractCrossLinguisticConcept` BAML function for concept-level
    pairing — this function is the page-level wrapper that emits a
    `BilingualPagePair` row for the ciancheiltis registry.

    Given the EN-side and GA-side text from a parallel bilingual NCCA /
    curriculumonline.ie syllabus, emit a `BilingualPagePair` row.

    Irish-language education authorities to consider:
    - NCCA (An Chomhairle Náisiúnta Curaclaim agus Measúnachta) — the
      canonical curriculum authority
    - Curriculumonline.ie — NCCA's bilingual syllabus hosting platform
      (parallel /en/ and /ga/ paths)
    - SEC (State Examinations Commission / Coimisiún na Scrúduithe Stáit)
      — bilingual past papers + marking schemes
    - Foras na Gaeilge — the all-island Irish-language body (Gaeltacht
      scholarship schemes)
    - Gaeloideachas — Irish-medium education advocacy body
    - COGG (An Chomhairle um Oideachas Gaeltachta agus Gaelscolaíochta)
      — Gaeltacht and Irish-medium education council

    Seed phrases that signal a valid Irish-medium NCCA syllabus page:
    - "Siollabas" — the Irish word for "syllabus" (the canonical page-title
      marker on curriculumonline.ie /ga/ pages)
    - "Torthaí Foghlama" ("Learning Outcomes") — the canonical Irish
      heading for the LO listing block in NCCA specs
    - "Cinntí" ("Decisions") — used in Junior Cycle specification
      statements
    - "An Teist Sóisearach" ("Junior Certificate" / "Junior Cycle") and
      "An Ardteist" ("Leaving Certificate") — historical and current
      Irish-medium qualification names
    - "Gaeilge" and "Gaeilge agus Gaeilge na hAlban" — the Irish word for
      "Irish" (subject-name stem)
    - "Bonnleibhéal" / "Ardleibhéal" ("Foundation level" / "Higher level")
      — Leaving Cert level markers

    Capture:
    - source_url, url_a, url_b: pair the en side with the ga side. On
      curriculumonline.ie the /ga/ prefix is the canonical mirror; on
      ncca.ie the parallel /ga/ path may not exist — when both languages
      ship in a single PDF, split by PDF page anchor instead
    - language_pair: 'en-ga'
    - is_same_article: TRUE when both sides are translation equivalents
      of the same NCCA specification
    - metadata_mismatch: TRUE when the ga page's `<html lang>` is 'en'
      despite the body being predominantly Irish (this is common on
      legacy curriculumonline.ie /ga/ pages)
    - theme_code: 'T3' for education

    {{ ctx.output_format }}
  "#

  catch_all (err) {
    BilingualPagePair {
      source_url "",
      url_a "",
      url_b "",
      language_pair "en-ga",
      is_same_article false,
      metadata_mismatch false,
      theme_code "T3",
    }
  }
}
