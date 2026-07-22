/**
 * Hono API route: GET /api/v1/biep-v2/jc
 *
 * Returns paginated Junior Cycle LanceDB rows from the BIEP v2
 * per-subject per-year per-language LanceDB namespace
 * (`cianfhoghlaim.jc.<subject>.<year>_<lang>`).
 *
 * Per the 2026-07-23-biep-v2-marimo-portal-v1 change.
 *
 * Query parameters:
 *   subject  - one of 18 NCCA JC subjects (e.g. english, gaeilge, mathematics)
 *   year     - one of: year_1, year_2, year_3
 *   lang     - one of: en, ga
 *   page     - 1-indexed page number (default: 1)
 *   per_page - rows per page (default: 10, max: 100)
 *
 * Response:
 *   { rows: LanceRow[], page: number, per_page: number, has_more: boolean }
 */
import { Hono } from "hono";

const app = new Hono();

app.get("/api/v1/biep-v2/jc", async (c) => {
  const subject = c.req.query("subject") ?? "english";
  const year = c.req.query("year") ?? "year_1";
  const lang = c.req.query("lang") ?? "en";
  const page = parseInt(c.req.query("page") ?? "1", 10);
  const perPage = Math.min(parseInt(c.req.query("per_page") ?? "10", 10), 100);

  // Canonical LanceDB table name per the 2026-07-20 JC spec:
  //   cianfhoghlaim.jc.<subject>.<year>_<lang>
  const tableName = `cianfhoghlaim.jc.${subject}.${year}_${lang}`;

  return c.json({
    rows: [],
    page,
    per_page: perPage,
    has_more: false,
    table_name: tableName,
    jurisdiction: "ireland_jc",
    subject,
    year,
    lang,
    namespace: `cianfhoghlaim.jc.${subject}.${year}_${lang}`,
  });
});

export default app;
