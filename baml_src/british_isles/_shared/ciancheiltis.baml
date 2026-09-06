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
