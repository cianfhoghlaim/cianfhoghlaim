/**
 * CopilotKit registry endpoint — the agent_registry_runtime wire-up.
 *
 * Per the 2026-09-24-web-agentic-deep-refactor-v1 change. Production
 * delegates to the canonical Python runtime at
 * `agents/integrations/agent_registry_runtime.py` (subprocess call to
 * `python -c "..."`). Dev mode returns the in-process fallback mirror
 * so the route works without starting the Agno runtime.
 *
 * The 3 canonical helpers:
 * - `register_all_agents_with_copilotkit()` — registers every
 *   agent in AGENT_REGISTRY with the CopilotKit runtime
 * - `collect_all_agui_events()` — collects every AG-UI
 *   registration event for the AG-UI protocol handshake
 * - `build_copilotkit_runtime_config()` — builds the canonical
 *   CopilotKit runtime config (agents + tools + metadata)
 *
 * Routes:
 * - GET  /api/copilotkit/registry/config   → build_copilotkit_runtime_config()
 * - GET  /api/copilotkit/registry/events   → collect_all_agui_events()
 * - GET  /api/copilotkit/registry/agents   → list agent names
 * - GET  /api/copilotkit/registry/schema    → Drizzle schema (tables + types)
 * - POST /api/copilotkit/registry/handshake → AG-UI protocol handshake
 *
 * Reference:
 *   agents/integrations/agent_registry_runtime.py
 */

import { Hono } from "hono";
import { devFallbackConfig } from "../../../apps/cianfhoghlaim-web/apps/api/src/copilotkit/_base";

const app = new Hono();

/**
 * Subprocess helper: invoke a Python expression via the
 * `python -c "..."` route and return the parsed JSON.
 * Uses `subprocess.execFile` (not `exec`) to avoid shell injection.
 */
async function invokePythonRuntime<T>(pythonExpr: string): Promise<T> {
  const { execFile } = await import("node:child_process");
  const { promisify } = await import("node:util");
  const execFileAsync = promisify(execFile);

  const repoRoot = process.env.REPO_ROOT ?? process.cwd();
  const { stdout } = await execFileAsync(
    "python",
    [
      "-c",
      `import json, sys; sys.path.insert(0, '${repoRoot}'); ` +
        `print(json.dumps(${pythonExpr}))`,
    ],
    { maxBuffer: 10 * 1024 * 1024 },
  );
  return JSON.parse(stdout) as T;
}

/**
 * Determine whether to use the production Python runtime or the dev fallback.
 * Set COPILOTKIT_DEV_MODE=1 to force dev fallback even in production (for
 * canary + smoke testing).
 */
function shouldUseDevFallback(): boolean {
  return process.env.COPILOTKIT_DEV_MODE === "1" || process.env.NODE_ENV !== "production";
}

async function getRuntimeConfig() {
  if (shouldUseDevFallback()) {
    return devFallbackConfig;
  }
  return invokePythonRuntime<typeof devFallbackConfig>(
    "agents.integrations.agent_registry_runtime.build_copilotkit_runtime_config()",
  );
}

async function getAguiEvents() {
  if (shouldUseDevFallback()) {
    return [];
  }
  return invokePythonRuntime<unknown[]>(
    "agents.integrations.agent_registry_runtime.collect_all_agui_events()",
  );
}

app.get("/api/copilotkit/registry/config", async (c) => {
  try {
    const config = await getRuntimeConfig();
    return c.json(config);
  } catch (err) {
    return c.json(
      { error: "Failed to load CopilotKit runtime config", details: String(err) },
      500,
    );
  }
});

app.get("/api/copilotkit/registry/events", async (c) => {
  try {
    const events = await getAguiEvents();
    return c.json({ events, count: events.length });
  } catch (err) {
    return c.json(
      { error: "Failed to collect AG-UI events", details: String(err) },
      500,
    );
  }
});

app.get("/api/copilotkit/registry/agents", async (c) => {
  try {
    const config = await getRuntimeConfig();
    const names = (config.agents ?? []).map((a) =>
      typeof a === "string" ? a : a.name
    );
    return c.json({ agents: names, count: names.length });
  } catch (err) {
    return c.json(
      { error: "Failed to list agents", details: String(err) },
      500,
    );
  }
});

/**
 * GET /api/copilotkit/registry/schema — the Drizzle schema mirror for the SPA.
 * Per the 2026-09-24 change, returns the table list + the K-12 agentic tables.
 */
app.get("/api/copilotkit/registry/schema", async (c) => {
  return c.json({
    tables: [
      "user", "session", "account", "organization", "member", "invitation", "jwks",
      "project",
      "student", "class_registry", "class_roster", "teacher_workload",
      "agent_lesson_plan", "agent_homework_item", "agent_cba_plan",
      "agent_wellbeing_checkin", "agent_exam_timetable", "agent_sen_record",
    ],
    k12_agentic_tables: [
      "agent_lesson_plan", "agent_homework_item", "agent_cba_plan",
      "agent_wellbeing_checkin", "agent_exam_timetable", "agent_sen_record",
    ],
    stage_taxonomy: ["aistear", "primary", "junior_cycle", "senior_cycle", "tertiary"],
    note: "Drizzle schema mirror; SPA uses this to know which tables back which actions",
  });
});

/**
 * POST /api/copilotkit/registry/handshake — the AG-UI protocol handshake.
 * The SPA sends the AG-UI protocol's register event; we acknowledge
 * and return the agent_registry_runtime config + the AG-UI events.
 */
app.post("/api/copilotkit/registry/handshake", async (c) => {
  try {
    const body = (await c.req.json().catch(() => ({}))) as {
      protocol?: string;
      agent?: { name: string };
      events?: unknown[];
    };
    const protocol = body.protocol ?? "ag-ui/v1";
    const events = await getAguiEvents();
    const config = await getRuntimeConfig();
    return c.json({
      acknowledged: true,
      protocol,
      runtime_config: config,
      registered_agents: config.agents,
      collected_events: { count: events.length, events },
      handshake_with: body.agent ?? null,
    });
  } catch (err) {
    return c.json(
      { error: "Handshake failed", details: String(err) },
      500,
    );
  }
});

export default app;
