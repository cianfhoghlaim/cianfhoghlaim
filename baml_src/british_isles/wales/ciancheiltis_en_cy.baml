// BAML schema: ciancheiltis Phase 1 — en-cy (Wales)
//
// Per the 2026-09-06-ciancheiltis-v1 openspec change (PR0.4).
// Phase 1 covers the en-cy (English ↔ Welsh / Cymraeg) language pair for the
// ciancheiltis umbrella project. Wales is the most mature Celtic-jurisdiction
// bilingual source set (legislation.gov.uk/uksi + /wsi, gov.wales, Hwb,
// WJEC/CBAC, the Welsh Language Commissioner, NHS Wales, and the 22 Welsh
// local authorities all publish en + cy in parallel).
//
// Two per-phase functions are declared here:
//   - ExtractWalesBilingualSyllabus(en_text, cy_text) — for the education
//     theme (T3: WJEC/CBAC + Hwb + Welsh-Medium syllabi). Seeds: "Llw
//     teyrngarwch" (the GCSE Welsh-language oath phrase), "Mae'r Gorchymyn
//     hwn" (the opening stem of all Welsh-language statutory instruments).
//   - ExtractWelshSI(url, body) — for the legislation theme (T1:
//     legislation.gov.uk/uksi + /wsi dual crawl). Returns a BilingualPagePair.
//
// Both functions route through `ciancheiltisCyExtract` (the canonical
// Welsh-aware client, registered in `baml_src/clients.baml`) which routes
// to `gemma-4-26B-A4B` via litellm → llama-swap. The default fallback
// client name on the `client` line below is `BIEPV3Extract` so the BAML
// compiler always resolves; runtime dispatch rewrites the client name
// based on the `language_pair` argument via the cognify adapter layer.
//
// Re-gen:  cd cianfhoghlaim && uv run baml-cli generate --from baml_src
// Quality: mise run cic:baml:lint  (enforces no stub prompts + catch_all coverage)

function ExtractWalesBilingualSyllabus(
  en_text: string,
  cy_text: string,
) -> BilingualPagePair {
  client BIEPV3Extract
  prompt #"
    {{ _.role("user") }}
    You are an expert at bilingual EN ↔ CY (Welsh / Cymraeg) syllabus extraction
    from Welsh-Medium and English-Medium WJEC / CBAC / CCC awarding-body
    qualification specifications, and from Hwb (hwb.gov.wales) learning
    resources. Given the EN-side and CY-side text from a parallel bilingual
    syllabus, emit a `BilingualPagePair` row.

    Welsh-language curriculum authorities to consider:
    - WJEC / CBAC (Welsh Joint Education Committee, the canonical awarding body)
    - Qualifications Wales (cy.wjec.co.uk mirror for cy-medium specs)
    - Hwb (hwb.gov.wales — Welsh Government digital learning platform)
    - CCC / Coleg Cymraeg Cenedlaethol (for HE-level cy-medium modules)
    - The 22 Welsh local authorities (for school-level curriculum addenda)

    Seed phrases that signal a valid Welsh-medium syllabus page:
    - "Llw teyrngarwch" — the GCSE Welsh-language oath phrase (must be present
      in any formal cy-medium qualification document)
    - "Mae'r Gorchymyn hwn" — the canonical opening stem of all Welsh-language
      statutory instruments (Use this to confirm a /wsi/ page is genuinely
      Welsh-medium rather than en-medium with a cy translation footer)
    - "Cwricwlwm i Gymru" — the Curriculum for Wales framework
    - "Cymhwyster" — the cy word for "qualification"
    - "TGAU" (CBAC GCSE) and "UG" / "Safon Uwch" (cy-medium A-Level)

    Capture:
    - source_url, url_a, url_b: pair the en side with the cy side (often the
      cy side is at the same host with a /cy/ prefix; WJEC PDFs are sometimes
      bilingual in a single document — split by PDF page anchor)
    - language_pair: 'en-cy'
    - is_same_article: TRUE when both sides are translation equivalents of the
      same qualification specification
    - metadata_mismatch: TRUE when the cy page's <html lang> tag is 'en' despite
      the body being predominantly Welsh (this is common on legacy hwb.gov.wales
      pages)
    - theme_code: 'T3' for WJEC / CBAC / Hwb education content

    {{ ctx.output_format }}
  "#

  catch_all (err) {
    BilingualPagePair {
      source_url "",
      url_a "",
      url_b "",
      language_pair "en-cy",
      is_same_article false,
      metadata_mismatch false,
      theme_code "T3",
    }
  }
}

function ExtractWelshSI(
  url: string,
  body: string,
) -> BilingualPagePair {
  client BIEPV3Extract
  prompt #"
    {{ _.role("user") }}
    You are an expert at bilingual EN ↔ CY extraction from UK / Welsh
    statutory instruments hosted on `legislation.gov.uk`. The UK National
    Archives publishes each statutory instrument (SI) twice — once at
    `/uksi/<year>/<number>/made` (the English-side canonical URL) and once
    at `/wsi/<year>/<number>/made` (the Welsh-side canonical URL). The two
    SIs share the same instrument number and date but carry different
    language bodies.

    Given a URL + the page body (markdown), identify the paired SI URL and
    emit a `BilingualPagePair` row.

    URL conventions:
    - English SI: `https://www.legislation.gov.uk/uksi/<year>/<number>/made`
    - Welsh   SI: `https://www.legislation.gov.uk/wsi/<year>/<number>/made`
    - Draft / made / revoked status is encoded in the trailing path segment
      (`/made`, `/introduction`, `/contents`)
    - Both languages MUST share the same `<year>/<number>` to be a valid pair

    Seed phrases that confirm a SI page is genuinely Welsh-medium:
    - "Mae'r Gorchymyn hwn" ("This Order") — opening stem of every cy SI
    - "Gweler" ("See") — the cy inter-section cross-reference convention
    - "yn dod i rym" ("coming into force") — the cy closing-formula convention
    - "y Cyfrin Gyngor" ("the Privy Council") — the cy signing authority
    - "deddfiad" — cy term for "enactment"

    Capture:
    - source_url: the URL that was fetched
    - url_a: the EN-side SI URL (rewrite to the /uksi/ form if missing)
    - url_b: the CY-side SI URL (rewrite to the /wsi/ form)
    - language_pair: 'en-cy'
    - is_same_article: TRUE when both URLs share the same instrument number
    - metadata_mismatch: TRUE when legislation.gov.uk's HTTP Content-Language
      header says 'eng' but the body is predominantly Welsh (this is the
      canonical ciancheiltis Phase 1 metadata_mismatch test case — the
      umbrella spec calls out legislation.gov.uk/uksi/2007/1484/made as the
      canonical smoke test that fires metadata_mismatch=true despite the
      metadata saying eng)
    - theme_code: 'T1' for legislation

    {{ ctx.output_format }}
  "#

  catch_all (err) {
    BilingualPagePair {
      source_url "",
      url_a "",
      url_b "",
      language_pair "en-cy",
      is_same_article false,
      metadata_mismatch false,
      theme_code "T1",
    }
  }
}
