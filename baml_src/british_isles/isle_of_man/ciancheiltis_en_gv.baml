// BAML schema: ciancheiltis Phase 5 — en-gv (Isle of Man)
//
// Per the 2026-09-06-ciancheiltis-v1 openspec change (PR0.9).
// Phase 5 covers the en-gv (English ↔ Manx / Gaelg) language pair
// for the Isle of Man under the *Tynwald* cultural framework (Tynwald
// is the Isle of Man's parliament — the longest continuous
// parliament in the world, predating Westminster by ~700 years).
// Phase 5 inherits the per-phase BAML layout of Phase 1
// (en-cy / Wales), Phase 2 (en-ga / Republic of Ireland), Phase 3
// (en-ga / Northern Ireland), and Phase 4 (en-gd / Scotland)
// verbatim — same shape, same catch_all coverage, same
// `_.role("user")` + `ctx.output_format` convention.
//
// IMPORTANT CONTEXT — Manx is in **revival** status:
// Manx (Gaelg) is the smallest Celtic-language corpus in the British
// Isles. The last traditional native speaker (Ned Maddrell) died in
// 1974; the language has been revived as a community L2 since the
// 1990s with ~2,200 self-reported speakers as of the 2021 Isle of
// Man census (vs. ~85,000 Scottish Gaelic speakers in Scotland).
// Crucially, there is **no statutory Manx-language commissioner** and
// **no statutory requirement to publish in Manx** — unlike Wales
// (Welsh Language (Wales) Measure 2011), the Republic of Ireland
// (Official Languages Act 2003), Northern Ireland (the forthcoming
// Identity and Language (Northern Ireland) Act 2022), or Scotland
// (Gaelic Language (Scotland) Act 2005).
//
// Phase 5 mandate (per the umbrella spec §6-phase language-pair
// staging + the dlt source strict-gate note at
// `dlt_sources/ciancheiltis/en_gv/__init__.py:1`):
// "capture what bilingual content exists and surface it faithfully".
// Phase 5 row counts from the dlt source layer will be smaller than
// Phases 1-4 — every emitted row is high-value.
//
// Source authority: the Tynwald legislative corpus (Acts of Tynwald
// + subordinate legislation + Tynwald Hansard) is the closest the Isle
// of Man comes to a T1 (legislation) row source. The
// `legislation.gov.im/cms/legislation/acts-of-tynwald/` stem (the
// canonical T1 stem) and the `tynwald.org.im/business/hansard/`
// Hansard stem are the Isle-of-Man equivalents of the Welsh
// `legislation.gov.uk/wsi/...` and Scottish `legislation.gov.uk/asp/
// ssi/ sdsi/` stems from Phases 1 + 4. The Tynwald surface is mostly
// English-only; a handful of Acts (mostly the older Statutes and
// recent Manx-medium ceremonial Acts) carry Manx-language
// translations or preambular Manx-language clauses.
//
// The canonical Phase 5 reference page is the Culture Vannin
// Manx-medium learning portal at
// `https://www.culturevannin.im/learn-gaelg/` — Culture Vannin is
// the Manx cultural foundation and the closest functional equivalent
// of the Phase 1 Welsh Language Commissioner / Coleg Cymraeg
// Cenedlaethol surface, the Phase 2 Foras na Gaeilge surface, and the
// Phase 4 Bòrd na Gàidhlig surface. The Phase 5 secondary surfaces
// are:
//   - `learnmanx.com` — Learn Manx adult-learning portal
//     (Culture Vannin + Manx Language Service)
//   - `bunscoillghaelgagh.sch.im` — Bunscoill Ghaelgagh network
//     (the 4 Manx-medium primary schools; the revival flagship)
//   - `manxlanguage.sch.im` — per-school Manx Language Service
//     offices (one per Bunscoill site)
//   - `corpus.gaelg.im` — the canonical Manx text corpus
//     (Culture Vannin / Manx Language Service; the Phase 5
//     equivalent of the Phase 4 Bòrd na Gàidhlig terminology
//     glossary and the Phase 1 Welsh CBAC corpus)
//
// Two per-phase functions are declared here:
//   - ExtractTynwaldAct(url, body) — for the legislation theme
//     (T1: legislation.gov.im/cms/legislation/acts-of-tynwald/ +
//     tynwald.org.im/business/hansard/). Returns a BilingualPagePair.
//   - ExtractCultureVanninPage(url, body) — for the culture /
//     language-body surface (T5: culturevannin.im/learn-gaelg/ +
//     learnmanx.com + bunscoillghaelgagh.sch.im +
//     manxlanguage.sch.im + corpus.gaelg.im). Returns a
//     BilingualPagePair.
//
// Both functions route through `CiancheiltisGvExtract` (the
// Phase 5 Manx client registered in `baml_src/clients.baml` by
// PR0.0) which routes to `gemma-4-26B-A4B` via litellm →
// llama-swap. Same model as `CiancheiltisCyExtract` (Phase 1 Welsh)
// + `CiancheiltisGdExtract` (Phase 4 Scottish Gaelic) because all
// three Celtic-language pairs route through the same Welsh-aware
// multilingual MoE; exposed as a separate client name so the
// cognify adapter layer can attach Phase 5-specific few-shot
// exemplars (Culture Vannin + Bunscoill + Gaelg Corpus vocabulary
// stem — "Bunscoill Ghaelgagh", "Gaelg", "Kione Hengagh",
// "Manannagh", "Cooish", "Gaelg-chiuit") independently of
// Phases 1-4.
//
// The shared `ExtractManxTerm` function (declared in
// `baml_src/british_isles/_shared/ciancheiltis.baml`) handles the
// Phase 5 T6 (terminology) companion rows from Culture Vannin +
// Bunscoill + Gaelg Corpus — emits a `ManxTermPair` row plus a
// `BilingualExplanatoryNotePair` row with a stable CC-GLV-NNN
// concept_id. T2/T3 (policy/education) for Phase 5 are smaller
// than the Welsh / Scottish equivalents because Manx has no
// statutory bilingual publication requirement — the dlt source
// layer maps the same T2/T3 surface area but with reduced row
// count expectations.
//
// Re-gen:  cd cianfhoghlaim && uv run baml-cli generate --from baml_src
// Quality: mise run cic:baml:lint  (enforces no stub prompts + catch_all coverage)

function ExtractTynwaldAct(
  url: string,
  body: string,
) -> BilingualPagePair {
  client CiancheiltisGvExtract
  prompt #"
    {{ _.role("user") }}
    You are an expert at bilingual EN ↔ GV (Manx / Gaelg)
    extraction from Isle of Man legislative publications on
    `legislation.gov.im` (Acts of Tynwald + subordinate legislation)
    and from Tynwald Hansard at `tynwald.org.im/business/hansard/`.

    IMPORTANT CONTEXT — Manx is in revival status (per the
    umbrella spec §6-phase language-pair staging + the dlt source
    strict-gate note at `dlt_sources/ciancheiltis/en_gv/__init__.py:1`):
    the last traditional native speaker died in 1974; there is no
    statutory Manx-language commissioner; there is no statutory
    requirement to publish in Manx. The Phase 5 mandate is "capture
    what bilingual content exists and surface it faithfully".
    Treat every Tynwald row as low-confidence until corroborated.

    Isle of Man legislation slug set (the 2 stems the ciancheiltis
    Phase 5 DLT source enumerates):
    - `/cms/legislation/acts-of-tynwald/<year>/<slug>` —
      Acts of Tynwald (the canonical primary-legislation stem —
      the older Statutes + recent ceremonial Acts occasionally
      carry Manx-language translations or preambular Manx clauses)
    - `/business/hansard/<session>` — Tynwald Hansard (the
      verbatim parliamentary record; the equivalent of
      `hansard.parliament.uk` for Westminster). Hansard is almost
      entirely English-only; the Manx-language surface is
      ceremonial / preambular only

    legislation.gov.im URL conventions:
    - English root: `https://www.legislation.gov.im/cms/...`
    - Manx root:    `https://www.legislation.gov.im/cms/...` —
      same path. There is no `/gv/` prefix; the gv-side is
      identified by the body content (a translation table within
      the same page, or a side-by-side Manx-language clause at the
      end of the Act). When no Manx-language sibling exists, set
      `is_same_article=false` and emit empty url_b
    - Tynwald Hansard (`tynwald.org.im/business/hansard/`) — the
      hansard surface rarely carries Manx-language content; the
      bilingual pairing rarely fires. When no Manx-language
      sibling exists, set `is_same_article=false`

    Seed phrases that confirm a Tynwald page is genuinely
    Manx-medium (Gaelg):
    - "Tinvaal" ("Tynwald") — the Manx-language short-title form
      of the Tynwald parliament and the canonical Manx-language
      institutional header on Isle of Man Government material
    - "Bunscoill Ghaelgagh" ("Manx-medium Primary School") — the
      canonical Manx-medium primary-school descriptor that
      appears on Education-related Acts + Hansard references to
      the Bunscoill network
    - "Gaelg" ("Manx") — when used as a language-name stem (rather
      than as a subject-name) on a Tynwald document, it signals
      the page is the gv-language version or carries a Manx
      translation clause
    - "Kione Hengagh" ("Department of Education, Sport and
      Culture" / DESC) — the Manx-language institutional footer
      on Isle of Man Government Manx-medium material; appears
      on Education Acts + Hansard contributions
    - "Manannagh" ("Manx / of the Isle of Man") — the
      Manx-language demonym / adjective; appears on bilingual
      Acts as a section-heading stem
    - "Ynsee / screeu" — Manx-medium "teaching / writing" stems
      used in Education Acts + Hansard education-related
      contributions
    - "Cultoor Vannin" / "Culture Vannin" — the Manx-language +
      English form of Culture Vannin (the Manx cultural
      foundation); appears on Cultural Acts + Hansard culture
      contributions

    Capture:
    - source_url: the URL that was fetched
    - url_a: the EN-side Tynwald URL (rewrite to the
      `https://www.legislation.gov.im/cms/legislation/acts-of-tynwald/<year>/<slug>`
      form for Acts, or pass through the
      `https://www.tynwald.org.im/business/hansard/<session>` form
      for Hansard)
    - url_b: the GV-side Tynwald URL. Most Tynwald Acts and
      Hansard rows have NO Manx-language sibling — when no
      sibling exists, set `is_same_article=false` and emit empty
      url_b (do NOT synthesise a sibling URL). When a Manx-
      language sibling exists, it is typically the same
      `https://www.legislation.gov.im/cms/legislation/acts-of-tynwald/<year>/<slug>`
      path with the body carrying the Manx translation
    - language_pair: 'en-gv'
    - is_same_article: TRUE only when both URLs share the same
      Tynwald Acts-of-Tynwald slug and the same session segment
      AND the body content is genuinely bilingual (corroborate
      from body content, NOT slug alone, because legislation.gov.im
      slugs are NOT deterministically translated to gv). Default
      FALSE for Hansard rows because Hansard rarely carries
      Manx-language content
    - metadata_mismatch: TRUE when the page's `<html lang>` or
      HTTP Content-Language header disagrees with the predominant
      body language. The Tynwald Hansard surface frequently
      ships `metadata["language"] = "eng"` despite a body that
      contains Manx-language ceremonial / preambular clauses —
      the ciancheiltis metadata-mismatch flag MUST fire here
    - theme_code: 'T1' for legislation

    {{ ctx.output_format }}
  "#

  catch_all (err) {
    BilingualPagePair {
      source_url "",
      url_a "",
      url_b "",
      language_pair "en-gv",
      is_same_article false,
      metadata_mismatch false,
      theme_code "T1",
    }
  }
}

function ExtractCultureVanninPage(
  url: string,
  body: string,
) -> BilingualPagePair {
  client CiancheiltisGvExtract
  prompt #"
    {{ _.role("user") }}
    You are an expert at bilingual EN ↔ GV (Manx / Gaelg)
    extraction from the Manx cultural + language-body surface.
    The canonical Phase 5 reference page is the Culture Vannin
    Manx-medium learning portal at
    `https://www.culturevannin.im/learn-gaelg/` — Culture Vannin
    is the Manx cultural foundation, the closest functional
    equivalent of the Phase 1 Welsh Language Commissioner /
    Coleg Cymraeg Cenedlaethol surface, the Phase 2 Foras na
    Gaeilge surface, and the Phase 4 Bòrd na Gàidhlig surface.

    Phase 5 secondary surfaces:
    - `culturevannin.im/learn-gaelg/` — Culture Vannin Manx-
      medium learning portal (the canonical Phase 5 reference
      page per the umbrella spec §Phase en-gv + the dlt source
      strict-gate note)
    - `learnmanx.com` — Learn Manx adult-learning portal
      (Culture Vannin + Manx Language Service)
    - `bunscoillghaelgagh.sch.im` — Bunscoill Ghaelgagh network
      (the 4 Manx-medium primary schools; the revival flagship)
    - `manxlanguage.sch.im` — per-school Manx Language Service
      offices (one per Bunscoill school site)
    - `corpus.gaelg.im` — the canonical Manx text corpus
      (Culture Vannin / Manx Language Service; the Phase 5
      equivalent of the Phase 4 Bòrd na Gàidhlig terminology
      glossary)

    Culture Vannin + Learn Manx URL conventions:
    - English root: `https://www.culturevannin.im/<slug>` (and
      `https://www.learnmanx.com/<slug>` for Learn Manx)
    - Manx root:    `https://www.culturevannin.im/<slug>` —
      same path. There is no `/gv/` prefix; the gv-side is
      identified by the body content. Some `/learn-gaelg/`
      sub-pages ship Manx-only content (no en-side sibling);
      some ship side-by-side bilingual content. Set
      `is_same_article=false` when no en-side sibling exists
    - Bunscoill Ghaelgagh: `https://bunscoillghaelgagh.sch.im/<slug>`
      — mostly bilingual school-recognition register +
      curriculum descriptors; the en-side and gv-side bodies
      are typically translation equivalents
    - Manx Language Service: `https://www.manxlanguage.sch.im/<slug>`
      — per-school MLS pages, mostly bilingual
    - Gaelg Corpus: `https://corpus.gaelg.im/<slug>` — corpus
      search / browse pages; the gv-side is the corpus itself
      (no en-side sibling for most rows; set
      `is_same_article=false`)

    Seed phrases that confirm a Culture Vannin / Learn Manx /
    Bunscoill page is genuinely Manx-medium (Gaelg):
    - "Bunscoill Ghaelgagh" ("Manx-medium Primary School") — the
      canonical Manx-medium primary-school descriptor that
      appears on every Culture Vannin + Bunscoill school-
      recognition register row (mirrors Phase 1 en-cy's "Addysg
      drwy Gyfrwng y Gymraeg" + Phase 4 gd's "Foghlam tron
      Ghàidhlig")
    - "Gaelg" ("Manx") — when used as a language-name stem on a
      Culture Vannin or Learn Manx page (rather than as a
      subject name); the single most reliable Manx-language page
      marker
    - "Kione Hengagh" ("Department of Education, Sport and
      Culture" / DESC) — the Manx-language institutional footer
      on Isle of Man Government Manx-medium material
    - "Manannagh" ("Manx / of the Isle of Man") — the
      Manx-language demonym / adjective; appears on Bunscoill +
      Culture Vannin material as a section-heading stem
    - "Cooish" ("Conversation") — the canonical Manx-medium
      conversation-class descriptor used by Learn Manx + the
      Manx Language Service adult-learning curriculum
    - "Gaelg-chiuit" ("Small Manx / colloquial Manx") — the
      colloquial Manx stem used by Culture Vannin + Learn Manx
      when contrasting with the classical / written form
    - "Cultoor Vannin" / "Culture Vannin" — the Manx-language +
      English form of Culture Vannin; appears on Culture
      Vannin institutional material
    - "Ynsee / screeu" — Manx-medium "teaching / writing" stems
      used on Bunscoill curriculum descriptors

    Capture:
    - source_url: the URL that was fetched
    - url_a: the EN-side Culture Vannin / Learn Manx /
      Bunscoill URL (rewrite to the
      `https://www.culturevannin.im/<slug>`,
      `https://www.learnmanx.com/<slug>`,
      `https://bunscoillghaelgagh.sch.im/<slug>`,
      `https://www.manxlanguage.sch.im/<slug>`, or
      `https://corpus.gaelg.im/<slug>` shape)
    - url_b: the GV-side Culture Vannin / Learn Manx /
      Bunscoill URL (same path as url_a for Culture Vannin /
      Learn Manx, because there is NO `/gv/` prefix — the
      gv-side is identified by the body content only). Set
      empty url_b when no Manx-language body is present
      (do NOT synthesise a sibling URL; Manx has no
      `/gv/` prefix convention)
    - language_pair: 'en-gv'
    - is_same_article: TRUE when both bodies are translation
      equivalents of the same source article (same publication
      date, same section IDs, same content stem — corroborate
      from body content, NOT slug alone, because Culture Vannin
      + Learn Manx slugs are NOT deterministically translated
      to gv). Default FALSE for Gaelg Corpus rows because the
      corpus is gv-only (no en-side sibling)
    - metadata_mismatch: TRUE when the gv page's `<html lang>` is
      'en' despite the body being predominantly Manx — this
      fires often on Culture Vannin + Learn Manx pages where
      the CMS does not flip the lang attribute alongside the
      body content (the same pattern that fires on the
      legislation.gov.im Acts-of-Tynwald stem)
    - theme_code: derive from the URL slug + body content (T3
      education, T5 language bodies / culture, T8 local
      government when the source is an IoM parish / sheading
      notice, T9 public broadcasting & culture when the source
      is a Culture Vannin event listing). T1 (legislation) is
      handled separately by `ExtractTynwaldAct` (above). T6
      (terminology) is handled separately by the shared
      `ExtractManxTerm` function in
      `baml_src/british_isles/_shared/ciancheiltis.baml` and
      emits a `ManxTermPair` row (the `ManxTermPair` companion
      row is written by the Phase 5 dlt source layer from the
      `is_culture_vannin_origin` + `is_bunscoill_origin` metadata
      flags)

    {{ ctx.output_format }}
  "#

  catch_all (err) {
    BilingualPagePair {
      source_url "",
      url_a "",
      url_b "",
      language_pair "en-gv",
      is_same_article false,
      metadata_mismatch false,
      theme_code "",
    }
  }
}