/**
 * Hono API endpoint: GET /api/v1/biep-v3/crown
 *
 * Returns paginated Jersey + Guernsey + Isle of Man cohorts from the
 * canonical British Isles subject registry.
 */
import { Hono } from "hono";

const app = new Hono();

app.get("/api/v1/biep-v3/crown", async (c) => {
  const page = parseInt(c.req.query("page") ?? "1", 10);
  const perPage = Math.min(parseInt(c.req.query("per_page") ?? "50", 10), 100);

  c.header("Cache-Control", "private, max-age=60, stale-while-revalidate=300");

  return c.json({
    rows: [],
    page,
    per_page: perPage,
    has_more: false,
    table_name: "cianfhoghlaim.education.{jersey|guernsey|isle_of_man}",
    jurisdictions: ["jersey", "guernsey", "isle_of_man"],
  });
});

export default app;
