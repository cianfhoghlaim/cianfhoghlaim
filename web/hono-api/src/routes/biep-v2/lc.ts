/**
 * Hono API route: GET /api/v1/biep-v2/lc
 *
 * Returns paginated Leaving Certificate LanceDB rows from the BIEP v2
 * per-subject per-level per-language LanceDB namespace
 * (`oideachais.lc.<subject>.<level>_<lang>`).
 *
 * Per the 2026-07-23-biep-v2-marimo-portal-v1 change.
 *
 * Query parameters:
 *   subject            - one of: mathematics, chemistry, geography, gaeilge, english, computer_science
 *   level              - one of: hl, ol, fl
 *   lang               - one of: en, ga
 *   page               - 1-indexed page number (default: 1)
 *   per_page           - rows per page (default: 10, max: 100)
 *
 * Response:
 *   { rows: LanceRow[], page: number, per_page: number, has_more: boolean }
 */
import { Hono } from "hono";
import { hc } from "hono/client";

const app = new Hono();

app.get("/api/v1/biep-v2/lc", async (c) => {
  const subject = c.req.query("subject") ?? "mathematics";
  const level = c.req.query("level") ?? "hl";
  const lang = c.req.query("lang") ?? "en";
  const page = parseInt(c.req.query("page") ?? "1", 10);
  const perPage = Math.min(parseInt(c.req.query("per_page") ?? "10", 10), 100);

  // Canonical LanceDB table name per the BIEP v1 spec:
  //   oideachais.lc.<subject>.<level>_<lang>
  const tableName = `oideachais.lc.${subject}.${level}_${lang}`;

  // Real impl: ibis.duckdb.connect() + ibis.lancedb.connect() + sql query.
  // For the TanStack Start build, this returns a stub that's used by
  // the marimo notebooks + the `biep-v2` web route.
  return c.json({
    rows: [],
    page,
    per_page: perPage,
    has_more: false,
    table_name: tableName,
    jurisdiction: "ireland_lc",
    subject,
    level,
    lang,
    namespace: `oideachais.lc.${subject}.${level}_${lang}`,
  });
});

export default app;
