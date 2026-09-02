/**
 * Hono app factory for the 8 Phase 14 vernacular routes.
 *
 * Per the 2026-09-01-cianfhoghlaim-nua-v7-vernaculars-pipelines-v1
 * change (Phase 14 of the cianfhoghlaim-nua v6 era plan). Adds the
 * canonical Hono app factory for the 8 British Isles vernacular
 * languages (7 + the Ulster Scots Northern Ireland companion).
 *
 * Each vernacular route exposes 4 endpoints:
 *  - GET  /health
 *  - POST /extract_subject_spec
 *  - POST /search_vernacular_corpus
 *  - POST /get_display_name
 */

import { Hono } from "hono";

type VernacularRouteSpec = {
  vernacular: string;
  display_name: string;
  jurisdiction: string;
  baml_function: string;
  language_code: string;
};

export const VERNACULAR_ROUTE_SPECS: readonly VernacularRouteSpec[] = [
  {
    vernacular: "welsh",
    display_name: "Welsh (Cymraeg)",
    jurisdiction: "WL",
    baml_function: "ExtractWelshSubjectSpec",
    language_code: "cy",
  },
  {
    vernacular: "scottish_gaelic",
    display_name: "Scottish Gaelic (Gàidhlig)",
    jurisdiction: "SC",
    baml_function: "ExtractScottishGaelicSubjectSpec",
    language_code: "gd",
  },
  {
    vernacular: "breton",
    display_name: "Breton (Brezhoneg)",
    jurisdiction: "BR",
    baml_function: "ExtractBretonSubjectSpec",
    language_code: "br",
  },
  {
    vernacular: "cornish",
    display_name: "Cornish (Kernewek)",
    jurisdiction: "KW",
    baml_function: "ExtractCornishSubjectSpec",
    language_code: "kw",
  },
  {
    vernacular: "manx",
    display_name: "Manx (Gaelg)",
    jurisdiction: "IM",
    baml_function: "ExtractManxSubjectSpec",
    language_code: "gv",
  },
  {
    vernacular: "jersey_french",
    display_name: "Jersey French (Jèrriais)",
    jurisdiction: "JE",
    baml_function: "ExtractJerseyFrenchSubjectSpec",
    language_code: "fr-je",
  },
  {
    vernacular: "guernsey_french",
    display_name: "Guernsey French (Guernésiais)",
    jurisdiction: "GG",
    baml_function: "ExtractGuernseyFrenchSubjectSpec",
    language_code: "fr-gg",
  },
  {
    vernacular: "ulster_scots",
    display_name: "Ulster Scots",
    jurisdiction: "NI",
    baml_function: "ExtractUlsterScotsSubjectSpec",
    language_code: "sco",
  },
] as const;

export function buildVernacularApp(spec: VernacularRouteSpec): Hono {
  const app = new Hono()
    .get("/health", (c) =>
      c.json({
        status: "ok",
        vernacular: spec.vernacular,
        display_name: spec.display_name,
        jurisdiction: spec.jurisdiction,
        language_code: spec.language_code,
        baml_function: spec.baml_function,
        actions: 4,
        phase: 14,
      }),
    )
    .post("/extract_subject_spec", (c) =>
      c.json({
        stub: true,
        vernacular: spec.vernacular,
        baml_function: spec.baml_function,
        phase: 14,
      }),
    )
    .post("/search_vernacular_corpus", (c) =>
      c.json({
        stub: true,
        vernacular: spec.vernacular,
        corpus: "phase14_vernacular",
        phase: 14,
      }),
    )
    .post("/get_display_name", (c) =>
      c.json({
        stub: true,
        vernacular: spec.vernacular,
        display_name: spec.display_name,
        jurisdiction: spec.jurisdiction,
        phase: 14,
      }),
    );
  return app;
}
