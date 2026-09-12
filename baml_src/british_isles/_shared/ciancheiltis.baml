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
