// BAML schema: ciancheiltis shared (cross-phase bilingual page + explanatory-note)
//
// Per the 2026-09-06-ciancheiltis-v1 openspec change (PR0.4).
// The ciancheiltis umbrella project is a long-distance Celtic bilingual
// alignment effort covering 6 phase language-pairs:
//
//   Phase 1: en-cy (Wales)           — ExtractWalesBilingualSyllabus, ExtractWelshSI
//   Phase 2: en-ga (Republic of Ireland)
//   Phase 3: en-ga (Northern Ireland)
//   Phase 4: en-gd (Scottish Gaelic)
//   Phase 5: en-gv (Manx)
//   Phase 6: en-ga (EU - Gaeltacht)
//
// This file declares the shared types + the 2 shared extraction functions
// (`ExtractCiancheiltisBilingualPage` + `ExtractBilingualExplanatoryNote`)
// that all phases route through. Per-phase function declarations live at
// `baml_src/british_isles/<jurisdiction>/ciancheiltis_<phase>.baml`.
//
// The 4 BAML client registrations (`ciancheiltis{Cy,Ga,Gd,Gv}Extract`) live
// at `baml_src/clients.baml` and route per-language:
//
//   cy (Welsh)        → ciancheiltisCyExtract  → gemma-4-26B-A4B   (Welsh-aware multilingual MoE)
//   ga (Irish)        → ciancheiltisGaExtract  → uccix-mistral-24b (modern Irish)
//   gd (Scottish Gael)→ ciancheiltisGdExtract  → gemma-4-26B-A4B
//   gv (Manx)         → ciancheiltisGvExtract  → gemma-4-26B-A4B (Manx few-shot)
//
// Per the 2026-08-15 centralized-model-registry change, the model strings
// resolved at runtime by MODEL_REGISTRY, env-var-driven via LiteLLM
// (litellm:4000 → llama-swap:8080). The fallback model string below is
// `minimax-m3` so the BAML compiler always resolves even when the litellm
// routing layer is unavailable in dev.
//
// Re-gen:  cd cianfhoghlaim && uv run baml-cli generate --from baml_src
// Quality: mise run cic:baml:lint  (enforces no stub prompts + catch_all coverage)

class BilingualPagePair {
  source_url string @description("Canonical URL of the page that was fetched (the EN or discovery URL).")
  url_a string @description("First half of the bilingual pair (canonical URL of language_a side).")
  url_b string @description("Second half of the bilingual pair (canonical URL of language_b side).")
  language_pair string @description("ISO 639-1 pair joined by '-' (e.g. 'en-cy', 'en-ga', 'en-gd', 'en-gv').")
  is_same_article bool @description("True when url_a and url_b are translation equivalents of the same underlying source article.")
  metadata_mismatch bool @description("True when the page's declared metadata language does NOT match the predominant content language (e.g. legislation.gov.uk/uksi serving 'eng' metadata for a 'cy' page).")
  theme_code string @description("One of T1-T10 mapping to the ciancheiltis 10-theme catalog (legislation, policy_consultations, education, healthcare, language_commissioner, termau, court_service, local_government, clarin_uk_corpora, gov_uk_circulars).")
}

class BilingualExplanatoryNotePair {
  en_note string @description("The English-language explanatory note text (typically 1-3 paragraphs).")
  cy_note string @description("The Celtic-language explanatory note text (Welsh / Irish / Scottish Gaelic / Manx / etc).")
  concept_id string @description("Stable cross-linguistic concept identifier (e.g. 'CC-CYM-NN-001' for Welsh, 'CC-GAE-NN-001' for Irish). Joins BilingualTopicEdge rows in meaisinfhoghlaim/alignment/schema.py.")
  confidence float @description("Translation fidelity score in [0.0, 1.0] where 1.0 = exact corroborated translation, 0.0 = unrelated content. Bridges to the ExtractCrossLinguisticConcept fidelity convention.")
}

// Phase 2 (en-ga / Republic of Ireland) shared types — added by PR0.6.
// `GaeilgeTermPair` is the canonical T6 (terminology) row for Téarma.ie /
// Teanglann.ie ingestion. The concept_id namespace follows the
// ExtractBilingualExplanatoryNote convention: CC-GAE-NNN for Irish terms.
class GaeilgeTermPair {
  term_en string @description("The English-side term (e.g. 'statutory instrument').")
  term_ga string @description("The Irish-side term (e.g. 'ionstraim reachtúil').")
  concept_id string @description("Stable cross-linguistic concept identifier in the CC-GAE-NNN namespace. Joins BilingualTopicEdge rows in meaisinfhoghlaim/alignment/schema.py.")
  domain string @description("The terminology domain (one of: legislation, education, healthcare, language_bodies, courts, local_government, public_broadcasting, statistics). Bridges to the ciancheiltis 10-theme catalog.")
}

// Phase 3 (en-ga / Northern Ireland) shared types — added by PR0.7.
// `NILanguagePair` tracks the NI-specific Irish-medium sourcing provenance
// (CnaG / comhairle.org vs Education Authority NI / eani.org.uk vs
// nidirect.gov.uk). Unlike `GaeilgeTermPair` (terminology row), this is
// the canonical "where did this NI Irish-language page come from?" row
// for the Phase 3 dlt source metadata column. Both flags MUST be settable
// independently (a CnaG-hosted page mirrored on nidirect.gov.uk sets
// is_cna_g_origin=true AND is_eani_origin=false; an Education Authority
// NI Irish-medium unit press release sets is_eani_origin=true).
class NILanguagePair {
  en_url string @description("Canonical English-side URL on the NI source domain.")
  ga_url string @description("Canonical Irish-side URL on the NI source domain.")
  source_domain string @description("The NI-specific Irish-medium source host (e.g. 'nidirect.gov.uk', 'comhairle.org', 'eani.org.uk', 'education-ni.gov.uk').")
  is_cna_g_origin bool @description("True when the ga-side page originates from Comhairle na Gaelscolaíochta (CnaG, comhairle.org) — the NI statutory Irish-medium education body.")
  is_eani_origin bool @description("True when the ga-side page originates from the Education Authority NI (eani.org.uk) Irish-medium unit.")
}

function ExtractCiancheiltisBilingualPage(
  page_markdown: string,
  language_pair: string,
  theme_code: string,
) -> BilingualPagePair {
  client BIEPV3Extract
  prompt #"
    {{ _.role("user") }}
    You are an expert at bilingual pair extraction across the British Isles Celtic-language
    jurisdictions. Given the markdown body of a single page (one half of a bilingual pair),
    identify its translation partner URL and emit a `BilingualPagePair` row.

    The page's declared metadata language MUST NOT be trusted blindly — many
    `legislation.gov.uk/uksi`, `gov.wales`, and `gov.ie` pages carry `eng` metadata
    despite the page body being predominantly Welsh / Irish / Scottish Gaelic / Manx.
    Always run a content-based check on the first 5 KB of the markdown body before
    settling on the language_pair field.

    Capture:
    - source_url: the canonical URL the page was fetched from
    - url_a, url_b: the two paired URLs (the current page and its translation partner)
    - language_pair: an ISO 639-1 pair joined by '-' (en-cy, en-ga, en-gd, en-gv)
    - is_same_article: TRUE when url_a and url_b are translation equivalents of the
      same source article (same title stem, same publication date, same section IDs)
    - metadata_mismatch: TRUE when the page's <html lang=...> or HTTP Content-Language
      header disagrees with the predominant content language you detected
    - theme_code: one of T1-T10 from the ciancheiltis theme catalog

    {% if language_pair == "en-cy" %}
    For Welsh (cy) pairing: look for the parallel `/cy` or `/welsh` path on the same
    host (e.g. `gov.wales/foo` ↔ `gov.wales/cy/foo`). CBAC/WJEC syllabi are
    bilingual in a single PDF — pair the cy half-page with the en half-page using
    the page_number anchor.
    {% elif language_pair == "en-ga" %}
    For Irish (ga) pairing: look for `asgaeilge` paths or the `/ga/` prefix on
    `gov.ie`, `oideachais.ie`, and `fulbright.ie`. The `ExtractCrossLinguisticConcept`
    convention is the canonical sibling for syllabus-level Irish↔English pairs.
    {% elif language_pair == "en-gd" %}
    For Scottish Gaelic (gd) pairing: look for `/gd/` paths on `gov.scot`,
    `scotland.gov.uk`, and SQA. The Bòrd na Gàidhlig site is the central registry.
    {% elif language_pair == "en-gv" %}
    For Manx (gv) pairing: Manx is the smallest corpus (under 2% of Celtic-language
    web content) — almost all `gv` pages live under `gov.im` and a handful of
    cultural archives. Treat any candidate as low-confidence until corroborated.
    {% endif %}

    {{ ctx.output_format }}
  "#

  catch_all (err) {
    BilingualPagePair {
      source_url "",
      url_a "",
      url_b "",
      language_pair "",
      is_same_article false,
      metadata_mismatch false,
      theme_code "",
    }
  }
}

function ExtractBilingualExplanatoryNote(
  en_note: string,
  cy_note: string,
) -> BilingualExplanatoryNotePair {
  client BIEPV3Extract
  prompt #"
    {{ _.role("user") }}
    You are an expert at cross-linguistic explanatory-note pairing, patterned on the
    Ireland education `ExtractCrossLinguisticConcept` template. Given parallel English
    and Celtic-language (Welsh / Irish / Scottish Gaelic / Manx / Cornish / Breton)
    explanatory notes from the same source article, emit a `BilingualExplanatoryNotePair`
    with a stable concept_id and a translation-fidelity confidence score.

    Conventions (inherited from `ExtractCrossLinguisticConcept`):
    - concept_id namespace per jurisdiction:
        CC-CYM-NNN  Welsh (Cymraeg)
        CC-GAE-NNN  Irish (Gaeilge)
        CC-GDH-NNN  Scottish Gaelic (Gàidhlig)
        CC-GLV-NNN  Manx (Gaelg)
        CC-COR-NNN  Cornish (Kernewek)
        CC-BRE-NNN  Breton (Brezhoneg)
    - confidence ∈ [0.0, 1.0]:
        1.0 = exact corroborated translation
        0.7-0.9 = close translation with minor reformulation
        0.4-0.6 = same topic, partial overlap
        0.0-0.3 = unrelated content (MUST also set concept_id to '')

    Emit empty concept_id + confidence 0.0 when the two notes are clearly about
    different topics — do not synthesise a concept_id to force a row.

    {{ ctx.output_format }}
  "#

  catch_all (err) {
    BilingualExplanatoryNotePair {
      en_note "",
      cy_note "",
      concept_id "",
      confidence 0.0,
    }
  }
}

// Phase 2 (en-ga / Republic of Ireland) shared extraction function —
// added by PR0.6. Given the gov.ie parallel-page URL pattern
// (`https://www.gov.ie/en/<slug>` ↔ `https://www.gov.ie/ga/<slug>`) and
// the markdown body of each side, this function emits a BilingualPagePair.
// It is the canonical T1/T2/T4/T5/T7/T8/T9/T10 pairer for gov.ie content
// (irishstatutebook.ie is handled by the per-phase
// `ExtractIrishStatuteBook` in `baml_src/british_isles/ireland/ciancheiltis_en_ga_roi.baml`).
function ExtractIrelandGAURLPair(
  url_en: string,
  url_ga: string,
  body_en: string,
  body_ga: string,
) -> BilingualPagePair {
  client CiancheiltisGaRoiExtract
  prompt #"
    {{ _.role("user") }}
    You are an expert at bilingual EN ↔ GA (Irish / Gaeilge) URL pairing for
    the parallel-page pattern on `gov.ie` and its departmental mirrors
    (e.g. `oideachais.ie`, `justice.ie`, `health.gov.ie`, `housing.gov.ie`,
    `enterprise.gov.ie`). The canonical pattern is:

        https://www.gov.ie/en/<slug>  ↔  https://www.gov.ie/ga/<slug>

    Both URLs are fetched (their bodies are passed as `body_en` and `body_ga`)
    and you MUST emit a `BilingualPagePair` row that confirms the pairing is
    a genuine translation (not two unrelated pages that happen to share a
    slug pattern).

    gov.ie parallel-page conventions:
    - English root: `https://www.gov.ie/en/...`
    - Irish   root: `https://www.gov.ie/ga/...`
    - Departmental mirrors sometimes invert the path (e.g.
      `oideachais.ie/en/news` vs `oideachais.ie/ga/nuacht` — note the
      ga-side uses `nuacht` not `news`). The slug rewrite is
      jurisdiction-specific.
    - Some news / press-release pages publish only the en-side; the ga-side
      may be missing or live at a translated slug. Set `is_same_article=false`
      when you cannot corroborate the pairing.
    - Slug translation is NOT deterministic — do not assume `news` ↔ `nuacht`,
      sometimes it's `news` ↔ `nuacht` but other times `news` ↔ `scelta` or
      `news` ↔ `fógraí`. Use the body content to corroborate.

    Seed phrases that confirm a page is genuinely Irish-medium (An Ghaeilge):
    - "Rialtas na hÉireann" ("Government of Ireland") — the canonical footer
      text on ga-side gov.ie pages
    - "Baile" ("Home") — the ga-side nav-bar landing link
    - "Nuacht" ("News"), "Preaseisiúint" ("Press release"),
      "Fógraí" ("Notices") — ga-side departmental labels
    - "Tuilleadh eolais" ("More information"), "Teagmháil" ("Contact"),
      "Achoimre ar an..." ("Summary of the...") — common ga-side boilerplate
    - "Gaeilge" — when used as a section-name stem (rather than as a
      subject-name), it signals the page is the ga-language version

    Capture:
    - source_url: pass through `url_en` (the en-side URL is the canonical
      discovery URL for the ciancheiltis dlt source pattern)
    - url_a: rewrite `url_en` to its canonical form (enforce the
      `https://www.gov.ie/en/<slug>` shape)
    - url_b: rewrite `url_ga` to its canonical form (enforce the
      `https://www.gov.ie/ga/<slug>` shape)
    - language_pair: 'en-ga'
    - is_same_article: TRUE when both bodies are translation equivalents
      of the same source article (same publication date, same section IDs,
      same content stem)
    - metadata_mismatch: TRUE when the ga page's `<html lang>` is 'en'
      despite the body being predominantly Irish — this fires often on
      gov.ie departmental mirrors where the CMS does not flip the lang
      attribute alongside the slug
    - theme_code: derive from the URL slug + body content (T1 legislation,
      T2 policy / consultations, T3 education, T4 healthcare, T5 language
      bodies, T7 courts, T8 local government, T9 public broadcasting,
      T10 statistics). T6 (terminology) is handled separately by
      Téarma.ie / Teanglann.ie ingestion via the `GaeilgeTermPair` class.

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
      theme_code "",
    }
  }
}

// Phase 3 (en-ga / Northern Ireland) shared extraction function —
// added by PR0.7. The function emits a `BilingualExplanatoryNotePair`
// for terminology ingested from NI-language-bodies (CnaG /
// comhairle.org + Education Authority NI / eani.org.uk + the
// Department of Education NI / education-ni.gov.uk). This is the
// T5 (language-bodies) terminology-pairing cousin of the Phase 2
// Téarma.ie / Teanglann.ie `GaeilgeTermPair` flow — same model
// (`uccix-mistral-24b`) but routed through the Phase 3
// `CiancheiltisGaNiExtract` client so the cognify adapter layer can
// attach NI-specific few-shot exemplars (e.g. the
// *Identity and Language (Northern Ireland) Act 2022* vocabulary stem
// — "Acht na dTeangacha", "An Chomhairle", "Oideachas trí Mheán na
// Gaeilge") independently of the Phase 2 ROI prompt body.
function ExtractNIBilingualTerm(
  en_term: string,
  ga_term: string,
  source: string,
) -> BilingualExplanatoryNotePair {
  client CiancheiltisGaNiExtract
  prompt #"
    {{ _.role("user") }}
    You are an expert at bilingual EN ↔ GA (Irish / Gaeilge) terminology
    extraction from Northern Ireland language bodies. Given an English
    term, a candidate Irish-language term, and the source domain where
    the pairing was observed, emit a `BilingualExplanatoryNotePair` row
    with a stable concept_id (CC-GAE-NNN namespace) and a translation-
    fidelity confidence score.

    Northern Ireland language bodies to consider:
    - Comhairle na Gaelscolaíochta (CnaG) — `comhairle.org` — the
      statutory Irish-medium education body for Northern Ireland
      (established under the Irish-medium education provisions of the
      *Identity and Language (Northern Ireland) Act 2022*)
    - Education Authority NI (EANI) — `eani.org.uk` — the regional
      education authority; their Irish-medium unit publishes bilingual
      parental guidance + enrolment forms
    - Department of Education NI — `education-ni.gov.uk` — the NI
      departmental policy home for Irish-medium education funding +
      the Irish-medium nursery capital scheme
    - nidirect.gov.uk — the NI government public-information portal
      (parallel `/articles/...` (en) ↔ `/gaeilge/airteagal/...` (ga)
      pages for citizen-facing content)

    Seed phrases that confirm a paired NI Irish-medium term is genuine:
    - "Acht na dTeangacha" ("Languages Act") — the Irish-language
      short-title form of the *Identity and Language (Northern Ireland)
      Act 2022* (commencement pending as of 2026-09)
    - "An Chomhairle" — the Irish-language short-title form of CnaG
      (the canonical "the Council" reference in NI Gaelscolaíochta
      discourse)
    - "Oideachas trí Mheán na Gaeilge" ("Education through the Medium
      of Irish") — the canonical Irish-medium descriptor that appears
      on CnaG and EANI materials
    - "Gaelscoil" / "Bunscoil" — the Irish-medium primary-school
      nomenclature used across NI
    - "An Ghaeilge" / "Gaeilge" — when used as a language-name stem
      on an NI government page (rather than as a subject-name on a
      CCEA exam paper)
    - "Tua" / "Iarbhunscoil" — Irish-medium post-primary descriptors
      used by CnaG in their school-recognition register

    Capture:
    - en_note: pass through `en_term` (the English-side term as it
      appeared in the NI source page)
    - cy_note: pass through `ga_term` (the Irish-side term as it
      appeared in the NI source page)
    - concept_id: emit `CC-GAE-NNN` where NNN is a zero-padded integer
      (001, 002, 003, ...) following the ExtractBilingualExplanatoryNote
      convention. Emit empty concept_id when the two terms are clearly
      not a translation pair (do NOT synthesise a concept_id to force
      a row).
    - confidence ∈ [0.0, 1.0]:
        1.0 = exact corroborated translation (e.g. both CnaG and
          EANI publish the same ga-side form for the same en-side
          term)
        0.7-0.9 = close translation with minor reformulation (e.g.
          the ga-side form differs slightly from the en-side stem
          because NI Gaelscolaíochta terminology evolved separately
          from the ROI standard)
        0.4-0.6 = same topic, partial overlap
        0.0-0.3 = unrelated content (MUST also set concept_id to '')

    Source conventions:
    - `source` will be one of:
        'cna_g'      (comhairle.org)
        'eani'       (eani.org.uk Irish-medium unit)
        'dept_ed_ni' (education-ni.gov.uk)
        'nidirect'   (nidirect.gov.uk parallel page)
        'other'      (catch-all)
      The source string MUST NOT influence the concept_id — it is
      metadata only and is logged to the NILanguagePair row separately
      by the Phase 3 dlt source layer.

    {{ ctx.output_format }}
  "#

  catch_all (err) {
    BilingualExplanatoryNotePair {
      en_note "",
      cy_note "",
      concept_id "",
      confidence 0.0,
    }
  }
}

// Phase 4 (en-gd / Scotland) shared types — added by PR0.8.
// `GaelicTermPair` is the canonical T6 (terminology) row for
// terminology ingested from Bòrd na Gàidhlig (gaidhlig.scot),
// Stòrlann Nàiseanta, and DASG (Deuchainn Àrd-sgoil — Bòrd na
// Gàidhlig's Gaelic-medium assessment programme). Like `GaeilgeTermPair`
// (Phase 2 / Téarma.ie) and unlike `NILanguagePair` (Phase 3 / source-
// provenance), this is the canonical "what is the Scottish Gaelic
// equivalent of this English term?" row for the Phase 4 dlt source.
// The `is_bord_na_gaidhlig_origin` flag MUST be settable independently
// of `domain` (a Bòrd na Gàidhlig-hosted page on healthcare terminology
// sets is_bord_na_gaidhlig_origin=true AND domain="healthcare"; a
// Stòrlann-hosted page on education terminology sets
// is_bord_na_gaidhlig_origin=false AND domain="education").
class GaelicTermPair {
  en_term string @description("The English-side term (e.g. 'statutory instrument', 'Gaelic-medium education').")
  gd_term string @description("The Scottish Gaelic-side term (e.g. 'ionnstramaid reachdail', 'Foghlam tron Ghàidhlig').")
  source string @description("The terminology source domain (one of: 'bord_na_gaidhlig', 'storlann', 'dasg', 'foghlam_alba', 'gov_scot', 'other').")
  domain string @description("The terminology domain (one of: legislation, education, healthcare, language_bodies, courts, local_government, public_broadcasting, statistics). Bridges to the ciancheiltis 10-theme catalog.")
  is_bord_na_gaidhlig_origin bool @description("True when the gd-side term originates from Bòrd na Gàidhlig (gaidhlig.scot) — the principal Scottish Gaelic language body established by the Gaelic Language (Scotland) Act 2005.")
}

// Phase 4 (en-gd / Scotland) shared extraction function — added by
// PR0.8. The function emits a `BilingualExplanatoryNotePair` row
// (using the shared concept_id namespace CC-GDH-NNN, where GDH is the
// Scottish Gaelic / Gàidhlig stem following the
// `ExtractBilingualExplanatoryNote` convention) for terminology
// ingested from the Scottish Gaelic language bodies (Bòrd na
// Gàidhlig + Stòrlann Nàiseanta + DASG). This is the T5 (language-
// bodies) terminology-pairing cousin of the Phase 2 Téarma.ie /
// Teanglann.ie `GaeilgeTermPair` flow and the Phase 3 CnaG / EANI /
// education-ni.gov.uk `ExtractNIBilingualTerm` flow — same model
// family (`gemma-4-26B-A4B` Welsh-aware multilingual MoE) but routed
// through the Phase 4 `CiancheiltisGdExtract` client so the cognify
// adapter layer can attach Phase 4-specific few-shot exemplars (Bòrd
// na Gàidhlig + Stòrlann + DASG vocabulary stem — "Bòrd na Gàidhlig",
// "Foghlam tron Ghàidhlig", "Aithris Ghàidhlig") independently of the
// Phase 1 (Welsh) prompt body.
function ExtractGaelicTerm(
  en_term: string,
  gd_term: string,
  source: string,
) -> BilingualExplanatoryNotePair {
  client CiancheiltisGdExtract
  prompt #"
    {{ _.role("user") }}
    You are an expert at bilingual EN ↔ GD (Scottish Gaelic / Gàidhlig)
    terminology extraction from Scottish Gaelic language bodies. Given
    an English term, a candidate Scottish Gaelic term, and the source
    domain where the pairing was observed, emit a
    `BilingualExplanatoryNotePair` row with a stable concept_id
    (CC-GDH-NNN namespace) and a translation-fidelity confidence
    score.

    Scottish Gaelic language bodies to consider:
    - Bòrd na Gàidhlig — `gaidhlig.scot` — the principal Scottish
      Gaelic language body, established by the *Gaelic Language
      (Scotland) Act 2005* (`/asp/2005/7/contents`). Publishes the
      Gaelic-medium news index at `/bord-na-gaidhlig/naidheachdan/`
      and the canonical Gaelic terminology glossary
    - Stòrlann Nàiseanta — the Gaelic-medium education resource
      body that publishes bilingual (en + gd) primary / secondary
      school resources across Scotland
    - DASG (Deuchainn Àrd-sgoil) — Bòrd na Gàidhlig's Gaelic-medium
      secondary-school assessment programme that publishes bilingual
      exam materials
    - Foghlam Alba (Education Scotland) — `education.gov.scot` —
      the Education Scotland / Foghlam Alba gd-side surface at
      `/the-improvement-continuum/foghlam-tron-ghaidhlig/`
    - Scottish Government (gov.scot) — the Scottish Government
      publishes a small but real Gaelic content section under the
      gd-side of `gov.scot/<slug>` URLs

    Seed phrases that confirm a paired Scottish Gaelic-medium term
    is genuine:
    - "Bòrd na Gàidhlig" — the principal Scottish Gaelic language
      body and the seed institution for Scottish Gaelic statutory
      references
    - "Foghlam tron Ghàidhlig" ("Education through Gaelic") — the
      canonical Scottish Gaelic-medium education descriptor that
      appears on Bòrd na Gàidhlig + Stòrlann + Foghlam Alba materials
    - "Aithris Ghàidhlig" ("Gaelic Statement" / "Gaelic Report") —
      the canonical Scottish Gaelic-language statutory reporting
      heading under the 2005 Act
    - "Achd na Gàidhlig" ("Gaelic Act") — the Gaelic-language
      short-title form of the *Gaelic Language (Scotland) Act 2005*
    - "a' Ghàidhlig" — when used as a language-name stem on a
      Scottish Government page (rather than as a subject-name on an
      SQA exam paper)
    - "Bun-sgoil" / "Àrd-sgoil" — Gaelic-medium primary / secondary
      school-naming nomenclature used by Stòrlann + DASG
    - "Ionad Foghlam Gàidhlig" — Gaelic Education Centre (Sabhal Mòr
      Ostaig + Foghlam Alba cross-reference)

    Capture:
    - en_note: pass through `en_term` (the English-side term as it
      appeared in the Scottish source page)
    - cy_note: pass through `gd_term` (the Scottish Gaelic-side
      term as it appeared in the Scottish source page)
    - concept_id: emit `CC-GDH-NNN` where NNN is a zero-padded
      integer (001, 002, 003, ...) following the
      ExtractBilingualExplanatoryNote convention (GDH = Gàidhlig /
      Scottish Gaelic). Emit empty concept_id when the two terms
      are clearly not a translation pair (do NOT synthesise a
      concept_id to force a row).
    - confidence ∈ [0.0, 1.0]:
        1.0 = exact corroborated translation (e.g. both Bòrd na
          Gàidhlig and Stòrlann publish the same gd-side form for
          the same en-side term)
        0.7-0.9 = close translation with minor reformulation (e.g.
          the gd-side form differs slightly from the en-side stem
          because Scottish Gaelic terminology evolved separately
          from Irish)
        0.4-0.6 = same topic, partial overlap
        0.0-0.3 = unrelated content (MUST also set concept_id to '')

    Source conventions:
    - `source` will be one of:
        'bord_na_gaidhlig' (gaidhlig.scot)
        'storlann'        (Stòrlann Nàiseanta)
        'dasg'            (DASG / Deuchainn Àrd-sgoil)
        'foghlam_alba'    (education.gov.scot /the-improvement-continuum/foghlam-tron-ghaidhlig/)
        'gov_scot'        (Scottish Government gd-side pages)
        'other'           (catch-all)
      The source string MUST NOT influence the concept_id — it is
      metadata only and is logged to the GaelicTermPair row
      separately by the Phase 4 dlt source layer.

    {{ ctx.output_format }}
  "#

  catch_all (err) {
    BilingualExplanatoryNotePair {
      en_note "",
      cy_note "",
      concept_id "",
      confidence 0.0,
    }
  }
}
