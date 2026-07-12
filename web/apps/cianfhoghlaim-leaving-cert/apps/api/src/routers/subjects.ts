// apps/api/src/routers/subjects.ts
// The 9 ADK agents metadata endpoint (8 NCCA + 1 cianfhoghlaim operator).
// Wired to apps/api/src/registry.ts.

import { Hono } from "hono";
import { AGENTS } from "../registry";

const subjects = new Hono();

subjects.get("/", (c) => {
  return c.json({
    status: "ok",
    count: AGENTS.length,
    agents: AGENTS.map((a) => ({
      id: a.id,
      name: a.name,
      name_ga: a.name_ga,
      role: a.role,
      color: a.color,
      eiraic_tier: a.eiraic_tier,
      baml_schema: a.baml_schema,
      dlt_source: a.dlt_source,
      cocoindex_path: a.cocoindex_path,
      notebook_path: a.notebook_path,
      tools: a.tools,
      content_types: a.content_types,
    })),
  });
});

subjects.get("/:subject", (c) => {
  const subject = c.req.param("subject");
  const agent = AGENTS.find((a) => a.id === subject);
  if (!agent) {
    return c.json({ error: "Subject not found" }, 404);
  }
  return c.json({ subject: agent });
});

export { subjects };