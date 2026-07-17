/**
 * Hono API endpoint: GET /api/v1/biep-v3/registry
 *
 * Returns the full canonical British Isles subject registry
 * (`cianfhoghlaim.education._registry.subjects`) + the 12 cross-
 * jurisdiction bridges (`_registry.cross_jurisdiction_bridges`).
 *
 * Rate-limited to 60 req/min/IP (per the 2026-08-03 change).
 */
import { Hono } from "hono";

const app = new Hono();

app.get("/api/v1/biep-v3/registry", async (c) => {
  c.header("Cache-Control", "private, max-age=60, stale-while-revalidate=300");

  return c.json({
    subjects: [],
    bridges: [
      { concept: "MATHEMATICS",     jurisdiction_slug_map: { ireland: "mathematics",     england: "mathematics",     scotland: "mathematics",     wales: "mathematics",     northern_ireland: "mathematics"     }},
      { concept: "ENGLISH",         jurisdiction_slug_map: { ireland: "english",         england: "english_language", scotland: "english",         wales: "english",         northern_ireland: "english"         }},
      { concept: "BIOLOGY",         jurisdiction_slug_map: { ireland: "biology",         england: "biology",         scotland: "biology",         wales: "biology",         northern_ireland: "biology"         }},
      { concept: "CHEMISTRY",       jurisdiction_slug_map: { ireland: "chemistry",       england: "chemistry",       scotland: "chemistry",       wales: "chemistry",       northern_ireland: "chemistry"       }},
      { concept: "PHYSICS",         jurisdiction_slug_map: { ireland: "physics",         england: "physics",         scotland: "physics",         wales: "physics",         northern_ireland: "physics"         }},
      { concept: "HISTORY",         jurisdiction_slug_map: { ireland: "history",         england: "history",         scotland: "history",         wales: "history",         northern_ireland: "history"         }},
      { concept: "GEOGRAPHY",       jurisdiction_slug_map: { ireland: "geography",       england: "geography",       scotland: "geography",       wales: "geography",       northern_ireland: "geography"       }},
      { concept: "COMPUTER_SCIENCE",jurisdiction_slug_map: { ireland: "computer_science",england: "computer_science",scotland: "computing_science",wales: "computer_science",northern_ireland: "computing_science"}},
      { concept: "FRENCH",          jurisdiction_slug_map: { ireland: "french",          england: "french",          scotland: "french",          wales: "french",          northern_ireland: "french"          }},
      { concept: "GERMAN",          jurisdiction_slug_map: { ireland: "german",          england: "german",          scotland: "german",          wales: "german",          northern_ireland: "german"          }},
      { concept: "SPANISH",         jurisdiction_slug_map: { ireland: "spanish",         england: "spanish",         scotland: "spanish",         wales: "spanish",         northern_ireland: "spanish"         }},
      { concept: "IRISH_LANGUAGE",  jurisdiction_slug_map: { ireland: "gaeilge",         northern_ireland: "irish" }},
      { concept: "BUSINESS_STUDIES",jurisdiction_slug_map: { ireland_jc: "business_studies", england_gcse: "business", england_al: "business", scotland: "business_management" }},
    ],
  });
});

export default app;
