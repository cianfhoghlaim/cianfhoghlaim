// apps/api/src/routers/content-types.ts
// The 6 cianfhoghlaim content types endpoint (per
// openspec/changes/cianfhoghlaim-website-rewrite/specs/.../spec.md R1 + R6).
// Returns the 6 content types + a stats summary. Backed by the BAML
// content_types.baml schema for the 6 functions.

import { Hono } from "hono";
import { AGENTS, getAgentById } from "../registry";
import { CONTENT_TYPES_LIST, TOTAL_CONTENT_COUNT, type ContentType } from "../content-types";

const types = new Hono();

// GET /api/content-types — list the 6 content types + their stats
types.get("/", (c) => {
  return c.json({
    content_types: CONTENT_TYPES_LIST,
    total_count: TOTAL_CONTENT_COUNT,
    agents: AGENTS.map((a) => ({
      id: a.id,
      name: a.name,
      content_types: a.content_types,
    })),
  });
});

// GET /api/content-types/:type — get info for a single content type
types.get("/:type", (c) => {
  const type = c.req.param("type") as ContentType;
  const ct = CONTENT_TYPES_LIST.find((t) => t.slug === type);
  if (!ct) {
    return c.json({ error: "Content type not found" }, 404);
  }
  return c.json({ content_type: ct });
});

export { types as contentTypes };