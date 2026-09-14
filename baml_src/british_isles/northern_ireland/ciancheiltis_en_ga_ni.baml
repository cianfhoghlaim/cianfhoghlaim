// BAML schema: ciancheiltis Phase 3 — en-ga (Northern Ireland)
//
// Per the 2026-09-06-ciancheiltis-v1 openspec change (PR0.7).
// Phase 3 covers the en-ga (English ↔ Irish / Gaeilge) language pair
// for Northern Ireland. Phase 3 inherits the per-phase BAML layout of
// Phase 1 (en-cy / Wales) and Phase 2 (en-ga / Republic of Ireland)
// verbatim — same shape, same catch_all coverage, same
// `_.role("user")` + `ctx.output_format` convention.
//
// Source authority: the *Identity and Language (Northern Ireland) Act
// 2022* (`https://www.legislation.gov.uk/uksi/2022/15/contents/made`)
// establishes the statutory framework for Irish-medium education in NI
// and confirms Irish as a recognised language in NI public life
// (commencement pending as of 2026-09). The legislation.gov.uk slug
// set spans four stems:
//   - `/uksi/...` — UK Statutory Instruments (the NI-level SIs that
//     extend to NI under the Identity and Language Act)
//   - `/nisi/...` — Northern Ireland Statutory Instruments (the
//     primary NI statutory instrument series)
//   - `/nid/...` — Northern Ireland Determinations (NI ministerial
//     determinations, e.g. education funding determinations)
//   - `/nia/...` — Northern Ireland Acts (Acts of the NI Assembly,
//     the canonical primary-legislation stem)
//
// All four stems MUST pair with their Irish-language siblings under
// the same `/contents/made` (or `/contents` / `/introduction`) path —
// the same metadata-mismatch-fires-on-`/uksi` pattern that Phase 1
// (en-cy) and Phase 2 (en-ga / ROI) already codify.
//
// Two per-phase functions are declared here:
//   - ExtractNIStatute(url, body) — for the legislation theme (T1:
//     legislation.gov.uk NI stems + nidirect.gov.uk secondary
//     legislation pages). Returns a BilingualPagePair.
//   - ExtractNIDirectBilingualPage(url_en, url_ga, body_en, body_ga)
//     — for the nidirect.gov.uk parallel-page pattern
//     (`/articles/<slug>` ↔ `/gaeilge/airteagal/<slug>`) and for
//     CnaG (comhairle.org), Education Authority NI (eani.org.uk),
//     and Department of Education NI (education-ni.gov.uk). Returns
//     a BilingualPagePair.
//
// Both functions route through `CiancheiltisGaNiExtract` (the Phase 3
// modern-Irish client registered in `baml_src/clients.baml` by PR0.7)
// which routes to `uccix-mistral-24b` via litellm → llama-swap. Same
// model as `CiancheiltisGaExtract` and `CiancheiltisGaRoiExtract`
// because all three (Phase 1 / Phase 2 / Phase 3) use modern Irish
// (An Caighdeán Oifigiúil) but exposed as separate client names so
// the cognify adapter layer can attach phase-specific few-shot
// exemplars and so each phase's prompt engineering can diverge
// independently in follow-up PRs without touching the other two
// client registrations.
//
// Re-gen:  cd cianfhoghlaim && uv run baml-cli generate --from baml_src
// Quality: mise run cic:baml:lint  (enforces no stub prompts + catch_all coverage)

function ExtractNIStatute(
  url: string,
  body: string,
) -> BilingualPagePair {
  client CiancheiltisGaNiExtract
  prompt #"
    {{ _.role("user") }}
    You are an expert at bilingual EN ↔ GA (Irish / Gaeilge) extraction
    from Northern Ireland legislation published on
    `legislation.gov.uk`. The canonical Phase 3 reference is the
    *Identity and Language (Northern Ireland) Act 2022* at
    `https://www.legislation.gov.uk/uksi/2022/15/contents/made`
    (commencement pending as of 2026-09). The Act establishes the
    statutory framework for Irish-medium education in NI, recognises
    Irish as a recognised language in NI public life, and creates
    the Office of the Identity and Language Commissioner.

    legislation.gov.uk Northern Ireland slug set (the 4 stems the
    ciancheiltis Phase 3 DLT source enumerates):
    - `/uksi/<year>/<number>/...` — UK Statutory Instruments that
      extend to NI (e.g. `/uksi/2022/15/contents/made`). Same
      metadata-mismatch-on-`/uksi` pattern as Phase 1 en-cy: the
      HTTP `Content-Language` header is `eng` even when the body
      is predominantly Irish
    - `/nisi/<year>/<number>/...` — Northern Ireland Statutory
      Instruments (the primary NI statutory instrument series;
      higher row count than `/uksi` in the NI surface)
    - `/nid/<year>/<number>/...` — Northern Ireland Determinations
      (NI ministerial determinations; e.g. education funding
      determinations + Irish-medium nursery capital-scheme
      determinations)
    - `/nia/<year>/<number>/...` — Northern Ireland Acts (Acts of
      the NI Assembly, the canonical primary-legislation stem; much
      smaller row count than `/nisi`)

    Each stem pairs with its Irish-language sibling under the same
    `/contents/made` (or `/contents` / `/introduction`) path. The
    canonical pattern is:

        https://www.legislation.gov.uk/<stem>/<year>/<number>/contents/made   (EN)
        https://www.legislation.gov.uk/<stem>/<year>/<number>/contents/ga     (GA — alternate segment)

    Some legacy NI Acts (pre-2010) pair at the `/contents` segment
    only, without the `/made` suffix. Both forms MUST be matched.

    Seed phrases that confirm a NI legislation page is genuinely
    Irish-medium (An Ghaeilge):
    - "Acht na dTeangacha" ("Languages Act") — the Irish-language
      short-title form of the *Identity and Language (Northern
      Ireland) Act 2022*
    - "Bunreacht na hÉireann" ("Constitution of Ireland") — cited in
      NI cross-border Irish-medium statutory references (rare but
      authoritative)
    - "An Chomhairle" ("The Council") — used in NI statutory
      references to Comhairle na Gaelscolaíochta (CnaG)
    - "Oideachas trí Mheán na Gaeilge" ("Education through the Medium
      of Irish") — the canonical Irish-medium descriptor in NI
      Department of Education circulars
    - "Tithe an Oireachtais" / "An túdarás" — Irish-language
      institutional references in NI cross-border statutory text
    - "an Ghaeilge" — when used as a language-name stem rather than
      as a subject-name stem

    Capture:
    - source_url: the URL that was fetched
    - url_a: the EN-side NI legislation URL (rewrite to the
      `/<stem>/<year>/<number>/contents/made` form if missing)
    - url_b: the GA-side NI legislation URL (rewrite to the
      `/<stem>/<year>/<number>/contents/ga` form, or `/contents`
      for pre-2010 legacy Acts)
    - language_pair: 'en-ga'
    - is_same_article: TRUE when both URLs share the same
      `<stem>/<year>/<number>` core and the same status segment
      (`made` ↔ `ga` / `contents`)
    - metadata_mismatch: TRUE when the page's `<html lang>` or HTTP
      Content-Language header disagrees with the predominant body
      language (canonical case: the `/uksi/...` slug series on
      legislation.gov.uk ships `metadata["language"] = "eng"`
      despite the body being predominantly Irish — the
      ciancheiltis metadata-mismatch flag MUST fire here, exactly
      as it does for Phase 1 en-cy on `/uksi/2007/1484/made`)
    - theme_code: 'T1' for legislation

    {{ ctx.output_format }}
  "#


}

function ExtractNIDirectBilingualPage(
  url_en: string,
  url_ga: string,
  body_en: string,
  body_ga: string,
) -> BilingualPagePair {
  client CiancheiltisGaNiExtract
  prompt #"
    {{ _.role("user") }}
    You are an expert at bilingual EN ↔ GA (Irish / Gaeilge) URL
    pairing for the Northern Ireland parallel-page pattern on
    `nidirect.gov.uk` and for the NI language-body + departmental
    surfaces that publish their own bilingual canonical mirrors.

    Canonical nidirect.gov.uk parallel-page convention:

        https://www.nidirect.gov.uk/articles/<slug>           (EN)
        https://www.nidirect.gov.uk/gaeilge/airteagal/<slug> (GA)

    The slug stem may differ slightly between the two sides (e.g.
    nidirect sometimes translates the slug on the ga side; not every
    en-side article has a published ga-side mirror). The bilingual
    pairing MUST be corroborated from the markdown body of each
    side before a row is emitted.

    NI language-body + departmental parallel surfaces:
    - Comhairle na Gaelscolaíochta (CnaG) — `comhairle.org` —
      publishes both en-side and ga-side pages for every
      Gaelscoil + Bunscoil in NI. The ga-side is canonical for
      Irish-medium school recognition register entries. CnaG does
      not currently enforce a strict `/ga/` prefix — instead the
      ga-side is identified by the `<html lang="ga">` attribute and
      the body content.
    - Education Authority NI (EANI) — `eani.org.uk` — publishes
      Irish-medium unit press releases + parental guidance in
      bilingual form on the same slug with a `/gaeilge/` prefix or
      a sibling `/ga/...` URL.
    - Department of Education NI — `education-ni.gov.uk` — the
      NI departmental policy home for Irish-medium education
      funding + the Irish-medium nursery capital scheme. Their
      circulars (`/publications/circulars/...`) sometimes ship in
      bilingual form with the `/gaeilge/...` sibling mirror.

    Seed phrases that confirm a page is genuinely Irish-medium
    (An Ghaeilge) in the NI surface:
    - "Rialtas Thuaisceart Éireann" ("Northern Ireland Government")
      — the canonical ga-side footer on education-ni.gov.uk pages
    - "Baile" ("Home") — the ga-side nav-bar landing link
    - "Nuacht" ("News"), "Preaseisiúint" ("Press release"),
      "Fógraí" ("Notices") — ga-side departmental labels
    - "Tuilleadh eolais" ("More information"), "Teagmháil"
      ("Contact"), "Achoimre ar an..." ("Summary of the...") —
      common ga-side boilerplate
    - "Oideachas trí Mheán na Gaeilge" ("Education through the
      Medium of Irish") — the canonical Irish-medium descriptor
      that appears on CnaG + EANI + education-ni.gov.uk materials
    - "Gaelscoil" / "Bunscoil" / "Iarbhunscoil" — the NI
      Irish-medium school-naming nomenclature (CnaG register)
    - "Acht na dTeangacha" ("Languages Act") — the short-title
      form of the *Identity and Language (Northern Ireland) Act
      2022* on CnaG + EANI pages
    - "An Chomhairle" ("The Council") — the short-title form of CnaG

    Capture:
    - source_url: pass through `url_en` (the en-side URL is the
      canonical discovery URL for the ciancheiltis dlt source
      pattern)
    - url_a: rewrite `url_en` to its canonical form (enforce the
      `https://www.nidirect.gov.uk/articles/<slug>` shape; for
      CnaG / EANI / education-ni.gov.uk pass through the en-side
      canonical URL)
    - url_b: rewrite `url_ga` to its canonical form (enforce the
      `https://www.nidirect.gov.uk/gaeilge/airteagal/<slug>` shape;
      for CnaG / EANI / education-ni.gov.uk pass through the
      ga-side canonical URL)
    - language_pair: 'en-ga'
    - is_same_article: TRUE when both bodies are translation
      equivalents of the same source article (same publication
      date, same section IDs, same content stem — corroborate
      from body content, NOT slug alone, because the NI slug
      translation is NOT deterministic across CnaG / EANI /
      nidirect)
    - metadata_mismatch: TRUE when the ga page's `<html lang>` is
      'en' despite the body being predominantly Irish — this
      fires often on nidirect.gov.uk where the CMS does not flip
      the lang attribute alongside the `/gaeilge/` prefix, and on
      CnaG pages where the lang attribute is set inconsistently
      across school-recognised register entries
    - theme_code: derive from the URL slug + body content (T1
      legislation, T2 policy / consultations, T3 education, T4
      healthcare, T5 language bodies, T7 courts, T8 local
      government, T9 public broadcasting, T10 statistics). T6
      (terminology) is handled separately by the shared
      `ExtractNIBilingualTerm` function in
      `baml_src/british_isles/_shared/ciancheiltis.baml` and
      emits a `BilingualExplanatoryNotePair` row (the
      NILanguagePair companion row is written by the Phase 3 dlt
      source layer from the source_domain metadata).

    {{ ctx.output_format }}
  "#


}
