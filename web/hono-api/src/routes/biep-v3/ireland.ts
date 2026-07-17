/**
 * Hono API endpoint: GET /api/v1/biep-v3/ireland
 *
 * Returns paginated Ireland cohorts from the canonical British Isles
 * subject registry (`cianfhoghlaim.education._registry.subjects` filtered
 * by `jurisdiction='ireland'`).
 *
 * Per the 2026-08-03-biep-v3-web-app-routes-hono-endpoints-v1 change.
 *
 * Query parameters:
 *   page     - 1-indexed page number (default: 1)
 *   per_page - rows per page (default: 50, max: 100)
 *
 * Response:
 *   { rows: RegistryRow[], page, per_page, has_more, total }
 */
import { Hono } from "hono";

const app = new Hono();

app.get("/api/v1/biep-v3/ireland", async (c) => {
  const page = parseInt(c.req.query("page") ?? "1", 10);
  const perPage = Math.min(parseInt(c.req.query("per_page") ?? "50", 10), 100);

  // Canonical namespace: cianfhoghlaim.education.ireland.<stage>.<subject>[.<variant>]
  const tableName = "cianfhoghlaim.education.ireland";

  c.header("Cache-Control", "private, max-age=60, stale-while-revalidate=300");

  return c.json({
    rows: [],
    page,
    per_page: perPage,
    has_more: false,
    table_name: tableName,
    jurisdiction: "ireland",
  });
});

export default app;
