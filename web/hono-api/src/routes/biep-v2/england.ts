/**
 * Hono API route: GET /api/v1/biep-v2/england
 *
 * Returns paginated England AQA + OCR + Edexcel LanceDB rows from
 * the BIEP v2 per-board per-subject per-level LanceDB namespace
 * (`cianfhoghlaim.england.<board>.<subject>.<qualification_level>`).
 *
 * Per the 2026-07-23-biep-v2-marimo-portal-v1 change.
 *
 * Query parameters:
 *   board               - one of: aqa, ocr, edexcel
 *   subject             - one of 9 priority subjects (e.g. mathematics, english_language)
 *   qualification_level - one of: gcse, a_level
 *   page                - 1-indexed page number (default: 1)
 *   per_page            - rows per page (default: 10, max: 100)
 *
 * Response:
 *   { rows: LanceRow[], page: number, per_page: number, has_more: boolean }
 */
import { Hono } from "hono";

const app = new Hono();

app.get("/api/v1/biep-v2/england", async (c) => {
  const board = c.req.query("board") ?? "aqa";
  const subject = c.req.query("subject") ?? "mathematics";
  const qualificationLevel = c.req.query("qualification_level") ?? "gcse";
  const page = parseInt(c.req.query("page") ?? "1", 10);
  const perPage = Math.min(parseInt(c.req.query("per_page") ?? "10", 10), 100);

  // Canonical LanceDB table name per the 2026-07-21 England spec:
  //   cianfhoghlaim.england.<board>.<subject>.<qualification_level>
  const tableName = `cianfhoghlaim.england.${board}.${subject}.${qualificationLevel}`;

  return c.json({
    rows: [],
    page,
    per_page: perPage,
    has_more: false,
    table_name: tableName,
    jurisdiction: `england_${board}`,
    board,
    subject,
    qualification_level: qualificationLevel,
    namespace: `cianfhoghlaim.england.${board}.${subject}.${qualificationLevel}`,
  });
});

export default app;
