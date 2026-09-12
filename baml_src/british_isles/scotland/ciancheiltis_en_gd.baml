// BAML schema: ciancheiltis Phase 4 — en-gd (Scotland)
//
// Per the 2026-09-06-ciancheiltis-v1 openspec change (PR0.8).
// Phase 4 covers the en-gd (English ↔ Scottish Gaelic / Gàidhlig)
// language pair for Scotland under the Gaelic Language (Scotland) Act
// 2005. Phase 4 inherits the per-phase BAML layout of Phase 1
// (en-cy / Wales), Phase 2 (en-ga / Republic of Ireland), and Phase 3
// (en-ga / Northern Ireland) verbatim — same shape, same catch_all
// coverage, same `_.role("user")` + `ctx.output_format` convention.
//
// Source authority: the *Gaelic Language (Scotland) Act 2005* (`/asp/2005/7/`)
// establishes the statutory framework that created Bòrd na Gàidhlig
// (the principal Scottish Gaelic language body) and gave Scottish
// Ministers a duty to promote the use of Gaelic. The legislation.gov.uk
// Scottish slug set spans three stems:
//   - `/asp/<year>/<number>/...` — Acts of the Scottish Parliament
//     (the canonical primary-legislation stem — e.g. `/asp/2005/7/contents`
//     is the *Gaelic Language (Scotland) Act 2005*)
//   - `/ssi/<year>/<number>/...` — Scottish Statutory Instruments
//     (the primary Scottish secondary-legislation stem; e.g. SSI 2018/304
//     on Gaelic-medium education reporting)
//   - `/sdsi/<year>/<number>/...` — Scottish Draft Statutory Instruments
//     (the pre-enactment draft stem; rarer row count but a T1 must-have)
//
// All three stems pair with their Scottish Gaelic-language siblings
// under the same `/contents` (or `/contents/made` / `/introduction`) path
// — the same metadata-mismatch-fires-on-`/asp` pattern that Phase 1
// (en-cy) and Phase 3 (en-ga / NI) already codify on the NI stems.
//
// The canonical Phase 4 reference page is the Bòrd na Gàidhlig news
// index at `https://www.gaidhlig.scot/bord-na-gaidhlig/naidheachdan/`
// (the "Bòrd na Gàidhlig — Naidheachdan" Gaelic-medium news surface,
// theme T5). The Phase 4 gov.scot surface is small but real — a small
// Gaelic content section lives under `gov.scot` and under Education
// Scotland / Foghlam Alba at
// `education.gov.scot/the-improvement-continuum/foghlam-tron-ghaidhlig/`.
//
// Two per-phase functions are declared here:
//   - ExtractScottishStatute(url, body) — for the legislation theme
//     (T1: legislation.gov.uk Scottish stems — `/asp/`, `/ssi/`,
//     `/sdsi/`). Returns a BilingualPagePair.
//   - ExtractScottishGovPage(url, body) — for the gov.scot surface
//     (T2 policy + T3 education, via the small Gaelic content section
//     and the Foghlam Alba / Foghlam tron Ghàidhlig Education Scotland
//     page). Returns a BilingualPagePair.
//
// Both functions route through `CiancheiltisGdExtract` (the Phase 4
// Scottish Gaelic client registered in `baml_src/clients.baml` by
// PR0.0) which routes to `gemma-4-26B-A4B` via litellm → llama-swap.
// Same model as `CiancheiltisCyExtract` because both Phase 1 (Welsh)
// and Phase 4 (Scottish Gaelic) are Celtic-language pairs that route
// through the Welsh-aware multilingual MoE; exposed as a separate
// client name so the cognify adapter layer can attach Phase 4-specific
// few-shot exemplars (Bòrd na Gàidhlig + Stòrlann + DASG vocabulary
// stem) independently of Phase 1.
//
// Re-gen:  cd cianfhoghlaim && uv run baml-cli generate --from baml_src
// Quality: mise run cic:baml:lint  (enforces no stub prompts + catch_all coverage)

function ExtractScottishStatute(
  url: string,
  body: string,
) -> BilingualPagePair {
  client CiancheiltisGdExtract
  prompt #"
    {{ _.role("user") }}
    You are an expert at bilingual EN ↔ GD (Scottish Gaelic / Gàidhlig)
    extraction from Scottish legislation published on
    `legislation.gov.uk`. The canonical Phase 4 reference is the
    *Gaelic Language (Scotland) Act 2005* at
    `https://www.legislation.gov.uk/asp/2005/7/contents` which
    established Bòrd na Gàidhlig (the principal Scottish Gaelic
    language body) and gave Scottish Ministers a duty to promote
    the use of Gaelic.

    legislation.gov.uk Scottish slug set (the 3 stems the
    ciancheiltis Phase 4 DLT source enumerates):
    - `/asp/<year>/<number>/...` — Acts of the Scottish Parliament
      (the canonical primary-legislation stem — the *Gaelic Language
      (Scotland) Act 2005* is `/asp/2005/7/contents`). Smaller row
      count than `/ssi/` but every T1 row is high-authority
    - `/ssi/<year>/<number>/...` — Scottish Statutory Instruments
      (the primary Scottish secondary-legislation stem; e.g.
      SSI 2018/304 on Gaelic-medium education reporting). Higher
      row count than `/asp/`
    - `/sdsi/<year>/<number>/...` — Scottish Draft Statutory
      Instruments (the pre-enactment draft stem; rarer row count but
      a T1 must-have for tracking forthcoming Scottish Gaelic
      obligations before they enter into force)

    Each stem pairs with its Scottish Gaelic-language sibling under
    the same `/contents` (or `/contents/made` / `/introduction`)
    path. The canonical pattern is:

        https://www.legislation.gov.uk/<stem>/<year>/<number>/contents   (EN)
        https://www.legislation.gov.uk/<stem>/<year>/<number>/contents   (GD — same path; gd-side is the body content)

    Some legacy Scottish Acts (pre-2010) pair at the `/contents`
    segment only, without the `/made` suffix. Both forms MUST be
    matched.

    Seed phrases that confirm a Scottish legislation page is
    genuinely Gaelic-medium (Gàidhlig):
    - "Bòrd na Gàidhlig" ("Gaelic Board") — the principal Scottish
      Gaelic language body, the canonical short-title form of the
      *Gaelic Language (Scotland) Act 2005* board body, and the
      seed institution for Scottish Gaelic statutory references
    - "Foghlam tron Ghàidhlig" ("Education through Gaelic") — the
      canonical Scottish Gaelic-medium education descriptor that
      appears on every SSI / ASP reference to Gaelic-medium
      schooling (mirrors Phase 1 en-cy's "Addysg drwy Gyfrwng y
      Gymraeg")
    - "Aithris Ghàidhlig" ("Gaelic Statement" / "Gaelic Report") —
      the canonical Scottish Gaelic-language statutory reporting
      heading under the 2005 Act
    - "Achd na Gàidhlig" ("Gaelic Act") — the Gaelic-language
      short-title form of the *Gaelic Language (Scotland) Act 2005*
    - "Ionad Foghlam Gàidhlig" ("Gaelic Education Centre") — the
      institutional reference for SMO / Sabhal Mòr Ostaig +
      Foghlam Alba
    - "Riaghaltas na h-Alba" ("Scottish Government") — the
      gd-side institutional footer on Scottish Government-published
      Gaelic-medium material
    - "a' Ghàidhlig" — when used as a language-name stem rather
      than as a subject-name stem
    - "Bun-sgoil" / "Àrd-sgoil" — Gaelic-medium primary /
      secondary school-naming nomenclature used in SSI / ASP
      education references

    Capture:
    - source_url: the URL that was fetched
    - url_a: the EN-side Scottish legislation URL (rewrite to the
      `/<stem>/<year>/<number>/contents` form if missing)
    - url_b: the GD-side Scottish legislation URL (rewrite to the
      `/<stem>/<year>/<number>/contents` form, or `/contents/made`
      for SSIs, or `/introduction` for `/sdsi/` drafts)
    - language_pair: 'en-gd'
    - is_same_article: TRUE when both URLs share the same
      `<stem>/<year>/<number>` core and the same status segment
      (`contents` ↔ `contents`, `contents/made` ↔ `contents/made`)
    - metadata_mismatch: TRUE when the page's `<html lang>` or HTTP
      Content-Language header disagrees with the predominant body
      language (canonical case: the `/asp/...` slug series on
      legislation.gov.uk ships `metadata["language"] = "eng"`
      despite the body being predominantly Scottish Gaelic — the
      ciancheiltis metadata-mismatch flag MUST fire here, exactly
      as it does for Phase 1 en-cy on `/uksi/2007/1484/made`)
    - theme_code: 'T1' for legislation

    {{ ctx.output_format }}
  "#

  catch_all (err) {
    BilingualPagePair {
      source_url "",
      url_a "",
      url_b "",
      language_pair "en-gd",
      is_same_article false,
      metadata_mismatch false,
      theme_code "T1",
    }
  }
}

function ExtractScottishGovPage(
  url: string,
  body: string,
) -> BilingualPagePair {
  client CiancheiltisGdExtract
  prompt #"
    {{ _.role("user") }}
    You are an expert at bilingual EN ↔ GD (Scottish Gaelic / Gàidhlig)
    extraction from Scottish Government pages on `gov.scot` (which
    publishes a small but real Gaelic content section) and from the
    Education Scotland / Foghlam Alba surface at
    `education.gov.scot/the-improvement-continuum/foghlam-tron-ghaidhlig/`.

    The canonical Phase 4 reference page is the Bòrd na Gàidhlig
    Gaelic-medium news index at
    `https://www.gaidhlig.scot/bord-na-gaidhlig/naidheachdan/` (T5
    language body — but the page-pairing logic is the same as for
    the gov.scot / education.gov.scot surfaces).

    gov.scot bilingual conventions:
    - English root: `https://www.gov.scot/...`
    - Scottish Gaelic root: `https://www.gov.scot/...` — same path;
      the gd-side is identified by the body content + the
      `<html lang="gd">` attribute (the gov.scot CMS does NOT
      enforce a `/gd/` prefix; it ships parallel `/<slug>` and
      `/<slug>` URLs where the body is the gd version and the
      metadata declares gd)
    - Education Scotland / Foghlam Alba pages live under
      `education.gov.scot/the-improvement-continuum/foghlam-tron-ghaidhlig/`
      with both an en-side (`foghlam-tron-ghaidhlig`) and a gd-side
      body. The slug is the same on both sides (English slug is the
      canonical discovery URL for the ciancheiltis dlt source pattern)
    - Some policy / news pages publish only the en-side; the gd-side
      may be missing or live at a translated slug. Set
      `is_same_article=false` when you cannot corroborate the pairing.

    Seed phrases that confirm a page is genuinely Scottish Gaelic-
    medium (Gàidhlig) on the Scottish surface:
    - "Bòrd na Gàidhlig" — the principal Scottish Gaelic language body
      and the seed institution for Scottish Gaelic statutory references
    - "Foghlam tron Ghàidhlig" ("Education through Gaelic") — the
      canonical Scottish Gaelic-medium education descriptor on the
      Foghlam Alba / Education Scotland pages
    - "Aithris Ghàidhlig" ("Gaelic Statement") — the gd-side policy /
      news heading
    - "Riaghaltas na h-Alba" ("Scottish Government") — the gd-side
      institutional footer on Scottish Government-published
      Gaelic-medium material
    - "Foghlam Alba" ("Education Scotland") — the institutional
      descriptor on the education.gov.scot gd-side pages
    - "a' Ghàidhlig" — when used as a language-name stem (rather than
      as a subject-name)
    - "DASG" (Bòrd na Gàidhlig's "Deuchainn Àrd-sgoil" Gaelic-medium
      assessment programme) — institutional reference on Foghlam Alba
      pages
    - "Stòrlann Nàiseanta" (the Gaelic-medium education resource body)
      — institutional reference on Foghlam Alba pages
    - "Sabhal Mòr Ostaig" (the Gaelic-medium HE college on Skye) —
      HE / Foghlam Alba cross-reference

    Capture:
    - source_url: the URL that was fetched
    - url_a: the EN-side Scottish Government page URL (rewrite to the
      `https://www.gov.scot/<slug>` shape for gov.scot, or pass through
      the en-side canonical URL for education.gov.scot
      `/foghlam-tron-ghaidhlig/...`)
    - url_b: the GD-side Scottish Government page URL (rewrite to the
      `https://www.gov.scot/<slug>` shape for gov.scot, or pass through
      the gd-side canonical URL for education.gov.scot
      `/foghlam-tron-ghaidhlig/...`)
    - language_pair: 'en-gd'
    - is_same_article: TRUE when both bodies are translation
      equivalents of the same source article (same publication date,
      same section IDs, same content stem — corroborate from body
      content, NOT slug alone, because gov.scot slugs are NOT
      deterministically translated to gd)
    - metadata_mismatch: TRUE when the gd page's `<html lang>` is
      'en' despite the body being predominantly Scottish Gaelic —
      this fires often on education.gov.scot gd-side pages where
      the CMS does not flip the lang attribute alongside the body
      content
    - theme_code: derive from the URL slug + body content (T2
      policy / consultations, T3 education, T5 language bodies).
      T1 (legislation) is handled separately by
      `ExtractScottishStatute` (above). T6 (terminology) is handled
      separately by the shared `ExtractGaelicTerm` function in
      `baml_src/british_isles/_shared/ciancheiltis.baml` and emits
      a `GaelicTermPair` row (the `GaelicTermPair` companion row is
      written by the Phase 4 dlt source layer from the
      `is_bord_na_gaidhlig_origin` metadata flag).

    {{ ctx.output_format }}
  "#

  catch_all (err) {
    BilingualPagePair {
      source_url "",
      url_a "",
      url_b "",
      language_pair "en-gd",
      is_same_article false,
      metadata_mismatch false,
      theme_code "",
    }
  }
}