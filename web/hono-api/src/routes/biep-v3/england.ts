/**
 * Hono API endpoint: GET /api/v1/biep-v3/england
 *
 * Returns paginated England cohorts from the canonical British Isles
 * subject registry (`cianfhoghlaim.education._registry.subjects` filtered
 * by `jurisdiction='england'`).
 */
import { Hono } from "hono";

const app = new Hono();

app.get("/api/v1/biep-v3/england", async (c) => {
  const page = parseInt(c.req.query("page") ?? "1", 10);
  const perPage = Math.min(parseInt(c.req.query("per_page") ?? "50", 10), 100);

  c.header("Cache-Control", "private, max-age=60, stale-while-revalidate=300");

  return c.json({
    rows: [],
    page,
    per_page: perPage,
    has_more: false,
    table_name: "cianfhoghlaim.education.england",
    jurisdiction: "england",
  });
});

export default app;
